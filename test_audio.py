from src.utils.audio_io import load_audio, save_audio

audio, sr = load_audio("data/examples/test.wav")
print("Loaded audio with sample rate:", sr)
print("Audio length:", len(audio))

save_audio("data/examples/out.wav", audio, sr)
print("Saved file!")
