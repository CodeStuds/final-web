# HireSight Leaderboard - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Ensure Prerequisites

You need data from both scoring systems:

1. **LinkedIn Resume Scores** - Run the resume matcher:
   ```bash
   cd ../ibhanwork
   python scorematcher.py
   ```
   This generates `results.csv` with candidate scores.

2. **GitHub Profile Scores** - Run the GitHub analyzer for each candidate:
   ```bash
   cd ../github-data-fetch
   python main.py <github-username>
   ```
   This generates `analysis_<username>.json` files in `reports/`.

### Step 2: Run the Leaderboard

```bash
cd backend/leaderboard
./run.sh
```

Or manually:
```bash
python main.py
```

### Step 3: View Results

Check the `output/` directory for:
- `leaderboard.json` - Structured data
- `leaderboard.csv` - Spreadsheet format
- `leaderboard.md` - Formatted report

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
✅ 4   David Brown               72.15%       68.50%       75.80%       Good Match
✅ 5   Emma Wilson               69.83%       73.20%       66.46%       Good Match
...
```

## 🎛️ Common Customizations

### Adjust Score Weights

Prioritize GitHub scores (70%) over LinkedIn (30%):
```bash
python main.py --linkedin-weight 0.3 --github-weight 0.7
```

### Filter Low Scores

Only show candidates scoring 60% or higher:
```bash
python main.py --min-score 0.6
```

### Show More Candidates

Display top 20 instead of 10:
```bash
python main.py --top 20
```

## 🔧 Troubleshooting

### "No candidate data found"
- Ensure LinkedIn `results.csv` exists in `../ibhanwork/`
- Ensure GitHub `analysis_*.json` files exist in `../github-data-fetch/reports/`

### "No candidates meet the minimum score threshold"
- Lower the `--min-score` parameter
- Check if data was loaded correctly
- Verify score values in source files

### Permission Denied
```bash
chmod +x run.sh
./run.sh
```

## 📚 Next Steps

1. Review the generated reports in `output/`
2. Adjust weights based on your hiring priorities
3. Use the leaderboard to shortlist candidates
4. Integrate with your hiring pipeline

## 💡 Pro Tips

- **Equal weights (50/50)**: Best for balanced evaluation
- **GitHub-heavy (70/30)**: For technical roles emphasizing coding skills
- **LinkedIn-heavy (70/30)**: For roles emphasizing experience/resume fit
- **Custom thresholds**: Use `--min-score` to filter out low matches early

---

Need help? Check the full README.md for detailed documentation.
