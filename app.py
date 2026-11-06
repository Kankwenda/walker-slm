"""API locale Walker SLM : POST /chat répond avec RAG web + petit modèle.

Clé API (optionnelle) : si la variable d'environnement WALKER_SLM_API_KEY
est définie au lancement, POST /chat exige l'en-tête X-API-Key avec cette
valeur (sinon 401). Sans la variable, l'API reste ouverte en local.
"""

import os

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

import rag
import slm
from config import HOST, MODEL_FILE, MODEL_PATH, PORT

app = FastAPI(title="Walker SLM", version="1.0.0")

# Clé secrète lue au lancement (vide = pas de contrôle, usage local).
API_KEY = os.environ.get("WALKER_SLM_API_KEY")


def _check_key(x_api_key: str | None):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(
            401, "Clé API manquante ou invalide (en-tête X-API-Key)"
        )


class ChatIn(BaseModel):
    question: str = Field(..., min_length=1)
    use_web: bool = True
    max_tokens: int = 512


class ChatOut(BaseModel):
    answer: str
    sources: list
    model: str


@app.get("/")
def root():
    return {"service": "walker-slm", "model": MODEL_FILE, "status": "ok"}


@app.get("/health")
def health():
    return {"model_present": os.path.exists(MODEL_PATH), "model": MODEL_FILE}


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn, x_api_key: str | None = Header(default=None)):
    _check_key(x_api_key)
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(
            503, "Modèle absent : lancez d'abord python download_model.py"
        )
    chunks, sources = rag.retrieve(body.question, use_web=body.use_web)
    context = rag.build_context(chunks)
    try:
        answer = slm.answer(body.question, context, max_tokens=body.max_tokens)
    except Exception as e:
        raise HTTPException(500, f"Erreur du modèle : {e}")
    return ChatOut(answer=answer, sources=sources, model=MODEL_FILE)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
