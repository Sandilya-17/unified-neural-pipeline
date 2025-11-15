from src.utils.audio_io import load_audio, save_audio
from src.preprocess.vad import simple_energy_vad, extract_speech

audio, sr = load_audio("data/examples/test.wav")
segments = simple_energy_vad(audio, sr)

print("Detected speech segments:")
for seg in segments:
    print(seg)

speech_audio = extract_speech(audio, sr, segments)
save_audio("data/examples/speech_only.wav", speech_audio, sr)

print("Saved speech_only.wav (silence removed)")
