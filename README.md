# Problemas económicos y sus consecuencias en el estudio — DataJam Edición 4

## Descripción del problema

Las dificultades económicas de los hogares son uno de los factores más determinantes en la permanencia escolar y universitaria en Bogotá. Los hogares en condición de pobreza monetaria enfrentan mayores barreras para sostener los costos directos e indirectos de la educación (transporte, materiales, tiempo dedicado al estudio frente a la necesidad de generar ingresos), lo que se traduce en mayores tasas de deserción, especialmente en las localidades del sur y periferia de la ciudad. Este proyecto busca cuantificar esa relación y visualizar en qué zonas de Bogotá el factor económico pesa más sobre la continuidad educativa.

**Pregunta analítica:** ¿Existe una relación significativa entre el nivel de pobreza monetaria por localidad y la tasa de deserción escolar en colegios oficiales de Bogotá?

**Hipótesis:** Las localidades con mayor incidencia de pobreza monetaria (como Ciudad Bolívar, Santa Fe y Usme) presentan tasas de deserción escolar significativamente más altas que las localidades con menor incidencia de pobreza (como Chapinero, Teusaquillo y Usaquén), lo que evidencia que el factor económico es un determinante estructural de la deserción, más allá de otras variables individuales o institucionales.

## Fuentes de datos

| Dataset | Fuente | Enlace | Última actualización |
|---|---|---|---|
| Vulnerabilidad Calidad del Agua. Bogotá D.C. | Portal de Datos Abiertos de Bogotá | [enlace](https://datosabiertos.bogota.gov.co/dataset/vulnerabilidad-calidad-del-agua-bogota-d-c) | AAAA-MM-DD |
| Pobreza y Desigualdad en Bogotá D.C. | Portal de Datos Abiertos de Bogotá | [enlace](https://datosabiertos.bogota.gov.co/dataset/pobreza-y-desigualdad-en-bogota-d-c) | AAAA-MM-DD |
| Encuesta Multipropósito de Bogotá 2014 | Portal de Datos Abiertos de Bogotá | [enlace](https://datosabiertos.bogota.gov.co/dataset/encuesta-multiproposito-de-bogota-2014/resource/1e70684d-1f82-4c70-a7cf-7ff2a0d84a6a?inner_span=True) | AAAA-MM-DD |
| Tasa del Sistema de Alertas por localidad. Bogotá D.C. (matriculados vs. estudiantes ubicados en la localidad) | Portal de Datos Abiertos de Bogotá | [enlace](https://datosabiertos.bogota.gov.co/dataset/tasa-del-sistema-de-alertas-por-localidad-bogota-d-c) | AAAA-MM-DD |
| Tasa de Reprobación por UPZ | Portal de Datos Abiertos de Bogotá | [enlace](https://datosabiertos.bogota.gov.co/dataset/tasa-de-reprobacion-por-upl) | AAAA-MM-DD |
| Tasa de Aprobación por UPZ | Portal de Datos Abiertos de Bogotá | [enlace](https://datosabiertos.bogota.gov.co/dataset/tasa-de-aprobacion-por-upl) | AAAA-MM-DD |
| Tasa de Deserción por UPZ | Portal de Datos Abiertos de Bogotá | [enlace](https://datosabiertos.bogota.gov.co/dataset/tasa-de-desercion-por-upl) | AAAA-MM-DD |

**Posibles factores adicionales a explorar** (sin dataset asignado aún):
- Calidad del transporte — posible cruce con la Encuesta Distrital de Percepción.
- Violencia intrafamiliar — posiblemente relacionada con nivel educativo de los padres y seguridad.
- Seguridad — posiblemente relacionada con calidad de servicios, recolección de basuras e iluminación.

> Nota: completar la columna "Última actualización" al momento de la descarga.

## Metodología general

1. **Recolección y depuración de datos:** descarga de los tres datasets vía la API de CKAN (`package_show` y `datastore_search`) o descarga directa en CSV/XLSX desde el portal. Limpieza de nombres de localidades para asegurar consistencia entre fuentes (normalización de texto, codificación UTF-8, eliminación de duplicados).
2. **Integración de fuentes:** cruce de las tasas de deserción escolar con los indicadores de pobreza monetaria y multidimensional, usando la localidad como llave común.
3. **Análisis exploratorio:** estadística descriptiva por localidad, cálculo de correlación entre pobreza monetaria y deserción, e identificación de valores atípicos (localidades que se desvían del patrón esperado).
4. **Construcción de visualizaciones:** mapas coropléticos por localidad, gráficos de dispersión (pobreza vs. deserción) y series de tiempo cuando la disponibilidad de datos lo permita.
5. **Formulación de hallazgos y recomendaciones:** interpretación de resultados y propuestas orientadas a política pública distrital (focalización de subsidios, transporte escolar, alimentación escolar, etc.).

## Estructura del repositorio

```
├── data/               # Datos crudos y procesados
├── notebooks/          # Notebooks o scripts de análisis (Python/R)
├── outputs/             # Resultados: visualizaciones, tablas, reportes
├── docs/                 # Documentación adicional (opcional)
├── requirements.txt     # Dependencias del proyecto
└── README.md
```

## Instrucciones de despliegue

```bash
git clone https://github.com/usuario/repositorio.git
cd repositorio
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Instrucciones de ejecución

```bash
# Ejemplo para ejecutar el notebook principal
jupyter notebook notebooks/analisis_principal.ipynb

# O si es un script
python notebooks/analisis_principal.py
```

## Visualización

Enlace al dashboard / visor interactivo: [agregar enlace]

## Equipo

| Integrante | Rol |
|---|---|
| Nombre 1 | Perfil técnico – análisis y visualización |
| Nombre 2 | Perfil de análisis sectorial / política pública |
| Nombre 3 | Perfil complementario (temático/metodológico) |

## 📄 Licencia

Este proyecto se desarrolla en el marco del DataJam – Edición 4 (Alcaldía Mayor de Bogotá / Universidad Distrital Francisco José de Caldas). La propiedad intelectual corresponde a los autores del equipo.
