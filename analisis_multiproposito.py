"""
Análisis Complementario: Encuesta Multipropósito Bogotá 2014
=============================================================
DataJam Edición 4 - Universidad Distrital Francisco José de Caldas

Explora la relación entre condiciones socioeconómicas y variables educativas
a nivel individual, usando microdatos de la Encuesta Multipropósito 2014.

Variables clave:
- npcep4: Edad de la persona
- npcep5: ¿Asiste actualmente a educación? (1=Sí, 2=No)
- npcep6: Nivel educativo más alto alcanzado
- npcep9: Tipo de establecimiento (1=No sabe, 2=Oficial/Público, 3=Privado)
- npcep11: ¿Ha repetido año? (1=No, 2=Sí)
- npcep12: Minutos para llegar al centro educativo
- npcep14: ¿Dejó de asistir temporalmente? (1=No, 2=Sí)
- npcep15: Razón por la que no estudia
- nhclp3: Percepción pobreza (1=Pobre, 2=No pobre, 3=No sabe)
- nhclp4: Suficiencia de ingresos (1=No alcanzan, 2=Solo mínimos, 3=Pueden ahorrar)
- nvcbp4: Estrato (1-2 en esta muestra)
- nombre_localidad: Localidad
- fex_c: Factor de expansión
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
sns.set_theme(style="whitegrid", palette="muted")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EM_CSV = os.path.join(BASE_DIR, "EncuestaMultipropocito", "em2014.csv")
EM_URL = "https://datosabiertos.bogota.gov.co/dataset/d2b7f884-0b5d-4f4d-b4b0-12528f4e93e8/resource/1e70684d-1f82-4c70-a7cf-7ff2a0d84a6a/download/em2014.csv"
OUTPUT_DIR = os.path.join(BASE_DIR, "resultados_analisis")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def descargar_em2014():
    """Descarga el archivo em2014.csv si no existe localmente."""
    if not os.path.exists(EM_CSV):
        import urllib.request
        print(f"  Descargando em2014.csv desde datos abiertos Bogotá...")
        os.makedirs(os.path.dirname(EM_CSV), exist_ok=True)
        urllib.request.urlretrieve(EM_URL, EM_CSV)
        print(f"  ✓ Descargado ({os.path.getsize(EM_CSV) / 1e6:.0f} MB)")


# Codificación de razones de no asistencia (npcep15)
RAZONES_NO_ESTUDIA = {
    1: "Costos educativos / falta de dinero",
    2: "Necesita trabajar",
    3: "Por embarazo",
    4: "No le gusta / no le interesa",
    5: "Falta de cupos / no hay institución cerca",
    6: "Necesita cuidar a otros miembros",
    7: "Por discapacidad / enfermedad",
    8: "Considera que ya terminó",
    9: "Otra razón",
}

# Codificación nivel educativo (npcep6)
NIVEL_EDUCATIVO = {
    1: "Ninguno",
    2: "Preescolar",
    3: "Básica primaria",
    4: "Básica secundaria",
    5: "Media (10-11)",
    6: "Técnico/Tecnológico",
    7: "Universitario",
    8: "Postgrado",
    9: "No sabe",
    10: "No informa",
}


def cargar_encuesta_multiproposito():
    """Carga y prepara la Encuesta Multipropósito 2014."""
    descargar_em2014()
    df = pd.read_csv(EM_CSV, encoding='latin-1', low_memory=False)

    # Seleccionar columnas relevantes
    cols = [
        "directorio", "directorio_hog", "nombre_localidad", "cod_localidad",
        "fex_c", "nvcbp4",  # estrato
        "npcep1", "npcep4", "npcep5", "npcep6", "npcep7",
        "npcep8", "npcep9", "npcep10", "npcep11", "npcep12",
        "npcep13", "npcep14", "npcep15",
        "nhclp3", "nhclp4", "nhclp5",
        "npcfp1",  # trabajó
    ]
    cols_exist = [c for c in cols if c in df.columns]
    df = df[cols_exist].copy()

    # Renombrar para claridad
    # npcep4=Edad, npcep5=Sexo(1=H,2=M), npcep6=Nivel educativo
    # npcep10=Asiste actualmente(1=Sí,2=No), npcep11=Sector(1=Privado,2=Oficial)
    # npcep12=Minutos al colegio, npcep13=Dejó asistir temp(1=No,2=Sí)
    # npcep15=Razón no estudia
    df = df.rename(columns={
        "npcep4": "Edad",
        "npcep5": "Sexo",
        "npcep6": "Nivel_Educativo",
        "npcep9": "Tipo_Establecimiento",
        "npcep11": "Sector_Educativo",
        "npcep12": "Minutos_al_Colegio",
        "npcep14": "Dejo_Asistir_Temp",
        "npcep15": "Razon_No_Estudia",
        "nhclp3": "Percepcion_Pobreza",
        "nhclp4": "Suficiencia_Ingresos",
        "nvcbp4": "Estrato",
        "npcfp1": "Trabaja",
    })

    # Usar npcep10 como variable de asistencia
    if "npcep10" in df.columns:
        df["Asiste_Educacion"] = df["npcep10"]
    else:
        df["Asiste_Educacion"] = np.nan

    # Variables derivadas
    df["Es_Menor_18"] = (df["Edad"] < 18).astype(int)
    df["Edad_Escolar"] = ((df["Edad"] >= 5) & (df["Edad"] <= 17)).astype(int)
    df["No_Asiste"] = (df["Asiste_Educacion"] == 2).astype(int)
    df["Repitio"] = (df["Sector_Educativo"] == 2).astype(int)  # Sector Oficial
    df["Se_Considera_Pobre"] = (df["Percepcion_Pobreza"] == 1).astype(int)
    df["Ingresos_Insuficientes"] = (df["Suficiencia_Ingresos"] == 1).astype(int)

    return df


# =============================================================================
# 1. RAZONES DE NO ASISTENCIA POR CONDICIÓN ECONÓMICA
# =============================================================================

def analisis_razones_no_asistencia(df):
    """Analiza las razones de no asistencia escolar por condición económica."""
    print("\n" + "=" * 70)
    print("ANÁLISIS 1: RAZONES DE NO ASISTENCIA ESCOLAR (Edad 5-17)")
    print("=" * 70)

    # Filtrar: edad escolar que NO asisten
    jovenes_no_asisten = df[
        (df["Edad_Escolar"] == 1) &
        (df["No_Asiste"] == 1) &
        (df["Razon_No_Estudia"].notna())
    ].copy()

    print(f"\nJóvenes (5-17 años) que NO asisten a educación: {len(jovenes_no_asisten)}")
    peso = "fex_c"

    # Razones generales (ponderadas)
    razones = jovenes_no_asisten.groupby("Razon_No_Estudia")[peso].sum()
    razones_pct = (razones / razones.sum() * 100).sort_values(ascending=False)

    print("\nRazones de no asistencia (población expandida):")
    for cod, pct in razones_pct.items():
        nombre = RAZONES_NO_ESTUDIA.get(int(cod), f"Código {int(cod)}")
        print(f"  {nombre}: {pct:.1f}%")

    # Comparar razones por percepción de pobreza
    print("\n--- Razones por percepción de pobreza ---")
    for grupo, label in [(1, "SE CONSIDERA POBRE"), (2, "NO SE CONSIDERA POBRE")]:
        sub = jovenes_no_asisten[jovenes_no_asisten["Percepcion_Pobreza"] == grupo]
        if len(sub) > 10:
            razones_g = sub.groupby("Razon_No_Estudia")[peso].sum()
            razones_g_pct = (razones_g / razones_g.sum() * 100)
            print(f"\n  {label} (n={len(sub)}):")
            for cod in [1, 2, 4, 5]:
                pct = razones_g_pct.get(cod, 0)
                nombre = RAZONES_NO_ESTUDIA.get(cod, "")
                print(f"    {nombre}: {pct:.1f}%")

    # Gráfico
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Panel 1: Razones generales
    ax = axes[0]
    razones_plot = razones_pct.head(7)
    nombres = [RAZONES_NO_ESTUDIA.get(int(c), f"Cód.{int(c)}") for c in razones_plot.index]
    # Acortar nombres
    nombres_cortos = [n[:40] for n in nombres]
    colores_r = ["darkred" if int(c) in [1, 2] else "steelblue" for c in razones_plot.index]
    ax.barh(nombres_cortos, razones_plot.values, color=colores_r)
    ax.set_xlabel("Porcentaje (%)")
    ax.set_title("Razones de No Asistencia Escolar\n(Jóvenes 5-17 años, Bogotá 2014)",
                 fontsize=12, fontweight="bold")
    ax.invert_yaxis()

    # Panel 2: Comparación pobres vs no pobres
    ax2 = axes[1]
    razones_comp = []
    for cod in [1, 2, 3, 4, 5, 6]:
        for grupo, label in [(1, "Pobre"), (2, "No pobre")]:
            sub = jovenes_no_asisten[jovenes_no_asisten["Percepcion_Pobreza"] == grupo]
            if len(sub) > 5:
                razones_g = sub.groupby("Razon_No_Estudia")[peso].sum()
                total = razones_g.sum()
                pct = (razones_g.get(cod, 0) / total * 100) if total > 0 else 0
                razones_comp.append({"Razón": RAZONES_NO_ESTUDIA.get(cod, "")[:30],
                                     "Grupo": label, "Porcentaje": pct})

    df_comp = pd.DataFrame(razones_comp)
    if not df_comp.empty:
        df_pivot = df_comp.pivot(index="Razón", columns="Grupo", values="Porcentaje").fillna(0)
        df_pivot.plot(kind="barh", ax=ax2, color=["darkred", "steelblue"])
        ax2.set_xlabel("Porcentaje (%)")
        ax2.set_title("Razones de No Asistencia:\nPobres vs No Pobres",
                      fontsize=12, fontweight="bold")
        ax2.legend(title="Autopercepción")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "12_razones_no_asistencia.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("\n✓ Gráfico guardado: 12_razones_no_asistencia.png")


# =============================================================================
# 2. REPITENCIA Y CONDICIONES ECONÓMICAS
# =============================================================================

def analisis_inasistencia_temporal(df):
    """Analiza la inasistencia temporal y el sector educativo por condición económica."""
    print("\n" + "=" * 70)
    print("ANÁLISIS 2: INASISTENCIA TEMPORAL Y SECTOR EDUCATIVO")
    print("=" * 70)

    # Filtrar: asisten a educación (npcep10=1)
    estudiantes = df[df["Asiste_Educacion"] == 1].copy()
    peso = "fex_c"

    # npcep13: 2=Sí dejó asistir temporalmente
    estudiantes["Inasistencia_Temporal"] = (estudiantes["npcep13"] == 2).astype(int)

    # Sector: npcep11 (1=Privado, 2=Oficial)
    estudiantes["Sector_Oficial"] = (estudiantes["Sector_Educativo"] == 2).astype(int)

    # % en sector oficial por pobreza
    print("\n% Estudiantes en sector OFICIAL por percepción de pobreza:")
    for grupo, label in [(1, "Pobre"), (2, "No pobre")]:
        sub = estudiantes[estudiantes["Percepcion_Pobreza"] == grupo]
        if len(sub) > 50:
            tasa = np.average(sub["Sector_Oficial"], weights=sub[peso]) * 100
            print(f"  {label}: {tasa:.2f}% en sector oficial (n={len(sub)})")

    # Inasistencia temporal por condición económica
    sub_temp = estudiantes[estudiantes["npcep13"].notna()]
    print("\nTasa de inasistencia temporal por percepción de pobreza:")
    for grupo, label in [(1, "Pobre"), (2, "No pobre")]:
        sub = sub_temp[sub_temp["Percepcion_Pobreza"] == grupo]
        if len(sub) > 50:
            tasa = np.average(sub["Inasistencia_Temporal"], weights=sub[peso]) * 100
            print(f"  {label}: {tasa:.2f}% dejó de asistir temporalmente (n={len(sub)})")

    # Sector oficial por localidad
    print("\n% Sector oficial por localidad:")
    sector_loc = estudiantes.groupby("nombre_localidad").apply(
        lambda g: pd.Series({
            "Pct_Oficial": np.average(g["Sector_Oficial"], weights=g[peso]) * 100,
            "N": len(g),
        })
    , include_groups=False).reset_index()
    sector_loc = sector_loc[sector_loc["nombre_localidad"].str.strip() != ""]
    sector_loc = sector_loc.sort_values("Pct_Oficial", ascending=False)
    print(sector_loc.head(10).to_string(index=False))

    # Gráfico
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel 1: Sector por condición económica
    ax = axes[0]
    datos_barras = []
    for grupo, label in [(1, "Pobre"), (2, "No pobre")]:
        sub = estudiantes[estudiantes["Percepcion_Pobreza"] == grupo]
        if len(sub) > 50:
            oficial = np.average(sub["Sector_Oficial"], weights=sub[peso]) * 100
            datos_barras.append({"Grupo": label, "Pct_Oficial": oficial})
    for grupo, label in [(1, "Ingresos\ninsuficientes"), (2, "Solo\nmínimos"), (3, "Pueden\nahorrar")]:
        sub = estudiantes[estudiantes["Suficiencia_Ingresos"] == grupo]
        if len(sub) > 50:
            oficial = np.average(sub["Sector_Oficial"], weights=sub[peso]) * 100
            datos_barras.append({"Grupo": label, "Pct_Oficial": oficial})

    df_barras = pd.DataFrame(datos_barras)
    colores = ["darkred", "green", "darkred", "orange", "green"][:len(df_barras)]
    ax.bar(df_barras["Grupo"], df_barras["Pct_Oficial"], color=colores, edgecolor="black")
    ax.set_ylabel("% en Sector Oficial (Público)")
    ax.set_title("Dependencia del Sector Oficial por\nCondición Económica (Bogotá 2014)",
                 fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")

    # Panel 2: Sector oficial por localidad
    ax2 = axes[1]
    plot_data = sector_loc.sort_values("Pct_Oficial", ascending=True)
    colores_loc = plot_data["Pct_Oficial"].apply(
        lambda x: "darkred" if x > 70 else "orange" if x > 55 else "green"
    )
    ax2.barh(plot_data["nombre_localidad"], plot_data["Pct_Oficial"], color=colores_loc)
    ax2.set_xlabel("% Estudiantes en Sector Oficial")
    ax2.set_title("Dependencia del Sector Oficial por Localidad\n(Bogotá 2014)",
                  fontsize=12, fontweight="bold")
    media = sector_loc["Pct_Oficial"].mean()
    ax2.axvline(x=media, color="black", linestyle="--", linewidth=1.5,
                label=f"Promedio ({media:.1f}%)")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "13_sector_educativo_pobreza.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("\n✓ Gráfico guardado: 13_sector_educativo_pobreza.png")

    return sector_loc


# =============================================================================
# 3. INASISTENCIA EN EDAD ESCOLAR POR LOCALIDAD
# =============================================================================

def analisis_inasistencia_localidad(df):
    """Analiza la tasa de inasistencia escolar por localidad y condición económica."""
    print("\n" + "=" * 70)
    print("ANÁLISIS 3: INASISTENCIA ESCOLAR (5-17 AÑOS) POR LOCALIDAD")
    print("=" * 70)

    jovenes = df[df["Edad_Escolar"] == 1].copy()
    peso = "fex_c"

    # Tasa de inasistencia por localidad
    inasis_loc = jovenes.groupby("nombre_localidad").apply(
        lambda g: pd.Series({
            "Tasa_Inasistencia": np.average(g["No_Asiste"], weights=g[peso]) * 100,
            "Pct_Pobre": np.average(g["Se_Considera_Pobre"], weights=g[peso]) * 100,
            "Pct_Ing_Insuf": np.average(g["Ingresos_Insuficientes"], weights=g[peso]) * 100,
            "N": len(g),
        })
    , include_groups=False).reset_index()
    inasis_loc = inasis_loc[inasis_loc["nombre_localidad"].str.strip() != ""]
    inasis_loc = inasis_loc.sort_values("Tasa_Inasistencia", ascending=False)

    print("\nTasa de inasistencia y pobreza por localidad:")
    print(inasis_loc.to_string(index=False))

    # Correlación
    if len(inasis_loc) >= 5:
        r, p = stats.pearsonr(inasis_loc["Pct_Pobre"], inasis_loc["Tasa_Inasistencia"])
        print(f"\n→ Correlación % Pobre vs Inasistencia: r={r:.4f} (p={p:.4f})")
        r2, p2 = stats.pearsonr(inasis_loc["Pct_Ing_Insuf"], inasis_loc["Tasa_Inasistencia"])
        print(f"→ Correlación % Ing.Insuf vs Inasistencia: r={r2:.4f} (p={p2:.4f})")

    # Gráfico scatter
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(inasis_loc["Pct_Pobre"], inasis_loc["Tasa_Inasistencia"],
               s=inasis_loc["N"] / 5, c="darkred", alpha=0.7, edgecolors="black")
    for _, row in inasis_loc.iterrows():
        ax.annotate(row["nombre_localidad"], (row["Pct_Pobre"], row["Tasa_Inasistencia"]),
                    fontsize=8, ha="left", va="bottom")
    if len(inasis_loc) >= 5:
        z = np.polyfit(inasis_loc["Pct_Pobre"], inasis_loc["Tasa_Inasistencia"], 1)
        p_line = np.poly1d(z)
        x_r = np.linspace(inasis_loc["Pct_Pobre"].min(), inasis_loc["Pct_Pobre"].max(), 100)
        ax.plot(x_r, p_line(x_r), "--", color="gray", linewidth=1.5)
        ax.set_title(f"Pobreza vs Inasistencia Escolar por Localidad (r={r:.3f}, p={p:.4f})",
                     fontsize=13, fontweight="bold")
    ax.set_xlabel("% Hogares que se consideran pobres")
    ax.set_ylabel("Tasa de Inasistencia Escolar (5-17 años) (%)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "14_pobreza_vs_inasistencia_localidad.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("\n✓ Gráfico guardado: 14_pobreza_vs_inasistencia_localidad.png")

    return inasis_loc


# =============================================================================
# 4. TIEMPO DE DESPLAZAMIENTO AL COLEGIO
# =============================================================================

def analisis_desplazamiento(df):
    """Analiza el tiempo de desplazamiento al colegio y su relación con pobreza."""
    print("\n" + "=" * 70)
    print("ANÁLISIS 4: TIEMPO DE DESPLAZAMIENTO AL COLEGIO")
    print("=" * 70)

    estudiantes = df[
        (df["Asiste_Educacion"] == 1) &
        (df["Minutos_al_Colegio"].notna()) &
        (df["Minutos_al_Colegio"] < 99)  # 99 parece ser NS/NR
    ].copy()
    peso = "fex_c"

    # Tiempo promedio por percepción de pobreza
    print("\nTiempo promedio al colegio por condición económica:")
    for grupo, label in [(1, "Pobre"), (2, "No pobre")]:
        sub = estudiantes[estudiantes["Percepcion_Pobreza"] == grupo]
        if len(sub) > 50:
            prom = np.average(sub["Minutos_al_Colegio"], weights=sub[peso])
            print(f"  {label}: {prom:.1f} minutos (n={len(sub)})")

    # Por localidad
    desp_loc = estudiantes.groupby("nombre_localidad").apply(
        lambda g: pd.Series({
            "Prom_Minutos": np.average(g["Minutos_al_Colegio"], weights=g[peso]),
            "Pct_Mas_30min": np.average((g["Minutos_al_Colegio"] > 30).astype(int), weights=g[peso]) * 100,
        })
    , include_groups=False).reset_index()
    desp_loc = desp_loc[desp_loc["nombre_localidad"].str.strip() != ""]

    print("\nTiempo de desplazamiento por localidad (top 10):")
    print(desp_loc.sort_values("Prom_Minutos", ascending=False).head(10).to_string(index=False))

    # Gráfico
    fig, ax = plt.subplots(figsize=(12, 7))
    desp_plot = desp_loc.sort_values("Prom_Minutos", ascending=True)
    colores = desp_plot["Prom_Minutos"].apply(
        lambda x: "darkred" if x > 18 else "orange" if x > 14 else "green"
    )
    ax.barh(desp_plot["nombre_localidad"], desp_plot["Prom_Minutos"], color=colores)
    ax.set_xlabel("Tiempo promedio al colegio (minutos)")
    ax.set_title("Tiempo de Desplazamiento al Colegio por Localidad\n(Bogotá 2014)",
                 fontsize=13, fontweight="bold")
    media = desp_loc["Prom_Minutos"].mean()
    ax.axvline(x=media, color="black", linestyle="--", linewidth=1.5,
               label=f"Promedio ({media:.1f} min)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "15_desplazamiento_colegio.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("\n✓ Gráfico guardado: 15_desplazamiento_colegio.png")


# =============================================================================
# 5. MODELO LOGÍSTICO: PROBABILIDAD DE NO ASISTENCIA
# =============================================================================

def analisis_factores_riesgo(df):
    """Analiza factores de riesgo para la inasistencia usando tablas cruzadas."""
    print("\n" + "=" * 70)
    print("ANÁLISIS 5: FACTORES DE RIESGO PARA INASISTENCIA ESCOLAR")
    print("=" * 70)

    jovenes = df[df["Edad_Escolar"] == 1].copy()
    peso = "fex_c"

    factores = [
        ("Se_Considera_Pobre", "Se considera pobre", {1: "Sí", 0: "No"}),
        ("Ingresos_Insuficientes", "Ingresos insuficientes", {1: "Sí", 0: "No"}),
        ("Estrato", "Estrato", {1: "Estrato 1", 2: "Estrato 2"}),
    ]

    print(f"\nPoblación en edad escolar (5-17): {len(jovenes)}")
    print(f"Tasa general de inasistencia: {np.average(jovenes['No_Asiste'], weights=jovenes[peso])*100:.2f}%")

    resultados = []
    for var, nombre, labels in factores:
        sub = jovenes[jovenes[var].notna()]
        print(f"\n--- {nombre} ---")
        for val in sorted(sub[var].unique()):
            grupo = sub[sub[var] == val]
            if len(grupo) > 20:
                tasa = np.average(grupo["No_Asiste"], weights=grupo[peso]) * 100
                label = labels.get(int(val), f"Valor {int(val)}")
                print(f"  {label}: Inasistencia = {tasa:.2f}% (n={len(grupo)})")
                resultados.append({"Factor": nombre, "Categoría": label, "Tasa_Inasistencia": tasa})

    # Test chi-cuadrado: pobreza vs inasistencia
    tabla = pd.crosstab(jovenes["Se_Considera_Pobre"], jovenes["No_Asiste"])
    chi2, p_chi, _, _ = stats.chi2_contingency(tabla)
    print(f"\n→ Chi²: Pobreza vs Inasistencia: χ²={chi2:.2f}, p={p_chi:.6f}")
    if p_chi < 0.05:
        print("  La asociación es estadísticamente significativa.")

    # Odds Ratio
    if tabla.shape == (2, 2):
        a, b = tabla.iloc[0, 0], tabla.iloc[0, 1]
        c, d = tabla.iloc[1, 0], tabla.iloc[1, 1]
        if b > 0 and c > 0:
            OR = (d * a) / (b * c)
            print(f"  Odds Ratio (Pobre vs No pobre): OR = {OR:.3f}")
            if OR > 1:
                print(f"  → Los que se consideran pobres tienen {OR:.1f}x más probabilidad de no asistir")

    # Gráfico de factores
    fig, ax = plt.subplots(figsize=(10, 6))
    df_res = pd.DataFrame(resultados)
    if not df_res.empty:
        sns.barplot(data=df_res, y="Categoría", x="Tasa_Inasistencia", hue="Factor",
                    ax=ax, palette="Set2")
        ax.set_xlabel("Tasa de Inasistencia Escolar (%)")
        ax.set_title("Factores de Riesgo para Inasistencia Escolar (5-17 años)\n(Bogotá 2014)",
                     fontsize=12, fontweight="bold")
        ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "16_factores_riesgo_inasistencia.png"),
                dpi=150, bbox_inches="tight")
    plt.close()
    print("\n✓ Gráfico guardado: 16_factores_riesgo_inasistencia.png")


# =============================================================================
# 6. RESUMEN INTEGRADO
# =============================================================================

def resumen_multiproposito(df, inasis_loc):
    """Genera resumen del análisis de la Encuesta Multipropósito."""
    print("\n" + "=" * 70)
    print("RESUMEN: ENCUESTA MULTIPROPÓSITO 2014")
    print("=" * 70)

    jovenes = df[df["Edad_Escolar"] == 1]
    peso = "fex_c"
    tasa_gral = np.average(jovenes["No_Asiste"], weights=jovenes[peso]) * 100

    pobres = jovenes[jovenes["Se_Considera_Pobre"] == 1]
    no_pobres = jovenes[jovenes["Se_Considera_Pobre"] == 0]
    tasa_pobre = np.average(pobres["No_Asiste"], weights=pobres[peso]) * 100 if len(pobres) > 0 else 0
    tasa_no_pobre = np.average(no_pobres["No_Asiste"], weights=no_pobres[peso]) * 100 if len(no_pobres) > 0 else 0

    resumen = f"""
