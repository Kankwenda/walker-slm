"""Tests hors-ligne du RAG léger (aucun modèle, aucun réseau)."""

from rag import build_context, chunk_text, rank_chunks


def test_chunk_text_coupe_en_morceaux():
    text = "Première phrase. Deuxième phrase. Troisième phrase. Quatrième phrase."
    chunks = chunk_text(text, size=30, overlap=5)
    assert len(chunks) >= 2
    assert all(len(c) <= 32 for c in chunks)
    assert "Première phrase" in chunks[0]


def test_chunk_text_vide():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_rank_chunks_garde_le_bon_morceau():
    chunks = [
        "Le ciel est bleu aujourd'hui.",
        "La capitale de la RDC est Kinshasa, ville sur le fleuve Congo.",
        "Les chats dorment beaucoup.",
    ]
    top = rank_chunks(chunks, "Quelle est la capitale de la RDC ?", top_n=1)
    assert top == [chunks[1]]


def test_build_context_numerote():
    ctx = build_context(["premier extrait", "deuxième extrait"])
    assert "[1] premier extrait" in ctx
    assert "[2] deuxième extrait" in ctx
    assert build_context([]) == ""
