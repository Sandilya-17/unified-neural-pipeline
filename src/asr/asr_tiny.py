# src/asr/asr_tiny.py

import numpy as np
import torch
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq


class TinyWhisperASR:
    """
    Very fast ASR using Whisper-Tiny model.
    CPU-friendly, used for chunk-level diarization.
    """

    def __init__(self, device="cpu", local_model_path=None):
        self.device = device
        model_id = local_model_path if local_model_path else "openai/whisper-tiny"

        # Processor (tokenizer + feature extractor)
        self.processor = AutoProcessor.from_pretrained(model_id)

        # ASR model
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id).to(device)

    def transcribe(self, audio: np.ndarray, sr: int):
        """
        Transcribe a single audio chunk.
        Returns: text, confidence
        """

        # Resample to 16k
        if sr != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            sr = 16000

        inputs = self.processor(
            audio,
            sampling_rate=sr,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            generated = self.model.generate(
                **inputs,
                max_new_tokens=64,
                do_sample=False
            )

        text = self.processor.batch_decode(generated, skip_special_tokens=True)[0]

        # crude confidence estimate (for compatibility)
        confidence = 0.8 if len(text.strip()) > 0 else 0.1

        return text.strip(), confidence
