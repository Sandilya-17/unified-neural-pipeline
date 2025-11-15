# src/asr/final_pass.py
from src.asr.asr_engine import WhisperASR
from src.postprocess.punctuator import Punctuator
from src.utils.audio_io import load_audio
import json
import numpy as np


def final_whisper_pass(audio_path, output_json=None, device="cpu"):
    """
    High-quality ASR + punctuation restoration.
    Runs Whisper-Small on the final target_speaker.wav
    """

    audio, sr = load_audio(audio_path)

    # Whisper-Small model
    asr = WhisperASR(
        model_name_or_path="openai/whisper-small",
        device=device
    )
    text, conf = asr.transcribe(audio, sr)

    # Punctuation restoration
    p = Punctuator(device=device)
    final_text = p.restore(text)

    result = {
        "text": final_text,
        "confidence": conf
    }

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m src.asr.final_pass <audiofile.wav>")
        exit()

    r = final_whisper_pass(sys.argv[1])
    print(r)
