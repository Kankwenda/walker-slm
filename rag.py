"""RAG léger pour Walker SLM : web en direct + documents locaux, sans base.

Il n'y a pas de base de connaissances intégrée, pas de base vectorielle et
pas d'embeddings : à chaque question, on cherche sur le web (DuckDuckGo, sans
clé API), on télécharge les pages, on les découpe en morceaux et on garde les
morceaux qui partagent le plus de mots avec la question. Les fichiers .txt
et .md placés dans docs/ sont traités de la même façon.
"""

import html
import os
import re
from html.parser import HTMLParser

import requests

from config import CHUNK_CHARS, CHUNK_OVERLAP, DOCS_DIR, SEARCH_RESULTS, TOP_CHUNKS

STOPWORDS = set(
    "le la les de des du un une et ou à au aux en dans sur pour que qui quoi "
    "ce cet cette ces il elle ils elles nous vous je tu me te se son sa ses "
    "leur leurs est sont ai as a ont être avoir pas plus moins très avec sans "
    "chez par comme tout tous toute toutes même aussi ne ni y c d j l m n s t".split()
)

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) WalkerSLM/1.0"}


class _TextExtractor(HTMLParser):
    """Extrait le texte lisible d'une page HTML (sans scripts ni menus)."""

    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav", "header", "footer", "noscript", "form"):
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "header", "footer", "noscript", "form"):
            self.skip = False
        if tag in ("p", "div", "h1", "h2", "h3", "h4", "li", "article", "section", "tr"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def clean_text(text):
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def fetch_text(url, timeout=12, max_chars=20000):
    """Télécharge une page et renvoie son texte lisible (chaîne vide si échec)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        parser = _TextExtractor()
        parser.feed(resp.text)
        return clean_text(" ".join(parser.parts))[:max_chars]
    except Exception:
        return ""


def search_web(query, max_results=SEARCH_RESULTS):
    """Recherche web sans clé API. Renvoie [{title, url, snippet}]."""
    try:
        from ddgs import DDGS

        with DDGS() as ddgs:
            out = []
            for r in ddgs.text(query, max_results=max_results):
                out.append(
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", ""),
                    }
                )
            return out
    except Exception:
        return _search_web_html(query, max_results)


def _search_web_html(query, max_results=SEARCH_RESULTS):
    """Secours : page HTML de DuckDuckGo, sans dépendance."""
    try:
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=HEADERS,
            timeout=12,
        )
        resp.raise_for_status()
        out = []
        for m in re.finditer(
            r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
            r".*?class=\"result__snippet\"[^>]*>(.*?)</a>",
            resp.text,
            re.S,
        ):
            url = html.unescape(m.group(1))
            title = clean_text(re.sub(r"<[^>]+>", "", m.group(2)))
            snippet = clean_text(re.sub(r"<[^>]+>", "", m.group(3)))
            out.append({"title": title, "url": url, "snippet": snippet})
            if len(out) >= max_results:
                break
        return out
    except Exception:
        return []


def chunk_text(text, size=CHUNK_CHARS, overlap=CHUNK_OVERLAP):
    """Découpe un texte en morceaux d'environ `size` caractères."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?…])\s+", text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) + 1 <= size:
            current = (current + " " + s).strip()
        else:
            if current:
                chunks.append(current)
            tail = current[-overlap:] if len(current) > overlap else current
            current = (tail + " " + s).strip() if tail else s
            while len(current) > size:
                chunks.append(current[:size])
                current = current[size:]
    if current:
        chunks.append(current)
    return chunks


def _terms(question):
    words = re.findall(r"[a-zàâäéèêëîïôöùûüç0-9]+", (question or "").lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]


def rank_chunks(chunks, question, top_n=TOP_CHUNKS):
    """Garde les morceaux qui partagent le plus de mots avec la question."""
    terms = _terms(question)
    if not terms:
        return chunks[:top_n]
    scored = []
    for c in chunks:
        low = c.lower()
        hits = sum(1 for t in terms if t in low)
        count = sum(low.count(t) for t in terms)
        scored.append((hits, count, c))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [c for _, _, c in scored[:top_n]]


def rank_pairs(pairs, question, top_n=TOP_CHUNKS):
    """Comme rank_chunks, mais garde la source de chaque morceau."""
    terms = _terms(question)
    if not terms:
        return pairs[:top_n]
    scored = []
    for ch, label, url in pairs:
        low = ch.lower()
        hits = sum(1 for t in terms if t in low)
        count = sum(low.count(t) for t in terms)
        scored.append((hits, count, ch, label, url))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [(c, l, u) for _, _, c, l, u in scored[:top_n]]


def retrieve(question, use_web=True, docs_dir=DOCS_DIR):
    """Cherche les passages utiles : web + fichiers de docs/.

    Renvoie (morceaux, sources) où sources = [{title, url}] pour citer.
    """
    sources = []
    if use_web:
        for r in search_web(question):
            text = fetch_text(r["url"])
            if text:
                sources.append((text, r["title"] or r["url"], r["url"]))
    if docs_dir and os.path.isdir(docs_dir):
        for name in sorted(os.listdir(docs_dir)):
            if name.endswith((".txt", ".md")):
                path = os.path.join(docs_dir, name)
                try:
                    with open(path, encoding="utf-8", errors="ignore") as f:
                        sources.append((f.read(), name, name))
                except OSError:
                    pass
    pairs = []
    for text, label, url in sources:
        for ch in chunk_text(text):
            pairs.append((ch, label, url))
    if not pairs:
        return [], []
    top = rank_pairs(pairs, question)
    chunks = [c for c, _, _ in top]
    seen = []
    for _, label, url in top:
        if (label, url) not in [(s["title"], s["url"]) for s in seen]:
            seen.append({"title": label, "url": url})
    return chunks, seen


def build_context(chunks):
    """Met en forme les morceaux retenus pour le prompt du modèle."""
    if not chunks:
        return ""
    parts = ["Extraits à utiliser pour répondre :"]
    for i, ch in enumerate(chunks, 1):
        parts.append(f"[{i}] {ch}")
    return "\n".join(parts)
