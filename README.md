# Walker SLM

Petit modèle de langue compressé + RAG web, sans base de connaissances.
Une API locale libre, sans quota, qui tient dans environ 220 Mo.

## En deux mots

Walker SLM fait tourner un tout petit modèle (360 millions de paramètres,
compressé à **219 Mo**) sur ton propre ordinateur ou téléphone. Il n'a pas
de base de connaissances intégrée : à chaque question, il cherche sur le web,
lit les pages trouvées et répond en français à partir de ces extraits. Tu
peux aussi lui donner tes propres documents (fichiers `.txt` / `.md` dans
`docs/`).

## Le modèle

- **SmolLM2-360M-Instruct**, quantifié `Q4_0` (GGUF)
- **Taille : 229 733 280 octets (~219 Mo)**, vérifié sur Hugging Face
- Licence Apache-2.0 — https://huggingface.co/bartowski/SmolLM2-360M-Instruct-GGUF
- Téléchargé au premier lancement depuis Hugging Face (il n'est pas dans le dépôt)

> Pourquoi le 360M ? Le 135M-Q8_0 (138 Mo) a été testé en direct le
> 6 novembre 2026 : il répétait la question, copiait des bouts de pages ou
> tournait en boucle. Le 360M répond en français aux questions simples.
> C'est le plus petit modèle qui répond vraiment.

## Limites honnêtes

- Un modèle de 360M reste très petit : il répond bien aux questions simples
  en français, mais il peut dériver ou répéter la même phrase en boucle sur
  les réponses longues. Le RAG web l'aide beaucoup (il reformule des textes
  trouvés en français), mais ne fait pas de miracles.
- Ce n'est pas un remplaçant des grosses API gratuites (Groq, Gemini) pour
  la qualité. En revanche : c'est à toi, sans compte, sans quota journalier,
  et ça tourne hors-ligne une fois le modèle téléchargé (sans le web, bien sûr).
- GitHub héberge le code uniquement : un fichier ne peut pas dépasser
  100 Mo sur GitHub, donc le modèle (219 Mo) se télécharge depuis Hugging
  Face au premier lancement. GitHub ne fait pas tourner le modèle : il faut
  un ordinateur, un téléphone (Termux) ou un petit serveur.

## Installation

```bash
git clone https://github.com/Kankwenda/walker-slm.git
cd walker-slm
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python download_model.py   # ~219 Mo, une seule fois
```

## Sur téléphone (Termux)

Installe Termux depuis **F-Droid** (pas le Play Store : sa version est
ancienne et cassée). Travaille dans le dossier d'accueil de Termux (`~`),
pas dans `/sdcard` (Android y bloque l'exécution des programmes).

**Option rapide — tester juste le modèle :**

```bash
pkg update && pkg upgrade -y
pkg install -y llama-cpp
curl -L -o model.gguf https://huggingface.co/bartowski/SmolLM2-360M-Instruct-GGUF/resolve/main/SmolLM2-360M-Instruct-Q4_0.gguf
sha256sum model.gguf   # doit donner c3608933eb6e5763b87f769bda40c204dc158333668c7af214644fe39da58627
llama-cli -m model.gguf -p "Quelle est la capitale de la RDC ?"
```

**Option complète — faire tourner le projet (RAG web + API) :**

```bash
pkg update && pkg upgrade -y
pkg install -y python git clang cmake make
git clone https://github.com/Kankwenda/walker-slm.git
cd walker-slm
pip install -r requirements.txt   # compile llama-cpp-python : long (20 à 30 min), une seule fois
python download_model.py          # ~219 Mo, une seule fois
python chat.py "Quelle est la capitale de la RDC ?"
```

Fais ça en Wi-Fi si tu peux : outils + modèle = plusieurs centaines de Mo.
Branche le téléphone pendant la compilation, ça chauffe et ça prend du
temps. Si la compilation échoue, essaie d'abord
`pkg install -y ninja libandroid-execinfo` puis relance `pip install`.

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

Réponse : `{"answer": "...", "sources": [{"title": ..., "url": ...}], "model": "SmolLM2-360M-Instruct-Q4_0.gguf"}`

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
