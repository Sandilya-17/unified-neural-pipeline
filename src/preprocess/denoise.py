import numpy as np
import librosa


def denoise_audio(audio, sr, n_fft=2048, prop_decrease=1.0):
    """
    Pure-Python spectral gating noise reduction.
    Works on Windows without external libraries.
    """
    # STFT
    stft = librosa.stft(audio, n_fft=n_fft)
    magnitude, phase = np.abs(stft), np.angle(stft)

    # Estimate noise from first 0.5 seconds
    noise_frames = int(0.5 * sr / (n_fft // 4))
    noise_profile = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)

    # Apply spectral gating
    magnitude_denoised = np.maximum(magnitude - prop_decrease * noise_profile, 0.0)

    # Reconstruct
    denoised_stft = magnitude_denoised * np.exp(1j * phase)
    denoised_audio = librosa.istft(denoised_stft)
    return denoised_audio.astype(np.float32)
