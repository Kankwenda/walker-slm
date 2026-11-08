#!/data/data/com.termux/files/usr/bin/bash
# Walker SLM + tunnel Cloudflare — démarrage en une commande (Termux).
# Usage :
#   cd ~/walker-slm
#   WALKER_SLM_API_KEY='ta-cle' bash termux/start-cloudflare.sh
# Sans clé, le serveur démarre ouvert : l'adresse du tunnel est publique,
# donc garde toujours ta clé active (voir README).
# Prérequis : projet installé (voir README, route Termux) et modèle déjà
# téléchargé (python download_model.py). cloudflared est installé si absent.
set -u
cd "$(dirname "$0")/.."

if [ -z "${WALKER_SLM_API_KEY:-}" ]; then
  echo "ATTENTION : aucune clé API définie (WALKER_SLM_API_KEY vide)."
  echo "L'adresse du tunnel sera publique et sans protection. Mets ta clé :"
  echo "  WALKER_SLM_API_KEY='ta-cle' bash termux/start-cloudflare.sh"
  echo "J'attends 5 secondes, Ctrl+C pour arrêter."
  sleep 5
fi

command -v cloudflared >/dev/null 2>&1 || pkg install -y cloudflared
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock

export WALKER_SLM_API_KEY="${WALKER_SLM_API_KEY:-}"
uvicorn app:app --host 127.0.0.1 --port 8000 > /tmp/walker-slm.log 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null; exit' INT TERM

echo "Démarrage du serveur, vérification de /health..."
for i in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1; then
    echo "Serveur OK. Lancement du tunnel Cloudflare..."
    break
  fi
  sleep 2
done
curl -sf http://127.0.0.1:8000/health || { echo "Le serveur ne répond pas, voir /tmp/walker-slm.log"; kill $SERVER_PID; exit 1; }

cloudflared tunnel --url http://localhost:8000 --no-autoupdate
kill $SERVER_PID 2>/dev/null
