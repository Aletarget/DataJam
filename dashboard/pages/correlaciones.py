"""
Página: Correlaciones Dinámicas
================================
Scatter plots interactivos para explorar correlaciones entre variables
socioeconómicas y resultados educativos por UPL.
"""

import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import cargar_cruce_encuesta_desercion
from theme import (
    BOGOTA_RED,
    BOGOTA_RED_DARK,
    BOGOTA_SCALE_HEATMAP,
    BOGOTA_SCALE_SEQUENTIAL,
    CHART_LAYOUT,
)

dash.register_page(__name__, path="/correlaciones", name="Correlaciones", order=1)

# =============================================================================
# DATOS
# =============================================================================

cruce = cargar_cruce_encuesta_desercion()

# Variables disponibles para ejes
VARIABLES = {
    # Educativas
    "Desercion_Oficial": "Tasa de Deserción Oficial (%)",
    "Desercion_NoOficial": "Tasa de Deserción No Oficial (%)",
    "Reprobacion_Oficial": "Tasa de Reprobación Oficial (%)",
    "Reprobacion_NoOficial": "Tasa de Reprobación No Oficial (%)",
    "Aprobacion_Oficial": "Tasa de Aprobación Oficial (%)",
    # Socioeconómicas
    "Pct_Pobre": "% Se considera pobre",
    "Pct_Ing_Insuficientes": "% Ingresos insuficientes",
    "Pct_Ing_Precarios": "% Ingresos precarios",
    "Pct_Inseg_Alimentaria": "% Inseguridad alimentaria",
    "Pct_Estrato_Bajo": "% Estrato 1-2",
    "Pct_Bajo_Acceso_Educ": "% Bajo acceso educación",
    "Pct_Bajo_Acceso_Empleo": "% Bajo acceso empleo",
    "Pct_Desempleado": "% Desempleado",
}

GRUPOS_VARIABLES = {
    "Educativas": [
        "Desercion_Oficial", "Desercion_NoOficial",
        "Reprobacion_Oficial", "Reprobacion_NoOficial", "Aprobacion_Oficial",
    ],
    "Socioeconómicas": [
        "Pct_Pobre", "Pct_Ing_Insuficientes", "Pct_Ing_Precarios",
        "Pct_Inseg_Alimentaria", "Pct_Estrato_Bajo",
        "Pct_Bajo_Acceso_Educ", "Pct_Bajo_Acceso_Empleo", "Pct_Desempleado",
    ],
}

# =============================================================================
# LAYOUT
# =============================================================================

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3("Explorador de Correlaciones", className="fw-bold mb-1"),
                html.P(
                    "Selecciona variables para los ejes X e Y y explora la relación "
                    "entre condiciones socioeconómicas y resultados educativos por UPL.",
                    className="text-muted mb-2",
                ),
                dbc.Alert(
                    "Usa esta vista para evaluar fuerza y dirección de relaciones. "
                    "La significancia estadística se resume en el panel lateral.",
                    color="light",
                    className="insight-card mb-0",
                ),
            ], className="section-hero mb-3"),
        ]),
    ]),

    # Controles
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("Eje X (Variable independiente)", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id="corr-var-x",
                        options=[
                            {"label": f"{'📊' if k in GRUPOS_VARIABLES['Educativas'] else '💰'} {v}", "value": k}
                            for k, v in VARIABLES.items()
                        ],
                        value="Pct_Pobre",
                        clearable=False,
                    ),
                ]),
            ], className="shadow-sm"),
        ], md=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("Eje Y (Variable dependiente)", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id="corr-var-y",
                        options=[
                            {"label": f"{'📊' if k in GRUPOS_VARIABLES['Educativas'] else '💰'} {v}", "value": k}
                            for k, v in VARIABLES.items()
                        ],
                        value="Desercion_Oficial",
                        clearable=False,
                    ),
                ]),
            ], className="shadow-sm"),
        ], md=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("Color por variable", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id="corr-color",
                        options=[{"label": "Sin color", "value": "none"}] + [
                            {"label": v, "value": k} for k, v in VARIABLES.items()
                        ],
                        value="none",
                        clearable=False,
                    ),
                ]),
            ], className="shadow-sm"),
        ], md=4),
    ], className="mb-3"),

    # Opciones adicionales
    dbc.Row([
        dbc.Col([
            dbc.Checklist(
                id="corr-opciones",
                options=[
                    {"label": " Mostrar línea de tendencia", "value": "tendencia"},
                    {"label": " Mostrar etiquetas de UPL", "value": "etiquetas"},
                ],
                value=["tendencia"],
                inline=True,
                className="mt-1",
            ),
        ]),
    ], className="mb-3"),

    # Gráficos
    dbc.Row([
        # Scatter principal
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(
                        dcc.Graph(id="corr-scatter", className="chart-main"),
                        type="default",
                    ),
                ]),
            ], className="shadow-sm"),
        ], lg=8),

        # Panel de estadísticas
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Estadísticas de Correlación", className="fw-bold text-primary mb-3 section-title"),
                    html.Div(id="corr-stats"),
                ]),
            ], className="shadow-sm mb-3"),

            # Matriz de correlaciones rápida
            dbc.Card([
                dbc.CardBody([
                    html.H6("Top Correlaciones con Deserción", className="fw-bold text-danger mb-3 section-title"),
                    html.Div(id="corr-top"),
                ]),
            ], className="shadow-sm"),
        ], lg=4),
    ]),

    # Heatmap de correlación completo
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Matriz de Correlaciones", className="fw-bold mb-2 section-title"),
                    dcc.Loading(
                        dcc.Graph(id="corr-heatmap", className="chart-medium"),
                        type="default",
                    ),
                ]),
            ], className="shadow-sm mt-3"),
        ]),
    ]),
], fluid=True)


