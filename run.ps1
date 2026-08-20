# =============================================================================
# DataJam — full project setup and dashboard launcher (Windows / PowerShell)
# =============================================================================
# Runs, in order:
#   1. Activate Python environment (conda env "p" or local .venv)
#   2. Install dependencies from requirements.txt
#   3. Download datasets from Bogotá open-data portal
#   4. Run consolidated analysis (generates output/ including conclusions)
#   5. Start the Dash dashboard at http://127.0.0.1:8050
#
# Usage:
#   .\run.ps1
# =============================================================================

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

function Write-Info([string]$Message) {
    Write-Host "[INFO]  $Message" -ForegroundColor Cyan
}

function Write-Err([string]$Message) {
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Invoke-ProjectStep {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )

    Write-Info $Label
    try {
        & $Action
    }
    catch {
        Write-Err "Step failed: $Label"
        Write-Err $_.Exception.Message
        exit 1
    }

    if ($LASTEXITCODE -ne $null -and $LASTEXITCODE -ne 0) {
        Write-Err "Step failed: $Label (exit code $LASTEXITCODE)"
        exit $LASTEXITCODE
    }
}

function Test-CondaEnvExists {
    param([string]$EnvName)

    if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
        return $false
    }

    $envList = & conda env list 2>$null
    if ($LASTEXITCODE -ne 0) {
        return $false
    }

    foreach ($line in $envList) {
        if ($line -match "^\s*$([regex]::Escape($EnvName))\s") {
            return $true
        }
    }

    return $false
}

function Initialize-PythonEnvironment {
    if (Test-CondaEnvExists -EnvName "p") {
        Write-Info 'Using conda environment: p'
        # conda run avoids relying on conda hook initialization in PowerShell
        return @{
            Mode   = "conda-run"
            Python = @("conda", "run", "--no-capture-output", "-n", "p", "python")
        }
    }

    $venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        Write-Info "Using virtual environment: .venv"
        return @{
            Mode   = "venv"
            Python = @($venvPython)
        }
    }

    $systemPython = Get-Command python -ErrorAction SilentlyContinue
    if (-not $systemPython) {
        Write-Err 'No Python found. Install Python 3, create conda env "p", or add python to PATH.'
        exit 1
    }

    Write-Info "Creating local virtual environment (.venv)"
    & python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Failed to create .venv"
        exit $LASTEXITCODE
    }

    if (-not (Test-Path $venvPython)) {
        Write-Err "Virtual environment was not created at $venvPython"
        exit 1
    }

    Write-Info "Using newly created virtual environment: .venv"
    return @{
        Mode   = "venv"
        Python = @($venvPython)
    }
}

function Invoke-Python {
    param(
        [Parameter(Mandatory = $true)][string[]]$PythonCommand,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
    )

    & $PythonCommand[0] @($PythonCommand[1..($PythonCommand.Count - 1)]) @Arguments
}

$pythonEnv = Initialize-PythonEnvironment
$pythonCmd = $pythonEnv.Python

try {
    $version = Invoke-Python -PythonCommand $pythonCmd -Arguments @("--version")
    Write-Info "Python executable: $($pythonCmd -join ' ') ($version)"
}
catch {
    Write-Err "Unable to run Python from selected environment."
    exit 1
}

# -----------------------------------------------------------------------------
# Project pipeline (matches README quick-start order)
# -----------------------------------------------------------------------------
Invoke-ProjectStep -Label "Installing dependencies" -Action {
    Invoke-Python -PythonCommand $pythonCmd -Arguments @("-m", "pip", "install", "--upgrade", "pip")
}

Invoke-ProjectStep -Label "Installing requirements.txt" -Action {
    Invoke-Python -PythonCommand $pythonCmd -Arguments @("-m", "pip", "install", "-r", "requirements.txt")
}

Invoke-ProjectStep -Label "Downloading datasets" -Action {
    Invoke-Python -PythonCommand $pythonCmd -Arguments @("scripts/descargar_datos.py")
}

Invoke-ProjectStep -Label "Running consolidated analysis" -Action {
    Invoke-Python -PythonCommand $pythonCmd -Arguments @("analisis_final.py")
}

Write-Info "Starting dashboard — open http://127.0.0.1:8050 (Ctrl+C to stop)"
Invoke-Python -PythonCommand $pythonCmd -Arguments @("dashboard/app.py")
