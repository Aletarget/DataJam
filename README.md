# Problemas Económicos y Deserción Escolar en Bogotá — DataJam Edición 4

**Universidad Distrital Francisco José de Caldas**

---

## Pregunta Analítica

> ¿Existe una relación significativa entre las condiciones socioeconómicas de los territorios (UPL) y la tasa de deserción escolar en colegios oficiales de Bogotá?

## Hipótesis

Las localidades con mayor incidencia de pobreza monetaria presentan tasas de deserción escolar más altas, mediadas por factores como transporte, reprobación, inseguridad alimentaria y acceso a empleo.

## Hallazgo Principal

La correlación directa pobreza → deserción **no es la más significativa**. El efecto es indirecto:

```
POBREZA → [transporte + inseguridad alimentaria + bajo acceso educativo] → REPROBACIÓN → DESERCIÓN
```

La reprobación es el predictor más fuerte de deserción a nivel territorial (r=0.50, p<0.001).

---

## Estructura del Repositorio

```
DataJam/
├── dashboard/                  # Dashboard interactivo (Plotly Dash)
│   ├── app.py                  # Punto de entrada — python dashboard/app.py
│   ├── data_loader.py          # Carga centralizada de datos
│   ├── assets/style.css        # Estilos
│   └── pages/
│       ├── mapa.py             # Mapa choropleth por UPL
│       ├── correlaciones.py    # Scatters dinámicos + heatmap
│       └── temporal.py         # Evolución temporal IPM y pobreza
├── scripts/
│   └── descargar_datos.py      # Descarga automática de datasets
├── data/                       # Datos (no versionados, se generan con el script)
│   ├── pobreza/
│   ├── desercion_upl/
│   ├── vulnerabilidad_agua/
│   ├── violencia_intrafamiliar/
│   ├── matricula/
│   ├── encuesta_multiproposito/
│   └── encuesta_distrital/
├── notebooks/                  # Notebooks paso a paso
│   ├── 01_descarga_y_exploracion.ipynb
│   ├── 02_limpieza_e_integracion.ipynb
│   ├── 03_analisis_exploratorio.ipynb
│   └── 04_transporte_violencia_conclusiones.ipynb
├── output/                     # Resultados generados
├── analisis_final.py           # Script consolidado de análisis
├── requirements.txt            # Dependencias
└── plan_datos_datajam_desercion_bogota.md
```

---

## Inicio Rápido

```bash
# 1. Clonar y configurar entorno
git clone https://github.com/Aletarget/DataJam.git
cd DataJam
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Descargar datos desde el Portal de Datos Abiertos de Bogotá
python scripts/descargar_datos.py

# 4. Ejecutar análisis
python analisis_final.py

# 5. Lanzar dashboard interactivo
python dashboard/app.py
# Abrir: http://127.0.0.1:8050
```

---

## Dashboard Interactivo

Visualización dinámica construida con [Plotly Dash](https://dash.plotly.com/) que permite explorar los resultados de forma interactiva.

```bash
python dashboard/app.py
```

**URL:** http://127.0.0.1:8050

### Páginas

| Ruta | Página | Descripción |
|------|--------|-------------|
| `/` | Mapa Territorial | Choropleth interactivo por UPL con 9 indicadores seleccionables, filtro por localidad, KPIs y ranking |
| `/correlaciones` | Correlaciones | Scatter plots dinámicos con selección de X/Y, línea de tendencia, estadísticas (Pearson/Spearman), heatmap |
| `/temporal` | Evolución Temporal | Serie temporal IPM + privaciones educativas, pobreza por localidad con slider de año |

### Requisitos

- Datos descargados en `data/` (ejecutar `python scripts/descargar_datos.py`)
- Dependencias instaladas (`pip install -r requirements.txt`)

---

## Fuentes de Datos

| Dataset | Fuente | Formato |
|---------|--------|---------|
| Tasa de Deserción por UPL | Secretaría de Educación de Bogotá (2024) | GeoJSON |
| Pobreza y Desigualdad | DANE / SDP (2003-2025) | CSV |
| Encuesta Distrital de Percepción | SDP - Año móvil 2025 | CSV |
| Vulnerabilidad Calidad del Agua | Secretaría de Ambiente | GeoJSON |
| Matrícula Jornada Única | Secretaría de Educación | GeoJSON |
| Violencia Intrafamiliar | Secretaría de Salud | CSV |
| Encuesta Multipropósito 2021 | SDP / DANE | CSV (opcional) |

Todos los datos provienen de [Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co) bajo licencias CC-BY-4.0.

---

## Metodología

1. **Recolección:** Descarga automática vía API CKAN del portal de datos abiertos
2. **Integración:** Cruce de tasas de deserción con indicadores de pobreza usando UPL como llave territorial
3. **Análisis exploratorio:** Correlaciones Pearson/Spearman, agregación ponderada de encuesta distrital por UPL
4. **Índice de riesgo:** Construcción de índice de riesgo educativo combinando vulnerabilidad socioeconómica + deserción
5. **Visualización:** Dashboard interactivo con mapas choropleth, scatters y series temporales

---

## Notebooks

| # | Notebook | Descripción |
|---|----------|-------------|
| 01 | Descarga y Exploración | Descarga de datos, inspección de estructura, verificación de calidad |
| 02 | Limpieza e Integración | Normalización de llaves geográficas, mapeo UPL→Localidad, tablas integradas |
| 03 | Análisis Exploratorio | Correlaciones, series temporales IPM vs educación, scatter plots |
| 04 | Transporte, Violencia y Conclusiones | Barreras de transporte, VIF, cadena causal y recomendaciones |

---

## Herramientas

- **Python 3.13** — Lenguaje principal
- **pandas / numpy / scipy** — Procesamiento y análisis estadístico
- **Plotly Dash** — Dashboard interactivo (visualización web)
- **Plotly Express** — Mapas choropleth, scatters, series temporales
- **Matplotlib / Seaborn** — Gráficos estáticos complementarios
- **Jupyter Notebooks** — Exploración paso a paso

---

## Resultados Clave

- El IPM pasó de 4.1% (2018) a 7.5% (2020, pandemia) y descendió a 2.2% (2025)
- La inasistencia escolar tuvo un pico de 6.0% en 2020, coincidiendo con el aumento del IPM
- Las localidades con mayor pobreza monetaria (Ciudad Bolívar 57.8%, Usme 57.4%) mantienen brechas persistentes
- La relación pobreza-deserción NO es lineal: está mediada por reprobación, transporte y acceso laboral
- Las UPLs más pobres tienen alta reprobación pero no siempre la mayor deserción oficial

---

## Equipo

| Integrante | Rol |
|---|---|
| Juan Diego Lozada | Perfil técnico — análisis y visualización |
| Alejandro Mora | Perfil de análisis sectorial / política pública |
| Johan Tamara Flautero | Perfil complementario (temático/metodológico) |

---

## Licencia

Proyecto desarrollado en el marco del DataJam Edición 4 (Alcaldía Mayor de Bogotá / Universidad Distrital Francisco José de Caldas). Los datos utilizados son de acceso público bajo licencias Creative Commons (CC-BY-4.0).
