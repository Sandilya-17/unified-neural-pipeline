# src/diarization/diarizer.py

import numpy as np
from src.preprocess.vad import segment_audio_by_vad
from src.speaker.embedder import SpeakerEmbedder
from src.asr.asr_tiny import TinyWhisperASR
from src.postprocess.punctuator import Punctuator
from src.separation.selector import separate_audio


def diarize_and_transcribe(audio, sr, target_audio, target_sr, use_demucs=True):
    """
    Perform:
        - VAD segmentation
        - Speaker embedding matching
        - Chunk ASR
        - Punctuation restoration
    """

    # 1. VAD
    print("→ Segmenting with VAD...")
    segments = segment_audio_by_vad(audio, sr)
    print(f"→ {len(segments)} VAD chunks found.")

    # 2. Speaker embedder (WavLM)
    print("→ Loading speaker embedder...")
    embedder = SpeakerEmbedder()
    print("→ Extracting target speaker embedding...")
    target_emb = embedder.embed(target_audio, target_sr)

    # 3. ASR model (Tiny)
    asr = TinyWhisperASR(device="cpu")

    # 4. Punctuator
    punct = Punctuator()


    diar = []

    for idx, seg in enumerate(segments):
        print(f"--- Processing chunk {idx+1}/{len(segments)} ---")

        # Speaker similarity
        emb = embedder.embed(seg["audio"], sr)
        similarity = float(np.dot(emb, target_emb))
        speaker = "Target" if similarity >= 0.6 else "Other"

        # ASR
        text, conf = asr.transcribe(seg["audio"], sr)
        text = punct.restore(text)

        diar.append({
            "speaker": speaker,
            "start": float(seg["start"]),
            "end": float(seg["end"]),
            "text": text.strip(),
            "confidence": float(conf)
        })

    return diar
