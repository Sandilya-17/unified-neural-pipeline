# target_extraction.py
"""
Run the offline pipeline:
- Load mixture and target sample from data/examples/
- Denoise -> VAD -> Separation -> Target matching -> ASR
- Save target_speaker.wav and diarization.json (simple format)
"""

import json
import os
from src.utils.audio_io import load_audio, save_audio, normalize_audio
from src.preprocess.denoise import denoise_audio
from src.preprocess.vad import simple_energy_vad
from src.separation.separator import simple_hpss_separation
from src.speaker.embedder import SpeakerEmbedder
from src.asr.asr_engine import WhisperASR

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# input files (place them in data/examples/)
MIXTURE_PATH = os.path.join(PROJECT_ROOT, "data", "examples", "mixture_audio.wav")
TARGET_SAMPLE_PATH = os.path.join(PROJECT_ROOT, "data", "examples", "target.wav")

# outputs
OUT_DIR = os.path.join(PROJECT_ROOT, "data", "outputs")
os.makedirs(OUT_DIR, exist_ok=True)
TARGET_SPEAKER_OUT = os.path.join(OUT_DIR, "target_speaker.wav")
DIARIZATION_JSON = os.path.join(OUT_DIR, "diarization.json")

# options
WHISPER_LOCAL_MODEL = None  # set to "models/whisper-small" if you downloaded model locally
WHISPER_MODEL = "openai/whisper-small"  # fallback HF name (we will use 'small' as requested)
DEVICE = "cpu"

def run_pipeline():
    # 1) load files
    print("Loading mixture and target sample...")
    mixture, sr = load_audio(MIXTURE_PATH)
    target, target_sr = load_audio(TARGET_SAMPLE_PATH)

    # 2) denoise mixture (optional)
    print("Denoising mixture...")
    denoised = denoise_audio(mixture, sr)
    denoised = normalize_audio(denoised)

    # 3) VAD (we will keep it simple: detect speech segments)
    print("Running VAD...")
    segments = simple_energy_vad(denoised, sr, frame_ms=30, threshold=0.0008)
    if len(segments) == 0:
        print("Warning: no speech segments found by VAD; proceeding with full audio")
        speech_audio = denoised
    else:
        # For now we concatenate speech regions into a continuous speech-only clip for separation
        from src.preprocess.vad import extract_speech
        speech_audio = extract_speech(denoised, sr, segments)

    # 4) Separation (simple HPSS-based)
    print("Running separation (simple HPSS)...")
    s1, s2 = simple_hpss_separation(speech_audio, sr)

    # 5) Speaker matching (embedding)
    print("Loading embedder and computing embeddings...")
    embedder = SpeakerEmbedder(device=DEVICE)
    # compute embeddings (embedder truncates long audio)
    emb_target = embedder.compute_embedding(target, target_sr)
    emb_s1 = embedder.compute_embedding(s1, sr)
    emb_s2 = embedder.compute_embedding(s2, sr)

    sim1 = embedder.cosine_similarity(emb_target, emb_s1)
    sim2 = embedder.cosine_similarity(emb_target, emb_s2)
    print("Similarity target->s1:", sim1)
    print("Similarity target->s2:", sim2)

    if sim1 > sim2:
        chosen = s1
        other = s2
        chosen_label = "Target"
        other_label = "Speaker_B"
    else:
        chosen = s2
        other = s1
        chosen_label = "Target"
        other_label = "Speaker_B"

    # save target speaker waveform
    save_audio(TARGET_SPEAKER_OUT, chosen, sr)
    print("Saved target speaker audio:", TARGET_SPEAKER_OUT)

    # 6) ASR for both streams
    print("Loading ASR model (Whisper-Small)...")
    asr = WhisperASR(model_name_or_path=WHISPER_MODEL, device=DEVICE, local_model_path=WHISPER_LOCAL_MODEL)

    print("Transcribing chosen (target) speaker...")
    text_target, conf_target = asr.transcribe(chosen, sr, max_length_seconds=60)
    print("Target transcript:", text_target, "conf:", conf_target)

    print("Transcribing other speaker...")
    text_other, conf_other = asr.transcribe(other, sr, max_length_seconds=60)
    print("Other transcript:", text_other, "conf:", conf_other)

    # 7) build simple diarization JSON (for now single segment per speaker)
    # Use 0.0 -> duration since we don't have per-turn segmentation yet.
    duration_sec = float(len(speech_audio) / sr)
    diar = [
        {
            "speaker": chosen_label,
            "start": 0.0,
            "end": duration_sec,
            "text": text_target,
            "confidence": round(conf_target, 4)
        },
        {
            "speaker": other_label,
            "start": 0.0,
            "end": duration_sec,
            "text": text_other,
            "confidence": round(conf_other, 4)
        }
    ]

    with open(DIARIZATION_JSON, "w", encoding="utf-8") as f:
        json.dump(diar, f, indent=2, ensure_ascii=False)

    print("Saved diarization JSON:", DIARIZATION_JSON)
    print("Pipeline finished.")

if __name__ == "__main__":
    # check inputs exist
    if not os.path.exists(MIXTURE_PATH):
        print("Error: mixture file not found:", MIXTURE_PATH)
        raise SystemExit(1)
    if not os.path.exists(TARGET_SAMPLE_PATH):
        print("Error: target sample not found:", TARGET_SAMPLE_PATH)
        raise SystemExit(1)

    run_pipeline()
