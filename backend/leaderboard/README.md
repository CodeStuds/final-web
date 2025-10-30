# HireSight Leaderboard System

A comprehensive system that combines LinkedIn resume matching scores and GitHub profile analysis scores to create a unified leaderboard of the most compatible candidates.

## 🎯 Overview

The leaderboard system integrates two scoring systems:
- **LinkedIn Scoring** (from `ibhanwork`): Resume-job description similarity (0-1 scale)
- **GitHub Scoring** (from `github-data-fetch`): Comprehensive developer profile analysis (0-100 scale)

It normalizes both scores to a 0-1 scale and calculates a weighted average to rank candidates.

## 📋 Features

- ✅ Automatic data loading from both sources
- ✅ Score normalization and weighted averaging
- ✅ Configurable weights for LinkedIn and GitHub scores
- ✅ Multiple output formats (JSON, CSV, Markdown)
- ✅ Tier classification (Excellent, Very Good, Good, etc.)
- ✅ Comprehensive statistics and visualizations
- ✅ Minimum score threshold filtering

## 🚀 Quick Start

### Prerequisites

Ensure you have Python 3.7+ installed and the required dependencies:

```bash
pip install -r requirements.txt
```

### Data Requirements

1. **LinkedIn Data**: CSV file with candidate names and scores
   - Location: `../ibhanwork/results.csv`
   - Format: Columns: `Candidate`, `Score`

2. **GitHub Data**: JSON analysis files for candidates
   - Location: `../github-data-fetch/reports/`
   - Format: `analysis_USERNAME.json` files

### Basic Usage

Run with default settings (50/50 weight):
```bash
python main.py
```

## 📖 Usage Examples

### Custom Weights

Prioritize GitHub scores (60%) over LinkedIn scores (40%):
```bash
python main.py --linkedin-weight 0.4 --github-weight 0.6
```

### Filter by Minimum Score

Only show candidates with combined score >= 0.5:
```bash
python main.py --min-score 0.5
```

### Show More Candidates

Display top 20 candidates instead of default 10:
```bash
python main.py --top 20
```

### Custom Data Paths

Specify custom paths for data sources:
```bash
python main.py \
  --linkedin-path /path/to/results.csv \
  --github-path /path/to/reports/ \
  --output-dir ./my_output
```

### JSON Output Only

Generate only JSON output (skip CSV and Markdown):
```bash
python main.py --json-only
```

### Console Output Only

Display results in console without generating files:
```bash
python main.py --no-output
```

## 📊 Output Files

The system generates three types of output files in the `output/` directory:

### 1. JSON Output (`leaderboard.json`)
Structured data with detailed scores:
```json
{
  "generated_at": "2025-01-15T10:30:00",
  "total_candidates": 25,
  "candidates": [
    {
      "rank": 1,
      "name": "John Doe",
      "combined_score": 0.8542,
      "linkedin_score": 0.8123,
      "github_score": 0.8961,
      "tier": "Excellent Match"
    }
  ]
}
```

### 2. CSV Output (`leaderboard.csv`)
Spreadsheet-compatible format:
```csv
Rank,Name,Combined Score,LinkedIn Score,GitHub Score,Tier,GitHub Username
1,John Doe,0.854200,0.812300,0.896100,Excellent Match,johndoe
```

### 3. Markdown Report (`leaderboard.md`)
Formatted report with tables and statistics:
- Ranked candidate table
- Tier distribution
- Score statistics
- Visual indicators

## ⚙️ Configuration

Edit `config.py` to change default settings:

```python
# Score weights (default: equal weight)
LINKEDIN_WEIGHT = 0.5
GITHUB_WEIGHT = 0.5

# Display settings
TOP_CANDIDATES_DISPLAY = 10
MIN_SCORE_THRESHOLD = 0.0

# Data paths
LINKEDIN_DATA_PATH = "../ibhanwork/results.csv"
GITHUB_DATA_PATH = "../github-data-fetch/reports"
```

## 🎯 Tier Classification

Combined scores are classified into tiers:

| Tier | Score Range | Emoji |
|------|-------------|-------|
| Excellent Match | 0.85 - 1.00 | 🥇 |
| Very Good Match | 0.75 - 0.84 | 🥈 |
| Good Match | 0.65 - 0.74 | 🥉 |
| Moderate Match | 0.50 - 0.64 | ✅ |
| Fair Match | 0.35 - 0.49 | ⚠️ |
| Low Match | 0.00 - 0.34 | ❌ |

## 📈 Score Calculation

### Score Normalization

1. **LinkedIn Scores**: Already 0-1 (from cosine similarity)
2. **GitHub Scores**: Divided by 100 to convert from 0-100 to 0-1

### Combined Score Formula

```
combined_score = (linkedin_score × linkedin_weight + github_score × github_weight) / (linkedin_weight + github_weight)
```

With default weights (0.5 each):
```
combined_score = (linkedin_score + github_score) / 2
```

### Handling Missing Scores

- If only LinkedIn score available: Use LinkedIn score directly
- If only GitHub score available: Use GitHub score directly
- If both available: Calculate weighted average
- If neither available: Exclude from leaderboard

## 🔧 Module Structure

```
backend/leaderboard/
├── main.py              # Main entry point
├── config.py            # Configuration settings
├── utils.py             # Utility functions (normalization, matching)
├── data_loader.py       # Data loading from both sources
├── leaderboard.py       # Score calculation and ranking
├── output_generator.py  # Output file generation
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🐛 Troubleshooting

### No candidates found
- Check that data files exist at specified paths
- Verify CSV format has `Candidate` and `Score` columns
- Ensure GitHub JSON files follow `analysis_USERNAME.json` naming

### All scores are zero
- Verify LinkedIn CSV contains valid numeric scores
- Check GitHub JSON files contain `match_results.overall_score`
- Review data format in source files

### Permission errors
- Ensure read access to input directories
- Ensure write access to output directory
- Try running with appropriate permissions

## 📝 Command Line Options

```
usage: main.py [-h] [--linkedin-path LINKEDIN_PATH] 
               [--github-path GITHUB_PATH]
               [--output-dir OUTPUT_DIR]
               [--linkedin-weight LINKEDIN_WEIGHT]
               [--github-weight GITHUB_WEIGHT]
               [--min-score MIN_SCORE]
               [--top TOP]
               [--json-only]
               [--no-output]

Options:
  --linkedin-path PATH     Path to LinkedIn results CSV
  --github-path PATH       Path to GitHub reports directory
  --output-dir PATH        Output directory for generated files
  --linkedin-weight FLOAT  Weight for LinkedIn score (0-1)
  --github-weight FLOAT    Weight for GitHub score (0-1)
  --min-score FLOAT        Minimum combined score threshold
  --top N                  Number of top candidates to display
  --json-only              Generate only JSON output
  --no-output              Skip file generation (console only)
```

## 🤝 Integration

This system integrates with:
- **ibhanwork**: LinkedIn resume matching system
- **github-data-fetch**: GitHub profile analysis system

Ensure both systems have been run and generated their output files before running the leaderboard.

## 📄 License

Part of the HireSight project.

---

*Generated by HireSight Leaderboard System*
