#!/bin/bash
set -e

# Détermination du dossier racine du projet
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Store Hours Pipeline - Full Setup"
echo "=========================================="

# 1. Gestion du fichier .env (Indispensable pour Airflow)
echo "[1/5] Checking environment configuration..."
if [ ! -f "./airflow-docker/.env" ]; then
    echo "Creating .env file with AIRFLOW_UID..."
    echo "AIRFLOW_UID=$(id -u)" > ./airflow-docker/.env
else
    echo ".env file already exists."
fi

# 2. Docker Containers starten
echo "[2/5] Starting Docker containers (Airflow, Postgres, Redis)..."
cd ./airflow-docker
docker compose down 2>/dev/null || true
docker compose build
docker compose up -d
cd "$PROJECT_ROOT"

# 3. Attente pour Elasticsearch
echo "[3/5] Waiting for Elasticsearch to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:9200/ > /dev/null 2>&1; then
    echo "Elasticsearch is ready!"
    break
  fi
  echo "Waiting for Elasticsearch... ($i/30)"
  sleep 2
done

# 4. Elasticsearch konfigurieren
echo "[4/5] Configuring Elasticsearch (ILM, Template)..."
# On utilise le script python dans le dossier setup
python3 ./setup/setup_elasticsearch.py

# 5. Node dependencies
echo "[5/5] Installing Node dependencies..."
npm install

echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Airflow UI: http://localhost:8080 (airflow/airflow)"
echo "2. Kibana: http://localhost:5601"
echo "3. Le DAG 'store_hours_pipeline' est prêt."
