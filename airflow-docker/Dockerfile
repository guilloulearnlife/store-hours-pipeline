FROM apache/airflow:3.1.3

USER root

# Installation de Node.js et npm
# Ajout de 'build-essential' pour garantir que les dépendances natives Node s'installent bien
RUN apt-get update && \
    apt-get install -y --no-install-recommends nodejs npm build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

# Installation des dépendances Python nécessaires pour ton script setup_elasticsearch.py
# (Si tu en as besoin dans Airflow)
RUN pip install elasticsearch
