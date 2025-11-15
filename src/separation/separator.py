import numpy as np
import librosa


def simple_hpss_separation(audio, sr):
    """
    Simple HPSS-based separation that works on Windows.
    HPSS returns harmonic & percussive components of the waveform.
    """

    # Ensure float32 audio
    audio = audio.astype(np.float32)

    # Use librosa HPSS (built-in waveform HPSS)
    harmonic_audio, percussive_audio = librosa.effects.hpss(audio)

    return harmonic_audio.astype(np.float32), percussive_audio.astype(np.float32)


def energy_based_split(audio, sr):
    """
    Very basic placeholder separator.
    """
    audio = audio.astype(np.float32)
    mid = len(audio) // 2
    return audio[:mid], audio[mid:]
