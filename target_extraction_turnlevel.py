# target_extraction_turnlevel.py
import os, json
from src.utils.audio_io import load_audio, save_audio, normalize_audio
from src.preprocess.denoise import denoise_audio
from src.diarization.diarizer import diarize_and_transcribe
from src.speaker.embedder import SpeakerEmbedder

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MIXTURE_PATH = os.path.join(PROJECT_ROOT, "data", "examples", "mixture_audio.wav")
TARGET_SAMPLE_PATH = os.path.join(PROJECT_ROOT, "data", "examples", "target.wav")
OUT_DIR = os.path.join(PROJECT_ROOT, "data", "outputs")
os.makedirs(OUT_DIR, exist_ok=True)
DIAR_JSON = os.path.join(OUT_DIR, "diarization_turns.json")
TARGET_WAV = os.path.join(OUT_DIR, "target_speaker.wav")

def run():
    print("Loading audio...")
    mixture, sr = load_audio(MIXTURE_PATH)
    target, tsr = load_audio(TARGET_SAMPLE_PATH)
    print("Denoising...")
    den = denoise_audio(mixture, sr)
    den = normalize_audio(den)

    print("Running turn-level diarization & ASR...")
    # create embedder and asr inside diarizer or pass custom ones
    diar = diarize_and_transcribe(den, sr, target, tsr, use_demucs=False)

    # Save target speaker combined audio (concat all target segments)
    target_segments = [d for d in diar if d["speaker"] == "Target"]
    if target_segments:
        # extract audio segments and concatenate from mixture for accurate audio
        import numpy as np
        from src.utils.audio_io import save_audio
        a_list = []
        for seg in target_segments:
            s_idx = int(seg["start"] * sr)
            e_idx = int(seg["end"] * sr)
            a_list.append(den[s_idx:e_idx])
        if a_list:
            merged = np.concatenate(a_list)
            save_audio(TARGET_WAV, merged, sr)
            print("Saved target_speaker.wav:", TARGET_WAV)

    # Write diarization JSON
    with open(DIAR_JSON, "w", encoding="utf-8") as f:
        json.dump(diar, f, indent=2, ensure_ascii=False)
    print("Saved diarization JSON:", DIAR_JSON)

if __name__ == "__main__":
    run()
