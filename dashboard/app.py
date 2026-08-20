"""
Dashboard Interactivo - DataJam Edición 4
==========================================
Análisis: Deserción Escolar, Pobreza y Condiciones Socioeconómicas en Bogotá D.C.
Universidad Distrital Francisco José de Caldas

Ejecutar con: python dashboard/app.py
"""

import dash
from dash import html, callback, Input, Output, State
import dash_bootstrap_components as dbc

# Inicializar app con tema Bootstrap base (overridden by assets/style.css)
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.title = "DataJam 4 - Deserción Escolar Bogotá"

# =============================================================================
# NAVBAR
# =============================================================================

navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row([
                dbc.Col(html.I(className="fas fa-graduation-cap me-2 fs-4"), width="auto"),
                dbc.Col(
                    html.Div([
                        html.Span("DataJam 4", className="fw-bold fs-5 navbar-brand-text"),
                        html.Span(
                            " | Deserción Escolar Bogotá",
                            className="navbar-subtitle ms-2 d-none d-md-inline",
                        ),
                    ], className="d-flex align-items-center flex-wrap"),
                ),
            ], align="center", className="g-0"),
            href="/",
            className="text-decoration-none",
        ),
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(
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
                dbc.NavItem(
                    dbc.NavLink(
                        [html.I(className="fas fa-lightbulb me-1"), "Conclusiones"],
                        href="/conclusiones",
                        active="exact",
                    )
                ),
            ], className="ms-auto", navbar=True),
            id="navbar-collapse",
            is_open=False,
            navbar=True,
        ),
    ], fluid=True),
    color="dark",
    dark=True,
    className="mb-4 navbar-bogota",
)

# =============================================================================
# LAYOUT PRINCIPAL
# =============================================================================

app.layout = html.Div([
    html.Link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css",
    ),
    navbar,
    dbc.Container(
        dash.page_container,
        fluid=True,
        className="px-3 px-md-4 pb-4 page-container",
    ),
    html.Footer(
        dbc.Container(
            html.Div([
                html.P([
                    html.Span("DataJam Edición 4", className="footer-accent"),
                    " — Universidad Distrital Francisco José de Caldas",
                ], className="text-center mb-1 fw-semibold"),
                html.P([
                    html.Span("Fuentes: ", className="fw-bold"),
                    "SED Bogotá, DANE, SDP, Encuesta Distrital de Percepción 2025",
                ], className="text-muted text-center small mb-0"),
            ]),
            fluid=True,
        ),
        className="site-footer",
    ),
])


@callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open"),
)
def toggle_navbar_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


# =============================================================================
# SERVER
# =============================================================================

server = app.server  # Para deploy con gunicorn

if __name__ == "__main__":
    app.run(debug=True, port=8050)
