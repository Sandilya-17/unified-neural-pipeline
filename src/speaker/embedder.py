# src/speaker/embedder.py
"""
Speaker Embedding Extraction using WavLM (Stable Version)
Uses AutoFeatureExtractor because WavLMFeatureExtractor is deprecated /
removed in new Transformers releases.
"""

import torch
import numpy as np
import librosa
from transformers import AutoFeatureExtractor, WavLMForXVector


class SpeakerEmbedder:
    def __init__(self, device="cpu"):
        self.device = device

        # Microsoft WavLM speaker verification model
        self.model_name = "microsoft/wavlm-base-plus-sv"

        # AutoFeatureExtractor works for all versions of Transformers
        self.extractor = AutoFeatureExtractor.from_pretrained(self.model_name)

        # Load model
        self.model = WavLMForXVector.from_pretrained(self.model_name).to(self.device)

    def _preprocess(self, audio, sr):
        """
        Resample audio to 16 kHz & prepare inputs.
        """
        if sr != 16000:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            sr = 16000

        inputs = self.extractor(
            audio,
            sampling_rate=sr,
            return_tensors="pt",
            padding=True
        ).to(self.device)

        return inputs

    def embed(self, audio, sr):
        """
        Compute speaker embedding (768-dim, L2-normalized).
        """

        inputs = self._preprocess(audio, sr)

        with torch.no_grad():
            emb = self.model(**inputs).embeddings  # [1, 768]

        emb = emb.cpu().numpy()[0]

        # L2 normalize (important for cosine similarity)
        emb = emb / (np.linalg.norm(emb) + 1e-8)

        return emb
