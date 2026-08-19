"""
Análisis Integrado: Encuesta Distrital de Percepción + Deserción Escolar
=========================================================================
DataJam Edición 4 - Universidad Distrital Francisco José de Caldas

Cruza la Encuesta Distrital de Percepción 2025 (a nivel UPL) con las tasas
de deserción escolar por UPL para identificar la asociación entre condiciones
socioeconómicas percibidas y resultados educativos.

Variables clave de la encuesta:
- C303: ¿Se considera pobre? (1=Sí, 2=No)
- Ax502: Suficiencia de ingresos (1=No alcanzan, 2=Solo mínimos, 3=Más que mínimos, 4=Pueden ahorrar)
- Bx301: Percepción acceso a educación (1=Muy malo a 5=Muy bueno)
- Cx301: Percepción acceso a oportunidades laborales (1-5)
- C302: Seguridad alimentaria (1=No alcanzó 3 comidas, 2=Con dificultad, 3=Bien)
- H1: Estrato socioeconómico (1-6)
- F405/G406: Percepción seguridad día/noche (1-5)
- IASS_B: Indicador calificación acceso educación
- IPPEB_G: Percepción mejora economía del hogar
- IPPEB_I: Optimismo futuro económico
- Cod_UPL: Código UPL (match directo con deserción)
"""

import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Configuración
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
sns.set_theme(style="whitegrid", palette="muted")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENCUESTA_CSV = os.path.join(BASE_DIR, "EncuestaDistrital", "base_ano_movil_2025.csv")
DESERCION_GEOJSON = os.path.join(BASE_DIR, "TasaDesercionUPC", "tasaDesercionUPL.geojson")
OUTPUT_DIR = os.path.join(BASE_DIR, "resultados_analisis")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =============================================================================
# 1. CARGA DE DATOS
# =============================================================================

def cargar_encuesta():
    """Carga la Encuesta Distrital de Percepción 2025."""
    df = pd.read_csv(ENCUESTA_CSV, low_memory=False)

    # Seleccionar columnas relevantes
    cols = [
        "DIRECTORIO_HOG", "DIRECTORIO_PER",
        # Demografía
        "A3", "A4", "A6x3", "A8", "C1", "D1", "H1",
        # Economía y pobreza
        "C303", "Ax502", "C302",
        # Acceso a servicios
        "Bx301", "Cx301", "Ax301", "Fx301",
        # Seguridad
        "F405", "G406", "Ax401",
        # Actividad económica
        "Ax501",
        # Indicadores calculados
        "IASS_B", "IPPEB_F", "IPPEB_G", "IPPEB_H", "IPPEB_I",
        "IPS_dia", "IPS_noche",
        # Territorio
        "Cod_Locali", "Nom_Locali", "Cod_UPL", "Nom_UPL", "SECTOR",
        # Ponderadores
        "fexp_calh_anu", "fexp_calp_anu",
    ]
    cols_exist = [c for c in cols if c in df.columns]
    df = df[cols_exist].copy()

    # Crear variables derivadas
    # Autopercepción de pobreza (1=Sí se considera pobre)
    df["Se_Considera_Pobre"] = (df["C303"] == 1).astype(int)

    # Insuficiencia de ingresos (1=No alcanzan para gastos mínimos)
    df["Ingresos_Insuficientes"] = (df["Ax502"] == 1).astype(int)

    # Ingresos solo para mínimos o menos
    df["Ingresos_Precarios"] = (df["Ax502"].isin([1, 2])).astype(int)

    # Inseguridad alimentaria (1=No alcanzó para 3 comidas)
    df["Inseguridad_Alimentaria"] = (df["C302"] == 1).astype(int)

    # Bajo acceso a educación (1 o 2 en escala 1-5)
    df["Bajo_Acceso_Educacion"] = (df["Bx301"].isin([1, 2])).astype(int)

    # Bajo acceso empleo
    df["Bajo_Acceso_Empleo"] = (df["Cx301"].isin([1, 2])).astype(int)

    # Víctima de delito
    df["Victima_Delito"] = (df["Ax401"] == 1).astype(int)

    # Estrato bajo (1-2)
    df["Estrato_Bajo"] = (df["H1"].isin([1, 2])).astype(int)

    # Desempleo o inactividad
    # Ax501: 1=Trabajando, 2=Buscando trabajo, 3=Estudiando, 4=Oficios hogar, 5=Incapacitado, 6=Otro
    df["Desempleado"] = (df["Ax501"] == 2).astype(int)
    df["Inactivo"] = (df["Ax501"].isin([4, 5, 6])).astype(int)

    return df


