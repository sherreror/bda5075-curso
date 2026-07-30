FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Java 17 (Spark 4.x) — instalado de forma determinista y fijado como JAVA_HOME.
# (Spark falla en Java 24/25: getSubject / Security Manager eliminado.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jdk-headless \
    && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && python -m ipykernel install --name python3 --display-name "Python 3"

ENV SPARK_LOCAL_IP=127.0.0.1 \
    PYSPARK_PYTHON=python3
