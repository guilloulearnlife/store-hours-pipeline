FROM apache/airflow:3.1.3

USER root

# Node.js und npm installieren
RUN apt-get update && \
    apt-get install -y nodejs npm && \
    apt-get clean

USER airflow
