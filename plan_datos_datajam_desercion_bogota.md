# DataJam Edición 4 — Plan de datos para analizar deserción escolar y vulnerabilidad económica

## Universidad Distrital Francisco José de Caldas

---

## 1. Objetivo del proyecto

El proyecto busca analizar la relación entre las **condiciones económicas de los hogares y la permanencia escolar en Bogotá**, utilizando datos abiertos del Distrito y datos de la Encuesta de Percepción/Encuesta Multipropósito.

### Pregunta analítica principal

> **¿Existe una relación significativa entre las condiciones socioeconómicas de las localidades y la tasa de deserción escolar en colegios oficiales de Bogotá?**

### Hipótesis inicial

> Las localidades con mayores niveles de vulnerabilidad económica presentan mayores tasas de deserción escolar.

Es importante que el análisis **no parta de que la hipótesis necesariamente es verdadera**. El objetivo de la DataJam debe ser determinar si los datos respaldan, contradicen o matizan la hipótesis.

### Precaución metodológica

Con datos agregados por localidad, UPL o UPZ podemos establecer **asociaciones territoriales**, pero no afirmar causalidad individual.

Por eso es mejor hablar de:

> **“asociación entre condiciones socioeconómicas y tasas de deserción escolar”**

y no de:

> **“la pobreza causa deserción”**.

---

# 2. Enfoque recomendado

No conviene comenzar descargando y procesando todos los datasets disponibles.

Se recomienda trabajar en tres etapas:

```text
ETAPA 1
¿Existe la relación?
        ↓
Pobreza + Deserción + Encuesta

ETAPA 2
¿Por qué podría existir?
        ↓
Reprobación + Transporte + Cupos + Ingresos

ETAPA 3
¿Dónde intervenir?
        ↓
Colegios + Trabajo infantil + Seguridad + Entorno
```

El resultado final podría ser un:

# Mapa de Vulnerabilidad Educativa de Bogotá

---

# 3. Datasets que debemos revisar primero

## 🔴 Prioridad 1 — imprescindibles

### 1. Tasa de Deserción por UPL/UPZ

**Función:** variable objetivo del proyecto.

Revisar:

- Año o periodo.
- Unidad territorial.
- Si está a nivel de UPL o UPZ.
- Si también contiene localidad.
- Tasa de deserción.
- Número de estudiantes.
- Matrícula.
- Número de desertores.
- Posibles variables por sexo, grado o sector.

### Pregunta clave

¿El dataset está realmente a nivel de UPL/UPZ o permite trabajar directamente por localidad?

Esto es fundamental porque el README plantea la hipótesis por localidad.

**No debemos hacer un JOIN artificial entre UPL/UPZ y localidad.**

---

## 🔴 2. Pobreza y Desigualdad en Bogotá D.C.

**Función:** principal fuente para evaluar la hipótesis económica.

Buscar variables como:

- Pobreza monetaria.
- Pobreza extrema.
- Pobreza multidimensional.
- Ingresos.
- Coeficiente de Gini.
- Localidad.
- Año.

Idealmente queremos una estructura parecida a:

```text
Localidad | Año | Pobreza monetaria | Pobreza extrema | IPM | Gini
```

Este será uno de los principales datasets para comparar contra la deserción.

---

## 🔴 3. Encuesta Multipropósito / Encuesta de Percepción

**Función:** complementar la medición oficial de pobreza y explorar mecanismos.

Variables de interés:

### Economía

- Ingresos del hogar.
- Autopercepción de pobreza.
- Estrato.

### Educación

- Percepción del acceso a educación.
- Asistencia educativa, si está disponible.
- Razones relacionadas con no estudiar, si existen.

### Trabajo

- Situación laboral.
- Desempleo.
- Actividad principal.

### Movilidad

- Medio de transporte.
- Tiempo de desplazamiento.
- Percepción del transporte.
- Costos de desplazamiento, si están disponibles.

Para la agregación de la encuesta se debe utilizar el ponderador correspondiente, por ejemplo:

```text
fexp_calh_anu
```

cuando corresponda a la unidad de análisis de hogares.

---

# 4. Datasets educativos complementarios

## 🟠 4. Tasa de Reprobación por UPL/UPZ

**Función:** estudiar un posible mecanismo entre vulnerabilidad y deserción.

Podemos analizar:

```text
Pobreza
   ↓
Reprobación
   ↓
Deserción
```

