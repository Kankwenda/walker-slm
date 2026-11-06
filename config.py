"""Configuration de Walker SLM.

Modèle vérifié sur Hugging Face le 2026-11-06 :
SmolLM2-135M-Instruct-Q8_0.gguf = 144 811 360 octets (~138 Mo).
Le 360M ne rentre pas sous 200 Mo (son plus petit fichier fait 209 Mo).
"""

import os

MODEL_REPO = "bartowski/SmolLM2-135M-Instruct-GGUF"
MODEL_FILE = "SmolLM2-135M-Instruct-Q8_0.gguf"
MODEL_URL = f"https://huggingface.co/{MODEL_REPO}/resolve/main/{MODEL_FILE}"
MODEL_SIZE = 144811360
# SHA-256 du fichier (oid LFS sur Hugging Face), vérifié au téléchargement.
MODEL_SHA256 = "5a1395716f7913741cc51d98581b9b1228d80987a9f7d3664106742eb06bba83"

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
