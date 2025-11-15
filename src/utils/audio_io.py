import librosa
import soundfile as sf
import numpy as np


def load_audio(path, target_sr=16000):
    """
    Loads an audio file, converts to mono, and resamples to target_sr.
    Returns waveform (numpy array) and sample rate.
    """
    audio, sr = librosa.load(path, sr=None, mono=True)
    if sr != target_sr:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
        sr = target_sr
    return audio, sr


def save_audio(path, audio, sr=16000):
    """Saves audio waveform to disk."""
    sf.write(path, audio, sr)


def normalize_audio(audio):
    """Normalizes audio to -1 to 1 range."""
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val
    return audio


def chunk_audio(audio, sr, chunk_ms=500):
    """
    Splits audio into fixed-size chunks (useful for streaming).
    Each chunk = chunk_ms milliseconds.
    """
    chunk_len = int(sr * (chunk_ms / 1000))
    for i in range(0, len(audio), chunk_len):
        yield audio[i:i + chunk_len]


def pad_audio(audio, target_len):
    """Pad audio to target length."""
    if len(audio) >= target_len:
        return audio[:target_len]
    pad_length = target_len - len(audio)
    return np.pad(audio, (0, pad_length))
