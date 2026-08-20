"""
Módulo de carga centralizada de datos para el Dashboard DataJam.
Carga y procesa todos los datasets necesarios para las visualizaciones.
"""

import os
import json
import math
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


# =============================================================================
# UTILIDADES DE REPROYECCIÓN
# =============================================================================

def _mercator_to_wgs84(x, y):
    """Convierte coordenadas EPSG:3857 (Web Mercator) a EPSG:4326 (WGS84)."""
    lon = x * 180.0 / 20037508.34
    lat = math.atan(math.exp(y * math.pi / 20037508.34)) * 360.0 / math.pi - 90.0
    return [lon, lat]


def _reproject_coords(coords):
    """Reproyecta recursivamente una estructura de coordenadas GeoJSON."""
    if isinstance(coords[0], (int, float)):
        # Es un punto [x, y] o [x, y, z]
        return _mercator_to_wgs84(coords[0], coords[1])
    else:
        return [_reproject_coords(c) for c in coords]


def _reproject_geojson(geojson):
    """Reproyecta un GeoJSON completo de EPSG:3857 a EPSG:4326."""
    reprojected = json.loads(json.dumps(geojson))  # Deep copy
    for feature in reprojected["features"]:
        feature["geometry"]["coordinates"] = _reproject_coords(
            feature["geometry"]["coordinates"]
        )
    # Actualizar CRS
    if "crs" in reprojected:
        del reprojected["crs"]
    return reprojected


# =============================================================================
# 1. DESERCIÓN POR UPL (GeoJSON)
# =============================================================================

def cargar_desercion_geojson():
    """Carga el GeoJSON de deserción con geometrías reproyectadas a WGS84."""
    path = os.path.join(DATA_DIR, "desercion_upl", "tasas_upl.geojson")
    with open(path, "r", encoding="utf-8") as f:
        geojson = json.load(f)
    # El GeoJSON original está en EPSG:3857, reproyectar a EPSG:4326
    return _reproject_geojson(geojson)


def cargar_desercion_df():
    """Carga las tasas de deserción como DataFrame."""
    geojson = cargar_desercion_geojson()
    registros = []
    for feat in geojson["features"]:
        p = feat["properties"]
        registros.append({
            "CODIGO_UPL": p["CODIGO_UPL"],
            "NOM_UPL": p["NOM_UPL"],
            "Desercion_Oficial": p["TtotalDeserOf_UPL"],
            "Desercion_NoOficial": p["TtotalDeserNOf_UPL"],
            "Reprobacion_Oficial": p["TtotalReprOf_UPL"],
            "Reprobacion_NoOficial": p["TtotalReprNOf_UPL"],
            "Aprobacion_Oficial": p["TtotalAprOf_UPL"],
            "Aprobacion_NoOficial": p["TtotalAprNOf_UPL"],
        })
    return pd.DataFrame(registros)


# =============================================================================
# 2. VULNERABILIDAD HÍDRICA POR LOCALIDAD (GeoJSON)
# =============================================================================

def cargar_vulnerabilidad_geojson():
    """Carga el GeoJSON de vulnerabilidad hídrica reproyectado a WGS84."""
    path = os.path.join(DATA_DIR, "vulnerabilidad_agua", "vulnerabilidad_agua.geojson")
    with open(path, "r", encoding="utf-8") as f:
        geojson = json.load(f)
    # Reproyectar si está en EPSG:3857
    if "crs" in geojson:
        return _reproject_geojson(geojson)
    return geojson


def cargar_vulnerabilidad_df():
    """Carga vulnerabilidad hídrica como DataFrame."""
    geojson = cargar_vulnerabilidad_geojson()
    registros = []
    for feat in geojson["features"]:
        p = feat["properties"]
        registros.append({
            "Cod_Localidad": p["cdglocalid"],
            "Localidad": p["localidad"],
            "Poblacion_2050": int(p["pbl2050to"]),
            "Cls_Poblacion": p["clspbl205"],
            "Disp_Hidrica": float(p["dsphidrica"]),
            "Cls_Disp_Hidrica": p["clsdsphid"],
            "Reg_Hidrica": float(p["rglhidrica"]),
            "Cls_Reg_Hidrica": p["clsrglhid"],
            "Calidad_Agua": float(p["cldagua"]),
            "Cls_Calidad_Agua": p["cls_cldagu"],
        })
    return pd.DataFrame(registros)


# =============================================================================
# 3. POBREZA Y DESIGUALDAD (CSV)
# =============================================================================

