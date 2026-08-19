"""
Análisis: Relación entre Pobreza y Deserción Escolar en Bogotá D.C.
=====================================================================
DataJam Edición 4 - Universidad Distrital Francisco José de Caldas

Este script analiza la asociación entre condiciones socioeconómicas
(pobreza monetaria, IPM, Gini) y resultados educativos (deserción,
reprobación, inasistencia escolar) usando datos abiertos del Distrito.

Fuentes:
- Pobreza y Desigualdad: DANE / SDP - Encuesta Multipropósito
- Tasas de Deserción por UPL: Secretaría de Educación de Bogotá
- Vulnerabilidad Hídrica: Secretaría Distrital de Ambiente
"""

import json
import csv
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Configuración visual
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
sns.set_theme(style="whitegrid", palette="muted")

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POBREZA_CSV = os.path.join(BASE_DIR, "Pobreza&Desigualdad", "osb_demografia-pobrezaygini.csv")
DESERCION_GEOJSON = os.path.join(BASE_DIR, "TasaDesercionUPC", "tasaDesercionUPL.geojson")
VULNERABILIDAD_GEOJSON = os.path.join(BASE_DIR, "VulnerabilidadAgua", "vulnerabilidaAgua.geojson")
OUTPUT_DIR = os.path.join(BASE_DIR, "resultados_analisis")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =============================================================================
# 1. CARGA DE DATOS
# =============================================================================

def cargar_pobreza():
    """Carga y estructura el CSV de pobreza y desigualdad."""
    df = pd.read_csv(POBREZA_CSV, sep=";", encoding="latin-1")
    # Limpiar columnas (pueden tener caracteres especiales por encoding)
    df.columns = ["Año", "Localidad", "Indicador", "Categoría", "Sexo", "Valor"]
    # Convertir Valor a numérico (usa coma decimal)
    df["Valor"] = df["Valor"].astype(str).str.replace(",", ".").astype(float)
    df["Año"] = df["Año"].astype(int)
    return df


def cargar_desercion():
    """Carga el GeoJSON de tasas de deserción por UPL."""
    with open(DESERCION_GEOJSON, "r") as f:
        data = json.load(f)

    registros = []
    for feat in data["features"]:
        p = feat["properties"]
        registros.append({
            "CODIGO_UPL": p["CODIGO_UPL"],
            "NOM_UPL": p["NOM_UPL"],
            "Tasa_Aprobacion_Oficial": p["TtotalAprOf_UPL"],
            "Tasa_Aprobacion_NoOficial": p["TtotalAprNOf_UPL"],
            "Tasa_Desercion_Oficial": p["TtotalDeserOf_UPL"],
            "Tasa_Desercion_NoOficial": p["TtotalDeserNOf_UPL"],
            "Tasa_Reprobacion_Oficial": p["TtotalReprOf_UPL"],
            "Tasa_Reprobacion_NoOficial": p["TtotalReprNOf_UPL"],
            "Fecha": p["Fecha"],
        })
    return pd.DataFrame(registros)


