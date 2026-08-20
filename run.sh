#!/usr/bin/env bash
# =============================================================================
# DataJam — full project setup and dashboard launcher (Linux / macOS)
# =============================================================================
# Runs, in order:
#   1. Activate Python environment (conda env "p" or local .venv)
#   2. Install dependencies from requirements.txt
#   3. Download datasets from Bogotá open-data portal
#   4. Run consolidated analysis (generates output/ including conclusions)
#   5. Start the Dash dashboard at http://127.0.0.1:8050
#
# Usage:
#   chmod +x run.sh
#   ./run.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

info()  { echo "[INFO]  $*"; }
error() { echo "[ERROR] $*" >&2; }
die()   { error "$*"; exit 1; }

run_step() {
  local label="$1"
  shift
  info "$label"
  if ! "$@"; then
    die "Step failed: $label"
  fi
}

# -----------------------------------------------------------------------------
# Python environment: prefer conda env "p", then .venv, then create .venv
# -----------------------------------------------------------------------------
activate_python() {
  if command -v conda >/dev/null 2>&1; then
    # shellcheck disable=SC1091
    eval "$(conda shell.bash hook 2>/dev/null)" || true
    if conda env list | awk '{print $1}' | grep -qx "p"; then
      conda activate p
      info "Using conda environment: p"
      return 0
    fi
    info 'Conda found but env "p" is missing; trying .venv fallback'
  fi

  if [[ -d ".venv" ]]; then
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
    info "Using virtual environment: .venv"
    return 0
  fi

  if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    return 1
  fi

  local py_cmd="python3"
  if ! command -v python3 >/dev/null 2>&1; then
    py_cmd="python"
  fi

  info "Creating local virtual environment (.venv)"
  "$py_cmd" -m venv .venv
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
  info "Using newly created virtual environment: .venv"
  return 0
}

if ! activate_python; then
  die "No usable Python found. Install Python 3, create conda env \"p\", or ensure python3 is on PATH."
fi

PYTHON="$(command -v python)"
info "Python executable: $PYTHON ($("$PYTHON" --version 2>&1))"

# -----------------------------------------------------------------------------
# Project pipeline (matches README quick-start order)
# -----------------------------------------------------------------------------
run_step "Installing dependencies" "$PYTHON" -m pip install --upgrade pip
run_step "Installing requirements.txt" "$PYTHON" -m pip install -r requirements.txt
run_step "Downloading datasets" "$PYTHON" scripts/descargar_datos.py
run_step "Running consolidated analysis" "$PYTHON" analisis_final.py

info "Starting dashboard — open http://127.0.0.1:8050 (Ctrl+C to stop)"
exec "$PYTHON" dashboard/app.py
