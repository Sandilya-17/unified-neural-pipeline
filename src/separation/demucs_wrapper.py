# src/separation/demucs_wrapper.py
import os
import tempfile
import numpy as np
from pathlib import Path
from typing import List, Tuple

try:
    # demucs provides an inference CLI and python API
    from demucs.apply import apply_model
    from demucs.pretrained import get_model
    DEMUCS_AVAILABLE = True
except Exception:
    DEMUCS_AVAILABLE = False

from ..utils.audio_io import save_audio, pad_audio

def demucs_separate(audio: np.ndarray, sr: int, model_name: str = "htdemucs") -> List[Tuple[np.ndarray,int]]:
    """
    Use Demucs to perform separation. Returns list of numpy arrays (sources).
    If demucs is not available, raises RuntimeError.
    """
    if not DEMUCS_AVAILABLE:
        raise RuntimeError("Demucs not available")

    # demucs expects files; write a temp wav
    import soundfile as sf
    tmpdir = tempfile.mkdtemp(prefix="demucs_tmp_")
    in_path = os.path.join(tmpdir, "input.wav")
    sf.write(in_path, audio, sr)

    model = get_model(model_name)
    # apply_model returns tuple (sources, rates) for each segment; use single file call
    sources = apply_model(model, in_path, tmpdir, shifts=1, overlap=0.25, device='cpu')

    # apply_model can save to disk; we'll try to load the output folder
    out_dir = os.path.join(tmpdir, "separated")
    results = []
    if os.path.isdir(out_dir):
        # demucs writes per-source wavs; load them
        for f in sorted(os.listdir(out_dir)):
            if f.endswith(".wav"):
                path = os.path.join(out_dir, f)
                import soundfile as sf
                y, r = sf.read(path)
                # ensure mono float32
                if y.ndim > 1:
                    y = y.mean(axis=1)
                results.append((y.astype("float32"), r))
    # cleanup optional: keep tmpdir for debugging; you can remove if desired
    return results
