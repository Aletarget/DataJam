"""
Página: Evolución Temporal
============================
Serie temporal interactiva del IPM y privaciones educativas en Bogotá,
con comparación por localidad de pobreza monetaria a lo largo del tiempo.
"""

import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy import stats
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import cargar_pobreza, obtener_serie_temporal_bogota

dash.register_page(__name__, path="/temporal", name="Evolución Temporal", order=2)

# =============================================================================
# DATOS
# =============================================================================

df_pobreza = cargar_pobreza()
serie_bogota = obtener_serie_temporal_bogota()

# Localidades disponibles para la serie de pobreza monetaria
localidades_disponibles = sorted(
    df_pobreza[
        (~df_pobreza["Localidad"].str.contains("Bogot", na=False)) &
        (df_pobreza["Indicador"] == "Pobreza monetaria") &
        (df_pobreza["Sexo"].str.contains("Ambos", na=False))
    ]["Localidad"].unique().tolist()
)

# Indicadores disponibles
INDICADORES_TEMPORALES = {
    "Pobreza monetaria": "Pobreza Monetaria (%)",
    "Pobreza monetaria extrema": "Pobreza Monetaria Extrema (%)",
    "Coeficiente de Gini": "Coeficiente de Gini",
    "IPM": "Índice de Pobreza Multidimensional (%)",
}

# Privaciones educativas disponibles en la serie
PRIVACIONES = [c for c in serie_bogota.columns if c not in ["Año", "IPM"]]

# =============================================================================
# LAYOUT
# =============================================================================

layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H3("Evolución Temporal: Pobreza e Indicadores Educativos", className="fw-bold mb-1"),
            html.P(
                "Análisis de la evolución del IPM, privaciones educativas y pobreza monetaria "
                "en Bogotá D.C. entre 2003 y 2025.",
                className="text-muted mb-3"
            ),
        ]),
    ]),

    # Sección 1: IPM + Privaciones Educativas (Bogotá)
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("IPM y Privaciones Educativas — Bogotá D.C.", className="mb-0 fw-bold"),
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Privaciones a mostrar", className="fw-bold mb-2"),
                            dcc.Checklist(
                                id="temporal-privaciones",
                                options=[{"label": f" {p}", "value": p} for p in PRIVACIONES],
                                value=PRIVACIONES[:3],  # Primeras 3 seleccionadas por defecto
                                className="mb-0",
                            ),
                        ], md=3),
                        dbc.Col([
                            dcc.Graph(id="temporal-ipm-educacion", style={"height": "450px"}),
                        ], md=9),
                    ]),
                ]),
            ], className="shadow-sm"),
        ]),
    ], className="mb-4"),

    # Sección 2: Pobreza por Localidad
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Pobreza Monetaria por Localidad", className="mb-0 fw-bold"),
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Indicador", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="temporal-indicador",
                                options=[{"label": v, "value": k} for k, v in INDICADORES_TEMPORALES.items()],
                                value="Pobreza monetaria",
                                clearable=False,
                            ),
                        ], md=4),
                        dbc.Col([
                            html.Label("Localidades a comparar", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="temporal-localidades",
                                options=[{"label": loc, "value": loc} for loc in localidades_disponibles],
                                value=["Ciudad Bolívar", "Usme", "Chapinero", "Usaquén"],
                                multi=True,
                                placeholder="Selecciona localidades...",
                            ),
                        ], md=8),
                    ], className="mb-3"),
                    dcc.Graph(id="temporal-localidades-chart", style={"height": "450px"}),
                ]),
            ], className="shadow-sm"),
        ]),
    ], className="mb-4"),

    # Sección 3: Comparación año a año (barras agrupadas)
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Comparación entre Años — Todas las Localidades", className="mb-0 fw-bold"),
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Año de comparación", className="fw-bold mb-2"),
                            dcc.Slider(
                                id="temporal-slider-año",
                                min=int(df_pobreza["Año"].min()),
                                max=int(df_pobreza["Año"].max()),
                                step=1,
                                value=2021,
                                marks={int(y): str(int(y)) for y in sorted(df_pobreza["Año"].unique())},
                                tooltip={"placement": "bottom", "always_visible": True},
                            ),
                        ]),
                    ], className="mb-3"),
                    dcc.Graph(id="temporal-barras-año", style={"height": "500px"}),
                ]),
            ], className="shadow-sm"),
        ]),
    ]),

    # Insight box
    dbc.Row([
        dbc.Col([
            dbc.Alert([
                html.H6("Hallazgo clave", className="alert-heading fw-bold"),
                html.P([
                    "El IPM pasó de 4.1% (2018) a un pico de 7.5% (2020, pandemia) y descendió "
                    "hasta 2.2% (2025). La inasistencia escolar mostró un pico dramático en 2020 (6.0%) "
                    "coincidiendo con el aumento del IPM. Las localidades con mayor pobreza monetaria "
                    "(Ciudad Bolívar, Usme, Bosa) mantienen brechas persistentes a lo largo de todo el período."
                ], className="mb-0"),
            ], color="info", className="mt-4"),
        ]),
    ]),
], fluid=True)


# =============================================================================
# CALLBACKS
# =============================================================================

