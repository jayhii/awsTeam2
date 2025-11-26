# PowerShell script to set up Python virtual environment
# HR Resource Optimization System - Development Environment Setup

Write-Host "Setting up Python virtual environment..." -ForegroundColor Green

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Display Python version
$pythonVersion = python --version
Write-Host "Using $pythonVersion" -ForegroundColor Cyan

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install development dependencies
Write-Host "Installing development dependencies..." -ForegroundColor Yellow
pip install -r requirements-dev.txt

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "Virtual environment is activated." -ForegroundColor Green
Write-Host "`nTo activate the environment in the future, run:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "`nTo deactivate, run:" -ForegroundColor Cyan
Write-Host "  deactivate" -ForegroundColor White
