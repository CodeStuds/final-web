#!/bin/bash
# HireSight Installation Verification Script

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║              HireSight Installation Check                    ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
python3 --version 2>/dev/null
if [ $? -eq 0 ]; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "   ✅ Python found: $PYTHON_VERSION"
else
    echo "   ❌ Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

# Check if requirements.txt exists
echo ""
echo "2️⃣  Checking requirements.txt..."
if [ -f "requirements.txt" ]; then
    echo "   ✅ requirements.txt found"
else
    echo "   ❌ requirements.txt not found. Are you in the correct directory?"
    exit 1
fi

# Check if pip is available
echo ""
echo "3️⃣  Checking pip..."
pip3 --version 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ pip found"
else
    echo "   ❌ pip not found. Please install pip."
    exit 1
fi

# Attempt to install dependencies
echo ""
echo "4️⃣  Installing dependencies..."
pip3 install -r requirements.txt -q
if [ $? -eq 0 ]; then
    echo "   ✅ Dependencies installed successfully"
else
    echo "   ⚠️  Some dependencies may have failed to install"
    echo "   Try manually: pip3 install -r requirements.txt"
fi

# Download TextBlob corpora
echo ""
echo "5️⃣  Downloading TextBlob corpora..."
python3 -m textblob.download_corpora 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ TextBlob corpora downloaded"
else
    echo "   ⚠️  TextBlob corpora download may have failed"
    echo "   Try manually: python3 -m textblob.download_corpora"
fi

# Check for GitHub token
echo ""
echo "6️⃣  Checking for GitHub token..."
if [ -z "$GITHUB_TOKEN" ]; then
    echo "   ⚠️  GITHUB_TOKEN environment variable not set"
    echo "   The tool will work but with limited rate limits (60 requests/hour)"
    echo ""
    echo "   To set it:"
    echo "   export GITHUB_TOKEN='your_token_here'"
    echo ""
else
    echo "   ✅ GITHUB_TOKEN is set"
fi

# Test imports
echo ""
echo "7️⃣  Testing module imports..."
python3 -c "
import sys
try:
    from github import Github
    from textblob import TextBlob
    import pandas
    import numpy
    print('   ✅ All modules import successfully')
    sys.exit(0)
except ImportError as e:
    print(f'   ❌ Import error: {e}')
    print('   Try: pip3 install -r requirements.txt')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Run example script
echo ""
echo "8️⃣  Running example script..."
python3 example.py
if [ $? -eq 0 ]; then
    echo "   ✅ Example script completed successfully"
else
    echo "   ❌ Example script failed"
    exit 1
fi

# Final summary
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║               ✅ INSTALLATION COMPLETE ✅                     ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 HireSight is ready to use!"
echo ""
echo "Try it out:"
echo "  python3 main.py octocat"
echo ""
echo "Or with a real username:"
echo "  python3 main.py <github-username>"
echo ""
echo "For more information:"
echo "  cat README.md"
echo "  cat QUICKSTART.md"
echo ""