# =============================================================================
# CALLBACKS
# =============================================================================

@callback(
    [Output("corr-scatter", "figure"),
     Output("corr-stats", "children"),
     Output("corr-top", "children"),
     Output("corr-heatmap", "figure")],
    [Input("corr-var-x", "value"),
     Input("corr-var-y", "value"),
     Input("corr-color", "value"),
     Input("corr-opciones", "value")],
)
def actualizar_correlaciones(var_x, var_y, var_color, opciones):
    df = cruce.copy()
    label_x = VARIABLES[var_x]
    label_y = VARIABLES[var_y]
    mostrar_tendencia = "tendencia" in opciones
    mostrar_etiquetas = "etiquetas" in opciones

    # --- SCATTER PLOT ---
    sub = df[[var_x, var_y, "Nom_UPL", "Localidad", "CODIGO_UPL"]].dropna()

    scatter_kwargs = dict(
        data_frame=sub,
        x=var_x,
        y=var_y,
        hover_name="Nom_UPL",
        hover_data={"Localidad": True, var_x: ":.2f", var_y: ":.2f"},
        labels={var_x: label_x, var_y: label_y},
    )

    if var_color != "none" and var_color in df.columns:
        sub[var_color] = df.loc[sub.index, var_color]
        scatter_kwargs["color"] = var_color
        scatter_kwargs["color_continuous_scale"] = BOGOTA_SCALE_SEQUENTIAL
        scatter_kwargs["labels"][var_color] = VARIABLES.get(var_color, var_color)
    else:
        scatter_kwargs["color_discrete_sequence"] = [BOGOTA_RED]

    if mostrar_etiquetas:
        scatter_kwargs["text"] = "Nom_UPL"

    fig_scatter = px.scatter(**scatter_kwargs)
    fig_scatter.update_traces(marker=dict(size=12, line=dict(width=1, color="black"), opacity=0.8))

    if mostrar_etiquetas:
        fig_scatter.update_traces(textposition="top center", textfont_size=9)

    # Línea de tendencia
    if mostrar_tendencia and len(sub) >= 5:
        x_vals = sub[var_x].values
        y_vals = sub[var_y].values
        slope, intercept, r, p, se = stats.linregress(x_vals, y_vals)
        x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
        y_line = slope * x_line + intercept
        fig_scatter.add_trace(go.Scatter(
            x=x_line, y=y_line, mode="lines",
            line=dict(color=BOGOTA_RED_DARK, width=2, dash="dash"),
            name=f"Tendencia (r={r:.3f})",
            showlegend=True,
        ))

    fig_scatter.update_layout(
        title=dict(text=f"<b>{label_x} vs {label_y}</b>", x=0.5, font_size=14, font_color=BOGOTA_RED_DARK),
        margin={"t": 60, "b": 50},
        **CHART_LAYOUT,
    )

    # --- ESTADÍSTICAS ---
    stats_content = html.Div([html.P("Datos insuficientes", className="text-muted")])
    if len(sub) >= 5:
        r_val, p_val = stats.pearsonr(sub[var_x], sub[var_y])
        rho, p_sp = stats.spearmanr(sub[var_x], sub[var_y])

        significancia = "Significativa (p < 0.05)" if p_val < 0.05 else \
                        "Marginal (p < 0.10)" if p_val < 0.10 else "No significativa"
        color_sig = "success" if p_val < 0.05 else "warning" if p_val < 0.10 else "secondary"

        # Interpretación de la fuerza
        abs_r = abs(r_val)
        if abs_r > 0.7:
            fuerza = "Fuerte"
        elif abs_r > 0.4:
            fuerza = "Moderada"
        elif abs_r > 0.2:
            fuerza = "Débil"
        else:
            fuerza = "Muy débil"

        direccion = "Positiva" if r_val > 0 else "Negativa"

        stats_content = html.Div([
            html.Div([
                html.Span("Pearson r", className="text-muted small d-block"),
                html.Span(f"{r_val:+.4f}", className="fs-4 fw-bold text-primary"),
            ], className="text-center mb-3 p-2 bg-light rounded"),
            html.Table([
                html.Tr([html.Td("p-valor:", className="text-muted"), html.Td(f"{p_val:.4f}", className="fw-bold")]),
                html.Tr([html.Td("Spearman:", className="text-muted"), html.Td(f"{rho:+.4f}", className="fw-bold")]),
                html.Tr([html.Td("N (UPLs):", className="text-muted"), html.Td(f"{len(sub)}", className="fw-bold")]),
                html.Tr([html.Td("Fuerza:", className="text-muted"), html.Td(fuerza, className="fw-bold")]),
                html.Tr([html.Td("Dirección:", className="text-muted"), html.Td(direccion, className="fw-bold")]),
            ], className="table table-sm mb-3"),
            dbc.Badge(significancia, color=color_sig, className="w-100 py-2"),
        ])

    # --- TOP CORRELACIONES CON DESERCIÓN ---
    vars_socio = GRUPOS_VARIABLES["Socioeconómicas"]
    top_items = []
    correlaciones = []
    for var in vars_socio:
        sub_c = df[["Desercion_Oficial", var]].dropna()
        if len(sub_c) >= 5:
            r_c, p_c = stats.pearsonr(sub_c["Desercion_Oficial"], sub_c[var])
            correlaciones.append((var, r_c, p_c))

    correlaciones.sort(key=lambda x: abs(x[1]), reverse=True)
    for var, r_c, p_c in correlaciones[:6]:
        color = "text-danger" if r_c > 0 else "text-primary"
        sig_mark = " *" if p_c < 0.05 else ""
        top_items.append(
            html.Div([
                html.Span(f"{r_c:+.3f}{sig_mark}", className=f"fw-bold {color} me-2"),
                html.Span(VARIABLES[var], className="small"),
            ], className="mb-2 border-bottom pb-1")
        )
    top_content = html.Div([
        html.Div(top_items),
        html.P("* = significativo p<0.05", className="text-muted small mt-2 mb-0"),
    ])

    # --- HEATMAP DE CORRELACIONES ---
    vars_heatmap = [v for v in VARIABLES.keys() if v in df.columns]
    df_corr = df[vars_heatmap].corr()
    labels_short = [VARIABLES[v][:25] for v in vars_heatmap]

    fig_heatmap = px.imshow(
        df_corr.values,
        x=labels_short,
        y=labels_short,
        color_continuous_scale=BOGOTA_SCALE_HEATMAP,
        zmin=-1, zmax=1,
        text_auto=".2f",
        aspect="auto",
    )
    fig_heatmap.update_layout(
        title=dict(text="<b>Matriz de Correlaciones (Pearson)</b>", x=0.5, font_size=14, font_color=BOGOTA_RED_DARK),
        margin={"t": 60, "b": 50},
        xaxis=dict(tickangle=45, tickfont=dict(size=9)),
        yaxis=dict(tickfont=dict(size=9)),
        **CHART_LAYOUT,
    )

    return fig_scatter, stats_content, top_content, fig_heatmap
