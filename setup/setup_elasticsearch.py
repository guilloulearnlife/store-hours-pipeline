#!/usr/bin/env python3
"""
Vollautomatisches Setup für die Store-Hours-Pipeline.
Führt aus:
1. Docker Containers (Airflow, Elasticsearch)
2. Elasticsearch Konfiguration (ILM, Template)
3. Node.js Dependencies
"""

import os
import sys
import time
import subprocess
import requests
import json

# Konfiguration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.path.basename(BASE_DIR) == "setup":
    BASE_DIR = os.path.dirname(BASE_DIR)
# On définit les dossiers par rapport à BASE_DIR
AIRFLOW_DIR = os.path.join(BASE_DIR, "airflow-docker")
PROJECT_DIR = BASE_DIR
ES_HOST = "http://localhost:9200"

class Colors:
    """Terminal Farben für lesbare Ausgabe."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def log_step(step_num, total, message):
    """Formatierte Schritt-Ausgabe."""
    print(f"\n{Colors.BOLD}[{step_num}/{total}] {message}{Colors.RESET}")

def log_success(message):
    print(f"  {Colors.GREEN}✓ {message}{Colors.RESET}")

def log_error(message):
    print(f"  {Colors.RED}✗ {message}{Colors.RESET}")

def log_info(message):
    print(f"  ℹ {message}")

def run_command(cmd, cwd=None, silent=False):
    """Führt Shell-Befehl aus."""
    try:
        if not silent:
            print(f"  $ {cmd}")
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=silent,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        log_error(f"Command failed: {e}")
        return False

def step_1_docker_setup():
    """Schritt 1: Docker Container starten."""
    log_step(1, 5, "Starting Docker containers...")
    
    log_info("Stopping existing containers...")
    run_command(f"cd {AIRFLOW_DIR} && docker compose down", silent=True)
    
    log_info("Building Docker image...")
    if not run_command(f"cd {AIRFLOW_DIR} && docker compose build"):
        log_error("Docker build failed")
        return False
    
    log_info("Starting containers...")
    if not run_command(f"cd {AIRFLOW_DIR} && docker compose up -d"):
        log_error("Docker compose up failed")
        return False
    
    log_success("Docker containers started")
    return True

def step_2_wait_elasticsearch():
    log_step(3, 6, "Waiting for Elasticsearch...")
    # On passe à 60 tentatives (3 minutes) pour être large
    for i in range(60): 
        try:
            resp = requests.get(ES_HOST, timeout=2)
            if resp.status_code == 200:
                log_success("Elasticsearch is ready")
                return True
        except:
            pass
        # Animation plus propre pour ne pas polluer le terminal
        print(f"  ℹ Waiting... ({i+1}/60) - Vérifiez Docker Desktop si ça dure trop longtemps", end="\r")
        time.sleep(3)
    return False

def step_3_elasticsearch_config():
    """Schritt 3: Elasticsearch konfigurieren."""
    log_step(3, 5, "Configuring Elasticsearch...")
    
    # ILM-Policy
    ilm_policy = {
        "policy": {
            "phases": {
                "hot": {
                    "min_age": "0d",
                    "actions": {
                        "rollover": {
                            "max_primary_shard_size": "50gb",
                            "max_age": "30d"
                        },
                        "set_priority": {"priority": 100}
                    }
                },
                "warm": {
                    "min_age": "30d",
                    "actions": {
                        "set_priority": {"priority": 50}
                    }
                },
                "delete": {
                    "min_age": "90d",
                    "actions": {
                        "delete": {}
                    }
                }
            }
        }
    }
    
    log_info("Creating ILM Policy...")
    try:
        resp = requests.put(
            f"{ES_HOST}/_ilm/policy/stores-hours-policy",
            json=ilm_policy,
            timeout=10
        )
        if resp.status_code in [200, 201]:
            log_success("ILM Policy created")
        else:
            log_error(f"ILM failed: {resp.status_code}")
            return False
    except Exception as e:
        log_error(f"ILM error: {e}")
        return False
    
    # Index-Template
    template = {
        "index_patterns": ["stores-hours-*"],
        "priority": 200,
        "template": {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "index.lifecycle.name": "stores-hours-policy",
                "index.lifecycle.rollover_alias": "stores-hours"
            },
            "mappings": {
                "properties": {
                    "source_id": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    "street": {"type": "keyword"},
                    "city": {"type": "keyword"},
                    "postcode": {"type": "keyword"},
                    "country": {"type": "keyword"},
                    "website": {"type": "keyword"},
                    "opening_hours_raw": {"type": "text"},
                    "opening_hours_parsed": {"type": "text"},
                    "opening_hours_parse_ok": {"type": "boolean"},
                    "opening_hours_parse_error": {"type": "text"},
                    "scrape_timestamp": {"type": "date"}
                }
            }
        }
    }
    
    log_info("Creating Index Template...")
    try:
        resp = requests.put(
            f"{ES_HOST}/_index_template/stores-hours-template",
            json=template,
            timeout=10
        )
        if resp.status_code in [200, 201]:
            log_success("Index Template created")
        else:
            log_error(f"Template failed: {resp.status_code}")
            return False
    except Exception as e:
        log_error(f"Template error: {e}")
        return False
    
    return True

def step_4_airflow_init():
    """Schritt 4: Airflow initialisieren."""
    log_step(4, 5, "Initializing Airflow...")
    
    log_info("Waiting for Airflow to be ready...")
    time.sleep(10)
    
    log_info("Running Airflow DB init...")
    run_command(f"cd {AIRFLOW_DIR} && docker compose exec -T airflow-scheduler airflow db init", silent=True)
    
    log_success("Airflow initialized")
    return True

def step_5_node_dependencies():
    """Schritt 5: Node.js Dependencies."""
    log_step(5, 5, "Installing Node.js dependencies...")
    
    if not run_command(f"cd {PROJECT_DIR} && npm install"):
        log_error("npm install failed")
        return False
    
    log_success("Node.js dependencies installed")
    return True

def verify_setup():
    """Verifizierung: Alles läuft?"""
    print(f"\n{Colors.BOLD}--- Verification ---{Colors.RESET}")
    
    # Elasticsearch
    try:
        resp = requests.get(ES_HOST)
        if resp.status_code == 200:
            log_success("Elasticsearch running")
    except:
        log_error("Elasticsearch not responding")
    
    # ILM Status
    try:
        resp = requests.get(f"{ES_HOST}/_ilm/status")
        if resp.status_code == 200:
            mode = resp.json().get("operation_mode", "unknown")
            log_success(f"ILM mode: {mode}")
    except:
        pass
    
    # Docker Containers
    log_info("Docker containers:")
    run_command("docker ps --filter 'name=airflow' --format '{{.Names}}: {{.Status}}'")

def main():
    """Hauptfunktion."""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("Store-Hours-Pipeline - Automated Setup")
    print(f"{'='*60}{Colors.RESET}\n")
    
    steps = [
        ("Docker Setup", step_1_docker_setup),
        ("Wait Elasticsearch", step_2_wait_elasticsearch),
        ("Configure Elasticsearch", step_3_elasticsearch_config),
        ("Initialize Airflow", step_4_airflow_init),
        ("Install Node Dependencies", step_5_node_dependencies),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            log_error(f"{step_name} failed!")
            return 1
    
    # Verification
    verify_setup()
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Setup complete!{Colors.RESET}\n")
    print("Next steps:")
    print(f"  1. Airflow UI:  {Colors.BOLD}http://localhost:8080{Colors.RESET} (airflow/airflow)")
    print(f"  2. Kibana:      {Colors.BOLD}http://localhost:5601{Colors.RESET}")
    print(f"  3. Trigger DAG manually or wait for 06:00 daily run\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

