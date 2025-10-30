#!/bin/bash
# Quick setup and run script for HireSight Leaderboard

echo "🚀 HireSight Leaderboard - Quick Start"
echo "======================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if data files exist
echo "📋 Checking data availability..."

LINKEDIN_DATA="../ibhanwork/results.csv"
GITHUB_DATA="../github-data-fetch/reports"

if [ ! -f "$LINKEDIN_DATA" ]; then
    echo "⚠️  LinkedIn data not found at: $LINKEDIN_DATA"
    echo "   Please run the LinkedIn matching system first."
    LINKEDIN_MISSING=1
fi

if [ ! -d "$GITHUB_DATA" ]; then
    echo "⚠️  GitHub data directory not found at: $GITHUB_DATA"
    echo "   Please run the GitHub analysis system first."
    GITHUB_MISSING=1
fi

if [ "$LINKEDIN_MISSING" = "1" ] || [ "$GITHUB_MISSING" = "1" ]; then
    echo ""
    echo "❌ Missing required data. Cannot proceed."
    echo ""
    echo "Setup instructions:"
    echo "1. Run LinkedIn resume matching: cd ../ibhanwork && python scorematcher.py"
    echo "2. Run GitHub profile analysis: cd ../github-data-fetch && python main.py <username>"
    echo "3. Return here and run: ./run.sh"
    exit 1
fi

echo "✅ Data files found"
echo ""

# Create output directory
echo "📁 Creating output directory..."
mkdir -p output
echo "✅ Output directory ready"
echo ""

# Run the leaderboard
echo "🎯 Generating leaderboard..."
echo ""
python3 main.py "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✨ Success! Check the output/ directory for results."
else
    echo ""
    echo "❌ Leaderboard generation failed with exit code: $EXIT_CODE"
    exit $EXIT_CODE
fi
