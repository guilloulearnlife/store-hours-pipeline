#!/bin/bash
set -e

echo "=========================================="
echo "Store Hours Pipeline - Full Setup"
echo "=========================================="

# 1. Docker Containers starten
echo "[1/4] Starting Docker containers..."
cd ~/airflow-docker
docker compose down 2>/dev/null || true
docker compose build
docker compose up -d
sleep 30

echo "[1/4] Waiting for Elasticsearch to be ready..."
for i in \{1..30\}; do
  if curl -s http://localhost:9200/ > /dev/null 2>&1; then
    echo "Elasticsearch is ready!"
    break
  fi
  echo "Waiting... ($i/30)"
  sleep 2
done

# 2. Elasticsearch konfigurieren
echo "[2/4] Configuring Elasticsearch (ILM, Template)..."
python3 ../setup/setup_elasticsearch.py

# 3. Airflow initialisieren
echo "[3/4] Initializing Airflow..."
cd ~/airflow-docker
docker compose exec -T airflow-init airflow db init 2>/dev/null || true

# 4. Node dependencies
echo "[4/4] Installing Node dependencies..."
cd ~/projektDataEngineering/store-hours-pipeline
npm install

echo "=========================================="
echo "\uc0\u9989  Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Airflow UI: http://localhost:8080 (airflow/airflow)"
echo "2. Kibana: http://localhost:5601"
echo "3. Trigger DAG manually or wait for 06:00 daily run"
echo ""
