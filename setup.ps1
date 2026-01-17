# =============================================================================
# NSA-X Project Setup Script (Windows PowerShell)
# =============================================================================
# Run this script to set up the complete development environment
# Usage: .\setup.ps1
# =============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NSA-X Development Environment Setup  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------------------------
# Prerequisites Check
# -----------------------------------------------------------------------------
Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Yellow

# Check Node.js
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Node.js not found. Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Red
    exit 1
}
Write-Host "  Node.js: $nodeVersion" -ForegroundColor Green

# Check Python
$pythonVersion = python --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Please install Python 3.11+ from https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "  Python: $pythonVersion" -ForegroundColor Green

# Check npm
$npmVersion = npm --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: npm not found." -ForegroundColor Red
    exit 1
}
Write-Host "  npm: $npmVersion" -ForegroundColor Green

Write-Host ""

# -----------------------------------------------------------------------------
# Frontend Setup
# -----------------------------------------------------------------------------
Write-Host "[2/6] Setting up frontend..." -ForegroundColor Yellow

# Copy .env.example to .env if not exists
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  Created .env from .env.example" -ForegroundColor Green
    }
}

# Install frontend dependencies
Write-Host "  Installing npm packages..." -ForegroundColor Gray
npm install --silent
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: npm install failed" -ForegroundColor Red
    exit 1
}
Write-Host "  Frontend dependencies installed" -ForegroundColor Green

Write-Host ""

# -----------------------------------------------------------------------------
# Backend Setup
# -----------------------------------------------------------------------------
Write-Host "[3/6] Setting up backend..." -ForegroundColor Yellow

Push-Location backend

# Create virtual environment if not exists
if (!(Test-Path "venv")) {
    Write-Host "  Creating Python virtual environment..." -ForegroundColor Gray
    python -m venv venv
}

# Activate virtual environment
Write-Host "  Activating virtual environment..." -ForegroundColor Gray
& .\venv\Scripts\Activate.ps1

# Install backend dependencies
Write-Host "  Installing Python packages..." -ForegroundColor Gray
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "  Backend dependencies installed" -ForegroundColor Green

# Copy .env.example to .env if not exists
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  Created backend .env from .env.example" -ForegroundColor Green
    }
}

Pop-Location

Write-Host ""

# -----------------------------------------------------------------------------
# Database Setup
# -----------------------------------------------------------------------------
Write-Host "[4/6] Setting up database..." -ForegroundColor Yellow

Push-Location backend
& .\venv\Scripts\Activate.ps1

# Run migrations (SQLite will be created automatically)
Write-Host "  Running database migrations..." -ForegroundColor Gray
alembic upgrade head 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Database migrations complete" -ForegroundColor Green
} else {
    Write-Host "  Note: Migrations may need manual setup (see backend/README.md)" -ForegroundColor Yellow
}

Pop-Location

Write-Host ""

# -----------------------------------------------------------------------------
# Verify Setup
# -----------------------------------------------------------------------------
Write-Host "[5/6] Verifying setup..." -ForegroundColor Yellow

# Check frontend build
Write-Host "  Checking frontend build..." -ForegroundColor Gray
npm run build --silent 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Frontend builds successfully" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Frontend build had issues" -ForegroundColor Yellow
}

Write-Host ""

# -----------------------------------------------------------------------------
# Success Message
# -----------------------------------------------------------------------------
Write-Host "[6/6] Setup complete!" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ready to start development!          " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor White
Write-Host ""
Write-Host "  Backend (Terminal 1):" -ForegroundColor Gray
Write-Host "    cd backend" -ForegroundColor White
Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "    uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "  Frontend (Terminal 2):" -ForegroundColor Gray
Write-Host "    npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "  Then open: http://localhost:8080" -ForegroundColor Cyan
Write-Host "  Login: admin / admin123" -ForegroundColor Cyan
Write-Host ""