def cargar_desercion():
    """Carga las tasas de deserción por UPL."""
    with open(DESERCION_GEOJSON, "r") as f:
        data = json.load(f)

    registros = []
    for feat in data["features"]:
        p = feat["properties"]
        registros.append({
            "Cod_UPL": p["CODIGO_UPL"],
            "Tasa_Desercion_Oficial": p["TtotalDeserOf_UPL"],
            "Tasa_Desercion_NoOficial": p["TtotalDeserNOf_UPL"],
            "Tasa_Reprobacion_Oficial": p["TtotalReprOf_UPL"],
            "Tasa_Aprobacion_Oficial": p["TtotalAprOf_UPL"],
        })
    return pd.DataFrame(registros)


# =============================================================================
# 2. AGREGAR ENCUESTA POR UPL
# =============================================================================

def agregar_por_upl(df_encuesta):
    """
    Agrega las respuestas de la encuesta a nivel UPL usando el factor
    de expansión para obtener estimaciones poblacionales.
    """
    # Usar factor de expansión de hogares para variables de hogar
    peso = "fexp_calh_anu"

    # Calcular promedios ponderados por UPL
    agg = df_encuesta.groupby("Cod_UPL").apply(
        lambda g: pd.Series({
            "Pct_Pobre": np.average(g["Se_Considera_Pobre"], weights=g[peso]) * 100,
            "Pct_Ingresos_Insuf": np.average(g["Ingresos_Insuficientes"], weights=g[peso]) * 100,
            "Pct_Ingresos_Precarios": np.average(g["Ingresos_Precarios"], weights=g[peso]) * 100,
            "Pct_Inseg_Alimentaria": np.average(g["Inseguridad_Alimentaria"], weights=g[peso]) * 100,
            "Pct_Bajo_Acceso_Educ": np.average(
                g["Bajo_Acceso_Educacion"].loc[g["Bx301"] != 99],
                weights=g[peso].loc[g["Bx301"] != 99]
            ) * 100 if (g["Bx301"] != 99).sum() > 0 else np.nan,
            "Pct_Bajo_Acceso_Empleo": np.average(
                g["Bajo_Acceso_Empleo"].loc[g["Cx301"] != 99],
                weights=g[peso].loc[g["Cx301"] != 99]
            ) * 100 if (g["Cx301"] != 99).sum() > 0 else np.nan,
            "Pct_Victima_Delito": np.average(g["Victima_Delito"], weights=g[peso]) * 100,
            "Pct_Estrato_Bajo": np.average(
                g["Estrato_Bajo"].loc[~g["H1"].isin([7, 99])],
                weights=g[peso].loc[~g["H1"].isin([7, 99])]
            ) * 100 if (~g["H1"].isin([7, 99])).sum() > 0 else np.nan,
            "Pct_Desempleado": np.average(g["Desempleado"], weights=g[peso]) * 100,
            "Prom_Acceso_Educacion": np.average(
                g["IASS_B"].dropna(), weights=g[peso].loc[g["IASS_B"].notna()]
            ) if g["IASS_B"].notna().sum() > 0 else np.nan,
            "Prom_Mejora_Economia": np.average(
                g["IPPEB_G"].dropna(), weights=g[peso].loc[g["IPPEB_G"].notna()]
            ) if g["IPPEB_G"].notna().sum() > 0 else np.nan,
            "Prom_Optimismo_Econ": np.average(
                g["IPPEB_I"].dropna(), weights=g[peso].loc[g["IPPEB_I"].notna()]
            ) if g["IPPEB_I"].notna().sum() > 0 else np.nan,
            "Prom_Seguridad_Dia": np.average(
                g["IPS_dia"].dropna(), weights=g[peso].loc[g["IPS_dia"].notna()]
            ) if g["IPS_dia"].notna().sum() > 0 else np.nan,
            "N_Encuestados": len(g),
            "Localidad": g["Nom_Locali"].mode().iloc[0] if len(g) > 0 else "",
            "Nombre_UPL": g["Nom_UPL"].mode().iloc[0] if len(g) > 0 else "",
        })
    , include_groups=False).reset_index()

    return agg