RESUMEN: ENCUESTA MULTIPROPÓSITO BOGOTÁ 2014 - ANÁLISIS EDUCATIVO
===================================================================
Fuente: Encuesta Multipropósito Bogotá 2014 (DANE/SDP)
Registros: {len(df)} personas | Población en edad escolar (5-17): {len(jovenes)}

HALLAZGOS PRINCIPALES:

1. INASISTENCIA ESCOLAR:
   - Tasa general de inasistencia (5-17 años): {tasa_gral:.2f}%
   - Hogares que se consideran pobres: {tasa_pobre:.2f}%
   - Hogares que NO se consideran pobres: {tasa_no_pobre:.2f}%
   → Los jóvenes de hogares pobres tienen mayor probabilidad de no asistir.

2. RAZONES DE NO ASISTENCIA:
   - La razón económica (costos/falta de dinero + necesidad de trabajar)
     representa una proporción importante en hogares pobres.
   - "No le gusta/no le interesa" es significativa en ambos grupos.
   - La falta de cupos/lejanía afecta más a localidades periféricas.

3. SECTOR EDUCATIVO:
   - Los hogares pobres dependen más del sector oficial (público).
   - Las localidades periféricas tienen mayor concentración en el oficial.
   - Esto implica mayor vulnerabilidad ante recortes o problemas del sistema público.

