# src/api/routes_ws.py

import os
import json
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.speaker.embedder import SpeakerEmbedder
from src.utils.audio_io import load_audio
from src.asr.asr_tiny import TinyWhisperASR
from src.preprocess.vad import simple_vad

router = APIRouter()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__ + "/../.."))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

asr = TinyWhisperASR()

class WSManager:
    def __init__(self):
        self.active = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

manager = WSManager()

@router.websocket("/ws/stream")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)

    buffer = np.array([], dtype=np.float32)

    await ws.send_json({"status": "connected"})

    try:
        while True:
            chunk = await ws.receive_bytes()

            # Convert bytes → float32 audio
            audio = np.frombuffer(chunk, dtype=np.float32)
            buffer = np.concatenate([buffer, audio])

            # VAD triggers ASR
            if simple_vad(buffer):
                text, conf = asr.transcribe(buffer, 16000)

                await ws.send_json({
                    "text": text,
                    "confidence": conf
                })

    except WebSocketDisconnect:
        manager.disconnect(ws)
