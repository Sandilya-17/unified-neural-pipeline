# src/api/routes_rest.py

import os
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from src.utils.audio_io import load_audio
from src.preprocess.denoise import denoise_audio
from src.diarization.diarizer import diarize_and_transcribe

router = APIRouter()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__ + "/../.."))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/process")
async def process_audio(mixture: UploadFile = File(...), target: UploadFile = File(...)):
    """
    REST endpoint to process mixture + target audio.
    Runs: denoise → diarization → speaker match → ASR
    """
    try:
        mix_path = os.path.join(UPLOAD_DIR, "mixture.wav")
        tgt_path = os.path.join(UPLOAD_DIR, "target.wav")

        # Save files
        with open(mix_path, "wb") as f:
            f.write(await mixture.read())
        with open(tgt_path, "wb") as f:
            f.write(await target.read())

        # Load & process
        mixture_audio, sr = load_audio(mix_path)
        target_audio, tsr = load_audio(tgt_path)

        denoised = denoise_audio(mixture_audio, sr)

        diarization_result = diarize_and_transcribe(
            denoised, sr, target_audio, tsr, use_demucs=False
        )

        return JSONResponse(diarization_result)

    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )
