#!/bin/bash
set -e

echo "=========================================="
echo "Store Hours Pipeline - Full Setup"
echo "=========================================="

# 1. Gestion du .env
if [ ! -f "./airflow-docker/.env" ]; then
    echo "Creating .env file..."
    echo "AIRFLOW_UID=$(id -u)" > ./airflow-docker/.env
fi

# 2. Docker : Pas de chemin absolu ici !
echo "[2/5] Starting Docker containers..."
cd ./airflow-docker
docker compose up -d --build
cd ..

# 3. Elasticsearch
echo "[3/5] Waiting for Elasticsearch..."
# ... (garde ta boucle de 30 secondes ici) ...

# 4. Config Python
echo "[4/5] Configuring Elasticsearch..."
python3 ./setup/setup_elasticsearch.py

# 5. Node
echo "[5/5] Installing Node dependencies..."
npm install

echo "✅ Setup complete!"
