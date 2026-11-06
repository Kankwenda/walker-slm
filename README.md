# Walker SLM

Petit modèle de langue compressé + RAG web, sans base de connaissances.
Une API locale libre, sans quota, qui tient dans moins de 200 Mo.

## En deux mots

Walker SLM fait tourner un tout petit modèle (135 millions de paramètres,
compressé à **138 Mo**) sur ton propre ordinateur ou téléphone. Il n'a pas
de base de connaissances intégrée : à chaque question, il cherche sur le web,
lit les pages trouvées et répond en français à partir de ces extraits. Tu
peux aussi lui donner tes propres documents (fichiers `.txt` / `.md` dans
`docs/`).

## Le modèle

- **SmolLM2-135M-Instruct**, quantifié `Q8_0` (GGUF)
- **Taille : 144 811 360 octets (~138 Mo)**, vérifié sur Hugging Face
- Licence Apache-2.0 — https://huggingface.co/bartowski/SmolLM2-135M-Instruct-GGUF
- Téléchargé au premier lancement depuis Hugging Face (il n'est pas dans le dépôt)

> Pourquoi pas le 360M ? Son plus petit fichier fait 209 Mo : il ne rentre
> pas sous les 200 Mo. Le 135M en Q8 est le plus gros modèle qui tient dans
> la limite.

## Limites honnêtes

- Un modèle de 135M reste très petit : ses réponses sont simples, son
  français imparfait, il peut se tromper. Le RAG web l'aide beaucoup (il
  reformule des textes trouvés en français), mais ne fait pas de miracles.
- Ce n'est pas un remplaçant des grosses API gratuites (Groq, Gemini) pour
  la qualité. En revanche : c'est à toi, sans compte, sans quota journalier,
  et ça tourne hors-ligne une fois le modèle téléchargé (sans le web, bien sûr).
- GitHub héberge le code uniquement : un fichier ne peut pas dépasser
  100 Mo sur GitHub, donc le modèle (138 Mo) se télécharge depuis Hugging
  Face au premier lancement. GitHub ne fait pas tourner le modèle : il faut
  un ordinateur, un téléphone (Termux) ou un petit serveur.

## Installation

```bash
git clone https://github.com/Kankwenda/walker-slm.git
cd walker-slm
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python download_model.py   # ~138 Mo, une seule fois
```

Sur Termux (Android), `llama-cpp-python` n'a pas de version précompilée :
il faut le compiler (`pkg install cmake clang python`, puis
`pip install llama-cpp-python`, c'est long) ou utiliser le binaire
`llama-server` des releases llama.cpp.

## Utilisation

Discussion en ligne de commande :

```bash
python chat.py "Quelle est la capitale de la RDC ?"
python chat.py   # mode interactif
```

API locale :

```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Quelle est la capitale de la RDC ?"}'
```

Réponse : `{"answer": "...", "sources": [{"title": ..., "url": ...}], "model": "SmolLM2-135M-Instruct-Q8_0.gguf"}`

## Comment marche le RAG (sans base)

1. Recherche web (DuckDuckGo, sans clé API) : 5 résultats.
2. Téléchargement des pages, extraction du texte.
3. Découpage en morceaux (~600 caractères).
4. Classement par mots-clés : on garde les 4 morceaux qui partagent le plus
   de mots avec la question.
5. Le modèle répond uniquement à partir de ces extraits, en français.

Aucune base vectorielle, aucun embedding, rien n'est stocké entre deux
questions. Les fichiers `.txt` / `.md` placés dans `docs/` sont traités
de la même façon que les pages web.

## Structure

```
walker-slm/
├── app.py             # API FastAPI : POST /chat, GET /health
├── chat.py            # discussion en ligne de commande
├── slm.py             # chargement et interrogation du modèle
├── rag.py             # recherche web, découpage, classement
├── download_model.py  # téléchargement du modèle (taille + sha256 vérifiés)
├── config.py          # modèle, limites, chemins
├── requirements.txt
├── docs/              # tes documents (.txt/.md) pour le RAG local
├── models/            # le modèle téléchargé (ignoré par git)
└── tests/             # tests hors-ligne du RAG
```

## Licence

Code sous licence Apache-2.0. Modèle SmolLM2 sous licence Apache-2.0
(Hugging Face).
