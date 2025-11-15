from src.utils.audio_io import load_audio
from src.speaker.embedder import SpeakerEmbedder
from src.separation.separator import simple_hpss_separation

print("Loading audio files...")

try:
    audio, sr = load_audio("data/examples/test.wav")
    print("Loaded test.wav OK")
except Exception as e:
    print("ERROR loading test.wav:", e)
    exit()

try:
    target_audio, target_sr = load_audio("data/examples/target.wav")
    print("Loaded target.wav OK")
except Exception as e:
    print("ERROR loading target.wav:", e)
    exit()

print("Running separation...")
s1, s2 = simple_hpss_separation(audio, sr)

print("Speaker 1 length (samples):", len(s1))
print("Speaker 2 length (samples):", len(s2))

embedder = SpeakerEmbedder()

print("Computing embeddings...")

try:
    emb_target = embedder.compute_embedding(target_audio, target_sr)
    print("Target embedding OK")
    print("Computing speaker 1 embedding...")

except Exception as e:
    print("ERROR embedding target:", e)
    exit()

try:
    emb_s1 = embedder.compute_embedding(s1, sr)
    print("Speaker 1 embedding OK")
    print("Computing speaker 1 embedding...")

except Exception as e:
    print("ERROR embedding speaker 1:", e)
    exit()

try:
    emb_s2 = embedder.compute_embedding(s2, sr)
    print("Speaker 2 embedding OK")
    print("Computing speaker 2 embedding...")

except Exception as e:
    print("ERROR embedding speaker 2:", e)
    exit()

print("Calculating similarities...")

sim1 = embedder.cosine_similarity(emb_target, emb_s1)
sim2 = embedder.cosine_similarity(emb_target, emb_s2)

print("Similarity with Speaker 1:", sim1)
print("Similarity with Speaker 2:", sim2)

if sim1 > sim2:
    print("Target speaker is: SPEAKER 1")
else:
    print("Target speaker is: SPEAKER 2")
