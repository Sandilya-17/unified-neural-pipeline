# src/preprocess/vad.py

import numpy as np
import librosa

# ----------------------------------------
# CONFIG: Minimum valid chunk for ASR
# ----------------------------------------
MIN_CHUNK_SEC = 0.30   # 300 ms minimum allowed
DEFAULT_FRAME_MS = 30


def simple_vad(audio, sr, threshold=0.015, frame_ms=DEFAULT_FRAME_MS):
    """
    Very lightweight VAD for streaming.
    Returns True if speech is detected in the audio chunk.
    """
    frame_len = int(sr * frame_ms / 1000)
    if len(audio) < frame_len:
        return False

    rms = librosa.feature.rms(y=audio, frame_length=frame_len, hop_length=frame_len)[0]
    return bool(np.max(rms) > threshold)


def detect_voice_activity(audio, sr, frame_ms=DEFAULT_FRAME_MS, threshold=0.002):
    """
    Simple energy-based VAD.
    Returns a list of booleans per frame (True = speech)
    """
    frame_len = int(sr * frame_ms / 1000)
    frames = range(0, len(audio), frame_len)

    vad_marks = []
    for start in frames:
        end = min(start + frame_len, len(audio))
        frame = audio[start:end]
        energy = np.mean(frame ** 2)
        vad_marks.append(energy > threshold)

    return vad_marks, frame_len


def segment_audio_by_vad(
    audio,
    sr,
    frame_ms=DEFAULT_FRAME_MS,
    threshold=0.002,
    min_speech_ms=300,
    min_silence_ms=300
):
    """
    Convert VAD boolean frames into continuous timestamped speech segments.
    Returns list of:
        { "start": sec, "end": sec, "audio": numpy_array }
    """

    vad_marks, frame_len = detect_voice_activity(audio, sr, frame_ms, threshold)
    min_speech_frames = int(min_speech_ms / frame_ms)
    min_silence_frames = int(min_silence_ms / frame_ms)

    segments = []
    start_idx = None
    silence_count = 0

    for i, is_speech in enumerate(vad_marks):
        if is_speech:
            if start_idx is None:
                start_idx = i
            silence_count = 0

        else:
            if start_idx is not None:
                silence_count += 1

                if silence_count >= min_silence_frames:
                    end_idx = i - silence_count + 1

                    # Only keep long enough speech segments
                    if (end_idx - start_idx) >= min_speech_frames:
                        start = start_idx * frame_len
                        end = end_idx * frame_len

                        # ---- FIX: Skip extremely short chunks ----
                        if (end - start) / sr >= MIN_CHUNK_SEC:
                            segments.append({
                                "start": start / sr,
                                "end": end / sr,
                                "audio": audio[start:end].copy()
                            })

                    start_idx = None

    # Final unfinished speech region
    if start_idx is not None:
        end_idx = len(vad_marks)
        if (end_idx - start_idx) >= min_speech_frames:
            start = start_idx * frame_len
            end = len(audio)

            if (end - start) / sr >= MIN_CHUNK_SEC:
                segments.append({
                    "start": start / sr,
                    "end": end / sr,
                    "audio": audio[start:end].copy()
                })

    return segments
