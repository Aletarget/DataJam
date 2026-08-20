"""
DESCARGA AUTOMÁTICA DE DATOS — DataJam Edición 4
==================================================
Universidad Distrital Francisco José de Caldas

Este script descarga todos los datasets necesarios desde el Portal de
Datos Abiertos de Bogotá (datosabiertos.bogota.gov.co) y la SDP.

Fuentes:
1. Pobreza y Desigualdad (Secretaría Distrital de Salud / DANE)
2. Tasa de Deserción por UPL (Secretaría Distrital de Educación)
3. Vulnerabilidad Calidad del Agua (Secretaría Distrital de Ambiente)
4. Violencia Intrafamiliar (Secretaría Distrital de Salud)
5. Matrícula en Jornada Única (Secretaría Distrital de Educación)
6. Encuesta Multipropósito 2021 (SDP/DANE)
7. Encuesta Distrital de Percepción 2025 (SDP)

Uso:
    python scripts/descargar_datos.py
    python scripts/descargar_datos.py --dataset pobreza
    python scripts/descargar_datos.py --solo-verificar
"""

import os
import sys
import time
import hashlib
import argparse
import requests
from pathlib import Path


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Timeout para descargas (segundos)
TIMEOUT = 120
# Reintentos en caso de fallo
MAX_RETRIES = 3
RETRY_DELAY = 5  # segundos entre reintentos

