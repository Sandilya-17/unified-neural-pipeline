from src.utils.audio_io import load_audio, save_audio
from src.preprocess.denoise import denoise_audio

audio, sr = load_audio("data/examples/test.wav")
clean = denoise_audio(audio, sr)

save_audio("data/examples/clean.wav", clean, sr)

print("Denoising complete. File saved as clean.wav")
