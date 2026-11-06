"""Discussion en ligne de commande avec Walker SLM (avec RAG web)."""

import argparse
import os
import sys

import rag
import slm
from config import MODEL_PATH


def ask(question, use_web=True):
    chunks, sources = rag.retrieve(question, use_web=use_web)
    context = rag.build_context(chunks)
    answer = slm.answer(question, context)
    print("\n" + answer + "\n")
    if sources:
        print("Sources :")
        for s in sources:
            print(f" - {s['title']} ({s['url']})")


def main():
    parser = argparse.ArgumentParser(
        description="Walker SLM : petit modèle + RAG web"
    )
    parser.add_argument("question", nargs="?", help="question (sinon mode interactif)")
    parser.add_argument("--no-web", action="store_true", help="sans recherche web")
    args = parser.parse_args()

    if not os.path.exists(MODEL_PATH):
        print("Modèle absent. Lancez d'abord : python download_model.py")
        sys.exit(1)

    if args.question:
        ask(args.question, use_web=not args.no_web)
        return

    print("Walker SLM — tapez votre question (vide pour quitter).")
    while True:
        try:
            q = input("\nVous : ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q:
            break
        ask(q, use_web=not args.no_web)


if __name__ == "__main__":
    try:
        main()
    finally:
        slm.close()
