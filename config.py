"""Configuration de Walker SLM.

Modèle vérifié sur Hugging Face le 2026-11-06 :
Qwen3-0.6B-Q4_K_M.gguf = 396 705 472 octets (~378 Mo).
Choisi après tests en direct : SmolLM2-360M (219 Mo) répondait mais
dérivait et inventait trop ; Qwen3-0.6B est nettement meilleur en français
et en raisonnement, pour une taille encore raisonnable sur téléphone.
Conversion GGUF par Unsloth du modèle Qwen3 d'Alibaba (Apache-2.0).
"""

import os

MODEL_REPO = "unsloth/Qwen3-0.6B-GGUF"
MODEL_FILE = "Qwen3-0.6B-Q4_K_M.gguf"
MODEL_URL = f"https://huggingface.co/{MODEL_REPO}/resolve/main/{MODEL_FILE}"
MODEL_SIZE = 396705472
# SHA-256 du fichier (oid LFS sur Hugging Face), vérifié au téléchargement.
MODEL_SHA256 = "ac2d97712095a558e31573f62f466a3f9d93990898b0ec79d7c974c1780d524a"

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
