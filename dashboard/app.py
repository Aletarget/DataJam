"""
Dashboard Interactivo - DataJam Edición 4
==========================================
Análisis: Deserción Escolar, Pobreza y Condiciones Socioeconómicas en Bogotá D.C.
Universidad Distrital Francisco José de Caldas

Ejecutar con: python dashboard/app.py
"""

import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc

# Inicializar app con tema Bootstrap
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.title = "DataJam 4 - Deserción Escolar Bogotá"

# =============================================================================
# NAVBAR
# =============================================================================

navbar = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.I(className="fas fa-graduation-cap me-2"),
                    html.Span("DataJam 4", className="fw-bold fs-5"),
                    html.Span(" | Deserción Escolar Bogotá", className="text-light opacity-75 ms-2"),
                ], className="d-flex align-items-center"),
                width="auto",
            ),
        ], align="center", className="g-0"),
        dbc.Nav([
            dbc.NavItem(
                dbc.NavLink(
                    [html.I(className="fas fa-map me-1"), "Mapa Territorial"],
                    href="/",
                    active="exact",
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [html.I(className="fas fa-chart-scatter me-1"), "Correlaciones"],
                    href="/correlaciones",
                    active="exact",
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [html.I(className="fas fa-chart-line me-1"), "Evolución Temporal"],
                    href="/temporal",
                    active="exact",
                )
            ),
        ], className="ms-auto", navbar=True),
    ], fluid=True),
    color="primary",
    dark=True,
    className="mb-3",
)

# =============================================================================
# LAYOUT PRINCIPAL
# =============================================================================

app.layout = html.Div([
    # Font Awesome para iconos
    html.Link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"
    ),
    navbar,
    dbc.Container(
        dash.page_container,
        fluid=True,
        className="px-4 pb-4",
    ),
    # Footer
    html.Footer(
        dbc.Container(
            html.Div([
                html.Hr(className="my-3"),
                html.P([
                    "DataJam Edición 4 — Universidad Distrital Francisco José de Caldas | ",
                    html.Span("Fuentes: ", className="fw-bold"),
                    "SED Bogotá, DANE, SDP, Encuesta Distrital de Percepción 2025",
                ], className="text-muted text-center small mb-0"),
            ]),
            fluid=True,
        )
    ),
])


# =============================================================================
# SERVER
# =============================================================================

server = app.server  # Para deploy con gunicorn

if __name__ == "__main__":
    app.run(debug=True, port=8050)
