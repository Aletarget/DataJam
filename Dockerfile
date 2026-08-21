FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python (solo las necesarias para el dashboard)
COPY requirements-dashboard.txt .
RUN pip install --no-cache-dir -r requirements-dashboard.txt

# Copiar solo lo necesario para el dashboard (~12MB de datos)
COPY dashboard/ ./dashboard/
COPY data/desercion_upl/ ./data/desercion_upl/
COPY data/encuesta_distrital/ ./data/encuesta_distrital/
COPY data/pobreza/ ./data/pobreza/
COPY output/CONCLUSIONES_FINALES.txt ./output/
COPY output/tabla_integrada_localidad.csv ./output/
COPY output/desercion_por_upl.csv ./output/

EXPOSE 8050

CMD ["gunicorn", "dashboard.app:server", "-b", "0.0.0.0:8050", "--workers", "2"]