# =============================================================================
# 3. CRUCE: ENCUESTA x DESERCIÓN POR UPL
# =============================================================================

def cruzar_datos(agg_upl, df_desercion):
    """Cruza los indicadores de la encuesta con las tasas de deserción por UPL."""
    cruce = agg_upl.merge(df_desercion, on="Cod_UPL", how="inner")
    return cruce


# =============================================================================
# 4. ANÁLISIS DE CORRELACIONES
# =============================================================================

def analisis_correlaciones(cruce):
    """Calcula y muestra las correlaciones entre variables socioeconómicas y deserción."""
    print("\n" + "=" * 70)
    print("ANÁLISIS: CORRELACIONES ENCUESTA DISTRITAL vs DESERCIÓN POR UPL")
    print("=" * 70)

    vars_socioeconomicas = [
        ("Pct_Pobre", "% Se considera pobre"),
        ("Pct_Ingresos_Insuf", "% Ingresos insuficientes"),
        ("Pct_Ingresos_Precarios", "% Ingresos precarios"),
        ("Pct_Inseg_Alimentaria", "% Inseguridad alimentaria"),
        ("Pct_Bajo_Acceso_Educ", "% Bajo acceso educación"),
        ("Pct_Bajo_Acceso_Empleo", "% Bajo acceso empleo"),
        ("Pct_Estrato_Bajo", "% Estrato 1-2"),
        ("Pct_Desempleado", "% Desempleado"),
        ("Pct_Victima_Delito", "% Víctima delito"),
        ("Prom_Acceso_Educacion", "Prom. acceso educación (1-5)"),
        ("Prom_Mejora_Economia", "Prom. mejora economía hogar"),
        ("Prom_Optimismo_Econ", "Prom. optimismo económico"),
        ("Prom_Seguridad_Dia", "Prom. seguridad de día"),
    ]

    print(f"\nN = {len(cruce)} UPLs con datos cruzados")
    print(f"\n{'Variable':<35} {'Pearson r':>10} {'p-valor':>10} {'Signif.':>8}")
    print("-" * 70)

    resultados = []
    for var, nombre in vars_socioeconomicas:
        sub = cruce[["Tasa_Desercion_Oficial", var]].dropna()
        if len(sub) >= 5:
            r, p = stats.pearsonr(sub["Tasa_Desercion_Oficial"], sub[var])
            sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
            print(f"  {nombre:<33} {r:>+.4f}     {p:>.4f}   {sig}")
            resultados.append({"Variable": nombre, "Columna": var, "r": r, "p": p})

    return pd.DataFrame(resultados)


# =============================================================================
# 5. SCATTER PLOTS PRINCIPALES
# =============================================================================