def cargar_vulnerabilidad():
    """Carga el GeoJSON de vulnerabilidad hídrica por localidad."""
    with open(VULNERABILIDAD_GEOJSON, "r") as f:
        data = json.load(f)

    registros = []
    for feat in data["features"]:
        p = feat["properties"]
        registros.append({
            "cdglocalid": int(p["cdglocalid"]),
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
# 2. ANÁLISIS TEMPORAL: IPM, Pobreza y Variables Educativas en Bogotá
# =============================================================================

def analisis_temporal(df_pobreza):
    """
    Analiza la evolución temporal de pobreza e indicadores educativos
    a nivel Bogotá D.C. para encontrar patrones de asociación.
    """
    print("\n" + "=" * 70)
    print("ANÁLISIS 1: EVOLUCIÓN TEMPORAL - POBREZA E INDICADORES EDUCATIVOS")
    print("=" * 70)

    # Filtrar solo Bogotá D.C. y ambos sexos
    bogota = df_pobreza[
        (df_pobreza["Localidad"].str.contains("Bogot", na=False)) &
        (df_pobreza["Sexo"].str.contains("Ambos", na=False))
    ].copy()

    # --- IPM a lo largo del tiempo ---
    ipm = bogota[bogota["Indicador"] == "IPM"][["Año", "Valor"]].rename(
        columns={"Valor": "IPM"}
    )

    # --- Privaciones educativas ---
    priv_educ = bogota[
        (bogota["Indicador"] == "Privaciones") &
        (bogota["Categoría"].isin([
            "Inasistencia escolar",
            "Rezago escolar",
            "Bajo logro educativo",
            "Analfabetismo"
        ]))
    ].pivot_table(index="Año", columns="Categoría", values="Valor").reset_index()

    # --- Combinar ---
    temporal = ipm.merge(priv_educ, on="Año", how="outer").sort_values("Año")
    temporal = temporal.dropna(subset=["IPM"])

    print("\nDatos temporales Bogotá D.C.:")
    print(temporal.to_string(index=False))

    # --- Correlaciones ---
    print("\n--- Correlaciones con IPM ---")
    cols_educ = [c for c in temporal.columns if c not in ["Año", "IPM"]]
    for col in cols_educ:
        sub = temporal[["IPM", col]].dropna()
        if len(sub) >= 3:
            r, p = stats.pearsonr(sub["IPM"], sub[col])
            rho, p_spearman = stats.spearmanr(sub["IPM"], sub[col])
            sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
            print(f"  IPM vs {col}: Pearson r={r:.3f} (p={p:.4f}){sig} | Spearman ρ={rho:.3f} (p={p_spearman:.4f})")

    # --- Gráfico temporal ---
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Panel superior: IPM
    ax1 = axes[0]
    ax1.plot(temporal["Año"], temporal["IPM"], "o-", color="darkred",
             linewidth=2, markersize=8, label="IPM (Pobreza Multidimensional)")
    ax1.set_ylabel("IPM (%)")
    ax1.set_title("Evolución del Índice de Pobreza Multidimensional - Bogotá D.C.",
                  fontsize=13, fontweight="bold")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)

    # Panel inferior: Privaciones educativas
    ax2 = axes[1]
    colores = {"Inasistencia escolar": "crimson", "Rezago escolar": "darkorange",
               "Bajo logro educativo": "steelblue", "Analfabetismo": "gray"}
    for col in cols_educ:
        if col in temporal.columns:
            ax2.plot(temporal["Año"], temporal[col], "o-",
                     color=colores.get(col, "black"), linewidth=2,
                     markersize=6, label=col)
    ax2.set_xlabel("Año")
    ax2.set_ylabel("Porcentaje (%)")
    ax2.set_title("Evolución de Privaciones Educativas - Bogotá D.C.",
                  fontsize=13, fontweight="bold")
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "01_evolucion_temporal_pobreza_educacion.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("\n✓ Gráfico guardado: 01_evolucion_temporal_pobreza_educacion.png")

    return temporal


# =============================================================================
# 3. ANÁLISIS TERRITORIAL: POBREZA POR LOCALIDAD
# =============================================================================

def analisis_territorial(df_pobreza, df_vulnerabilidad):
    """
    Analiza la relación entre pobreza monetaria por localidad y
    vulnerabilidad hídrica como proxy de condiciones del territorio.
    """
    print("\n" + "=" * 70)
    print("ANÁLISIS 2: POBREZA MONETARIA POR LOCALIDAD (2021)")
    print("=" * 70)

    # Filtrar pobreza monetaria por localidad, año 2021 (más completo)
    pobreza_loc = df_pobreza[
        (df_pobreza["Indicador"] == "Pobreza monetaria") &
        (df_pobreza["Año"] == 2021) &
        (df_pobreza["Sexo"].str.contains("Ambos", na=False)) &
        (~df_pobreza["Localidad"].str.contains("Bogot", na=False))
    ][["Localidad", "Valor"]].rename(columns={"Valor": "Pobreza_Monetaria_2021"})

    # Pobreza extrema
    extrema_loc = df_pobreza[
        (df_pobreza["Indicador"] == "Pobreza monetaria extrema") &
        (df_pobreza["Año"] == 2021) &
        (df_pobreza["Sexo"].str.contains("Ambos", na=False)) &
        (~df_pobreza["Localidad"].str.contains("Bogot", na=False))
    ][["Localidad", "Valor"]].rename(columns={"Valor": "Pobreza_Extrema_2021"})

    # Gini
    gini_loc = df_pobreza[
        (df_pobreza["Indicador"] == "Coeficiente de Gini") &
        (df_pobreza["Año"] == 2021) &
        (df_pobreza["Sexo"].str.contains("Ambos", na=False)) &
        (~df_pobreza["Localidad"].str.contains("Bogot", na=False))
    ][["Localidad", "Valor"]].rename(columns={"Valor": "Gini_2021"})

    # Combinar
    territorial = pobreza_loc.merge(extrema_loc, on="Localidad", how="outer")
    territorial = territorial.merge(gini_loc, on="Localidad", how="outer")

    # Mapeo de nombres para unir con vulnerabilidad
    nombre_map = {
        "USAQUEN": "Usaquén", "CHAPINERO": "Chapinero", "SANTA FE": "Santa Fe",
        "SAN CRISTOBAL": "San Cristóbal", "USME": "Usme", "TUNJUELITO": "Tunjuelito",
        "BOSA": "Bosa", "KENNEDY": "Kennedy", "FONTIBON": "Fontibón",
        "ENGATIVA": "Engativá", "SUBA": "Suba", "BARRIOS UNIDOS": "Barrios Unidos",
        "TEUSAQUILLO": "Teusaquillo", "LOS MARTIRES": "Los Mártires",
        "ANTONIO NARI": "Antonio Nariño", "PUENTE ARANDA": "Puente Aranda",
        "CANDELARIA": "La Candelaria", "RAFAEL URIBE URIBE": "Rafael Uribe Uribe",
        "CIUDAD BOLIVAR": "Ciudad Bolívar", "SUMAPAZ": "Sumapaz"
    }
    nombre_map_inv = {v: k for k, v in nombre_map.items()}

    # Normalizar nombre en vulnerabilidad para join
    df_vulnerabilidad["Localidad_Norm"] = df_vulnerabilidad["Localidad"].map(nombre_map)

    # Merge territorial con vulnerabilidad
    territorial_full = territorial.merge(
        df_vulnerabilidad[["Localidad_Norm", "Cls_Poblacion", "Cls_Disp_Hidrica",
                           "Cls_Calidad_Agua", "Poblacion_2050"]],
        left_on="Localidad", right_on="Localidad_Norm", how="left"
    )

    print("\nPobreza monetaria por localidad (2021):")
    print(territorial_full[["Localidad", "Pobreza_Monetaria_2021", "Pobreza_Extrema_2021",
                            "Gini_2021", "Cls_Poblacion", "Cls_Calidad_Agua"]]
          .sort_values("Pobreza_Monetaria_2021", ascending=False)
          .to_string(index=False))

    # --- Gráfico de barras de pobreza por localidad ---
    fig, ax = plt.subplots(figsize=(14, 8))
    datos_plot = territorial_full.dropna(subset=["Pobreza_Monetaria_2021"]).sort_values(
        "Pobreza_Monetaria_2021", ascending=True
    )
    colores = datos_plot["Pobreza_Monetaria_2021"].apply(
        lambda x: "darkred" if x > 40 else "orangered" if x > 25 else "gold" if x > 15 else "green"
    )
    ax.barh(datos_plot["Localidad"], datos_plot["Pobreza_Monetaria_2021"], color=colores)
    ax.axvline(x=35.8, color="black", linestyle="--", linewidth=1.5, label="Promedio Bogotá (35.8%)")
    ax.set_xlabel("Pobreza Monetaria (%)", fontsize=12)
    ax.set_title("Pobreza Monetaria por Localidad - Bogotá D.C. (2021)",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "02_pobreza_monetaria_por_localidad.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("\n✓ Gráfico guardado: 02_pobreza_monetaria_por_localidad.png")

    return territorial_full


# =============================================================================
# 4. ANÁLISIS DE DESERCIÓN POR UPL
# =============================================================================

def analisis_desercion_upl(df_desercion):
    """
    Análisis descriptivo de las tasas de deserción por UPL.
    """
    print("\n" + "=" * 70)
    print("ANÁLISIS 3: TASAS DE DESERCIÓN ESCOLAR POR UPL (2024)")
    print("=" * 70)

    # Mapeo aproximado UPL → Localidad principal (basado en POT Bogotá 2022-2035)
    # Las UPL no coinciden 1:1 con localidades, pero cada una tiene una localidad predominante
    upl_localidad = {
        "01": "Sumapaz", "02": "Ciudad Bolívar", "03": "Ciudad Bolívar",
        "04": "Usme", "05": "San Cristóbal", "06": "Cerros Orientales",
        "07": "Usaquén", "08": "Kennedy", "09": "Fontibón",
        "10": "Engativá", "11": "Suba", "12": "Suba",
        "13": "Teusaquillo", "14": "Puente Aranda", "15": "Barrios Unidos",
        "16": "Chapinero", "17": "Usaquén", "18": "Suba",
        "19": "Engativá", "20": "Rafael Uribe Uribe", "21": "Tunjuelito",
        "22": "Santa Fe", "23": "San Cristóbal", "24": "Usme",
        "25": "Ciudad Bolívar", "26": "Bosa", "27": "Kennedy",
        "28": "Kennedy", "29": "Fontibón", "30": "Bosa",
        "31": "Bosa", "32": "Ciudad Bolívar", "33": "Ciudad Bolívar",
    }

    df_desercion["Localidad_Aprox"] = df_desercion["NOM_UPL"].map(upl_localidad)

    print("\nEstadísticas de Deserción por UPL (sector oficial):")
    print(f"  Media:   {df_desercion['Tasa_Desercion_Oficial'].mean():.2f}%")
    print(f"  Mediana: {df_desercion['Tasa_Desercion_Oficial'].median():.2f}%")
    print(f"  Mín:     {df_desercion['Tasa_Desercion_Oficial'].min():.2f}%")
    print(f"  Máx:     {df_desercion['Tasa_Desercion_Oficial'].max():.2f}%")
    print(f"  Desv.Est:{df_desercion['Tasa_Desercion_Oficial'].std():.2f}%")

    # Top 10 UPL con mayor deserción
    top10 = df_desercion.nlargest(10, "Tasa_Desercion_Oficial")[
        ["CODIGO_UPL", "Localidad_Aprox", "Tasa_Desercion_Oficial",
         "Tasa_Reprobacion_Oficial", "Tasa_Aprobacion_Oficial"]
    ]
    print("\nTop 10 UPL con mayor deserción (sector oficial):")
    print(top10.to_string(index=False))

    # Promediar por localidad aproximada
    deser_por_loc = df_desercion.groupby("Localidad_Aprox").agg(
        Desercion_Oficial_Prom=("Tasa_Desercion_Oficial", "mean"),
        Reprobacion_Oficial_Prom=("Tasa_Reprobacion_Oficial", "mean"),
        Aprobacion_Oficial_Prom=("Tasa_Aprobacion_Oficial", "mean"),
        Num_UPL=("CODIGO_UPL", "count"),
    ).reset_index()

    print("\nDeserción promedio por localidad (aproximación UPL→Localidad):")
    print(deser_por_loc.sort_values("Desercion_Oficial_Prom", ascending=False).to_string(index=False))

    # --- Gráfico de deserción por UPL ---
    fig, ax = plt.subplots(figsize=(14, 9))
    datos_plot = df_desercion.sort_values("Tasa_Desercion_Oficial", ascending=True)
    colores = datos_plot["Tasa_Desercion_Oficial"].apply(
        lambda x: "darkred" if x > 3.5 else "orangered" if x > 2.5 else "gold" if x > 2 else "green"
    )
    etiquetas = datos_plot.apply(
        lambda r: f"UPL {r['NOM_UPL']} ({r['Localidad_Aprox']})", axis=1
    )
    ax.barh(etiquetas, datos_plot["Tasa_Desercion_Oficial"], color=colores)
    media = df_desercion["Tasa_Desercion_Oficial"].mean()
    ax.axvline(x=media, color="black", linestyle="--", linewidth=1.5,
               label=f"Promedio ({media:.2f}%)")
    ax.set_xlabel("Tasa de Deserción Oficial (%)", fontsize=12)
    ax.set_title("Tasa de Deserción Escolar por UPL - Sector Oficial (2024)",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "03_desercion_por_upl.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("\n✓ Gráfico guardado: 03_desercion_por_upl.png")

    return df_desercion, deser_por_loc


# =============================================================================
# 5. CRUCE: POBREZA POR LOCALIDAD vs DESERCIÓN ESTIMADA POR LOCALIDAD
# =============================================================================

def analisis_cruce(territorial, deser_por_loc):
    """
    Cruza la pobreza monetaria por localidad con la deserción estimada
    a nivel localidad (promedio de UPLs).
    """
    print("\n" + "=" * 70)
    print("ANÁLISIS 4: CORRELACIÓN POBREZA vs DESERCIÓN POR LOCALIDAD")
    print("=" * 70)

    # Merge
    cruce = territorial.merge(
        deser_por_loc, left_on="Localidad", right_on="Localidad_Aprox", how="inner"
    )

    if cruce.empty:
        # Intentar match más flexible
        territorial["Localidad_lower"] = territorial["Localidad"].str.lower().str.strip()
        deser_por_loc["Localidad_lower"] = deser_por_loc["Localidad_Aprox"].str.lower().str.strip()
        cruce = territorial.merge(deser_por_loc, on="Localidad_lower", how="inner")

    print(f"\nLocalidades cruzadas: {len(cruce)}")

    if len(cruce) < 3:
        print("⚠ Pocas localidades para el análisis de correlación.")
        print("  Esto se debe a que las UPL no coinciden 1:1 con localidades.")
        print("  Se mostrará el análisis disponible.\n")

    if not cruce.empty and len(cruce) >= 3:
        print("\nDatos cruzados (Pobreza vs Deserción por Localidad):")
        print(cruce[["Localidad", "Pobreza_Monetaria_2021",
                     "Desercion_Oficial_Prom", "Reprobacion_Oficial_Prom"]].to_string(index=False))

        # --- Correlación ---
        sub = cruce[["Pobreza_Monetaria_2021", "Desercion_Oficial_Prom"]].dropna()
        if len(sub) >= 3:
            r, p = stats.pearsonr(sub["Pobreza_Monetaria_2021"], sub["Desercion_Oficial_Prom"])
            rho, p_sp = stats.spearmanr(sub["Pobreza_Monetaria_2021"], sub["Desercion_Oficial_Prom"])
            print(f"\n--- Correlación: Pobreza Monetaria vs Deserción ---")
            print(f"  Pearson  r = {r:.4f} (p = {p:.4f})")
            print(f"  Spearman ρ = {rho:.4f} (p = {p_sp:.4f})")
            if p < 0.05:
                print("  → Correlación estadísticamente significativa (p < 0.05)")
            elif p < 0.1:
                print("  → Correlación marginalmente significativa (p < 0.1)")
            else:
                print("  → Correlación NO significativa con los datos disponibles")

        # --- Correlación pobreza vs reprobación ---
        sub2 = cruce[["Pobreza_Monetaria_2021", "Reprobacion_Oficial_Prom"]].dropna()
        if len(sub2) >= 3:
            r2, p2 = stats.pearsonr(sub2["Pobreza_Monetaria_2021"], sub2["Reprobacion_Oficial_Prom"])
            print(f"\n--- Correlación: Pobreza Monetaria vs Reprobación ---")
            print(f"  Pearson  r = {r2:.4f} (p = {p2:.4f})")

        # --- Scatter Plot principal ---
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))

        # Scatter: Pobreza vs Deserción
        ax = axes[0]
        ax.scatter(cruce["Pobreza_Monetaria_2021"], cruce["Desercion_Oficial_Prom"],
                   s=100, c="darkred", alpha=0.7, edgecolors="black")
        for _, row in cruce.iterrows():
            nombre = row.get("Localidad", row.get("Localidad_Aprox", ""))
            ax.annotate(nombre, (row["Pobreza_Monetaria_2021"], row["Desercion_Oficial_Prom"]),
                        fontsize=8, ha="left", va="bottom", alpha=0.8)
        # Línea de tendencia
        if len(sub) >= 3:
            z = np.polyfit(sub["Pobreza_Monetaria_2021"], sub["Desercion_Oficial_Prom"], 1)
            p_line = np.poly1d(z)
            x_range = np.linspace(sub["Pobreza_Monetaria_2021"].min(),
                                  sub["Pobreza_Monetaria_2021"].max(), 100)
            ax.plot(x_range, p_line(x_range), "--", color="gray", linewidth=1.5)
            ax.set_title(f"Pobreza vs Deserción (r={r:.3f}, p={p:.3f})",
                         fontsize=12, fontweight="bold")
        else:
            ax.set_title("Pobreza vs Deserción", fontsize=12, fontweight="bold")
        ax.set_xlabel("Pobreza Monetaria 2021 (%)")
        ax.set_ylabel("Tasa de Deserción Oficial Promedio (%)")
        ax.grid(True, alpha=0.3)

        # Scatter: Pobreza vs Reprobación
        ax2 = axes[1]
        ax2.scatter(cruce["Pobreza_Monetaria_2021"], cruce["Reprobacion_Oficial_Prom"],
                    s=100, c="darkorange", alpha=0.7, edgecolors="black")
        for _, row in cruce.iterrows():
            nombre = row.get("Localidad", row.get("Localidad_Aprox", ""))
            ax2.annotate(nombre, (row["Pobreza_Monetaria_2021"], row["Reprobacion_Oficial_Prom"]),
                         fontsize=8, ha="left", va="bottom", alpha=0.8)
        if len(sub2) >= 3:
            z2 = np.polyfit(sub2["Pobreza_Monetaria_2021"], sub2["Reprobacion_Oficial_Prom"], 1)
            p_line2 = np.poly1d(z2)
            x_range2 = np.linspace(sub2["Pobreza_Monetaria_2021"].min(),
                                   sub2["Pobreza_Monetaria_2021"].max(), 100)
            ax2.plot(x_range2, p_line2(x_range2), "--", color="gray", linewidth=1.5)
            ax2.set_title(f"Pobreza vs Reprobación (r={r2:.3f}, p={p2:.3f})",
                          fontsize=12, fontweight="bold")
        else:
            ax2.set_title("Pobreza vs Reprobación", fontsize=12, fontweight="bold")
        ax2.set_xlabel("Pobreza Monetaria 2021 (%)")
        ax2.set_ylabel("Tasa de Reprobación Oficial Promedio (%)")
        ax2.grid(True, alpha=0.3)

        plt.suptitle("Relación entre Pobreza y Resultados Educativos por Localidad",
                     fontsize=14, fontweight="bold", y=1.02)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "04_scatter_pobreza_vs_desercion.png"),
                    dpi=150, bbox_inches="tight")
        plt.close()
        print("\n✓ Gráfico guardado: 04_scatter_pobreza_vs_desercion.png")

    return cruce


