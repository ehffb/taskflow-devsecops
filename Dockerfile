# Dockerfile INSEGURO - linha de base usada no Modulo 2 (Hardening).
# Cada comentario "# FALHA" indica uma pratica que sera corrigida
# durante a aula de hardening de containers.

# FALHA 1: tag "latest" nao fixada -> build nao reprodutivel e pode
# puxar uma imagem base com vulnerabilidades novas sem aviso.
FROM python:3.12-slim

WORKDIR /app

RUN groupadd -r taskflow && useradd -r -g taskflow taskflow

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R taskflow:taskflow /app

USER taskflow

EXPOSE 5000

CMD ["python", "app.py"]
