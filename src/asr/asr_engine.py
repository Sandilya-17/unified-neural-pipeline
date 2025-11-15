# src/asr/asr_engine.py
"""
Stable Whisper ASR for Transformers 4.40+ (no encoder_attention_mask argument).
Uses safe token limits and chunk truncation for CPU speed.
"""

import os
import torch
import librosa
import numpy as np
import torch.nn.functional as F
from transformers import WhisperProcessor, WhisperForConditionalGeneration


class WhisperASR:
    def __init__(
        self,
        model_name_or_path="openai/whisper-small",
        device="cpu",
        local_model_path=None,
        max_new_tokens=120,          # safe limit
        max_audio_sec=30,            # limit each chunk length
    ):
        self.device = device
        self.max_new_tokens = max_new_tokens
        self.max_audio_sec = max_audio_sec

        # Select model source
        model_source = local_model_path if local_model_path else model_name_or_path

        # Load Whisper processor + model
        self.processor = WhisperProcessor.from_pretrained(model_source)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_source).to(device)

        # Force English transcription
        self.language = "en"
        self.task = "transcribe"

        # Set forced decoder prompt IDs
        try:
            self.model.config.forced_decoder_ids = (
                self.processor.get_decoder_prompt_ids(
                    language=self.language,
                    task=self.task
                )
            )
        except Exception:
            pass

    def transcribe(
        self,
        audio: np.ndarray,
        sr: int,
        max_length_seconds: int = None,
        max_new_tokens: int = None
    ):
        """
        Transcribe audio and return (text, confidence)
        """

        # Apply defaults
        if max_length_seconds is None:
            max_length_seconds = self.max_audio_sec
        if max_new_tokens is None:
            max_new_tokens = self.max_new_tokens

        # --- 1) Clip audio ---
        max_len = int(sr * max_length_seconds)
        if len(audio) > max_len:
            audio = audio[:max_len]

        # --- 2) Resample to 16k ---
        if sr != 16000:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            sr = 16000

        # --- 3) Prepare features ---
        inputs = self.processor(
            audio,
            sampling_rate=sr,
            return_tensors="pt",
            padding=True
        ).to(self.device)

        input_features = inputs.input_features

        # --- 4) Generate transcription ---
        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    input_features,
                    return_dict_in_generate=True,
                    output_scores=True,
                    max_new_tokens=max_new_tokens,
                    task="transcribe",
                    language="en",
                )
        except ValueError:
            # fallback for token overflow
            with torch.no_grad():
                outputs = self.model.generate(
                    input_features,
                    return_dict_in_generate=True,
                    output_scores=True,
                    max_new_tokens=80,
                    task="transcribe",
                    language="en",
                )

        # --- 5) Decode text ---
        text = self.processor.batch_decode(
            outputs.sequences,
            skip_special_tokens=True
        )[0].strip()

        # --- 6) Compute confidence ---
        confidence = 0.0
        try:
            scores = outputs.scores
            max_probs = []
            for s in scores:
                probs = F.softmax(s, dim=-1)
                maxp = float(probs.max(dim=-1)[0].mean().cpu().numpy())
                max_probs.append(maxp)
            if max_probs:
                confidence = float(np.mean(max_probs))
        except Exception:
            confidence = 0.0

        return text, confidence