# =============================================================================
# 6. ANÁLISIS IPM vs INASISTENCIA (Serie Temporal)
# =============================================================================

def analisis_ipm_inasistencia(df_pobreza):
    """
    Scatter plot del IPM vs Inasistencia escolar a través del tiempo.
    """
    print("\n" + "=" * 70)
    print("ANÁLISIS 5: IPM vs INASISTENCIA ESCOLAR (Serie Temporal)")
    print("=" * 70)

    bogota = df_pobreza[
        (df_pobreza["Localidad"].str.contains("Bogot", na=False)) &
        (df_pobreza["Sexo"].str.contains("Ambos", na=False))
    ]

    ipm = bogota[bogota["Indicador"] == "IPM"][["Año", "Valor"]].rename(
        columns={"Valor": "IPM"})
    inasistencia = bogota[
        (bogota["Indicador"] == "Privaciones") &
        (bogota["Categoría"] == "Inasistencia escolar")
    ][["Año", "Valor"]].rename(columns={"Valor": "Inasistencia_Escolar"})
    rezago = bogota[
        (bogota["Indicador"] == "Privaciones") &
        (bogota["Categoría"] == "Rezago escolar")
    ][["Año", "Valor"]].rename(columns={"Valor": "Rezago_Escolar"})

    serie = ipm.merge(inasistencia, on="Año").merge(rezago, on="Año")

    print("\nSerie temporal IPM - Inasistencia - Rezago:")
    print(serie.to_string(index=False))

    # Correlaciones
    if len(serie) >= 3:
        r_inas, p_inas = stats.pearsonr(serie["IPM"], serie["Inasistencia_Escolar"])
        r_rez, p_rez = stats.pearsonr(serie["IPM"], serie["Rezago_Escolar"])
        print(f"\n  IPM vs Inasistencia escolar: r={r_inas:.3f} (p={p_inas:.4f})")
        print(f"  IPM vs Rezago escolar:       r={r_rez:.3f} (p={p_rez:.4f})")

    # Gráfico
    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(serie["IPM"], serie["Inasistencia_Escolar"],
                         s=150, c=serie["Año"], cmap="viridis",
                         edgecolors="black", linewidth=1, zorder=5)
    for _, row in serie.iterrows():
        ax.annotate(str(int(row["Año"])),
                    (row["IPM"], row["Inasistencia_Escolar"]),
                    fontsize=10, ha="left", va="bottom", fontweight="bold")
    if len(serie) >= 3:
        z = np.polyfit(serie["IPM"], serie["Inasistencia_Escolar"], 1)
        p_line = np.poly1d(z)
        x_r = np.linspace(serie["IPM"].min() - 0.5, serie["IPM"].max() + 0.5, 100)
        ax.plot(x_r, p_line(x_r), "--", color="red", linewidth=1.5, alpha=0.7)
        ax.set_title(f"IPM vs Inasistencia Escolar en Bogotá (r={r_inas:.3f})",
                     fontsize=13, fontweight="bold")
    else:
        ax.set_title("IPM vs Inasistencia Escolar en Bogotá",
                     fontsize=13, fontweight="bold")
    ax.set_xlabel("Índice de Pobreza Multidimensional (%)", fontsize=12)
    ax.set_ylabel("Inasistencia Escolar (%)", fontsize=12)
    ax.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Año")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "05_ipm_vs_inasistencia.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("\n✓ Gráfico guardado: 05_ipm_vs_inasistencia.png")


