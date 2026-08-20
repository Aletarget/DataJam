# Problemas económicos y sus consecuencias en el estudio — DataJam Edición 4

## Descripción del problema

Las dificultades económicas de los hogares son uno de los factores más determinantes en la permanencia escolar y universitaria en Bogotá. Los hogares en condición de pobreza monetaria enfrentan mayores barreras para sostener los costos directos e indirectos de la educación (transporte, materiales, tiempo dedicado al estudio frente a la necesidad de generar ingresos), lo que se traduce en mayores tasas de deserción, especialmente en las localidades del sur y periferia de la ciudad.

**Pregunta analítica:** ¿Existe una relación significativa entre el nivel de pobreza monetaria por localidad y la tasa de deserción escolar en colegios oficiales de Bogotá?

**Hipótesis:** Las localidades con mayor incidencia de pobreza monetaria presentan tasas de deserción escolar significativamente más altas, mediadas por factores como transporte, violencia intrafamiliar y hacinamiento escolar.

## Estructura del repositorio

```
├── scripts/                  # Scripts de descarga automática de datos
│   └── descargar_datos.py    # Descarga todos los datasets del portal de datos abiertos
├── data/                     # Datos descargados (no versionados, se generan con el script)
│   ├── pobreza/
│   ├── desercion_upl/
│   ├── vulnerabilidad_agua/
│   ├── violencia_intrafamiliar/
│   ├── matricula/
│   ├── encuesta_multiproposito/
│   └── encuesta_distrital/
├── notebooks/                # Notebooks paso a paso del análisis
│   ├── 01_descarga_y_exploracion.ipynb
│   ├── 02_limpieza_e_integracion.ipynb
│   ├── 03_analisis_exploratorio.ipynb
│   └── 04_transporte_violencia_conclusiones.ipynb
├── output/                   # Resultados: visualizaciones, tablas, reportes
├── analisis_final.py         # Script consolidado que ejecuta todo el análisis
├── requirements.txt          # Dependencias del proyecto
├── plan_datos_datajam_desercion_bogota.md  # Plan metodológico detallado
└── README.md
```

## Inicio rápido

```bash
# 1. Clonar y configurar entorno
git clone <url-del-repositorio>
cd DataJam
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Descargar datos desde el Portal de Datos Abiertos de Bogotá
python scripts/descargar_datos.py

# 3. Ejecutar análisis completo
python analisis_final.py

# 4. O seguir paso a paso con los notebooks
jupyter notebook notebooks/
```

## Descarga de datos

El script `scripts/descargar_datos.py` descarga automáticamente todos los datasets necesarios desde el [Portal de Datos Abiertos de Bogotá](https://datosabiertos.bogota.gov.co). No es necesario descargar nada manualmente.

```bash
# Descargar todo (sin los archivos opcionales grandes)
python scripts/descargar_datos.py --sin-opcionales

# Descargar un dataset específico
python scripts/descargar_datos.py --dataset pobreza

# Verificar qué datos hay disponibles localmente
python scripts/descargar_datos.py --solo-verificar

# Descargar todo incluyendo la Encuesta Multipropósito (~500MB)
python scripts/descargar_datos.py
```

## Fuentes de datos

| Dataset | Fuente | Formato | Tamaño aprox. |
|---|---|---|---|
| Pobreza y Desigualdad | Sec. Distrital de Salud / DANE | CSV | 30 KB |
| Tasa de Deserción por UPL | Sec. Distrital de Educación | GeoJSON | 2.5 MB |
| Vulnerabilidad Calidad del Agua | Sec. Distrital de Ambiente | GeoJSON | 2.5 MB |
| Violencia Intrafamiliar | Sec. Distrital de Salud | CSV | 110 MB |
| Matrícula Jornada Única | Sec. Distrital de Educación | GeoJSON | 230 KB |
| Encuesta Multipropósito 2021 | SDP / DANE | CSV | 500 MB (opcional) |
| Encuesta Distrital Percepción 2025 | SDP | CSV | (opcional) |

Todos los datos provienen de fuentes públicas con licencia CC-BY-4.0 o CC-BY-SA-4.0.

## Notebooks (paso a paso)

| # | Notebook | Descripción |
|---|---|---|
| 01 | Descarga y Exploración | Descarga de datos, inspección de estructura, verificación de calidad |
| 02 | Limpieza e Integración | Normalización de llaves geográficas, mapeo UPL→Localidad, tablas integradas |
| 03 | Análisis Exploratorio | Correlaciones, series temporales IPM vs educación, gráficos de dispersión |
| 04 | Transporte, Violencia y Conclusiones | Barreras de transporte, VIF, cadena causal y recomendaciones |

## Metodología

1. **Recolección:** descarga automática vía API CKAN del portal de datos abiertos
2. **Integración:** cruce de tasas de deserción con indicadores de pobreza usando localidad/UPL como llave
3. **Análisis exploratorio:** correlaciones Pearson, estadística descriptiva, identificación de patrones
4. **Visualizaciones:** gráficos de dispersión, series temporales, mapas de barras por localidad
5. **Hallazgos:** la pobreza no causa directamente deserción — el efecto es indirecto, mediado por reprobación

## Hallazgo principal

La correlación directa pobreza→deserción NO es la más significativa. El efecto es **indirecto**:

```
POBREZA → [transporte + violencia + hacinamiento] → REPROBACIÓN → DESERCIÓN
```

La reprobación es el predictor más fuerte de deserción a nivel territorial (r=0.50, p<0.001).

## Equipo

| Integrante | Rol |
|---|---|
| Nombre 1 | Perfil técnico – análisis y visualización |
| Nombre 2 | Perfil de análisis sectorial / política pública |
| Nombre 3 | Perfil complementario (temático/metodológico) |

## Licencia

Este proyecto se desarrolla en el marco del DataJam – Edición 4 (Alcaldía Mayor de Bogotá / Universidad Distrital Francisco José de Caldas). Los datos utilizados son de acceso público bajo licencias Creative Commons.
