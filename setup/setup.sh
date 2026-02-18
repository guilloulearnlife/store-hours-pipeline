#!/bin/bash
set -e

echo "=========================================="
echo "Store Hours Pipeline - Full Setup"
echo "=========================================="

# 1. Aller dans le dossier Airflow (qui est maintenant juste à côté)
echo "[1/4] Starting Docker containers..."
cd ./store-hours-pipeline/airflow-docker
docker compose down 2>/dev/null || true
docker compose build
docker compose up -d
sleep 30

# Attente pour Elasticsearch
echo "[1/4] Waiting for Elasticsearch to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:9200/ > /dev/null 2>&1; then
    echo "Elasticsearch is ready!"
    break
  fi
  echo "Waiting... ($i/30)"
  sleep 2
done

# 2. Configurer Elasticsearch
echo "[2/4] Configuring Elasticsearch (ILM, Template)..."
# On remonte d'un cran pour trouver le dossier setup
cd ..
python3 ./setup/setup_elasticsearch.py

# 3. Airflow initialiser
echo "[3/4] Initializing Airflow..."
cd ./airflow-docker
docker compose exec -T airflow-init airflow db init 2>/dev/null || true

# 4. Dépendances Node
echo "[4/4] Installing Node dependencies..."
cd ..
npm install

echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
