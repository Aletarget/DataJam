FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python
COPY requirements-dashboard.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dashboard.txt

# Copiar scripts y código
COPY scripts/ ./scripts/
COPY dashboard/ ./dashboard/
COPY analisis_final.py .

# Descargar datos y generar outputs necesarios
RUN python scripts/descargar_datos.py --sin-opcionales && \
    python analisis_final.py

EXPOSE 8050

CMD ["gunicorn", "dashboard.app:server", "-b", "0.0.0.0:8050", "--workers", "2"]