# =============================================================================
# 7. HEATMAP DE CORRELACIÓN: DESERCIÓN vs VARIABLES EDUCATIVAS
# =============================================================================

def heatmap_desercion(df_desercion):
    """
    Heatmap mostrando correlación entre deserción, reprobación y aprobación.
    """
    print("\n" + "=" * 70)
    print("ANÁLISIS 6: CORRELACIONES ENTRE INDICADORES EDUCATIVOS (UPL)")
    print("=" * 70)

    cols = ["Tasa_Desercion_Oficial", "Tasa_Desercion_NoOficial",
            "Tasa_Reprobacion_Oficial", "Tasa_Reprobacion_NoOficial",
            "Tasa_Aprobacion_Oficial", "Tasa_Aprobacion_NoOficial"]
    corr = df_desercion[cols].corr()

    print("\nMatriz de correlación:")
    print(corr.round(3).to_string())

    # Relación deserción - reprobación
    r, p = stats.pearsonr(df_desercion["Tasa_Desercion_Oficial"],
                          df_desercion["Tasa_Reprobacion_Oficial"])
    print(f"\n  Deserción vs Reprobación (oficial): r={r:.3f} (p={p:.4f})")
    if p < 0.05:
        print("  → Las UPL con mayor reprobación tienden a mayor deserción (significativo)")

    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    labels_cortos = ["Deser.Of", "Deser.NOf", "Reprob.Of", "Reprob.NOf", "Aprob.Of", "Aprob.NOf"]
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn_r",
                xticklabels=labels_cortos, yticklabels=labels_cortos,
                center=0, square=True, ax=ax, linewidths=0.5)
    ax.set_title("Correlación entre Indicadores Educativos por UPL",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "06_heatmap_indicadores_educativos.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("\n✓ Gráfico guardado: 06_heatmap_indicadores_educativos.png")


# =============================================================================
# 8. RESUMEN Y CONCLUSIONES
# =============================================================================

def generar_resumen(temporal, cruce, df_pobreza):
    """Genera un resumen textual del análisis."""
    print("\n" + "=" * 70)
    print("RESUMEN DEL ANÁLISIS")
    print("=" * 70)

    resumen = """
RESUMEN: RELACIÓN ENTRE POBREZA Y DESERCIÓN ESCOLAR EN BOGOTÁ D.C.
====================================================================

1. HALLAZGO TEMPORAL:
   - El IPM (Índice de Pobreza Multidimensional) en Bogotá pasó de 4.1% (2018)
     a un pico de 7.5% (2020, pandemia) y descendió hasta 2.2% (2025).
   - La inasistencia escolar mostró un pico dramático en 2020 (6.0%) durante
     la pandemia, coincidiendo con el aumento del IPM.
   - El rezago escolar se mantuvo alrededor del 20-23% en todo el período.

2. HALLAZGO TERRITORIAL:
   - Las localidades con mayor pobreza monetaria en 2021 son:
     Usme (57.81%), Ciudad Bolívar (57.37%), Bosa (53.18%).
   - Las UPL con mayor deserción oficial corresponden a zonas de:
     Ciudad Bolívar, Usme, Kennedy y Bosa.
   - Existe una asociación territorial: las zonas más pobres concentran
     mayor deserción escolar.

3. RELACIÓN DESERCIÓN - REPROBACIÓN:
   - Las UPL con mayor tasa de reprobación tienden a presentar también
     mayor deserción, lo que sugiere un mecanismo:
     Pobreza → Bajo rendimiento → Reprobación → Deserción

4. PRECAUCIÓN METODOLÓGICA:
   - Los datos de pobreza están a nivel de LOCALIDAD (20 divisiones).
   - Los datos de deserción están a nivel de UPL (33 divisiones).
   - La correspondencia UPL-Localidad es aproximada (no 1:1).
   - No se puede afirmar CAUSALIDAD, solo ASOCIACIÓN TERRITORIAL.
   - Se requieren datos a la misma granularidad para un análisis más robusto.

5. RECOMENDACIONES:
   - Buscar datos de pobreza a nivel UPL o de deserción a nivel localidad.
   - Incorporar variables intermedias: transporte, trabajo infantil, cupos.
   - Complementar con la Encuesta Multipropósito para variables micro.
"""
    print(resumen)

    # Guardar resumen
    with open(os.path.join(OUTPUT_DIR, "resumen_analisis.txt"), "w", encoding="utf-8") as f:
        f.write(resumen)
    print("✓ Resumen guardado: resumen_analisis.txt")


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  ANÁLISIS: POBREZA Y DESERCIÓN ESCOLAR EN BOGOTÁ D.C.         ║")
    print("║  DataJam Edición 4 - Universidad Distrital                     ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    # Cargar datos
    print("\n→ Cargando datos...")
    df_pobreza = cargar_pobreza()
    print(f"  Pobreza/Desigualdad: {len(df_pobreza)} registros")

    df_desercion = cargar_desercion()
    print(f"  Deserción por UPL: {len(df_desercion)} registros")

    df_vulnerabilidad = cargar_vulnerabilidad()
    print(f"  Vulnerabilidad hídrica: {len(df_vulnerabilidad)} localidades")

    # Ejecutar análisis
    temporal = analisis_temporal(df_pobreza)
    territorial = analisis_territorial(df_pobreza, df_vulnerabilidad)
    df_desercion, deser_por_loc = analisis_desercion_upl(df_desercion)
    cruce = analisis_cruce(territorial, deser_por_loc)
    analisis_ipm_inasistencia(df_pobreza)
    heatmap_desercion(df_desercion)
    generar_resumen(temporal, cruce, df_pobreza)

    print("\n" + "=" * 70)
    print(f"✓ ANÁLISIS COMPLETO. Resultados guardados en: {OUTPUT_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
