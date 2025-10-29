# HireSight 🎯

**Comprehensive GitHub Profile Analysis for Developer Hiring**

HireSight is a sophisticated, production-ready tool that performs deep analysis of GitHub profiles to evaluate technical candidates. It goes far beyond simple resume parsing, using real behavioral signals, code patterns, and contribution history to assess skills, work style, code quality, and growth potential.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

### Comprehensive Analysis Pipeline

- **Profile Metadata Extraction**: Account age, followers, repository overview, and social signals
- **Deep Repository Analysis**: Analyzes top 10 most active repositories with:
  - Language detection (GitHub stats + file analysis)
  - Framework & tool identification (100+ dependencies mapped)
  - Package file parsing (package.json, requirements.txt, go.mod, Cargo.toml, etc.)
  - CI/CD detection (GitHub Actions, GitLab CI, Jenkins, etc.)

- **Contribution Pattern Analysis**:
  - Commit frequency and consistency scoring
  - Conventional commit usage detection
  - Pull request activity and merge rates
  - Code review behavior and sentiment analysis

- **Skill Confidence Scoring** (0-100):
  - Evidence-weighted scoring (lines of code, repo count, recency, complexity)
  - Automatic categorization (Languages, Frameworks, Tools, Databases, DevOps)
  - Last-used tracking for each skill

- **Work Style Classification**:
  - Solo Developer
  - Collaborative
  - Mentorship
  - Async-Friendly

- **Code Quality Assessment**:
  - Documentation quality (README, descriptions, licenses)
  - Testing practices (frameworks, CI/CD)
  - Maintenance score (activity, age, originality)
  - Overall quality tier classification

- **Learning Trajectory Analysis**:
  - Skill acquisition patterns
  - Technology diversification
  - Learning velocity calculation
  - Growth potential assessment

### Four-Factor Matching Algorithm

1. **Current Fit (40%)**: Direct skill overlap with job requirements
2. **Growth Potential (30%)**: Learning ability and adaptability
3. **Collaboration Fit (20%)**: Work style and team dynamics compatibility
4. **Code Quality (10%)**: Standards and best practices

### Bias Detection & Fairness

Automatically identifies potential biases in job requirements:
- Education bias (degree requirements)
- Geographic bias (location restrictions)
- Experience bias (arbitrary years of experience)
- Problematic keywords ("ninja", "rockstar", etc.)

### Rich Output Formats

- **JSON**: Comprehensive machine-readable data
- **Markdown**: Beautiful, human-readable reports
- **Console**: Quick summary with key metrics

## 📋 Requirements

- Python 3.10 or higher
- GitHub Personal Access Token (optional but recommended)
- Internet connection

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd github-data-fetch

# Install dependencies
pip install -r requirements.txt

# Download TextBlob corpora (required for sentiment analysis)
python -m textblob.download_corpora
```

### 2. Set Up GitHub Token (Recommended)

To avoid API rate limits (60 requests/hour without token vs 5000/hour with token):

```bash
# Linux/Mac
export GITHUB_TOKEN="your_github_personal_access_token"

# Windows (Command Prompt)
set GITHUB_TOKEN=your_github_personal_access_token

# Windows (PowerShell)
$env:GITHUB_TOKEN="your_github_personal_access_token"
```

**How to create a GitHub Personal Access Token:**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "HireSight Analysis")
4. Select scopes: `public_repo`, `read:user`
5. Click "Generate token"
6. Copy the token and set it as an environment variable

### 3. Run Analysis

```bash
# Basic usage with GitHub username
python main.py octocat

# Or with full GitHub URL
python main.py https://github.com/torvalds

# With custom job requirements
python main.py username --job-title "Backend Developer" \
    --required-skills "Python,Django,PostgreSQL,Docker" \
    --preferred-skills "AWS,Redis,GraphQL"

# With work style preference
python main.py username --work-style collaborative

# Specify output directory
python main.py username --output-dir ./reports

# Analyze more repositories
python main.py username --top-repos 15

# Disable caching (always fetch fresh data)
python main.py username --no-cache

# Generate only JSON output
python main.py username --json-only
```

## 📊 Output Files

After running the analysis, you'll get:

1. **`analysis_username.json`**: Complete analysis data in JSON format
   - Profile metadata
   - Skill inventory with confidence scores
   - Contribution patterns
   - Work style classification
   - Code quality metrics
   - Matching results
   - Bias analysis

2. **`report_username.md`**: Human-readable Markdown report including:
   - Executive summary
   - Detailed skill breakdown
   - Match analysis with component scores
   - Growth potential assessment
   - Work style indicators
   - Contribution statistics
   - Code quality evaluation
   - Hiring recommendations
   - Suggested interview questions
   - Bias detection results

## 📁 Project Structure

```
github-data-fetch/
├── main.py                 # Entry point and CLI
├── data_fetcher.py         # GitHub API interactions
├── analyzer.py             # Core analysis logic
├── matcher.py              # Matching algorithm & bias detection
├── output_generator.py     # Report generation
├── utils.py                # Helper functions
├── config.py               # Configuration and mappings
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Customizing Job Requirements

