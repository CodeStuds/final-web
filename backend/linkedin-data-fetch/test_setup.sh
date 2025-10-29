#!/bin/bash
# Test script to verify the setup

echo "==================================="
echo "LinkedIn Data Scraper - Setup Test"
echo "==================================="
echo ""

# Check Python
echo "1. Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✓ $PYTHON_VERSION"
else
    echo "   ✗ Python 3 not found. Please install Python 3.7+"
    exit 1
fi
echo ""

# Check required files
echo "2. Checking required files..."
FILES=("manifest.json" "popup.html" "popup.js" "content.js" "background.js" "turndown.min.js" "webhook_server.py" "requirements.txt")
ALL_PRESENT=true

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file missing"
        ALL_PRESENT=false
    fi
done
echo ""

# Check icon files
echo "3. Checking icon files..."
ICON_PRESENT=true
for size in 16 48 128; do
    if [ -f "icon${size}.png" ]; then
        echo "   ✓ icon${size}.png"
    else
        echo "   ⚠ icon${size}.png missing (not critical, but recommended)"
        ICON_PRESENT=false
    fi
done

if [ "$ICON_PRESENT" = false ]; then
    echo ""
    echo "   To create icons, run: ./create_icons.sh"
    echo "   Or see QUICKSTART.md for other options"
fi
echo ""

# Test Python dependencies
echo "4. Checking Python dependencies..."
if python3 -c "import flask" 2>/dev/null; then
    echo "   ✓ flask installed"
else
    echo "   ✗ flask not installed"
    echo "   Run: pip install -r requirements.txt"
fi

if python3 -c "import flask_cors" 2>/dev/null; then
    echo "   ✓ flask-cors installed"
else
    echo "   ✗ flask-cors not installed"
    echo "   Run: pip install -r requirements.txt"
fi
echo ""

# Summary
echo "==================================="
echo "Setup Summary"
echo "==================================="
if [ "$ALL_PRESENT" = true ]; then
    echo "✓ All required files present"
else
    echo "✗ Some required files are missing"
fi

echo ""
echo "Next steps:"
echo "1. Create icon files if missing (see QUICKSTART.md)"
echo "2. Install Python dependencies: pip install -r requirements.txt"
echo "3. Load the extension in your browser"
echo "4. Start the webhook server: python3 webhook_server.py"
echo ""
echo "See QUICKSTART.md for detailed instructions!"