Pregunta:

> ¿Las zonas con mayor vulnerabilidad económica presentan también mayores niveles de reprobación?

---

## 🟠 5. Tasa de Aprobación por UPL/UPZ

**Función:** variable de contraste.

Permite estudiar si existe el patrón:

```text
Mayor vulnerabilidad
        ↓
Menor aprobación
        ↓
Mayor deserción
```

---

## 🟠 6. Colegios Bogotá D.C.

**Función:** análisis espacial.

Variables importantes:

- Identificador del colegio.
- Nombre.
- Localidad.
- UPL/UPZ.
- Coordenadas.
- Sector.
- Tipo de institución.

Esto permitirá eventualmente hacer:

```text
Colegio
   ↓
Entorno territorial
   ↓
Pobreza
Transporte
Seguridad
Oferta educativa
   ↓
Deserción
```

---

## 🟠 7. Oferta de cupos sector oficial

**Función:** medir capacidad del sistema educativo.

Podemos estudiar si las zonas con menor disponibilidad de cupos presentan condiciones diferentes de permanencia escolar.

---

## 🟠 8. Demanda de cupos sector oficial

**Función:** medir presión sobre el sistema educativo.

Una posible variable sería:

### Índice de presión educativa

```text
Demanda de cupos
─────────────────
Oferta de cupos
```

Una zona con alta demanda y baja oferta podría presentar mayor presión sobre el sistema.

---

# 5. Movilidad

## 🟡 9. Beneficiarios de transporte Bogotá D.C.

**Función:** estudiar el transporte como barrera indirecta para la permanencia escolar.

Variables a buscar:

- Localidad.
- Colegio.
- Número de estudiantes beneficiarios.
- Cobertura.
- Año.

Pregunta:

> ¿Las zonas con mayores dificultades económicas tienen menor cobertura de transporte escolar y mayor deserción?

---

## 🟡 10. Encuesta de Movilidad / Investigación de Viajeros

Revisar datasets como:

- Encuesta de Movilidad Bogotá.
- Base Investigación Viajeros Bogotá 2023.
- Base Investigación Viajeros Bogotá 2024.
- Base Investigación Viajeros Bogotá 2025.

Buscar:

- Tiempo de viaje.
- Medio de transporte.
- Número de viajes.
- Costos.
- Origen/destino.
- Motivo del viaje.
- Viajes relacionados con instituciones educativas.

Esto puede permitir construir una hipótesis más innovadora:

> **La pobreza puede relacionarse con la deserción no solamente por falta de ingresos, sino también por las dificultades y costos asociados al desplazamiento hacia el colegio.**

---

# 6. Alimentación y apoyo social

## 🟡 11. Beneficiarios de alimentación Bogotá D.C.

**Función:** estudiar un mecanismo de apoyo socioeconómico.

Pregunta:

> ¿La cobertura de alimentación escolar está relacionada con las condiciones económicas y la permanencia educativa?

Puede servir como variable de contexto o como posible factor protector.

---

# 7. Trabajo infantil

## 🟡 12. Niñas, niños y adolescentes identificados desde el sector salud en trabajo infantil en Bogotá D.C.

Este dataset es especialmente interesante para la hipótesis.

Una posible cadena explicativa:

```text
Pobreza
   ↓
Necesidad económica
   ↓
Trabajo infantil
   ↓
Menor tiempo disponible para estudiar
   ↓
Mayor riesgo de deserción
```

Pregunta:

> ¿Las localidades con mayor vulnerabilidad económica presentan también mayor incidencia de trabajo infantil y deserción escolar?

Si los datos tienen suficiente cobertura territorial y temporal, este puede ser uno de los análisis secundarios más fuertes.

---

# 8. Seguridad y entorno

Estos datasets NO deberían ser la primera prioridad, pero pueden incorporarse posteriormente.

## 🟡 13. Violencia intrafamiliar

Pregunta:

> ¿La violencia intrafamiliar presenta alguna asociación territorial con la deserción escolar?

## 🟡 14. Delitos de alto impacto

Puede utilizarse para construir indicadores de seguridad alrededor de colegios o por territorio.

## 🟡 15. Seguridad nocturna

Buscar datasets relacionados con:

- Condiciones de seguridad nocturna.
- Seguridad de mujeres.
- Percepción de seguridad.

## 🟡 16. Alumbrado público