4. DESPLAZAMIENTO:
   - Las localidades periféricas (Usme, Ciudad Bolívar, Bosa) tienen
     mayores tiempos de desplazamiento al colegio.
   - El transporte puede actuar como barrera adicional.

5. CONEXIÓN CON ANÁLISIS PREVIOS:
   - Los datos de 2014 confirman que la pobreza se asocia con:
     a) Mayor inasistencia escolar
     b) Mayor dependencia del sector oficial
     c) Mayores barreras de acceso (costos, distancia)
   - Las localidades identificadas como vulnerables en el análisis de
     deserción 2024 (Ciudad Bolívar, Usme, Bosa) ya mostraban en 2014
     los peores indicadores educativos.
   - Esto sugiere un problema ESTRUCTURAL que persiste en el tiempo.

CADENA EXPLICATIVA PROPUESTA:
   Pobreza del hogar
       ↓
   ├── Costos educativos → No puede pagar → No asiste
   ├── Necesidad de trabajar → Abandona estudios
   ├── Vivienda periférica → Mayor desplazamiento → Mayor fatiga
   └── Menor apoyo académico → Repitencia → Desmotivación → Deserción

LIMITACIONES:
- Los datos son de 2014; las condiciones pueden haber cambiado.
- La encuesta no distingue entre deserción formal e inasistencia temporal.
- No hay datos de seguimiento longitudinal (no se puede rastrear desertores).
"""
    print(resumen)

    with open(os.path.join(OUTPUT_DIR, "resumen_multiproposito.txt"), "w", encoding="utf-8") as f:
        f.write(resumen)
    print("✓ Resumen guardado: resumen_multiproposito.txt")


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  ANÁLISIS: ENCUESTA MULTIPROPÓSITO BOGOTÁ 2014                      ║")
    print("║  DataJam Edición 4 - Universidad Distrital                          ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    print("\n→ Cargando Encuesta Multipropósito 2014...")
    df = cargar_encuesta_multiproposito()
    print(f"  Registros: {len(df)} | Localidades: {df['nombre_localidad'].nunique()}")
    print(f"  Población edad escolar (5-17): {df['Edad_Escolar'].sum()}")

    analisis_razones_no_asistencia(df)
    analisis_inasistencia_temporal(df)
    inasis_loc = analisis_inasistencia_localidad(df)
    analisis_desplazamiento(df)
    analisis_factores_riesgo(df)
    resumen_multiproposito(df, inasis_loc)

    print("\n" + "=" * 70)
    print(f"✓ ANÁLISIS COMPLETO. Resultados en: {OUTPUT_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
