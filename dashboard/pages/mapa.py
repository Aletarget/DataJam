"""
Página: Mapa Territorial
=========================
Mapa choropleth interactivo de Bogotá por UPL mostrando deserción escolar,
reprobación y condiciones socioeconómicas de la Encuesta Distrital.
"""

import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import cargar_desercion_geojson, cargar_cruce_encuesta_desercion

dash.register_page(__name__, path="/", name="Mapa Territorial", order=0)

# =============================================================================
# DATOS
# =============================================================================

geojson = cargar_desercion_geojson()
cruce = cargar_cruce_encuesta_desercion()

# Opciones de indicadores para el mapa
INDICADORES_MAPA = {
    "Desercion_Oficial": "Tasa de Deserción Oficial (%)",
    "Reprobacion_Oficial": "Tasa de Reprobación Oficial (%)",
    "Aprobacion_Oficial": "Tasa de Aprobación Oficial (%)",
    "Pct_Pobre": "% Hogares que se consideran pobres",
    "Pct_Ing_Precarios": "% Hogares con ingresos precarios",
    "Pct_Inseg_Alimentaria": "% Inseguridad alimentaria",
    "Pct_Estrato_Bajo": "% Hogares estrato 1-2",
    "Pct_Bajo_Acceso_Educ": "% Bajo acceso a educación",
    "Pct_Desempleado": "% Desempleo",
}

ESCALAS_COLOR = {
    "Desercion_Oficial": "Reds",
    "Reprobacion_Oficial": "OrRd",
    "Aprobacion_Oficial": "Greens",
    "Pct_Pobre": "YlOrRd",
    "Pct_Ing_Precarios": "YlOrRd",
    "Pct_Inseg_Alimentaria": "Purples",
    "Pct_Estrato_Bajo": "Blues",
    "Pct_Bajo_Acceso_Educ": "RdPu",
    "Pct_Desempleado": "Oranges",
}

# =============================================================================
# LAYOUT
# =============================================================================

layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H3("Mapa Territorial: Indicadores por UPL", className="fw-bold mb-1"),
            html.P(
                "Visualización geoespacial de indicadores educativos y socioeconómicos "
                "por Unidad de Planeamiento Local (UPL) en Bogotá D.C.",
                className="text-muted mb-3"
            ),
        ]),
    ]),

    # Controles
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("Indicador a visualizar", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id="mapa-indicador",
                        options=[{"label": v, "value": k} for k, v in INDICADORES_MAPA.items()],
                        value="Desercion_Oficial",
                        clearable=False,
                        className="mb-0",
                    ),
                ]),
            ], className="shadow-sm"),
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("Filtrar por localidad", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id="mapa-localidad",
                        options=[{"label": "Todas", "value": "Todas"}] + [
                            {"label": loc, "value": loc}
                            for loc in sorted(cruce["Localidad"].dropna().unique())
                        ],
                        value="Todas",
                        clearable=False,
                        className="mb-0",
                    ),
                ]),
            ], className="shadow-sm"),
        ], md=6),
    ], className="mb-3"),

    # Mapa + Tarjetas resumen
    dbc.Row([
        # Mapa principal
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="mapa-choropleth", style={"height": "600px"}),
                ]),
            ], className="shadow-sm"),
        ], lg=8),

        # Panel lateral con KPIs y ranking
        dbc.Col([
            # KPIs
            dbc.Card([
                dbc.CardBody([
                    html.H6("Resumen del Indicador", className="fw-bold text-primary mb-3"),
                    html.Div(id="mapa-kpis"),
                ]),
            ], className="shadow-sm mb-3"),

            # Ranking top 5
            dbc.Card([
                dbc.CardBody([
                    html.H6("Top 5 UPLs (Mayor Valor)", className="fw-bold text-danger mb-3"),
                    html.Div(id="mapa-ranking"),
                ]),
            ], className="shadow-sm"),
        ], lg=4),
    ]),

    # Gráfico de barras complementario
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="mapa-barras"),
                ]),
            ], className="shadow-sm mt-3"),
        ]),
    ]),
], fluid=True)


# =============================================================================
# CALLBACKS
# =============================================================================

