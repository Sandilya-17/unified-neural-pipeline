from src.utils.audio_io import load_audio, save_audio
from src.separation.separator import simple_hpss_separation

audio, sr = load_audio("data/examples/test.wav")
s1, s2 = simple_hpss_separation(audio, sr)

save_audio("data/examples/speaker1.wav", s1, sr)
save_audio("data/examples/speaker2.wav", s2, sr)

print("Separation complete!")
