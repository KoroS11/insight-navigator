#!/bin/bash
# =============================================================================
# NSA-X Project Setup Script (Linux/macOS)
# =============================================================================
# Run this script to set up the complete development environment
# Usage: chmod +x setup.sh && ./setup.sh
# =============================================================================

set -e

echo "========================================"
echo "  NSA-X Development Environment Setup  "
echo "========================================"
echo ""

# -----------------------------------------------------------------------------
# Prerequisites Check
# -----------------------------------------------------------------------------
echo "[1/6] Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi
echo "  Node.js: $(node --version)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found. Please install Python 3.11+"
    exit 1
fi
echo "  Python: $(python3 --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm not found."
    exit 1
fi
echo "  npm: $(npm --version)"

echo ""

# -----------------------------------------------------------------------------
# Frontend Setup
# -----------------------------------------------------------------------------
echo "[2/6] Setting up frontend..."

# Copy .env.example to .env if not exists
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "  Created .env from .env.example"
fi

# Install frontend dependencies
echo "  Installing npm packages..."
npm install --silent
echo "  Frontend dependencies installed"

echo ""

# -----------------------------------------------------------------------------
# Backend Setup
# -----------------------------------------------------------------------------
echo "[3/6] Setting up backend..."

cd backend

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "  Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "  Installing Python packages..."
pip install -r requirements.txt --quiet
echo "  Backend dependencies installed"

# Copy .env.example to .env if not exists
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "  Created backend .env from .env.example"
fi

cd ..

echo ""

# -----------------------------------------------------------------------------
# Database Setup
# -----------------------------------------------------------------------------
echo "[4/6] Setting up database..."

cd backend
source venv/bin/activate

# Run migrations (SQLite will be created automatically)
echo "  Running database migrations..."
if alembic upgrade head 2>/dev/null; then
    echo "  Database migrations complete"
else
    echo "  Note: Migrations may need manual setup (see backend/README.md)"
fi

cd ..

echo ""

# -----------------------------------------------------------------------------
# Verify Setup
# -----------------------------------------------------------------------------
echo "[5/6] Verifying setup..."

# Check frontend build
echo "  Checking frontend build..."
if npm run build --silent 2>/dev/null; then
    echo "  Frontend builds successfully"
else
    echo "  WARNING: Frontend build had issues"
fi

echo ""

# -----------------------------------------------------------------------------
# Success Message
# -----------------------------------------------------------------------------
echo "[6/6] Setup complete!"
echo ""
echo "========================================"
echo "  Ready to start development!          "
echo "========================================"
echo ""
echo "To start the application:"
echo ""
echo "  Backend (Terminal 1):"
echo "    cd backend"
echo "    source venv/bin/activate"
echo "    uvicorn app.main:app --reload"
echo ""
echo "  Frontend (Terminal 2):"
echo "    npm run dev"
echo ""
echo "  Then open: http://localhost:8080"
echo "  Login: admin / admin123"
echo ""
