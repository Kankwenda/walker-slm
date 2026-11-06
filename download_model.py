"""Télécharge le modèle GGUF depuis Hugging Face (premier lancement).

Le modèle (~378 Mo) n'est pas dans le dépôt : GitHub refuse les fichiers
de plus de 100 Mo. Il est téléchargé une seule fois, puis vérifié
(taille + SHA-256).
"""

import hashlib
import os
import sys
import urllib.request

from config import MODEL_PATH, MODEL_SHA256, MODEL_SIZE, MODEL_URL


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    if os.path.exists(MODEL_PATH):
        size = os.path.getsize(MODEL_PATH)
        if size == MODEL_SIZE and _sha256(MODEL_PATH) == MODEL_SHA256:
            print(f"Modèle déjà présent et valide : {MODEL_PATH} ({size} octets)")
            return
        print("Fichier présent mais invalide, nouveau téléchargement...")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    print(f"Téléchargement : {MODEL_URL}")
    print(f"Taille attendue : {MODEL_SIZE} octets (~378 Mo)")

    last = [0]

    def progress(blocks, block_size, total):
        done = blocks * block_size
        pct = min(100, done * 100 // total) if total else 0
        if pct - last[0] >= 10:
            last[0] = pct
            print(f"  {pct}% ({done // 1024 // 1024} Mo)")

    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, reporthook=progress)

    size = os.path.getsize(MODEL_PATH)
    digest = _sha256(MODEL_PATH)
    if size != MODEL_SIZE or digest != MODEL_SHA256:
        print(f"ERREUR : fichier invalide (taille {size}, sha256 {digest})")
        sys.exit(1)
    print(f"Modèle prêt : {MODEL_PATH} ({size} octets, sha256 vérifié)")


if __name__ == "__main__":
    main()