@callback(
    [Output("mapa-choropleth", "figure"),
     Output("mapa-kpis", "children"),
     Output("mapa-ranking", "children"),
     Output("mapa-barras", "figure")],
    [Input("mapa-indicador", "value"),
     Input("mapa-localidad", "value")],
)
def actualizar_mapa(indicador, localidad):
    df = cruce.copy()

    # Filtrar por localidad si aplica
    if localidad != "Todas":
        df = df[df["Localidad"] == localidad]

    label = INDICADORES_MAPA[indicador]
    escala = ESCALAS_COLOR.get(indicador, "Viridis")

    # --- MAPA CHOROPLETH ---
    fig_mapa = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations="CODIGO_UPL",
        featureidkey="properties.CODIGO_UPL",
        color=indicador,
        color_continuous_scale=escala,
        hover_name="Nom_UPL",
        hover_data={
            "CODIGO_UPL": True,
            indicador: ":.2f",
            "Localidad": True,
            "N_Encuestados": True,
        },
        labels={indicador: label},
        mapbox_style="carto-positron",
        center={"lat": 4.65, "lon": -74.1},
        zoom=10,
        opacity=0.7,
    )
    fig_mapa.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title=dict(text=f"<b>{label}</b>", x=0.5, font_size=14),
        coloraxis_colorbar=dict(title=dict(text=label, font_size=11), thickness=15),
    )

    # --- KPIs ---
    media = df[indicador].mean()
    mediana = df[indicador].median()
    minimo = df[indicador].min()
    maximo = df[indicador].max()
    n_upls = len(df)

    kpis = html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("Promedio", className="text-muted small d-block"),
                    html.Span(f"{media:.2f}%", className="fs-5 fw-bold text-primary"),
                ], className="text-center"),
            ], width=6),
            dbc.Col([
                html.Div([
                    html.Span("Mediana", className="text-muted small d-block"),
                    html.Span(f"{mediana:.2f}%", className="fs-5 fw-bold text-info"),
                ], className="text-center"),
            ], width=6),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("Mínimo", className="text-muted small d-block"),
                    html.Span(f"{minimo:.2f}%", className="fs-5 fw-bold text-success"),
                ], className="text-center"),
            ], width=4),
            dbc.Col([
                html.Div([
                    html.Span("Máximo", className="text-muted small d-block"),
                    html.Span(f"{maximo:.2f}%", className="fs-5 fw-bold text-danger"),
                ], className="text-center"),
            ], width=4),
            dbc.Col([
                html.Div([
                    html.Span("UPLs", className="text-muted small d-block"),
                    html.Span(f"{n_upls}", className="fs-5 fw-bold"),
                ], className="text-center"),
            ], width=4),
        ]),
    ])

    # --- RANKING TOP 5 ---
    top5 = df.nlargest(5, indicador)[["Nom_UPL", "Localidad", indicador]]
    ranking_items = []
    for i, (_, row) in enumerate(top5.iterrows(), 1):
        ranking_items.append(
            html.Div([
                html.Span(f"{i}. ", className="fw-bold text-danger"),
                html.Span(f"UPL {row['Nom_UPL']} ", className="fw-bold"),
                html.Span(f"({row['Localidad']})", className="text-muted small"),
                html.Span(f" — {row[indicador]:.2f}%", className="text-primary fw-bold"),
            ], className="mb-2 border-bottom pb-1")
        )
    ranking = html.Div(ranking_items)

    # --- BARRAS ---
    df_sorted = df.sort_values(indicador, ascending=True)
    fig_barras = px.bar(
        df_sorted,
        x=indicador,
        y="Nom_UPL",
        orientation="h",
        color=indicador,
        color_continuous_scale=escala,
        labels={indicador: label, "Nom_UPL": "UPL"},
        hover_data={"Localidad": True, indicador: ":.2f"},
    )
    fig_barras.update_layout(
        title=dict(text=f"<b>{label} por UPL</b>", x=0.5, font_size=14),
        height=max(400, len(df) * 22),
        margin={"t": 50, "b": 30},
        showlegend=False,
        yaxis=dict(tickfont=dict(size=10)),
        coloraxis_showscale=False,
    )
    # Línea de media
    fig_barras.add_vline(
        x=media, line_dash="dash", line_color="black",
        annotation_text=f"Media: {media:.2f}%", annotation_position="top",
    )

    return fig_mapa, kpis, ranking, fig_barras
