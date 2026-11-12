"""TruthGuard AI API. Predictions are screening signals, not proof of truth."""
import os
from pathlib import Path
from typing import Literal

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "fake_news_pipeline.joblib"
app = FastAPI(title="TruthGuard AI API", version="1.0.0", description="Educational news-text screening API")
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])

class NewsRequest(BaseModel):
    text: str = Field(min_length=40, max_length=12000)

class NewsResponse(BaseModel):
    label: Literal["likely_real", "likely_fake", "uncertain"]
    confidence: float
    summary: str
    checks: list[str]


def load_model():
    if not MODEL_PATH.exists():
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception as exc:
        raise RuntimeError(f"Could not load model: {exc}") from exc

model = load_model()

@app.get("/")
def health():
    return {"name": "TruthGuard AI", "status": "ok", "model_loaded": model is not None}

@app.post("/predict", response_model=NewsResponse)
def predict(payload: NewsRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="The classifier has not been trained yet. Run backend/train.py with a labelled dataset.")
    try:
        prediction = int(model.predict([payload.text])[0])
        probabilities = model.predict_proba([payload.text])[0]
        confidence = float(max(probabilities)) * 100
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Model analysis failed.") from exc

    # Dataset convention: 1 = REAL, 0 = FAKE. The score describes model certainty only.
    if confidence < 65:
        label = "uncertain"
        summary = "The model is not confident enough to assign a useful screening label. Verify this claim independently."
    elif prediction == 1:
        label = "likely_real"
        summary = "The text resembles examples labelled as real in the training dataset. This does not independently verify the claims."
    else:
        label = "likely_fake"
        summary = "The text resembles examples labelled as fake in the training dataset. Treat this as a warning to investigate, not a verdict."

    return NewsResponse(label=label, confidence=round(confidence, 1), summary=summary, checks=[
        "Locate the original source and read the complete report, not just a repost or screenshot.",
        "Check publication date, author, cited documents, images, and links to primary evidence.",
        "Search for independent confirmation from reputable newsrooms or relevant official sources.",
        "Look for corrections, context, satire labels, or later updates before sharing."
    ])
