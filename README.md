# Walker SLM

Petit modèle de langue compressé + RAG web, sans base de connaissances.
Une API locale libre, sans quota, qui tient dans environ 380 Mo.

## En deux mots

Walker SLM fait tourner un tout petit modèle (600 millions de paramètres,
compressé à **378 Mo**) sur ton propre ordinateur ou téléphone. Il n'a pas
de base de connaissances intégrée : à chaque question, il cherche sur le web,
lit les pages trouvées et répond en français à partir de ces extraits. Tu
peux aussi lui donner tes propres documents (fichiers `.txt` / `.md` dans
`docs/`).

## Le modèle

- **Qwen3-0.6B-Instruct**, quantifié `Q4_K_M` (GGUF)
- **Taille : 396 705 472 octets (~378 Mo)**, vérifié sur Hugging Face
- Licence Apache-2.0 — https://huggingface.co/unsloth/Qwen3-0.6B-GGUF
  (conversion Unsloth du modèle Qwen3 d'Alibaba)
- Téléchargé au premier lancement depuis Hugging Face (il n'est pas dans le dépôt)

> Pourquoi Qwen3 ? SmolLM2-360M (219 Mo) a été testé en direct le
> 6 novembre 2026 : il répondait aux questions simples, mais dérivait et
> inventait trop (ex. capitale de la RDC = « l'université »). Qwen3-0.6B
> est nettement meilleur en français et en raisonnement, pour 378 Mo —
> encore raisonnable sur téléphone.

## Limites honnêtes

- Un modèle de 0.6B reste petit : il répond bien mieux que le 360M, mais
  il peut encore se tromper ou dériver sur les questions difficiles. Le RAG
  web l'aide beaucoup (il reformule des textes trouvés en français), mais
  ne fait pas de miracles. Vérifie toujours les réponses importantes.
- Ce n'est pas un remplaçant des grosses API gratuites (Groq, Gemini) pour
  la qualité. En revanche : c'est à toi, sans compte, sans quota journalier,
  et ça tourne hors-ligne une fois le modèle téléchargé (sans le web, bien sûr).
- GitHub héberge le code uniquement : un fichier ne peut pas dépasser
  100 Mo sur GitHub, donc le modèle (378 Mo) se télécharge depuis Hugging
  Face au premier lancement. GitHub ne fait pas tourner le modèle : il faut
  un ordinateur, un téléphone (Termux) ou un petit serveur.

## Installation

```bash
git clone https://github.com/Kankwenda/walker-slm.git
cd walker-slm
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python download_model.py   # ~378 Mo, une seule fois
```

## Sur téléphone (Termux)

Installe Termux depuis **F-Droid** (pas le Play Store : sa version est
ancienne et cassée). Travaille dans le dossier d'accueil de Termux (`~`),
pas dans `/sdcard` (Android y bloque l'exécution des programmes).

**Option rapide — tester juste le modèle :**

```bash
pkg update && pkg upgrade -y
pkg install -y llama-cpp
curl -L -o model.gguf https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q4_K_M.gguf
sha256sum model.gguf   # doit donner ac2d97712095a558e31573f62f466a3f9d93990898b0ec79d7c974c1780d524a
llama-cli -m model.gguf -p "Quelle est la capitale de la RDC ?"
```

**Option complète — faire tourner le projet (RAG web + API) :**

```bash
pkg update && pkg upgrade -y
pkg install -y python git clang cmake make
git clone https://github.com/Kankwenda/walker-slm.git
cd walker-slm
pip install -r requirements.txt   # compile llama-cpp-python : long (20 à 30 min), une seule fois
python download_model.py          # ~378 Mo, une seule fois
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

Réponse : `{"answer": "...", "sources": [{"title": ..., "url": ...}], "model": "Qwen3-0.6B-Q4_K_M.gguf"}`

### Clé API (optionnelle)

Par défaut, l'API locale n'a pas de clé : elle n'écoute que sur ton
appareil (`127.0.0.1`), donc tes projets sur le même téléphone/PC
l'appellent sans clé.

Pour la protéger (par exemple si tu l'exposes à d'autres appareils),
définis une clé avant de lancer le serveur :

```bash
export WALKER_SLM_API_KEY="ta-clé-secrète"
uvicorn app:app --host 127.0.0.1 --port 8000
```

Ensuite chaque appel à `/chat` doit envoyer l'en-tête `X-API-Key` :

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ta-clé-secrète" \
  -d '{"question": "Quelle est la capitale de la RDC ?"}'
```

Sans la bonne clé, `/chat` répond `401`. Sans la variable
`WALKER_SLM_API_KEY`, l'API reste ouverte en local.

### Dans un projet HTML (JavaScript)

Oui : une page HTML peut appeler l'API avec `fetch` (le serveur autorise
les appels depuis le navigateur). Exemple :

```js
const res = await fetch("http://127.0.0.1:8000/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": "ta-clé-secrète"
  },
  body: JSON.stringify({ question: "Quelle est la capitale de la RDC ?" })
});
const data = await res.json();
console.log(data.answer);   // la réponse
console.log(data.sources);  // les sources
```

Le fichier `exemple.html` (à la racine du dépôt) est une page prête à
l'emploi : ouvre-la dans ton navigateur, colle ta clé, pose ta question.
Le fichier `walker_chatbot.html` est une interface de chat mobile complète
(bulles, historique, sources, clé gardée dans le navigateur).
Elles parlent au serveur sur le même appareil (`127.0.0.1`). Pour appeler
l'API depuis un autre appareil sur le même Wi-Fi, lance le serveur avec
`--host 0.0.0.0` et utilise l'adresse IP Wi-Fi du téléphone/PC à la place
de `127.0.0.1`.

Attention : une clé écrite dans une page HTML est visible par quiconque
lit le code de la page. Pour un usage perso en local, pas de souci. Ne
publie pas une page qui contient ta clé.

### Sur d'autres machines

**Installer le projet ailleurs :** mêmes étapes que sur ton téléphone ou
ton PC (`git clone`, `pip install -r requirements.txt`,
`python download_model.py`, puis `python chat.py` ou `uvicorn`). Le modèle
(~378 Mo) se télécharge une fois par machine, en Wi-Fi de préférence.

**Appeler l'API depuis une autre machine sur le même Wi-Fi :** lance le
serveur en écoutant tout le réseau :

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Puis, depuis l'autre machine, appelle `http://<adresse-IP>:8000/chat`
avec ta clé API (en-tête `X-API-Key`). Pour trouver l'adresse IP du
téléphone : dans Termux, `ifconfig` (ligne `inet`), ou dans les réglages
Wi-Fi du téléphone. Protège toujours l'API avec ta clé quand elle est
ouverte sur le réseau.

**Rendre l'API publique gratuitement, sans carte bancaire
(Cloudflare Tunnel) :** le téléphone n'est pas joignable directement
depuis internet, mais un tunnel Cloudflare donne une adresse HTTPS
publique à ton API — sans compte, sans carte, en une commande.

```bash
# Onglet Termux 1 — le serveur (local seulement, le tunnel s'en charge) :
uvicorn app:app --host 127.0.0.1 --port 8000

# Onglet Termux 2 — le tunnel :
pkg install -y cloudflared
cloudflared tunnel --url http://localhost:8000 --no-autoupdate
```

Ou en une seule commande, avec ta clé API (le script lance le serveur,
attend qu'il réponde, puis lance le tunnel) :

```bash
cd ~/walker-slm
WALKER_SLM_API_KEY='ta-cle' bash termux/start-cloudflare.sh
```

Cloudflare affiche alors une adresse du type
`https://xxxx.trycloudflare.com` : c'est ton API, joignable de partout.
Mets cette adresse dans tes pages HTML à la place de
`http://<adresse-IP>:8000`, avec ta clé API en en-tête `X-API-Key`.

Limites honnêtes : l'adresse change à chaque redémarrage du tunnel (il
faut la recopier dans tes pages) ; le téléphone doit rester allumé et
Termux éveillé (`termux-wake-lock`, paquet `termux-api`) sinon le
serveur et le tunnel s'arrêtent ; l'adresse est publique, donc garde
toujours ta clé API active. Un VPS (Oracle Cloud Free Tier) reste la
solution stable, mais il demande une carte bancaire.

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
├── exemple.html       # page de test navigateur (fetch + clé API)
├── walker_chatbot.html # interface chat mobile complète
├── requirements.txt
├── docs/              # tes documents (.txt/.md) pour le RAG local
├── models/            # le modèle téléchargé (ignoré par git)
└── tests/             # tests hors-ligne du RAG
```

## Licence

Code sous licence Apache-2.0. Modèle Qwen3 sous licence Apache-2.0
(Hugging Face).