# Registro de datasets con sus URLs de descarga directa
DATASETS = {
    "pobreza": {
        "nombre": "Pobreza y Desigualdad en Bogotá D.C.",
        "fuente": "Secretaría Distrital de Salud / OSB",
        "licencia": "CC-BY-4.0",
        "archivos": [
            {
                "url": "https://datosabiertos.bogota.gov.co/dataset/200931ad-6bec-4ceb-b16b-c2d3e6e41fc0/resource/f0a69906-e310-4448-91a1-559d777d7845/download/osb_demografia-pobrezaygini.csv",
                "destino": "pobreza/osb_demografia-pobrezaygini.csv",
                "descripcion": "Indicadores de pobreza monetaria, IPM y Gini por localidad (2011-2025)",
            },
            {
                "url": "https://datosabiertos.bogota.gov.co/dataset/200931ad-6bec-4ceb-b16b-c2d3e6e41fc0/resource/5a6499fe-efdd-4868-9a85-ef9373b34611/download/metadato_osb_demografia-pobrezaygini.csv",
                "destino": "pobreza/metadato_osb_demografia-pobrezaygini.csv",
                "descripcion": "Metadatos del dataset de pobreza",
            },
        ],
    },
    "desercion_upl": {
        "nombre": "Tasa de Deserción por UPL",
        "fuente": "Secretaría Distrital de Educación",
        "licencia": "CC-BY-SA-4.0",
        "archivos": [
            {
                "url": "https://datosabiertos.bogota.gov.co/dataset/a64daa53-eae3-44a9-ab43-897f17674519/resource/49a97065-5956-4d79-bb8f-1c28d98e5c0d/download/tasas_upl_122024.geojson",
                "destino": "desercion_upl/tasas_upl.geojson",
                "descripcion": "Tasas de deserción, reprobación y aprobación por UPL (GeoJSON, dic 2024)",
            },
        ],
    },
    "vulnerabilidad_agua": {
        "nombre": "Vulnerabilidad Calidad del Agua. Bogotá D.C.",
        "fuente": "Secretaría Distrital de Ambiente",
        "licencia": "CC-BY-4.0",
        "archivos": [
            {
                "url": "https://datosabiertos.bogota.gov.co/dataset/39c47946-fce5-4ed8-b7b6-8ade61945421/resource/697c9d45-3646-4356-8842-35c003912783/download/vulnerabilidad_agua.geojson",
                "destino": "vulnerabilidad_agua/vulnerabilidad_agua.geojson",
                "descripcion": "Vulnerabilidad hídrica por localidad (GeoJSON)",
            },
        ],
    },
    "violencia_intrafamiliar": {
        "nombre": "Violencia Intrafamiliar y de Género en Bogotá D.C.",
        "fuente": "Secretaría Distrital de Salud / OSB",
        "licencia": "CC-BY-4.0",
        "archivos": [
            {
                "url": "https://datosabiertos.bogota.gov.co/dataset/a1e1ef90-10c0-436f-a290-d1f7c1cf2242/resource/bbe9e920-c564-40f2-a307-5ae1ff087168/download/osb_saludmental-vintrafamiliar.csv",
                "destino": "violencia_intrafamiliar/osb_saludmental-vintrafamiliar.csv",
                "descripcion": "Casos de violencia intrafamiliar (~110MB, CSV sep=';')",
            },
        ],
    },
    "matricula": {
        "nombre": "Matrícula en Jornada Única en Colegios Oficiales. Bogotá D.C.",
        "fuente": "Secretaría Distrital de Educación",
        "licencia": "CC-BY-SA-4.0",
        "archivos": [
            {
                "url": "https://datosabiertos.bogota.gov.co/dataset/4e1dea84-98b9-4b56-9eef-49b02e0b2a75/resource/07ad78d2-2c67-47a1-ba45-024aa4f830aa/download/matriculajunica03_2025.geojson",
                "destino": "matricula/matriculaciones.geojson",
                "descripcion": "Matrícula oficial por colegio y localidad (GeoJSON, mar 2025)",
            },
        ],
    },
    "encuesta_multiproposito": {
        "nombre": "Encuesta Multipropósito de Bogotá 2021",
        "fuente": "SDP / DANE",
        "licencia": "CC-BY-4.0",
        "nota": "Archivo grande (~500MB). La EM2021 se descarga desde la SDP.",
        "archivos": [
            {
                "url": "https://datosabiertos.bogota.gov.co/dataset/8ac12a95-1415-4812-b343-f07f90608014/resource/b3fd892e-b9f9-4f34-ac22-6cc50612eac9/download/em2021.csv",
                "destino": "encuesta_multiproposito/em2021.csv",
                "descripcion": "Microdatos completos Encuesta Multipropósito 2021 (~500MB)",
                "opcional": True,
            },
        ],
    },
    "encuesta_distrital": {
        "nombre": "Encuesta Distrital de Percepción Ciudadana 2025",
        "fuente": "Secretaría Distrital de Planeación",
        "licencia": "CC-BY-4.0",
        "nota": "La Encuesta Distrital se descarga desde la SDP.",
        "archivos": [
            {
                "url": "https://www.sdp.gov.co/sites/default/files/edp-documentos/base_ano_movil_2025.csv",
                "destino": "encuesta_distrital/base_ano_movil_2025.csv",
                "descripcion": "Encuesta Distrital de Percepción - año móvil 2025",
            },
            {
                "url": "https://www.sdp.gov.co/sites/default/files/edp-documentos/20260331_diccionario_base_ano_movil_2025.xlsx",
                "destino": "encuesta_distrital/20260331_diccionario_base_ano_movil_2025.xlsx",
                "descripcion": "Diccionario de variables de la Encuesta Distrital 2025",
            },
        ],
    },
}


# =============================================================================
# FUNCIONES DE DESCARGA
# =============================================================================

