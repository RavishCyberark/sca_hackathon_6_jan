#!/bin/bash
set -e

echo "================================================"
echo "  AI Test Case Generator - Setup Script"
echo "================================================"
echo ""

# Check if Python 3.11 is installed
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 is not installed. Please install Python 3.11 first."
    exit 1
fi

PYTHON_VERSION=$(python3.11 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION found"

# Remove old virtual environment if exists
if [ -d ".venv" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf .venv
fi

if [ -d "venv" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment with Python 3.11..."
python3.11 -m venv .venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip and setuptools
echo "⬆️  Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers (chromium)..."
playwright install chromium

# Check Ollama
echo ""
echo "🔍 Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo "✅ Ollama server is running"
    else
        echo "⚠️  Ollama is installed but not running."
        echo "   Start it with: ollama serve"
    fi
    
    # Check for recommended model
    if ollama list 2>/dev/null | grep -q "qwen2.5-coder"; then
        echo "✅ qwen2.5-coder model is available"
    else
        echo "⚠️  qwen2.5-coder model not found."
        echo "   Pull it with: ollama pull qwen2.5-coder:7b"
    fi
else
    echo "⚠️  Ollama is not installed."
    echo "   Install with: brew install ollama"
    echo "   Then run: ollama serve && ollama pull qwen2.5-coder:7b"
fi

# Check GitHub CLI
echo ""
echo "🔍 Checking GitHub CLI installation..."
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI is installed"
    
    # Check authentication
    if gh auth status &> /dev/null; then
        echo "✅ GitHub CLI is authenticated"
    else
        echo "⚠️  GitHub CLI is not authenticated."
        echo "   Run: gh auth login"
    fi
else
    echo "⚠️  GitHub CLI is not installed."
    echo "   Install with: brew install gh"
    echo "   Then run: gh auth login"
fi

# Create output directory if not exists
mkdir -p output/generated_tests
touch output/generated_tests/.gitkeep

echo ""
echo "================================================"
echo "  ✅ Setup Complete!"
echo "================================================"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To generate tests, run:"
echo "  python -m src.main --input input/sample_scenarios.txt --output output/generated_tests/"
echo ""
echo "To generate tests AND create a PR, run:"
echo "  python -m src.main --input input/sample_scenarios.txt --push-pr"
echo ""