Puede utilizarse para estudiar condiciones del entorno de los colegios.

## 🟡 17. Reconocimiento del entorno barrial

Puede aportar variables de percepción sobre las condiciones del entorno.

---

# 9. Salud y asistencia

También conviene revisar:

## Ausentismo escolar por enfermedad respiratoria en niños menores de 14 años

Pregunta:

> ¿El ausentismo asociado a problemas de salud puede ayudar a explicar diferencias territoriales en permanencia escolar?

También pueden revisarse:

- Embarazo adolescente.
- Desnutrición.
- Exceso de peso.
- Indicadores de salud infantil.

Estos serían factores complementarios, no el núcleo inicial del proyecto.

---

# 10. Orden recomendado de revisión

Si el equipo está empezando a trabajar ahora, descarguen/revisen primero estos:

```text
1.  Tasa de Deserción por UPL/UPZ
2.  Pobreza y Desigualdad en Bogotá D.C.
3.  Encuesta Multipropósito / Encuesta de Percepción
4.  Tasa de Reprobación por UPL/UPZ
5.  Tasa de Aprobación por UPL/UPZ
6.  Colegios Bogotá D.C.
7.  Oferta de cupos sector oficial
8.  Demanda de cupos sector oficial
9.  Beneficiarios de transporte Bogotá D.C.
10. Encuesta de Movilidad / Investigación de Viajeros
11. Beneficiarios de alimentación Bogotá D.C.
12. Trabajo infantil
13. Violencia intrafamiliar
14. Delitos de alto impacto
15. Seguridad / entorno / alumbrado
```

---

# 11. Primera etapa del análisis

La primera prueba debe ser sencilla.

## Hipótesis base

```text
POBREZA ───────────────→ DESERCIÓN
```

Variables:

### X

Pobreza monetaria por localidad/territorio.

### Y

Tasa de deserción.

### Análisis

1. Estadística descriptiva.
2. Mapa de pobreza.
3. Mapa de deserción.
4. Scatter plot.
5. Correlación Pearson.
6. Correlación Spearman.
7. Identificación de valores atípicos.

---

# 12. El scatter plot principal

Debe tener:

```text
Eje X:
Pobreza monetaria

Eje Y:
Tasa de deserción
```

Cada punto representa una localidad o unidad territorial.

Podemos identificar:

```text
              DESERCIÓN
                  ↑
                  │          ●
                  │      ●
                  │    ●
                  │  ●
                  │ ●
                  │
                  └────────────────→ POBREZA
```

Si aparece una tendencia positiva, tenemos evidencia a favor de la hipótesis.

Si no aparece, también es un resultado importante.

---

# 13. Segunda etapa: buscar mecanismos

Una vez validada la relación básica, agregar:

```text
Pobreza
   │
   ├── Ingresos
   ├── Reprobación
   ├── Transporte
   ├── Oferta de cupos
   ├── Demanda de cupos
   └── Trabajo infantil
             │
             ↓
         DESERCIÓN
```

Preguntas:

### Economía

> ¿Las localidades con menor ingreso presentan mayor deserción?

### Rendimiento

> ¿La reprobación está asociada con la deserción?

### Transporte

> ¿Los territorios con mayores dificultades de movilidad presentan mayor deserción?

### Oferta educativa

> ¿La presión sobre los cupos está relacionada con la permanencia?

### Trabajo infantil

> ¿El trabajo infantil puede ser un mecanismo que conecte vulnerabilidad económica y deserción?

---

# 14. Tercera etapa: análisis territorial

Después podemos incorporar:

- Colegios.
- Seguridad.
- Violencia.
- Alumbrado.
- Entorno.
- Salud.

La idea es pasar de:

```text
Localidad → deserción
```

a:

```text
Colegio
   ↓
Entorno inmediato
   ├── Pobreza
   ├── Transporte
   ├── Seguridad
   ├── Oferta educativa
   ├── Servicios
   └── Condiciones sociales
   ↓
Vulnerabilidad educativa
```

---

# 15. Producto final propuesto

## Mapa de Vulnerabilidad Educativa de Bogotá

Para cada localidad/colegio se podría mostrar:

```text
CIUDAD BOLÍVAR

Pobreza              ██████████
Desempleo             ███████
Dificultad transporte ████████
Reprobación           ██████
Inseguridad           █████████
Deserción             ████████

VULNERABILIDAD: ALTA
```

