"""
Pagina: Conclusiones
====================
Resumen ejecutivo de hallazgos del analisis final y validaciones de consistencia
estadistica para transparencia de resultados.
"""

import dash
from dash import html
import dash_bootstrap_components as dbc
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import cargar_conclusiones_estructuradas


dash.register_page(__name__, path="/conclusiones", name="Conclusiones", order=3)


def _badge_significancia(hallazgo):
    p_val = hallazgo.get("p")
    if p_val is None:
        return dbc.Badge("Sin p-valor", color="secondary", className="me-2")
    if p_val < 0.01:
        return dbc.Badge(f"p={p_val:.4f}", color="success", className="me-2")
    if p_val < 0.05:
        return dbc.Badge(f"p={p_val:.4f}", color="primary", className="me-2")
    if p_val < 0.10:
        return dbc.Badge(f"p={p_val:.4f}", color="warning", className="me-2")
    return dbc.Badge(f"p={p_val:.4f}", color="secondary", className="me-2")


def _render_hallazgos(hallazgos):
    if not hallazgos:
        return dbc.Alert("No se pudieron parsear hallazgos estadisticos del archivo.", color="warning")

    cards = []
    for h in hallazgos:
        cards.append(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div([
                            dbc.Badge(f"Hallazgo {h['indice']}", color="dark", className="me-2"),
                            _badge_significancia(h),
                            dbc.Badge(h["nivel_significancia"], color="warning", text_color="dark"),
                        ], className="mb-2"),
                        html.H6(h["titulo"], className="fw-bold"),
                        html.P(
                            f"Pearson r = {h['pearson']:.3f}" if h.get("pearson") is not None else "Pearson: no disponible",
                            className="mb-1 text-primary fw-semibold",
                        ),
                        html.Ul([html.Li(i) for i in h.get("interpretacion", [])], className="mb-0"),
                    ]),
                    className="shadow-sm hallazgo-card",
                ),
                md=6,
                className="mb-3",
            )
        )
    return dbc.Row(cards)


def _render_alertas(alertas):
    if not alertas:
        return dbc.Alert("No se detectaron inconsistencias automaticas en los hallazgos parseados.", color="success")

    rows = []
    for a in alertas:
        color = "warning" if a["tipo"] == "warning" else "info"
        rows.append(dbc.Alert(a["mensaje"], color=color, className="mb-2 py-2"))
    return html.Div(rows)


def _seccion_texto(titulo, texto):
    if not texto:
        return None
    return dbc.Card(
        dbc.CardBody([
            html.H5(titulo, className="fw-bold mb-2 text-primary"),
            html.Pre(texto, className="mb-0 text-body", style={"whiteSpace": "pre-wrap", "fontFamily": "inherit"}),
        ]),
        className="shadow-sm mb-3",
    )


def layout():
    data = cargar_conclusiones_estructuradas()

    if not data["existe"]:
        return dbc.Container([
            dbc.Alert(data["error"], color="danger", className="mt-3"),
            html.P("Ejecuta el analisis final para generar el archivo de conclusiones en output.")
        ], fluid=True)

    secciones = data["secciones"]
    hallazgos = data["hallazgos"]
    alertas = data["alertas"]

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H3("Conclusiones y Recomendaciones", className="fw-bold mb-1"),
                    html.P(
                        "Sintesis ejecutiva basada en output/CONCLUSIONES_FINALES.txt con chequeos de coherencia estadistica.",
                        className="text-muted mb-2",
                    ),
                    dbc.Badge(f"Actualizado: {data['actualizado']}", color="primary"),
                ], className="section-hero mb-3"),
            ])
        ]),

        dbc.Row([
            dbc.Col([
                html.H5("Hallazgos cuantitativos", className="fw-bold mb-3 section-title"),
                _render_hallazgos(hallazgos),
            ])
        ]),

        dbc.Row([
            dbc.Col(_seccion_texto(
                "Cadena causal propuesta",
                secciones.get("CADENA CAUSAL PROPUESTA (respaldada por datos)", ""),
            ), md=12),
        ]),

        dbc.Row([
            dbc.Col(_seccion_texto(
                "Rol del transporte",
                secciones.get("ROL DEL TRANSPORTE (datos reales Multipropósito 2021)", ""),
            ), md=6),
            dbc.Col(_seccion_texto(
                "Hallazgo contra-intuitivo",
                secciones.get("HALLAZGO CONTRA-INTUITIVO", ""),
            ), md=6),
        ]),

        dbc.Row([
            dbc.Col(_seccion_texto(
                "Nuevas hipotesis",
                secciones.get("NUEVAS HIPÓTESIS", ""),
            ), md=6),
            dbc.Col(_seccion_texto(
                "Recomendaciones",
                secciones.get("RECOMENDACIONES", ""),
            ), md=6),
        ]),
    ], fluid=True)