def calcular_md5(filepath: Path) -> str:
    """Calcula el hash MD5 de un archivo."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def formato_tamano(bytes_size: int) -> str:
    """Convierte bytes a formato legible."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def descargar_archivo(url: str, destino: Path, descripcion: str = "", opcional: bool = False) -> bool:
    """
    Descarga un archivo desde una URL con reintentos y barra de progreso.
    
    Returns:
        True si se descargó correctamente, False si falló.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)

    # Si ya existe, verificar tamaño
    if destino.exists():
        tamano = destino.stat().st_size
        print(f"  ✓ Ya existe: {destino.name} ({formato_tamano(tamano)})")
        return True

    print(f"  ↓ Descargando: {descripcion or destino.name}")
    print(f"    URL: {url[:80]}...")

    # Headers que simulan un navegador (algunos sitios bloquean requests sin User-Agent)
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    }

    for intento in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, stream=True, timeout=TIMEOUT, allow_redirects=True, headers=headers)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(destino, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            pct = downloaded / total_size * 100
                            print(f"\r    Progreso: {formato_tamano(downloaded)} / {formato_tamano(total_size)} ({pct:.0f}%)", end="", flush=True)

            print()  # Nueva línea después del progreso
            tamano_final = destino.stat().st_size
            print(f"  ✓ Completado: {destino.name} ({formato_tamano(tamano_final)})")
            return True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404 and opcional:
                print(f"\n  ⚠ No encontrado (404) — dataset opcional, se omite.")
                return False
            print(f"\n  ✗ Error HTTP: {e.response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"\n  ✗ Error de conexión")
        except requests.exceptions.Timeout:
            print(f"\n  ✗ Timeout después de {TIMEOUT}s")
        except Exception as e:
            print(f"\n  ✗ Error inesperado: {e}")

        if intento < MAX_RETRIES:
            print(f"    Reintentando en {RETRY_DELAY}s... (intento {intento}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)

    # Si se agotan los reintentos
    if destino.exists():
        destino.unlink()  # Eliminar archivo parcial
    if opcional:
        print(f"  ⚠ No se pudo descargar (opcional): {destino.name}")
        return False
    else:
        print(f"  ✗ FALLÓ después de {MAX_RETRIES} intentos: {destino.name}")
        return False


def descargar_dataset(nombre_clave: str) -> dict:
    """
    Descarga todos los archivos de un dataset.
    
    Returns:
        dict con conteos de éxito/fallo.
    """
    if nombre_clave not in DATASETS:
        print(f"  ✗ Dataset desconocido: {nombre_clave}")
        print(f"    Disponibles: {', '.join(DATASETS.keys())}")
        return {"exito": 0, "fallo": 1}

    ds = DATASETS[nombre_clave]
    print(f"\n{'═' * 60}")
    print(f"  {ds['nombre']}")
    print(f"  Fuente: {ds['fuente']} | Licencia: {ds['licencia']}")
    if "nota" in ds:
        print(f"  Nota: {ds['nota']}")
    print(f"{'═' * 60}")

    exito = 0
    fallo = 0
    for archivo in ds["archivos"]:
        destino = DATA_DIR / archivo["destino"]
        ok = descargar_archivo(
            url=archivo["url"],
            destino=destino,
            descripcion=archivo.get("descripcion", ""),
            opcional=archivo.get("opcional", False),
        )
        if ok:
            exito += 1
        else:
            fallo += 1

    return {"exito": exito, "fallo": fallo}


def verificar_datos() -> None:
    """Verifica qué datos están disponibles localmente."""
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  VERIFICACIÓN DE DATOS LOCALES                              ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    total_archivos = 0
    encontrados = 0

    for nombre_clave, ds in DATASETS.items():
        print(f"  [{nombre_clave}] {ds['nombre']}")
        for archivo in ds["archivos"]:
            total_archivos += 1
            destino = DATA_DIR / archivo["destino"]
            if destino.exists():
                tamano = destino.stat().st_size
                print(f"    ✓ {archivo['destino']} ({formato_tamano(tamano)})")
                encontrados += 1
            else:
                opcional = archivo.get("opcional", False)
                marca = "⚠ (opcional)" if opcional else "✗"
                print(f"    {marca} {archivo['destino']} — NO ENCONTRADO")
        print()

    print(f"  Resumen: {encontrados}/{total_archivos} archivos disponibles")
    if encontrados < total_archivos:
        print(f"  Ejecuta 'python scripts/descargar_datos.py' para descargar los faltantes.")


# =============================================================================
# PROCESAMIENTO POST-DESCARGA: Encuesta Multipropósito 2021
# =============================================================================

def procesar_encuesta_multiproposito() -> None:
    """
    Procesa el CSV grande de la Encuesta Multipropósito 2021 y genera
    extractos temáticos más manejables para el análisis.
    """
    import pandas as pd

    em_path = DATA_DIR / "encuesta_multiproposito" / "em2021.csv"
    if not em_path.exists():
        print("  ⚠ em2021.csv no encontrado — omitiendo procesamiento.")
        return

    print("\n→ Procesando Encuesta Multipropósito 2021...")

    # Columnas de interés para educación y transporte
    cols_educacion = [
        "NPCEP4",       # Edad
        "NPCEP10",      # ¿Asiste a algún establecimiento educativo?
        "NPCEP11AA",    # Minutos de desplazamiento al colegio
        "NHCLP3",       # ¿Se considera pobre?
        "NHCLP4",       # Suficiencia de ingresos (1=no alcanzan, 2=solo mínimos, 3=pueden ahorrar)
        "COD_LOCALIDAD",
        "NOMBRE_LOCALIDAD",
        "FEX_C",        # Factor de expansión
    ]

    try:
        df = pd.read_csv(em_path, usecols=cols_educacion, encoding="latin-1", low_memory=False)
    except (ValueError, UnicodeDecodeError):
        # Intentar con todas las columnas y seleccionar después
        df = pd.read_csv(em_path, encoding="latin-1", low_memory=False)
        cols_presentes = [c for c in cols_educacion if c in df.columns]
        df = df[cols_presentes]

    # Extracto 1: Tiempo al colegio (menores 5-17 que asisten)
    mask_asiste = (
        (df["NPCEP4"] >= 5) & (df["NPCEP4"] <= 17) &
        (df["NPCEP10"] == 1) & (df["NPCEP11AA"].notna()) &
        (df["NPCEP11AA"] < 90)  # Filtrar outliers
    )
    tiempo = df[mask_asiste].rename(columns={
        "NPCEP4": "Edad",
        "NPCEP11AA": "Minutos_al_Colegio",
        "NHCLP3": "Percepcion_Pobreza",
        "NHCLP4": "Suficiencia_Ingresos",
        "FEX_C": "Factor_Expansion",
    })
    tiempo_path = DATA_DIR / "encuesta_multiproposito" / "em2021_tiempo_colegio.csv"
    tiempo.to_csv(tiempo_path, index=False)
    print(f"  ✓ em2021_tiempo_colegio.csv ({len(tiempo)} registros)")

    # Extracto 2: Inasistencia escolar (menores 5-17)
    mask_menor = (df["NPCEP4"] >= 5) & (df["NPCEP4"] <= 17)
    inasis = df[mask_menor].rename(columns={
        "NPCEP4": "Edad",
        "NPCEP10": "Asiste_Educacion",
        "NHCLP3": "Percepcion_Pobreza",
        "NHCLP4": "Suficiencia_Ingresos",
        "FEX_C": "Factor_Expansion",
    })
    inasis_path = DATA_DIR / "encuesta_multiproposito" / "em2021_inasistencia_escolar.csv"
    inasis.to_csv(inasis_path, index=False)
    print(f"  ✓ em2021_inasistencia_escolar.csv ({len(inasis)} registros)")

    # Extracto 3: Resumen por localidad
    import numpy as np
    resumen_rows = []
    for loc, g in inasis.groupby("NOMBRE_LOCALIDAD"):
        n = len(g)
        tasa_inasis = np.average((g["Asiste_Educacion"] != 1).astype(int), weights=g["Factor_Expansion"]) * 100
        pct_pobre = np.average((g["Percepcion_Pobreza"] == 1).astype(int), weights=g["Factor_Expansion"]) * 100
        pct_insuf = np.average((g["Suficiencia_Ingresos"] == 1).astype(int), weights=g["Factor_Expansion"]) * 100

        # Tiempo promedio (solo los que asisten)
        asistentes = g[(g["Asiste_Educacion"] == 1)]
        tiempo_sub = df.loc[asistentes.index]
        if "Minutos_al_Colegio" in asistentes.columns:
            min_col = asistentes["Minutos_al_Colegio"]
        else:
            min_col = tiempo_sub.get("NPCEP11AA", pd.Series(dtype=float))

        prom_min = np.nan
        pct_30 = np.nan
        if min_col.notna().sum() > 10:
            valid = min_col.dropna()
            w = g.loc[valid.index, "Factor_Expansion"]
            prom_min = np.average(valid, weights=w)
            pct_30 = np.average((valid > 30).astype(int), weights=w) * 100

        resumen_rows.append({
            "NOMBRE_LOCALIDAD": loc,
            "Tasa_Inasistencia": round(tasa_inasis, 2),
            "Pct_Pobre": round(pct_pobre, 2),
            "Pct_Ing_Insuficientes": round(pct_insuf, 2),
            "N_Encuestados": n,
            "Prom_Minutos_Colegio": round(prom_min, 1) if not np.isnan(prom_min) else None,
            "Pct_Mas_30min": round(pct_30, 1) if not np.isnan(pct_30) else None,
        })

    resumen = pd.DataFrame(resumen_rows)
    resumen_path = DATA_DIR / "encuesta_multiproposito" / "em2021_resumen_localidad.csv"
    resumen.to_csv(resumen_path, index=False)
    print(f"  ✓ em2021_resumen_localidad.csv ({len(resumen)} localidades)")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Descarga los datasets del Portal de Datos Abiertos de Bogotá para el DataJam.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Datasets disponibles:
  pobreza                 Pobreza y Desigualdad (CSV, ~30KB)
  desercion_upl           Tasa de Deserción por UPL (GeoJSON, ~2.5MB)
  vulnerabilidad_agua     Vulnerabilidad Calidad del Agua (GeoJSON, ~2.5MB)
  violencia_intrafamiliar Violencia Intrafamiliar (CSV, ~110MB)
  matricula               Matrícula Jornada Única (GeoJSON, ~230KB)
  encuesta_multiproposito Encuesta Multipropósito 2021 (CSV, ~500MB)
  encuesta_distrital      Encuesta Distrital Percepción 2025 (CSV)

Ejemplos:
  python scripts/descargar_datos.py                    # Descarga todo
  python scripts/descargar_datos.py --dataset pobreza  # Solo pobreza
  python scripts/descargar_datos.py --solo-verificar   # Solo verifica
  python scripts/descargar_datos.py --sin-opcionales   # Sin archivos grandes
"""
    )
    parser.add_argument(
        "--dataset", "-d",
        help="Descargar solo un dataset específico",
        choices=list(DATASETS.keys()),
    )
    parser.add_argument(
        "--solo-verificar", "-v",
        action="store_true",
        help="Solo verificar qué datos están disponibles localmente",
    )
    parser.add_argument(
        "--sin-opcionales",
        action="store_true",
        help="No descargar archivos marcados como opcionales (ej: em2021.csv de 500MB)",
    )
    parser.add_argument(
        "--procesar",
        action="store_true",
        help="Procesar la Encuesta Multipropósito después de descargar",
    )

    args = parser.parse_args()

    # Crear directorio de datos
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.solo_verificar:
        verificar_datos()
        return

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  DESCARGA DE DATOS — DataJam Edición 4                      ║")
    print("║  Portal de Datos Abiertos de Bogotá                         ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"\n  Directorio de datos: {DATA_DIR}")

    total_exito = 0
    total_fallo = 0

    if args.dataset:
        resultado = descargar_dataset(args.dataset)
        total_exito += resultado["exito"]
        total_fallo += resultado["fallo"]
    else:
        for nombre_clave in DATASETS:
            # Omitir opcionales si se pidió
            if args.sin_opcionales:
                ds = DATASETS[nombre_clave]
                archivos_filtrados = [a for a in ds["archivos"] if not a.get("opcional", False)]
                if not archivos_filtrados:
                    print(f"\n  ⏭ Omitiendo {ds['nombre']} (opcional)")
                    continue

            resultado = descargar_dataset(nombre_clave)
            total_exito += resultado["exito"]
            total_fallo += resultado["fallo"]

    # Procesar EM2021 si se pidió o si se descargó
    if args.procesar or (not args.dataset or args.dataset == "encuesta_multiproposito"):
        em_path = DATA_DIR / "encuesta_multiproposito" / "em2021.csv"
        if em_path.exists():
            procesar_encuesta_multiproposito()

    # Resumen final
    print(f"\n{'═' * 60}")
    print(f"  RESUMEN: {total_exito} archivos descargados, {total_fallo} fallos")
    if total_fallo > 0:
        print("  ⚠ Algunos archivos no se pudieron descargar.")
        print("    Ejecuta de nuevo o descárgalos manualmente.")
    else:
        print("  ✓ Todos los archivos descargados correctamente.")
    print(f"{'═' * 60}")


if __name__ == "__main__":
    main()