You can customize job requirements via command-line arguments or by modifying `config.py`:

```python
DEFAULT_JOB_REQUIREMENTS = {
    'title': 'Your Job Title',
    'required_skills': ['Skill1', 'Skill2', 'Skill3'],
    'preferred_skills': ['Skill4', 'Skill5'],
    'experience_level': 'mid',  # junior, mid, senior
    'team_size': 'medium',       # solo, small, medium, large
    'work_style': 'collaborative',  # solo, collaborative, mixed
}
```

### Extending Dependency Mappings

Add new frameworks/tools in `config.py`:

```python
DEPENDENCY_MAPPINGS = {
    'your-framework': {
        'type': 'framework',
        'category': 'Backend',
        'name': 'Your Framework'
    },
    # ... more mappings
}
```

## 📈 Example Output

```
╔══════════════════════════════════════════════════════════════╗
║              HIRESIGHT ANALYSIS SUMMARY                      ║
╚══════════════════════════════════════════════════════════════╝

Candidate: octocat
Overall Match: 78.5/100 (High Match)

Skills: 24 identified
Top Skills: JavaScript, Python, React, Docker, TypeScript

Components:
  • Current Fit:        75.2/100
  • Growth Potential:   82.3/100
  • Collaboration Fit:  76.0/100
  • Code Quality:       68.5/100

Work Style: Collaborative
Quality Tier: Good

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🎯 Use Cases

1. **Technical Hiring**: Evaluate candidates objectively based on actual code and contributions
2. **Talent Sourcing**: Discover candidates with specific skill sets
3. **Team Building**: Find candidates whose work style matches your team culture
4. **Skills Gap Analysis**: Identify training needs and ramp-up timelines
5. **Bias Mitigation**: Detect and eliminate unconscious biases in job descriptions
6. **Portfolio Review**: Understand a developer's technical journey and expertise

## 🔒 Privacy & Ethics

- **Public Data Only**: Analyzes only publicly available GitHub information
- **Rate Limiting**: Respects GitHub API limits
- **Consent-Based**: Requires explicit username input
- **No Data Storage**: No persistent storage of candidate data (optional caching for efficiency)
- **Bias Detection**: Actively identifies potential discrimination in hiring criteria

## 🐛 Troubleshooting

### API Rate Limit Errors

```
Error: rate limit exceeded
```

**Solution**: Set a GitHub Personal Access Token (see Setup section)

### Username Not Found

```
Error: Failed to fetch profile for username
```

**Solutions**:
- Verify the username is correct
- Ensure the profile is public
- Check GitHub API status: https://www.githubstatus.com/

### Missing Dependencies

```
ModuleNotFoundError: No module named 'github'
```

**Solution**: Install dependencies: `pip install -r requirements.txt`

### TextBlob Sentiment Analysis Errors

```
LookupError: Resource 'corpora/brown' not found
```

**Solution**: Download TextBlob corpora: `python -m textblob.download_corpora`

## 🔄 Caching

HireSight uses intelligent caching to optimize API usage:
- Cached data is stored in `.cache/` directory
- Default cache lifetime: 24 hours
- Use `--no-cache` flag to disable caching and fetch fresh data
- Cache files are named by username

To clear cache:
```bash
rm -rf .cache/
```

## ⚡ Performance Tips

1. **Use GitHub Token**: Increases rate limit from 60 to 5000 requests/hour
2. **Adjust Top Repos**: Use `--top-repos 5` for faster analysis (default: 10)
3. **Enable Caching**: Don't use `--no-cache` unless you need fresh data
4. **Batch Analysis**: Run multiple analyses to utilize API quota efficiently

## 📝 Development

### Adding New Analysis Modules

1. Add your analysis function to `analyzer.py`
2. Update `perform_complete_analysis()` to include your module
3. Add output formatting in `output_generator.py`

### Extending Matching Algorithm

Modify weights in `config.py`:

```python
MATCHING_WEIGHTS = {
    'current_fit': 0.40,
    'growth_potential': 0.30,
    'collaboration_fit': 0.20,
    'code_quality': 0.10,
}
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional language/framework detection
- More sophisticated sentiment analysis
- Machine learning-based skill prediction
- Portfolio quality assessment
- Team compatibility analysis

## 📄 License

MIT License - feel free to use this tool for any purpose.

## 🙏 Acknowledgments

- **PyGithub**: GitHub API wrapper
- **TextBlob**: Sentiment analysis
- **GitHub API**: Comprehensive developer data

## 📞 Support

For issues, questions, or suggestions:
1. Check the Troubleshooting section
2. Review GitHub API documentation: https://docs.github.com/en/rest
3. Verify your GitHub token permissions

---

**HireSight** - Making technical hiring more objective, fair, and data-driven. 🚀