@callback(
    Output("temporal-ipm-educacion", "figure"),
    Input("temporal-privaciones", "value"),
)
def actualizar_ipm_educacion(privaciones_seleccionadas):
    """Gráfico dual: IPM arriba, privaciones educativas abajo."""
    serie = serie_bogota.copy()

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            "<b>Índice de Pobreza Multidimensional (IPM)</b>",
            "<b>Privaciones Educativas</b>",
        ),
        row_heights=[0.4, 0.6],
    )

    # Panel superior: IPM
    fig.add_trace(
        go.Scatter(
            x=serie["Año"], y=serie["IPM"],
            mode="lines+markers",
            name="IPM",
            line=dict(color="#c0392b", width=3),
            marker=dict(size=10),
            hovertemplate="Año: %{x}<br>IPM: %{y:.2f}%<extra></extra>",
        ),
        row=1, col=1,
    )

    # Sombrear zona pandemia
    fig.add_vrect(
        x0=2019.5, x1=2021.5,
        fillcolor="rgba(255,0,0,0.05)", line_width=0,
        annotation_text="COVID-19", annotation_position="top left",
        row=1, col=1,
    )

    # Panel inferior: Privaciones educativas
    colores = px.colors.qualitative.Set2
    for i, priv in enumerate(privaciones_seleccionadas):
        if priv in serie.columns:
            fig.add_trace(
                go.Scatter(
                    x=serie["Año"], y=serie[priv],
                    mode="lines+markers",
                    name=priv,
                    line=dict(color=colores[i % len(colores)], width=2.5),
                    marker=dict(size=7),
                    hovertemplate=f"{priv}<br>Año: %{{x}}<br>Valor: %{{y:.2f}}%<extra></extra>",
                ),
                row=2, col=1,
            )

    # Sombrear pandemia en panel inferior también
    fig.add_vrect(
        x0=2019.5, x1=2021.5,
        fillcolor="rgba(255,0,0,0.05)", line_width=0,
        row=2, col=1,
    )

    fig.update_xaxes(title_text="Año", row=2, col=1)
    fig.update_yaxes(title_text="IPM (%)", row=1, col=1)
    fig.update_yaxes(title_text="Porcentaje (%)", row=2, col=1)
    fig.update_layout(
        margin={"t": 60, "b": 40},
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        hovermode="x unified",
    )

    return fig


@callback(
    Output("temporal-localidades-chart", "figure"),
    [Input("temporal-indicador", "value"),
     Input("temporal-localidades", "value")],
)
def actualizar_localidades(indicador, localidades):
    """Líneas de evolución del indicador seleccionado por localidad."""
    if not localidades:
        return go.Figure().update_layout(
            annotations=[dict(text="Selecciona al menos una localidad", showarrow=False, font_size=16)]
        )

    df = df_pobreza[
        (df_pobreza["Indicador"] == indicador) &
        (df_pobreza["Sexo"].str.contains("Ambos", na=False)) &
        (df_pobreza["Localidad"].isin(localidades))
    ].copy()

    label = INDICADORES_TEMPORALES[indicador]

    fig = px.line(
        df, x="Año", y="Valor", color="Localidad",
        markers=True,
        labels={"Valor": label, "Año": "Año"},
        color_discrete_sequence=px.colors.qualitative.Bold,
    )

    fig.update_traces(line=dict(width=2.5), marker=dict(size=8))
    fig.update_layout(
        title=dict(text=f"<b>{label} por Localidad</b>", x=0.5, font_size=14),
        margin={"t": 60, "b": 40},
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        hovermode="x unified",
    )

    # Agregar línea de Bogotá como referencia
    bogota = df_pobreza[
        (df_pobreza["Indicador"] == indicador) &
        (df_pobreza["Sexo"].str.contains("Ambos", na=False)) &
        (df_pobreza["Localidad"].str.contains("Bogot", na=False))
    ]
    if not bogota.empty:
        fig.add_trace(go.Scatter(
            x=bogota["Año"], y=bogota["Valor"],
            mode="lines",
            name="Bogotá (promedio)",
            line=dict(color="black", width=2, dash="dash"),
            opacity=0.6,
        ))

    return fig


@callback(
    Output("temporal-barras-año", "figure"),
    Input("temporal-slider-año", "value"),
)
def actualizar_barras_año(año):
    """Barras horizontales de pobreza monetaria por localidad para un año dado."""
    df = df_pobreza[
        (df_pobreza["Indicador"] == "Pobreza monetaria") &
        (df_pobreza["Año"] == año) &
        (df_pobreza["Sexo"].str.contains("Ambos", na=False)) &
        (~df_pobreza["Localidad"].str.contains("Bogot", na=False))
    ].copy()

    if df.empty:
        # Intentar el año más cercano disponible
        return go.Figure().update_layout(
            annotations=[dict(
                text=f"No hay datos de pobreza monetaria para {año}",
                showarrow=False, font_size=14,
            )]
        )

    df = df.sort_values("Valor", ascending=True)

    # Color basado en valor
    fig = px.bar(
        df, x="Valor", y="Localidad",
        orientation="h",
        color="Valor",
        color_continuous_scale="YlOrRd",
        labels={"Valor": "Pobreza Monetaria (%)", "Localidad": ""},
        hover_data={"Valor": ":.1f"},
    )

    # Línea de media de Bogotá
    bogota_val = df_pobreza[
        (df_pobreza["Indicador"] == "Pobreza monetaria") &
        (df_pobreza["Año"] == año) &
        (df_pobreza["Sexo"].str.contains("Ambos", na=False)) &
        (df_pobreza["Localidad"].str.contains("Bogot", na=False))
    ]["Valor"]

    if not bogota_val.empty:
        media_bog = bogota_val.iloc[0]
        fig.add_vline(
            x=media_bog, line_dash="dash", line_color="black", line_width=2,
            annotation_text=f"Bogotá: {media_bog:.1f}%",
            annotation_position="top",
        )

    fig.update_layout(
        title=dict(text=f"<b>Pobreza Monetaria por Localidad — {año}</b>", x=0.5, font_size=14),
        margin={"t": 60, "b": 40},
        coloraxis_showscale=False,
        yaxis=dict(tickfont=dict(size=11)),
    )

    return fig
