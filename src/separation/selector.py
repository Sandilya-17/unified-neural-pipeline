# src/separation/selector.py

from .separator import simple_hpss_separation

try:
    from .demucs_wrapper import demucs_separate, DEMUCS_AVAILABLE
except:
    DEMUCS_AVAILABLE = False


def separate_audio(audio, sr, prefer_demucs=True):
    """
    Use Demucs if installed, fallback to HPSS if not.
    Returns a list of separated sources.
    """

    if prefer_demucs and DEMUCS_AVAILABLE:
        try:
            outs = demucs_separate(audio, sr)
            if len(outs) >= 2:
                return [outs[0][0], outs[1][0]]
        except:
            pass

    # fallback if demucs fails
    s1, s2 = simple_hpss_separation(audio, sr)
    return [s1, s2]
