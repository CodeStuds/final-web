# HireSight Leaderboard - Project Overview

## 🎯 Purpose

The HireSight Leaderboard system is a unified candidate ranking platform that combines scores from two independent assessment systems:
- **LinkedIn Resume Matching** (text similarity analysis)
- **GitHub Profile Analysis** (comprehensive developer evaluation)

By normalizing and combining these scores, it provides a holistic view of candidate compatibility.

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    LEADERBOARD SYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                │
│  │   LinkedIn   │         │   GitHub     │                │
│  │   Scores     │         │   Scores     │                │
│  │  (0-1 scale) │         │ (0-100 scale)│                │
│  └──────┬───────┘         └──────┬───────┘                │
│         │                        │                         │
│         └────────┬───────────────┘                         │
│                  ▼                                          │
│         ┌─────────────────┐                                │
│         │  Data Loader    │                                │
│         │  - Normalize    │                                │
│         │  - Merge        │                                │
│         └────────┬────────┘                                │
│                  ▼                                          │
│         ┌─────────────────┐                                │
│         │  Leaderboard    │                                │
│         │  Generator      │                                │
│         │  - Calculate    │                                │
│         │  - Rank         │                                │
│         │  - Classify     │                                │
│         └────────┬────────┘                                │
│                  ▼                                          │
│         ┌─────────────────┐                                │
│         │  Output         │                                │
│         │  Generator      │                                │
│         │  - JSON         │                                │
│         │  - CSV          │                                │
│         │  - Markdown     │                                │
│         └─────────────────┘                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Module Breakdown

1. **config.py**
   - Configuration constants
   - Default paths and weights
   - Display settings

2. **utils.py**
   - Score normalization functions
   - Name matching utilities
   - Formatting helpers
   - Tier classification

3. **data_loader.py**
   - Loads LinkedIn CSV data
   - Loads GitHub JSON reports
   - Merges candidate data by name matching
   - Handles missing scores

4. **leaderboard.py**
   - Calculates weighted combined scores
   - Ranks candidates
   - Classifies into tiers
   - Generates statistics

5. **output_generator.py**
   - Generates JSON output
   - Generates CSV output
   - Generates Markdown reports
   - Formats data for display

6. **main.py**
   - Command-line interface
   - Argument parsing
   - Orchestrates the pipeline
   - Error handling

## 📊 Data Flow

### Input Data

**LinkedIn Data (CSV)**
```csv
Candidate,Score
John Doe,0.8542
Jane Smith,0.7321
```

**GitHub Data (JSON)**
```json
{
  "analysis": {
    "profile": {
      "name": "John Doe",
      "username": "johndoe"
    }
  },
  "match_results": {
    "overall_score": 87.50
  }
}
```

### Processing Pipeline

1. **Load**: Read data from both sources
2. **Normalize**: Convert GitHub scores from 0-100 to 0-1
3. **Merge**: Match candidates by name
4. **Calculate**: Apply weighted average formula
5. **Rank**: Sort by combined score
6. **Classify**: Assign tier based on score
7. **Output**: Generate reports in multiple formats

### Output Data

**JSON Output**
```json
{
  "generated_at": "2025-10-29T10:30:00",
  "total_candidates": 25,
  "candidates": [
    {
      "rank": 1,
      "name": "John Doe",
      "combined_score": 0.8671,
      "linkedin_score": 0.8542,
      "github_score": 0.8800,
      "tier": "Excellent Match"
    }
  ]
}
```

## 🔢 Score Calculation

### Normalization

**LinkedIn**: Already 0-1 (cosine similarity)
```python
normalized = score  # No change needed
```

**GitHub**: Convert from 0-100 to 0-1
```python
normalized = score / 100.0
```

### Combined Score

```python
combined = (linkedin_score × linkedin_weight + 
           github_score × github_weight) / 
           (linkedin_weight + github_weight)
```

With default weights (0.5 each):
```python
combined = (linkedin_score + github_score) / 2
```

### Tier Classification

| Score Range | Tier              | Icon |
|-------------|-------------------|------|
| 0.85 - 1.00 | Excellent Match   | 🥇   |
| 0.75 - 0.84 | Very Good Match   | 🥈   |
| 0.65 - 0.74 | Good Match        | 🥉   |
| 0.50 - 0.64 | Moderate Match    | ✅   |
| 0.35 - 0.49 | Fair Match        | ⚠️   |
| 0.00 - 0.34 | Low Match         | ❌   |

