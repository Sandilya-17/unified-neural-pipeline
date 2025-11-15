# src/api/server.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes_rest import router as rest_router
from src.api.routes_ws import router as ws_router

app = FastAPI(
    title="Unified Neural Pipeline API",
    description="Speaker Targeting + Diarization + ASR",
    version="1.0.0"
)

# CORS for React UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Register API routers
app.include_router(rest_router, prefix="/api")
app.include_router(ws_router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