def cargar_pobreza():
    """Carga el dataset de pobreza, IPM y Gini por localidad/año."""
    path = os.path.join(DATA_DIR, "pobreza", "osb_demografia-pobrezaygini.csv")
    df = pd.read_csv(path, sep=";", encoding="latin-1")
    df.columns = ["Año", "Localidad", "Indicador", "Categoría", "Sexo", "Valor"]
    df["Valor"] = df["Valor"].astype(str).str.replace(",", ".").astype(float)
    df["Año"] = df["Año"].astype(int)
    return df


def obtener_serie_temporal_bogota():
    """Obtiene serie temporal IPM + privaciones educativas para Bogotá."""
    df = cargar_pobreza()
    bogota = df[
        (df["Localidad"].str.contains("Bogot", na=False)) &
        (df["Sexo"].str.contains("Ambos", na=False))
    ]

    # IPM
    ipm = bogota[bogota["Indicador"] == "IPM"][["Año", "Valor"]].rename(
        columns={"Valor": "IPM"})

    # Privaciones educativas
    privaciones = bogota[
        (bogota["Indicador"] == "Privaciones") &
        (bogota["Categoría"].isin([
            "Inasistencia escolar",
            "Rezago escolar",
            "Bajo logro educativo",
            "Analfabetismo"
        ]))
    ].pivot_table(index="Año", columns="Categoría", values="Valor").reset_index()

    # Combinar
    serie = ipm.merge(privaciones, on="Año", how="outer").sort_values("Año").dropna(subset=["IPM"])
    return serie


def obtener_pobreza_por_localidad(año=2021):
    """Obtiene pobreza monetaria por localidad para un año dado."""
    df = cargar_pobreza()
    pobreza_loc = df[
        (df["Indicador"] == "Pobreza monetaria") &
        (df["Año"] == año) &
        (df["Sexo"].str.contains("Ambos", na=False)) &
        (~df["Localidad"].str.contains("Bogot", na=False))
    ][["Localidad", "Valor"]].rename(columns={"Valor": "Pobreza_Monetaria"})

    gini_loc = df[
        (df["Indicador"] == "Coeficiente de Gini") &
        (df["Año"] == año) &
        (df["Sexo"].str.contains("Ambos", na=False)) &
        (~df["Localidad"].str.contains("Bogot", na=False))
    ][["Localidad", "Valor"]].rename(columns={"Valor": "Gini"})

    ipm_loc = df[
        (df["Indicador"] == "IPM") &
        (df["Año"] == año) &
        (df["Sexo"].str.contains("Ambos", na=False)) &
        (~df["Localidad"].str.contains("Bogot", na=False))
    ][["Localidad", "Valor"]].rename(columns={"Valor": "IPM"})

    result = pobreza_loc.merge(gini_loc, on="Localidad", how="outer")
    result = result.merge(ipm_loc, on="Localidad", how="outer")
    return result


# =============================================================================
# 4. ENCUESTA DISTRITAL - AGREGADO POR UPL
# =============================================================================