El objetivo no es simplemente mostrar un mapa, sino identificar:

> **¿Dónde la combinación de factores económicos, educativos y territoriales coincide con mayores niveles de deserción?**

---

# 16. Una posible arquitectura del modelo

```text
                    VULNERABILIDAD ECONÓMICA
                              │
             ┌────────────────┼────────────────┐
             ↓                ↓                ↓
          Pobreza          Ingresos        Desempleo
             │                │                │
             └────────────────┼────────────────┘
                              ↓
                    BARRERAS / MECANISMOS
                              │
          ┌───────────────────┼───────────────────┐
          ↓                   ↓                   ↓
     Transporte          Rendimiento         Trabajo infantil
          │                   │                   │
          ↓                   ↓                   ↓
    Accesibilidad        Reprobación          Menor tiempo
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ↓
                       DESERCIÓN ESCOLAR
```

Seguridad, salud, vivienda y entorno pueden incorporarse posteriormente como variables contextuales.

---

# 17. Qué NO hacer todavía

No conviene:

- Descargar todos los datasets disponibles.
- Hacer JOINs sin revisar primero la granularidad.
- Mezclar localidad, UPL y UPZ como si fueran equivalentes.
- Crear un índice de vulnerabilidad antes de validar las variables.
- Asumir que la pobreza causa deserción.
- Seleccionar únicamente variables que confirmen la hipótesis.
- Hacer un modelo complejo antes de entender los datos.

Primero:

```text
DATOS
  ↓
CALIDAD
  ↓
GRANULARIDAD
  ↓
JOIN
  ↓
ANÁLISIS EXPLORATORIO
  ↓
HIPÓTESIS
  ↓
MODELO
```

---

# 18. Qué revisar de cada dataset

Cuando descarguen cada dataset, documenten:

```text
Nombre:
Fuente:
Año:
Número de filas:
Número de columnas:

Unidad de observación:
    localidad / UPL / UPZ / colegio / hogar / persona

Nivel geográfico:

Variables importantes:

Llave primaria:

Llave para JOIN:

Periodo temporal:

Valores faltantes:

Duplicados:

Diccionario disponible:

Observaciones:
```

La **unidad de observación** y la **llave de JOIN** son especialmente importantes.

---

# 19. Estrategia de JOIN

Antes de cruzar datasets, determinar la unidad común.

Idealmente:

```text
Localidad
```

Si la deserción está a nivel UPL/UPZ:

```text
UPL/UPZ
```

Si queremos análisis por colegio:

```text
ID_COLEGIO
```

No se debe asumir que:

```text
UPZ = UPL = Localidad
```

Son unidades territoriales diferentes.

---

# 20. Resultado esperado del primer dataset integrado

Idealmente queremos llegar a una tabla como:

```text
Localidad
Año
Pobreza monetaria
Pobreza extrema
IPM
Ingreso
Deserción
Reprobación
Aprobación
Oferta cupos
Demanda cupos
Cobertura transporte
Cobertura alimentación
Trabajo infantil
```

Después podemos añadir variables de movilidad y entorno.

---

# 21. Prioridad definitiva

### 🔴 Núcleo del proyecto

```text
Deserción
Pobreza
Encuesta Multipropósito
Reprobación
Aprobación
```

### 🟠 Explicación educativa

```text
Colegios
Oferta de cupos
Demanda de cupos
Alimentación
Transporte escolar
```

### 🟡 Mecanismos socioeconómicos

```text
Ingresos
Desempleo
Trabajo infantil
Movilidad
```

### 🟢 Contexto territorial

```text
Seguridad
Violencia
Alumbrado
Salud
Vivienda
Entorno
```

---

# 22. Siguiente paso

No empezar todavía por un modelo complejo.

Primero revisar los **10 datasets prioritarios**:

1. Tasa de Deserción por UPL/UPZ
2. Pobreza y Desigualdad
3. Encuesta Multipropósito / Percepción
4. Reprobación
5. Aprobación
6. Colegios
7. Oferta de cupos
8. Demanda de cupos
9. Transporte escolar
10. Movilidad

Para cada uno se debe revisar:

**columnas → años → granularidad → llaves → valores faltantes → cobertura temporal.**

Con esa revisión podremos definir correctamente el JOIN y construir el primer dataset analítico antes de incorporar las variables adicionales.
