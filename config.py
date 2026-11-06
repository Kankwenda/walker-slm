"""Configuration de Walker SLM.

Modèle vérifié sur Hugging Face le 2026-11-06 :
SmolLM2-360M-Instruct-Q4_0.gguf = 229 733 280 octets (~219 Mo).
Choisi après tests en direct : le 135M-Q8_0 (138 Mo) était trop faible
(répétitions, boucles) ; le 360M répond en français aux questions simples.
"""

import os

MODEL_REPO = "bartowski/SmolLM2-360M-Instruct-GGUF"
MODEL_FILE = "SmolLM2-360M-Instruct-Q4_0.gguf"
MODEL_URL = f"https://huggingface.co/{MODEL_REPO}/resolve/main/{MODEL_FILE}"
MODEL_SIZE = 229733280
# SHA-256 du fichier (oid LFS sur Hugging Face), vérifié au téléchargement.
MODEL_SHA256 = "c3608933eb6e5763b87f769bda40c204dc158333668c7af214644fe39da58627"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)
DOCS_DIR = os.path.join(BASE_DIR, "docs")

# Modèle : contexte et génération.
N_CTX = 4096
MAX_TOKENS = 512
TEMPERATURE = 0.3  # basse : on veut des réponses fidèles aux extraits.
TOP_P = 0.9

# RAG léger.
SEARCH_RESULTS = 5
CHUNK_CHARS = 600
CHUNK_OVERLAP = 100
TOP_CHUNKS = 4

# API locale.
HOST = "127.0.0.1"
PORT = 8000