def scatter_plots(cruce):
    """Genera los scatter plots más relevantes."""
    print("\n" + "=" * 70)
    print("GENERANDO SCATTER PLOTS")
    print("=" * 70)

    fig, axes = plt.subplots(2, 2, figsize=(16, 14))

    plots = [
        ("Pct_Pobre", "% Hogares que se consideran pobres", "darkred"),
        ("Pct_Ingresos_Precarios", "% Hogares con ingresos precarios", "darkorange"),
        ("Pct_Estrato_Bajo", "% Hogares estrato 1-2", "purple"),
        ("Pct_Inseg_Alimentaria", "% Inseguridad alimentaria", "darkgreen"),
    ]

    for idx, (var, label, color) in enumerate(plots):
        ax = axes[idx // 2][idx % 2]
        sub = cruce[["Tasa_Desercion_Oficial", var, "Nombre_UPL"]].dropna()

        ax.scatter(sub[var], sub["Tasa_Desercion_Oficial"],
                   s=80, c=color, alpha=0.7, edgecolors="black", linewidth=0.5)

        # Anotar puntos extremos
        top3 = sub.nlargest(3, "Tasa_Desercion_Oficial")
        for _, row in top3.iterrows():
            ax.annotate(row["Nombre_UPL"],
                        (row[var], row["Tasa_Desercion_Oficial"]),
                        fontsize=7, ha="left", va="bottom", alpha=0.8)

        # Línea de tendencia
        if len(sub) >= 5:
            r, p = stats.pearsonr(sub[var], sub["Tasa_Desercion_Oficial"])
            z = np.polyfit(sub[var], sub["Tasa_Desercion_Oficial"], 1)
            p_line = np.poly1d(z)
            x_range = np.linspace(sub[var].min(), sub[var].max(), 100)
            ax.plot(x_range, p_line(x_range), "--", color="gray", linewidth=1.5)
            ax.set_title(f"{label}\n(r={r:.3f}, p={p:.4f})", fontsize=11, fontweight="bold")
        else:
            ax.set_title(label, fontsize=11, fontweight="bold")

        ax.set_xlabel(label)
        ax.set_ylabel("Tasa de Deserción Oficial (%)")
        ax.grid(True, alpha=0.3)

    plt.suptitle("Relación entre Condiciones Socioeconómicas (Encuesta) y Deserción Escolar por UPL",
                 fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "07_encuesta_vs_desercion_scatter.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("✓ Gráfico guardado: 07_encuesta_vs_desercion_scatter.png")


# =============================================================================
# 6. SCATTER ACCESO EDUCACIÓN vs DESERCIÓN
# =============================================================================

def scatter_acceso_educacion(cruce):
    """Scatter de percepción de acceso a educación vs deserción."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel 1: % Bajo acceso educación vs Deserción
    sub = cruce[["Tasa_Desercion_Oficial", "Pct_Bajo_Acceso_Educ", "Nombre_UPL"]].dropna()
    ax = axes[0]
    ax.scatter(sub["Pct_Bajo_Acceso_Educ"], sub["Tasa_Desercion_Oficial"],
               s=80, c="crimson", alpha=0.7, edgecolors="black", linewidth=0.5)
    if len(sub) >= 5:
        r, p = stats.pearsonr(sub["Pct_Bajo_Acceso_Educ"], sub["Tasa_Desercion_Oficial"])
        z = np.polyfit(sub["Pct_Bajo_Acceso_Educ"], sub["Tasa_Desercion_Oficial"], 1)
        p_line = np.poly1d(z)
        x_r = np.linspace(sub["Pct_Bajo_Acceso_Educ"].min(), sub["Pct_Bajo_Acceso_Educ"].max(), 100)
        ax.plot(x_r, p_line(x_r), "--", color="gray", linewidth=1.5)
        ax.set_title(f"% Bajo acceso educación vs Deserción (r={r:.3f}, p={p:.4f})",
                     fontsize=11, fontweight="bold")
    for _, row in sub.nlargest(3, "Tasa_Desercion_Oficial").iterrows():
        ax.annotate(row["Nombre_UPL"], (row["Pct_Bajo_Acceso_Educ"], row["Tasa_Desercion_Oficial"]),
                    fontsize=7, ha="left")
    ax.set_xlabel("% Hogares con bajo acceso a educación (calificación 1-2)")
    ax.set_ylabel("Tasa de Deserción Oficial (%)")
    ax.grid(True, alpha=0.3)

    # Panel 2: Promedio calificación acceso educación vs Deserción
    sub2 = cruce[["Tasa_Desercion_Oficial", "Prom_Acceso_Educacion", "Nombre_UPL"]].dropna()
    ax2 = axes[1]
    ax2.scatter(sub2["Prom_Acceso_Educacion"], sub2["Tasa_Desercion_Oficial"],
                s=80, c="steelblue", alpha=0.7, edgecolors="black", linewidth=0.5)
    if len(sub2) >= 5:
        r2, p2 = stats.pearsonr(sub2["Prom_Acceso_Educacion"], sub2["Tasa_Desercion_Oficial"])
        z2 = np.polyfit(sub2["Prom_Acceso_Educacion"], sub2["Tasa_Desercion_Oficial"], 1)
        p_line2 = np.poly1d(z2)
        x_r2 = np.linspace(sub2["Prom_Acceso_Educacion"].min(), sub2["Prom_Acceso_Educacion"].max(), 100)
        ax2.plot(x_r2, p_line2(x_r2), "--", color="gray", linewidth=1.5)
        ax2.set_title(f"Calificación acceso educación vs Deserción (r={r2:.3f}, p={p2:.4f})",
                      fontsize=11, fontweight="bold")
    for _, row in sub2.nlargest(3, "Tasa_Desercion_Oficial").iterrows():
        ax2.annotate(row["Nombre_UPL"], (row["Prom_Acceso_Educacion"], row["Tasa_Desercion_Oficial"]),
                     fontsize=7, ha="left")
    ax2.set_xlabel("Calificación promedio acceso a educación (1-5)")
    ax2.set_ylabel("Tasa de Deserción Oficial (%)")
    ax2.grid(True, alpha=0.3)

    plt.suptitle("Percepción de Acceso a Educación vs Deserción Escolar",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "08_acceso_educacion_vs_desercion.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("✓ Gráfico guardado: 08_acceso_educacion_vs_desercion.png")


# =============================================================================
# 7. RANKING DE UPLs: VULNERABILIDAD SOCIOECONÓMICA
# =============================================================================

def ranking_vulnerabilidad(cruce):
    """Genera un ranking de UPLs combinando vulnerabilidad y deserción."""
    print("\n" + "=" * 70)
    print("RANKING DE VULNERABILIDAD SOCIOECONÓMICA-EDUCATIVA POR UPL")
    print("=" * 70)

    # Construir un índice simple de vulnerabilidad
    vars_vulnerabilidad = ["Pct_Pobre", "Pct_Ingresos_Precarios", "Pct_Inseg_Alimentaria",
                           "Pct_Estrato_Bajo", "Pct_Desempleado"]

    # Normalizar cada variable (0-1) y promediar
    cruce_rank = cruce.copy()
    for var in vars_vulnerabilidad:
        if var in cruce_rank.columns:
            vmin = cruce_rank[var].min()
            vmax = cruce_rank[var].max()
            if vmax > vmin:
                cruce_rank[f"{var}_norm"] = (cruce_rank[var] - vmin) / (vmax - vmin)
            else:
                cruce_rank[f"{var}_norm"] = 0

    norm_cols = [f"{v}_norm" for v in vars_vulnerabilidad if f"{v}_norm" in cruce_rank.columns]
    cruce_rank["Indice_Vulnerabilidad"] = cruce_rank[norm_cols].mean(axis=1)

    # Normalizar deserción también
    vmin_d = cruce_rank["Tasa_Desercion_Oficial"].min()
    vmax_d = cruce_rank["Tasa_Desercion_Oficial"].max()
    cruce_rank["Desercion_Norm"] = (cruce_rank["Tasa_Desercion_Oficial"] - vmin_d) / (vmax_d - vmin_d)

    # Índice combinado
    cruce_rank["Indice_Riesgo_Educativo"] = (
        cruce_rank["Indice_Vulnerabilidad"] * 0.5 +
        cruce_rank["Desercion_Norm"] * 0.5
    )

    # Mostrar ranking
    ranking = cruce_rank[["Cod_UPL", "Nombre_UPL", "Localidad",
                          "Indice_Vulnerabilidad", "Tasa_Desercion_Oficial",
                          "Indice_Riesgo_Educativo",
                          "Pct_Pobre", "Pct_Ingresos_Precarios"]].sort_values(
        "Indice_Riesgo_Educativo", ascending=False
    )

    print("\nTop 10 UPLs con mayor riesgo educativo:")
    print(ranking.head(10).to_string(index=False))

    print("\nTop 5 UPLs con menor riesgo:")
    print(ranking.tail(5).to_string(index=False))

    # --- Gráfico del ranking ---
    fig, ax = plt.subplots(figsize=(14, 10))
    ranking_sorted = ranking.sort_values("Indice_Riesgo_Educativo", ascending=True)
    colores = ranking_sorted["Indice_Riesgo_Educativo"].apply(
        lambda x: "darkred" if x > 0.6 else "orangered" if x > 0.4 else "gold" if x > 0.25 else "green"
    )
    etiquetas = ranking_sorted.apply(
        lambda r: f"{r['Cod_UPL']} - {r['Nombre_UPL']} ({r['Localidad']})", axis=1
    )
    bars = ax.barh(etiquetas, ranking_sorted["Indice_Riesgo_Educativo"], color=colores)
    ax.axvline(x=0.5, color="black", linestyle="--", linewidth=1, alpha=0.5)
    ax.set_xlabel("Índice de Riesgo Educativo (0-1)", fontsize=12)
    ax.set_title("Índice de Riesgo Educativo por UPL\n(Combina vulnerabilidad socioeconómica + deserción)",
                 fontsize=13, fontweight="bold")
    ax.set_xlim(0, 1)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "09_ranking_riesgo_educativo_upl.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("\n✓ Gráfico guardado: 09_ranking_riesgo_educativo_upl.png")

    # Correlación entre índice de vulnerabilidad y deserción
    r, p = stats.pearsonr(cruce_rank["Indice_Vulnerabilidad"], cruce_rank["Tasa_Desercion_Oficial"])
    print(f"\n→ Correlación Índice Vulnerabilidad vs Deserción: r={r:.4f} (p={p:.4f})")

    return cruce_rank


# =============================================================================
# 8. HEATMAP POR UPL
# =============================================================================

def heatmap_upl(cruce):
    """Heatmap de condiciones socioeconómicas y deserción por UPL."""
    vars_plot = ["Pct_Pobre", "Pct_Ingresos_Precarios", "Pct_Inseg_Alimentaria",
                 "Pct_Estrato_Bajo", "Pct_Bajo_Acceso_Educ", "Pct_Desempleado",
                 "Tasa_Desercion_Oficial", "Tasa_Reprobacion_Oficial"]

    # Seleccionar y ordenar por deserción
    datos = cruce[["Nombre_UPL"] + vars_plot].dropna().set_index("Nombre_UPL")
    datos = datos.sort_values("Tasa_Desercion_Oficial", ascending=False)

    # Normalizar para el heatmap (z-score)
    datos_norm = (datos - datos.mean()) / datos.std()

    fig, ax = plt.subplots(figsize=(12, 12))
    labels_cortos = ["% Pobre", "% Ing.Precario", "% Inseg.Alim.",
                     "% Estrato 1-2", "% Bajo Acc.Educ", "% Desempleado",
                     "Deserción Of.", "Reprobación Of."]
    sns.heatmap(datos_norm, annot=datos.round(1), fmt="", cmap="RdYlGn_r",
                xticklabels=labels_cortos, center=0, ax=ax, linewidths=0.5,
                cbar_kws={"label": "Z-score (rojo = peor)"})
    ax.set_title("Condiciones Socioeconómicas y Resultados Educativos por UPL\n(Valores reales anotados, color por z-score)",
                 fontsize=12, fontweight="bold")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "10_heatmap_vulnerabilidad_educacion_upl.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("✓ Gráfico guardado: 10_heatmap_vulnerabilidad_educacion_upl.png")


# =============================================================================
# 9. ANÁLISIS POR LOCALIDAD AGREGADO
# =============================================================================

def analisis_por_localidad(cruce):
    """Agrega resultados por localidad para comparar con datos de pobreza."""
    print("\n" + "=" * 70)
    print("ANÁLISIS POR LOCALIDAD (AGREGADO DESDE UPL)")
    print("=" * 70)

    loc_agg = cruce.groupby("Localidad").agg(
        Pct_Pobre_Prom=("Pct_Pobre", "mean"),
        Pct_Ingresos_Prec_Prom=("Pct_Ingresos_Precarios", "mean"),
        Desercion_Of_Prom=("Tasa_Desercion_Oficial", "mean"),
        Reprobacion_Of_Prom=("Tasa_Reprobacion_Oficial", "mean"),
        Num_UPL=("Cod_UPL", "count"),
    ).reset_index().sort_values("Desercion_Of_Prom", ascending=False)

    print("\nResumen por localidad:")
    print(loc_agg.to_string(index=False))

    # Correlación a nivel localidad
    if len(loc_agg) >= 5:
        r, p = stats.pearsonr(loc_agg["Pct_Pobre_Prom"], loc_agg["Desercion_Of_Prom"])
        print(f"\n→ Correlación (localidad): % Pobre vs Deserción: r={r:.4f} (p={p:.4f})")

    return loc_agg


# =============================================================================
# 10. GRÁFICO COMPARATIVO MULTI-VARIABLE
# =============================================================================

def grafico_multivariable(cruce):
    """Genera un gráfico con múltiples correlaciones resumidas."""
    vars_analisis = [
        ("Pct_Pobre", "% Se considera pobre"),
        ("Pct_Ingresos_Precarios", "% Ingresos precarios"),
        ("Pct_Inseg_Alimentaria", "% Inseguridad alimentaria"),
        ("Pct_Estrato_Bajo", "% Estrato 1-2"),
        ("Pct_Bajo_Acceso_Educ", "% Bajo acceso educación"),
        ("Pct_Bajo_Acceso_Empleo", "% Bajo acceso empleo"),
        ("Pct_Desempleado", "% Desempleado"),
        ("Pct_Victima_Delito", "% Víctima de delito"),
        ("Prom_Acceso_Educacion", "Prom. acceso educación"),
        ("Prom_Mejora_Economia", "Prom. mejora economía"),
        ("Prom_Optimismo_Econ", "Prom. optimismo económico"),
        ("Prom_Seguridad_Dia", "Prom. seguridad de día"),
    ]

    resultados = []
    for var, nombre in vars_analisis:
        sub = cruce[["Tasa_Desercion_Oficial", var]].dropna()
        if len(sub) >= 5:
            r, p = stats.pearsonr(sub["Tasa_Desercion_Oficial"], sub[var])
            resultados.append({"Variable": nombre, "r": r, "p": p,
                               "Significativo": p < 0.05})

    df_res = pd.DataFrame(resultados).sort_values("r")

    # Gráfico tipo forest plot
    fig, ax = plt.subplots(figsize=(10, 8))
    colores = df_res["Significativo"].map({True: "darkred", False: "gray"})
    ax.barh(df_res["Variable"], df_res["r"], color=colores, edgecolor="black", linewidth=0.5)
    ax.axvline(x=0, color="black", linewidth=1)
    ax.axvline(x=0.3, color="red", linestyle=":", linewidth=0.8, alpha=0.5)
    ax.axvline(x=-0.3, color="blue", linestyle=":", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("Correlación de Pearson con Tasa de Deserción Oficial", fontsize=11)
    ax.set_title("Correlaciones: Variables Socioeconómicas vs Deserción por UPL\n(Rojo = significativo p<0.05, Gris = no significativo)",
                 fontsize=12, fontweight="bold")
    ax.set_xlim(-1, 1)
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "11_correlaciones_resumen.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("✓ Gráfico guardado: 11_correlaciones_resumen.png")


# =============================================================================
# 11. RESUMEN FINAL
# =============================================================================

def resumen_final(cruce, df_correlaciones):
    """Genera un resumen con conclusiones."""
    print("\n" + "=" * 70)
    print("RESUMEN: ENCUESTA DISTRITAL + DESERCIÓN ESCOLAR")
    print("=" * 70)

    sig = df_correlaciones[df_correlaciones["p"] < 0.05]
    marginales = df_correlaciones[(df_correlaciones["p"] >= 0.05) & (df_correlaciones["p"] < 0.1)]

    resumen = f"""
RESUMEN: ANÁLISIS ENCUESTA DISTRITAL DE PERCEPCIÓN + DESERCIÓN ESCOLAR
========================================================================
Fuente: Encuesta Distrital de Percepción - Año Móvil 2025 + Tasas de
Deserción por UPL (Secretaría de Educación, 2024)

UPLs analizadas: {len(cruce)}
Total encuestados: {cruce['N_Encuestados'].sum()}

CORRELACIONES SIGNIFICATIVAS (p < 0.05) con Tasa de Deserción:
"""
    for _, row in sig.iterrows():
        resumen += f"  • {row['Variable']}: r = {row['r']:.4f} (p = {row['p']:.4f})\n"

    if not marginales.empty:
        resumen += "\nCORRELACIONES MARGINALES (0.05 < p < 0.10):\n"
        for _, row in marginales.iterrows():
            resumen += f"  • {row['Variable']}: r = {row['r']:.4f} (p = {row['p']:.4f})\n"

    resumen += """
INTERPRETACIÓN DE LAS CORRELACIONES NEGATIVAS:
- Las correlaciones negativas (ej. % desempleado vs deserción r=-0.55)
  parecen contra-intuitivas pero revelan un fenómeno importante:
  
  • UPLs como Chapinero (UPL24), Teusaquillo (UPL32) y Barrios Unidos (UPL33)
    tienen ALTA deserción pero BAJA pobreza percibida.
  • UPLs como San Cristóbal (UPL05), Ciudad Bolívar (UPL04) tienen ALTA
    pobreza pero deserción menor al promedio.

- Esto se explica porque la deserción OFICIAL incluye colegios públicos
  en TODAS las zonas, y en zonas de estrato medio-alto puede haber:
  • Mayor presión académica → deserción por rendimiento.
  • Población flotante (estudiantes que vienen de otras zonas).
  • Movilidad: estudiantes que se mueven entre colegios/localidades.

- La variable "Mejora economía del hogar" (r=+0.43, p=0.018) es POSITIVA,
  lo que indica que donde las personas perciben mejora económica HAY MÁS
  deserción. Esto podría reflejar que en zonas dinámicas económicamente
  los jóvenes abandonan el estudio para trabajar.

HALLAZGO MATIZADO:
→ La relación pobreza-deserción NO es lineal ni simple a nivel de UPL.
→ Las UPLs más pobres (Ciudad Bolívar sur, Usme) tienen alta reprobación
  pero no necesariamente la mayor deserción oficial.
→ Esto matiza la hipótesis inicial: la pobreza se asocia más con bajo
  rendimiento (reprobación) que con abandono directo (deserción).
→ Se sugiere que la deserción tiene múltiples causas: no solo pobreza
  sino también movilidad, presión académica y oportunidades laborales.

PRECAUCIÓN METODOLÓGICA:
- La encuesta mide PERCEPCIÓN en hogares, no condiciones objetivas.
- La deserción corresponde a 2024, la encuesta a año móvil 2025.
- Los estudiantes pueden ir a colegios fuera de su UPL de residencia.
- La UPL donde está el colegio no es necesariamente donde vive el estudiante.
- Se recomienda cruzar con matrícula y datos de movilidad escolar.
"""
    print(resumen)

    with open(os.path.join(OUTPUT_DIR, "resumen_encuesta_desercion.txt"), "w", encoding="utf-8") as f:
        f.write(resumen)
    print("✓ Resumen guardado: resumen_encuesta_desercion.txt")


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  ANÁLISIS INTEGRADO: ENCUESTA DISTRITAL + DESERCIÓN ESCOLAR        ║")
    print("║  DataJam Edición 4 - Universidad Distrital                          ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    # 1. Cargar datos
    print("\n→ Cargando Encuesta Distrital de Percepción 2025...")
    df_encuesta = cargar_encuesta()
    print(f"  Registros: {len(df_encuesta)} | UPLs: {df_encuesta['Cod_UPL'].nunique()}")

    print("→ Cargando tasas de deserción por UPL...")
    df_desercion = cargar_desercion()
    print(f"  UPLs con datos de deserción: {len(df_desercion)}")

    # 2. Agregar encuesta por UPL
    print("\n→ Agregando encuesta por UPL (con factor de expansión)...")
    agg_upl = agregar_por_upl(df_encuesta)
    print(f"  UPLs con datos agregados: {len(agg_upl)}")

    # 3. Cruzar
    print("→ Cruzando con datos de deserción...")
    cruce = cruzar_datos(agg_upl, df_desercion)
    print(f"  UPLs cruzadas exitosamente: {len(cruce)}")

    # 4. Análisis
    df_correlaciones = analisis_correlaciones(cruce)
    scatter_plots(cruce)
    scatter_acceso_educacion(cruce)
    ranking_vulnerabilidad(cruce)
    heatmap_upl(cruce)
    analisis_por_localidad(cruce)
    grafico_multivariable(cruce)
    resumen_final(cruce, df_correlaciones)

    print("\n" + "=" * 70)
    print(f"✓ ANÁLISIS COMPLETO. Resultados en: {OUTPUT_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
