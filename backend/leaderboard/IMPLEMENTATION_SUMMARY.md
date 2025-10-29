# 🎉 HireSight Leaderboard System - Implementation Complete!

## ✅ What Was Built

A comprehensive leaderboard system that combines LinkedIn resume matching scores and GitHub profile analysis scores to create a unified ranking of the most compatible candidates.

## 📁 Created Files

```
backend/leaderboard/
├── main.py                 # Main entry point with CLI
├── config.py               # Configuration settings
├── utils.py                # Utility functions for normalization and matching
├── data_loader.py          # Loads and merges data from both sources
├── leaderboard.py          # Calculates scores and generates rankings
├── output_generator.py     # Generates JSON, CSV, and Markdown reports
├── example.py              # Usage examples and demonstrations
├── run.sh                  # Quick start shell script
├── requirements.txt        # Python dependencies
├── README.md               # Complete documentation
├── QUICKSTART.md           # 5-minute setup guide
├── PROJECT_OVERVIEW.md     # Technical architecture document
└── .gitignore              # Git ignore patterns
```

## 🎯 Key Features

✅ **Score Normalization**
- Converts LinkedIn scores (0-1) and GitHub scores (0-100) to common scale
- Handles missing scores gracefully

✅ **Weighted Averaging**
- Configurable weights for LinkedIn and GitHub scores
- Default: 50/50 split, customizable via command line

✅ **Intelligent Ranking**
- Sorts candidates by combined score
- Classifies into 6 tiers (Excellent to Low Match)
- Provides detailed statistics

✅ **Multiple Output Formats**
- **JSON**: Structured data for APIs
- **CSV**: Spreadsheet-compatible
- **Markdown**: Human-readable reports

✅ **Flexible Configuration**
- Custom weights (--linkedin-weight, --github-weight)
- Minimum score filtering (--min-score)
- Top N display (--top)
- Custom data paths

## 🚀 Quick Start

### 1. Run with default settings:
```bash
cd backend/leaderboard
./run.sh
```

### 2. Or use Python directly:
```bash
python main.py
```

### 3. Customize weights:
```bash
python main.py --linkedin-weight 0.6 --github-weight 0.4
```

### 4. Filter by score:
```bash
python main.py --min-score 0.7 --top 20
```

## 📊 Example Output

```
🏆 CANDIDATE LEADERBOARD - TOP COMPATIBLE CANDIDATES
================================================================================

📊 Statistics:
   Total Candidates: 15
   Average Score: 67.34%
   Median Score: 65.20%
   Score Range: 42.15% - 89.67%

⚖️  Weights:
   LinkedIn: 50%
   GitHub: 50%

🥇 Top 10 Candidates:
--------------------------------------------------------------------------------
Rank   Name                      Combined     LinkedIn     GitHub       Tier      
--------------------------------------------------------------------------------
🥇 1   Alice Johnson             89.67%       87.50%       91.83%       Excellent Match
🥈 2   Bob Smith                 83.45%       79.20%       87.70%       Very Good Match
🥉 3   Carol Davis               78.92%       82.10%       75.74%       Very Good Match
```

## 📋 How It Works

1. **Loads LinkedIn scores** from `../ibhanwork/results.csv`
2. **Loads GitHub scores** from `../github-data-fetch/reports/*.json`
3. **Normalizes scores** to 0-1 scale
4. **Calculates weighted average** based on configurable weights
5. **Ranks candidates** by combined score
6. **Classifies into tiers** (Excellent, Very Good, Good, etc.)
7. **Generates reports** in JSON, CSV, and Markdown formats

## 🎛️ Configuration Examples

### Equal Weight (Default)
```bash
python main.py
# LinkedIn: 50%, GitHub: 50%
```

### GitHub-Heavy (for technical roles)
```bash
python main.py --linkedin-weight 0.3 --github-weight 0.7
# LinkedIn: 30%, GitHub: 70%
```

### LinkedIn-Heavy (for experience-focused roles)
```bash
python main.py --linkedin-weight 0.7 --github-weight 0.3
# LinkedIn: 70%, GitHub: 30%
```

### High-Scoring Candidates Only
```bash
python main.py --min-score 0.75
# Only candidates scoring ≥75%
```

## 📁 Output Files

Generated in `output/` directory:

1. **leaderboard.json** - Structured data with all details
2. **leaderboard.csv** - Spreadsheet format
3. **leaderboard.md** - Formatted report with tables

## 🔧 Prerequisites

Before running the leaderboard, ensure you have:

1. **LinkedIn data**: Run the resume matcher
   ```bash
   cd ../ibhanwork
   python scorematcher.py
   ```

2. **GitHub data**: Run profile analysis for each candidate
   ```bash
   cd ../github-data-fetch
   python main.py <username>
   ```

## 💡 Use Cases

### Scenario 1: Initial Screening
Quickly identify top candidates:
```bash
python main.py --min-score 0.6 --top 20
```

### Scenario 2: Technical Role Hiring
Prioritize coding skills:
```bash
python main.py --github-weight 0.7 --linkedin-weight 0.3
```

### Scenario 3: Comprehensive Review
Generate full report:
```bash
python main.py --top 50
```

## 📚 Documentation

- **README.md**: Complete reference guide
- **QUICKSTART.md**: 5-minute setup guide
- **PROJECT_OVERVIEW.md**: Technical architecture
- **example.py**: Code examples

## 🎓 Score Tier Guide

| Tier | Score Range | Meaning | Icon |
|------|-------------|---------|------|
| Excellent Match | 85-100% | Top candidates, highly compatible | 🥇 |
| Very Good Match | 75-84% | Strong candidates, good fit | 🥈 |
| Good Match | 65-74% | Solid candidates, worth considering | 🥉 |
| Moderate Match | 50-64% | Decent fit, may need development | ✅ |
| Fair Match | 35-49% | Partial fit, significant gaps | ⚠️ |
| Low Match | 0-34% | Poor fit, not recommended | ❌ |

## 🛠️ Troubleshooting

### "No candidate data found"
- Ensure `../ibhanwork/results.csv` exists
- Ensure `../github-data-fetch/reports/*.json` files exist

### "No candidates meet minimum score"
- Lower the `--min-score` parameter
- Check if data was loaded correctly

### Permission denied on run.sh
```bash
chmod +x run.sh
./run.sh
```

## 🎉 Success!

Your leaderboard system is ready to use! It will:
- ✅ Combine LinkedIn and GitHub scores
- ✅ Normalize to 0-1 scale
- ✅ Calculate weighted averages
- ✅ Rank all candidates
- ✅ Generate multiple report formats
- ✅ Provide actionable insights

## 📞 Next Steps

1. **Test the system**: Run `./run.sh` or `python main.py`
2. **Review outputs**: Check the `output/` directory
3. **Adjust weights**: Experiment with different weight configurations
4. **Integrate**: Use the JSON/CSV outputs in your hiring pipeline

---

**Built with ❤️ for HireSight - Making candidate evaluation fair and comprehensive**