def cargar_encuesta_agregada_upl():
    """
    Carga la encuesta distrital y agrega indicadores por UPL.
    Retorna un DataFrame con % de indicadores socioeconómicos por UPL.
    """
    path = os.path.join(DATA_DIR, "encuesta_distrital", "base_ano_movil_2025.csv")
    cols_necesarias = [
        "C303", "Ax502", "Bx301", "Cx301", "C302", "H1",
        "Ax401", "Ax501", "F405", "G406",
        "IASS_B", "IPPEB_G", "IPPEB_I", "IPS_dia",
        "Cod_Locali", "Nom_Locali", "Cod_UPL", "Nom_UPL",
        "fexp_calh_anu",
    ]
    df = pd.read_csv(path, low_memory=False)
    cols_exist = [c for c in cols_necesarias if c in df.columns]
    df = df[cols_exist].copy()

    # Variables derivadas
    df["Se_Considera_Pobre"] = (df["C303"] == 1).astype(int)
    df["Ingresos_Insuficientes"] = (df["Ax502"] == 1).astype(int)
    df["Ingresos_Precarios"] = (df["Ax502"].isin([1, 2])).astype(int)
    df["Inseguridad_Alimentaria"] = (df["C302"] == 1).astype(int)
    df["Bajo_Acceso_Educacion"] = (df["Bx301"].isin([1, 2])).astype(int)
    df["Bajo_Acceso_Empleo"] = (df["Cx301"].isin([1, 2])).astype(int)
    df["Estrato_Bajo"] = (df["H1"].isin([1, 2])).astype(int)
    df["Desempleado"] = (df["Ax501"] == 2).astype(int)

    peso = "fexp_calh_anu"

    # Agregar por UPL
    def agg_upl(g):
        result = {}
        result["Pct_Pobre"] = np.average(g["Se_Considera_Pobre"], weights=g[peso]) * 100
        result["Pct_Ing_Insuficientes"] = np.average(g["Ingresos_Insuficientes"], weights=g[peso]) * 100
        result["Pct_Ing_Precarios"] = np.average(g["Ingresos_Precarios"], weights=g[peso]) * 100
        result["Pct_Inseg_Alimentaria"] = np.average(g["Inseguridad_Alimentaria"], weights=g[peso]) * 100
        result["Pct_Estrato_Bajo"] = np.average(g["Estrato_Bajo"], weights=g[peso]) * 100
        result["Pct_Desempleado"] = np.average(g["Desempleado"], weights=g[peso]) * 100

        # Acceso educación (excluir NS/NR = 99)
        mask_educ = g["Bx301"] != 99
        if mask_educ.sum() > 0:
            result["Pct_Bajo_Acceso_Educ"] = np.average(
                g.loc[mask_educ, "Bajo_Acceso_Educacion"],
                weights=g.loc[mask_educ, peso]
            ) * 100
        else:
            result["Pct_Bajo_Acceso_Educ"] = np.nan

        # Acceso empleo
        mask_emp = g["Cx301"] != 99
        if mask_emp.sum() > 0:
            result["Pct_Bajo_Acceso_Empleo"] = np.average(
                g.loc[mask_emp, "Bajo_Acceso_Empleo"],
                weights=g.loc[mask_emp, peso]
            ) * 100
        else:
            result["Pct_Bajo_Acceso_Empleo"] = np.nan

        result["N_Encuestados"] = len(g)
        result["Localidad"] = g["Nom_Locali"].mode().iloc[0] if len(g) > 0 else ""
        result["Nom_UPL"] = g["Nom_UPL"].mode().iloc[0] if len(g) > 0 else ""
        return pd.Series(result)

    agg = df.groupby("Cod_UPL").apply(agg_upl, include_groups=False).reset_index()
    return agg


# =============================================================================
# 5. CRUCE: ENCUESTA + DESERCIÓN POR UPL
# =============================================================================

def cargar_cruce_encuesta_desercion():
    """
    Cruza los datos de la encuesta distrital (agregados por UPL)
    con las tasas de deserción por UPL.
    """
    agg_enc = cargar_encuesta_agregada_upl()
    df_deser = cargar_desercion_df()

    # Ambos datasets usan formato "UPLxx"
    cruce = agg_enc.merge(df_deser, left_on="Cod_UPL", right_on="CODIGO_UPL", how="inner")
    return cruce


# =============================================================================
# 6. VIOLENCIA INTRAFAMILIAR
# =============================================================================

def cargar_violencia():
    """Carga datos de violencia intrafamiliar."""
    path = os.path.join(DATA_DIR, "violencia_intrafamiliar", "osb_saludmental-vintrafamiliar.csv")
    df = pd.read_csv(path, sep=";", encoding="latin-1")
    # Corregir BOM en nombre de columna
    df.columns = [c.replace("\ufeff", "") for c in df.columns]
    df = df.rename(columns={"ano": "Año"})
    return df


# =============================================================================
# 7. MATRICULACIONES
# =============================================================================

def cargar_matricula_df():
    """Carga las matriculaciones como DataFrame."""
    path = os.path.join(DATA_DIR, "matricula", "matriculaciones.geojson")
    with open(path, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    registros = []
    for feat in geojson["features"]:
        p = feat["properties"]
        registros.append({
            "Nombre_Establecimiento": p.get("NOMBRE_EST", ""),
            "Nombre_Sede": p.get("NOMBRE_SED", ""),
            "Direccion": p.get("DIRECCION", ""),
            "Sector": p.get("SECTOR", 0),
            "Matricula_Preescolar": p.get("TMATRIC_PR", 0) or 0,
            "Matricula_Primaria": p.get("TMATRIC__1", 0) or 0,
            "Matricula_Secundaria": p.get("TMATRIC_SE", 0) or 0,
            "Matricula_Media": p.get("TMATRIC_ME", 0) or 0,
            "Matricula_Total": p.get("TMATRIC_GE", 0) or 0,
            "Cod_Localidad": p.get("loc", ""),
        })
    return pd.DataFrame(registros)
