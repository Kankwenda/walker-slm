"""Chargement et interrogation du SLM (llama-cpp-python)."""

import re

from config import MAX_TOKENS, MODEL_PATH, N_CTX, TEMPERATURE, TOP_P

SYSTEM = (
    "Tu es Walker, un assistant utile. Réponds en français, de façon courte "
    "et claire, uniquement à partir des extraits fournis. Si les extraits "
    "ne contiennent pas la réponse, dis-le simplement. Ne devine rien."
)

# Qwen3 raisonne dans des balises <think>...</think> : on les enlève pour
# ne garder que la réponse finale.
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _strip_think(text):
    """Enlève le raisonnement <think> de Qwen3 (y compris non fermé)."""
    text = _THINK_RE.sub("", text)
    if "<think>" in text:
        text = text.split("<think>")[0]
    return text.strip()


_llm = None


def load_model(path=MODEL_PATH):
    """Charge le modèle une seule fois (ou lève une erreur claire)."""
    global _llm
    if _llm is None:
        try:
            from llama_cpp import Llama
        except ImportError as e:
            raise RuntimeError(
                "llama-cpp-python n'est pas installé : pip install -r requirements.txt"
            ) from e
        _llm = Llama(model_path=path, n_ctx=N_CTX, verbose=False)
    return _llm


def close():
    """Ferme proprement le modèle (évite une erreur à la fermeture du programme)."""
    global _llm
    if _llm is not None:
        try:
            _llm.close()
        except Exception:
            pass
        _llm = None


def answer(question, context="", max_tokens=MAX_TOKENS):
    """Répond à la question à partir du contexte (extraits RAG)."""
    llm = load_model()
    if context:
        user = f"{context}\n\nQuestion : {question}\nRéponds en français."
    else:
        user = f"Question : {question}\nRéponds en français."
    out = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        temperature=TEMPERATURE,
        top_p=TOP_P,
        max_tokens=max_tokens,
        repeat_penalty=1.1,
    )
    return _strip_think(out["choices"][0]["message"]["content"].strip())
