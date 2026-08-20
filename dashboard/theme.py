"""
Shared Bogotá-inspired theme tokens for the DataJam dashboard.
Red as primary accent, yellow for highlights and CTAs.
"""

# Core palette (Bogotá flag-inspired, professional tones)
BOGOTA_RED = "#C8102E"
BOGOTA_RED_DARK = "#8B0A1F"
BOGOTA_RED_LIGHT = "#FEE2E2"
BOGOTA_YELLOW = "#FFD100"
BOGOTA_YELLOW_DARK = "#CA8A04"
BOGOTA_YELLOW_LIGHT = "#FEF9C3"
BOGOTA_GOLD = "#F59E0B"

TEXT_PRIMARY = "#1F2937"
TEXT_MUTED = "#6B7280"
SURFACE = "#FFFFFF"
BACKGROUND = "#FAF8F5"
BORDER = "#E5E7EB"

# Qualitative series for multi-line / scatter charts
BOGOTA_QUALITATIVE = [
    BOGOTA_RED,
    BOGOTA_YELLOW_DARK,
    BOGOTA_RED_DARK,
    BOGOTA_GOLD,
    "#E57373",
    "#FBBF24",
    "#991B1B",
    "#D97706",
]

# Plotly continuous scales
BOGOTA_SCALE_SEQUENTIAL = [
    [0.0, BOGOTA_YELLOW_LIGHT],
    [0.35, BOGOTA_YELLOW],
    [0.65, BOGOTA_GOLD],
    [1.0, BOGOTA_RED],
]

BOGOTA_SCALE_DIVERGING = [
    [0.0, BOGOTA_RED_DARK],
    [0.5, "#FAFAF9"],
    [1.0, BOGOTA_YELLOW_DARK],
]

BOGOTA_SCALE_HEATMAP = [
    [0.0, BOGOTA_RED_DARK],
    [0.25, BOGOTA_RED],
    [0.5, "#FAFAF9"],
    [0.75, BOGOTA_GOLD],
    [1.0, BOGOTA_YELLOW_DARK],
]

# Map indicator scales (red/yellow family)
MAP_SCALES = {
    "Desercion_Oficial": BOGOTA_SCALE_SEQUENTIAL,
    "Reprobacion_Oficial": BOGOTA_SCALE_SEQUENTIAL,
    "Aprobacion_Oficial": [[0, BOGOTA_YELLOW_LIGHT], [0.5, BOGOTA_GOLD], [1, "#166534"]],
    "Pct_Pobre": BOGOTA_SCALE_SEQUENTIAL,
    "Pct_Ing_Precarios": BOGOTA_SCALE_SEQUENTIAL,
    "Pct_Inseg_Alimentaria": BOGOTA_SCALE_SEQUENTIAL,
    "Pct_Estrato_Bajo": BOGOTA_SCALE_SEQUENTIAL,
    "Pct_Bajo_Acceso_Educ": BOGOTA_SCALE_SEQUENTIAL,
    "Pct_Desempleado": BOGOTA_SCALE_SEQUENTIAL,
}

# Default Plotly layout tweaks for consistency
CHART_LAYOUT = {
    "font": {"family": "Inter, Segoe UI, sans-serif", "color": TEXT_PRIMARY, "size": 12},
    "paper_bgcolor": SURFACE,
    "plot_bgcolor": SURFACE,
}