## 🎛️ Configuration Options

### Weights

Adjust the importance of each scoring system:
- **Equal (50/50)**: Balanced evaluation
- **GitHub-heavy (70/30)**: Technical skills focus
- **LinkedIn-heavy (70/30)**: Experience/resume focus

### Thresholds

- **Minimum Score**: Filter out low-scoring candidates
- **Top N Display**: Limit console output to top candidates

### Paths

- **LinkedIn Path**: Location of resume matching results
- **GitHub Path**: Directory containing analysis reports
- **Output Path**: Where to save generated reports

## 🔄 Integration Points

### Input Integration

**From ibhanwork (LinkedIn)**
- Expects: `results.csv` with Candidate and Score columns
- Format: CSV with UTF-8 encoding
- Scores: 0-1 scale (cosine similarity)

**From github-data-fetch**
- Expects: `analysis_USERNAME.json` files
- Format: JSON with nested structure
- Scores: 0-100 scale (match percentage)

### Output Integration

Generated files can be consumed by:
- Web dashboards (JSON API)
- Spreadsheet applications (CSV)
- Documentation systems (Markdown)
- Recruiting platforms (via API integration)

## 🚀 Usage Scenarios

### Scenario 1: Initial Screening
```bash
python main.py --min-score 0.6 --top 20
```
Quickly identify top 20 candidates scoring >60%

### Scenario 2: Technical Role
```bash
python main.py --github-weight 0.7 --linkedin-weight 0.3
```
Prioritize coding skills and GitHub activity

### Scenario 3: Experience-Focused Role
```bash
python main.py --linkedin-weight 0.7 --github-weight 0.3
```
Prioritize resume match and experience

### Scenario 4: Comprehensive Review
```bash
python main.py --top 50 --min-score 0.4
```
Generate full leaderboard for detailed review

## 📈 Performance Considerations

- **Data Loading**: O(n) for n candidates
- **Score Calculation**: O(n) for n candidates
- **Sorting**: O(n log n) for n candidates
- **Memory**: Minimal - all data structures fit in RAM

Typical performance:
- 100 candidates: < 1 second
- 1000 candidates: < 5 seconds
- 10000 candidates: < 30 seconds

## 🧪 Testing Strategy

### Unit Tests (To Be Added)
- Score normalization accuracy
- Weight calculation correctness
- Name matching fuzzy logic
- Tier classification boundaries

### Integration Tests (To Be Added)
- End-to-end pipeline
- File I/O operations
- Error handling
- Edge cases (missing data, invalid formats)

## 🔮 Future Enhancements

### Potential Features
1. **Web Dashboard**: Interactive UI for exploring results
2. **Real-time Updates**: Watch for new data and auto-refresh
3. **Advanced Matching**: Machine learning-based name matching
4. **Visualizations**: Charts and graphs for score distributions
5. **Export Options**: PDF reports, Excel files
6. **API Server**: REST API for programmatic access
7. **Database Integration**: Store historical leaderboards
8. **Notifications**: Alert when high-scoring candidates are found

### Planned Improvements
- Add comprehensive unit tests
- Implement caching for repeated runs
- Add progress bars for large datasets
- Support for additional data sources
- Customizable tier thresholds
- Multi-job leaderboards

## 📝 Best Practices

### For Users
1. Run both source systems first
2. Verify data quality before running leaderboard
3. Experiment with different weights
4. Use appropriate minimum score thresholds
5. Review tier distributions for reasonableness

### For Developers
1. Keep modules loosely coupled
2. Use dataclasses for structured data
3. Validate inputs early
4. Provide clear error messages
5. Log important operations
6. Document configuration options

## 🤝 Contributing

To extend this system:
1. Add new data sources in `data_loader.py`
2. Implement custom scoring in `leaderboard.py`
3. Add output formats in `output_generator.py`
4. Update configuration in `config.py`
5. Add command-line options in `main.py`

## 📄 License

Part of the HireSight project for comprehensive candidate evaluation.

---

*Last Updated: 2025-10-29*
