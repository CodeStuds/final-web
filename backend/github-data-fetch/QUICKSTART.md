# HireSight Quick Reference

## Installation

```bash
pip install -r requirements.txt
python -m textblob.download_corpora
export GITHUB_TOKEN="your_token_here"
```

## Basic Usage

```bash
# Analyze a profile
python main.py username

# With GitHub URL
python main.py https://github.com/username

# Test installation
python example.py
```

## Common Commands

```bash
# Custom job requirements
python main.py username \
    --job-title "Backend Developer" \
    --required-skills "Python,Django,PostgreSQL" \
    --preferred-skills "Redis,Docker"

# More detailed analysis
python main.py username --top-repos 15

# Specify output directory
python main.py username --output-dir ./reports

# JSON only (no Markdown)
python main.py username --json-only

# Disable caching (fresh data)
python main.py username --no-cache

# Quiet mode (less output)
python main.py username --quiet
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `username` | GitHub username or URL | *required* |
| `--token` | GitHub token | `$GITHUB_TOKEN` |
| `--top-repos N` | Number of repos to analyze | 10 |
| `--job-title` | Job title | "Full-Stack Developer" |
| `--required-skills` | Required skills (comma-separated) | JS,React,Python,Docker |
| `--preferred-skills` | Preferred skills (comma-separated) | TS,AWS,GraphQL |
| `--work-style` | Required work style | collaborative |
| `--output-dir` | Output directory | current directory |
| `--no-cache` | Disable caching | false |
| `--json-only` | Generate only JSON | false |
| `--quiet` | Suppress progress messages | false |

## Output Files

- `analysis_username.json` - Complete analysis data
- `report_username.md` - Human-readable report
- `.cache/` - Cached API responses (24hr TTL)

## Scoring System

### Overall Match (0-100)
- **Current Fit**: 40% - Direct skill overlap
- **Growth Potential**: 30% - Learning ability
- **Collaboration Fit**: 20% - Work style match
- **Code Quality**: 10% - Best practices

### Match Tiers
- **Top Match**: 85-100
- **High Match**: 70-84
- **Moderate Match**: 50-69
- **Low Match**: 0-49

### Skill Confidence (0-100)
- **Lines of Code**: 20 points max
- **Repository Count**: 30 points max
- **Recency**: 30 points max (last 12 months)
- **Complexity**: 20 points max

## Work Styles Detected

1. **Solo Developer** - Independent project ownership (>80% contributions)
2. **Collaborative** - Active in discussions (review ratio >0.6)
3. **Mentorship** - Detailed, constructive reviews (>100 chars avg)
4. **Async-Friendly** - Conventional commits, clear communication (>50% usage)

## Code Quality Tiers

- **Excellent**: 75-100
- **Good**: 60-74
- **Fair**: 40-59
- **Needs Improvement**: 0-39

## Troubleshooting

### Rate Limit Errors
```bash
# Set GitHub token
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
```

### Module Not Found
```bash
pip install -r requirements.txt
```

### TextBlob Errors
```bash
python -m textblob.download_corpora
```

### Clear Cache
```bash
rm -rf .cache/
```

### Check API Status
- Visit: https://www.githubstatus.com/

## Supported Technologies

### Languages
JavaScript, TypeScript, Python, Java, Go, Rust, Ruby, PHP, C++, C#, Kotlin, Swift, etc.

### Frameworks
React, Vue, Angular, Django, Flask, FastAPI, Spring Boot, Express, NestJS, Rails, etc.

### Tools & DevOps
Docker, Kubernetes, Terraform, Ansible, Jenkins, GitHub Actions, GitLab CI, CircleCI, etc.

### Databases
PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, Cassandra, SQLite, etc.

### Testing
Jest, Pytest, JUnit, Mocha, Cypress, Playwright, RSpec, etc.

## Configuration Files

### Supported Package Files
- `package.json` (Node.js)
- `requirements.txt` (Python)
- `Pipfile` (Python)
- `pyproject.toml` (Python)
- `go.mod` (Go)
- `Cargo.toml` (Rust)
- `Gemfile` (Ruby)
- `pom.xml` (Java)
- `composer.json` (PHP)

### Supported CI/CD Files
- `.github/workflows/` (GitHub Actions)
- `.gitlab-ci.yml` (GitLab CI)
- `.travis.yml` (Travis CI)
- `Jenkinsfile` (Jenkins)
- `.circleci/config.yml` (CircleCI)
- `azure-pipelines.yml` (Azure Pipelines)

## API Rate Limits

| Auth Status | Requests/Hour |
|-------------|---------------|
| Unauthenticated | 60 |
| Authenticated | 5,000 |

## Environment Variables

```bash
# Required for higher rate limits
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Optional: default output directory
export HIRESIGHT_OUTPUT_DIR="./reports"
```

## Best Practices

1. **Always use a GitHub token** for production use
2. **Analyze 10-15 repos** for comprehensive results
3. **Review bias detection** results before finalizing requirements
4. **Consider growth potential** alongside current fit
5. **Use caching** for repeated analyses (within 24hrs)
6. **Batch analyze** similar candidates together
7. **Document decisions** using generated reports

## Example Workflow

```bash
# 1. Set up environment
export GITHUB_TOKEN="your_token"
mkdir -p ./candidate_reports

# 2. Define job requirements
JOB_TITLE="Senior Backend Engineer"
REQUIRED="Python,Django,PostgreSQL,Docker"
PREFERRED="AWS,Redis,GraphQL,Kubernetes"

# 3. Analyze candidates
for candidate in candidate1 candidate2 candidate3; do
    python main.py "$candidate" \
        --job-title "$JOB_TITLE" \
        --required-skills "$REQUIRED" \
        --preferred-skills "$PREFERRED" \
        --output-dir "./candidate_reports/$candidate"
done

# 4. Review generated reports
ls -la ./candidate_reports/*/report_*.md

# 5. Make informed hiring decisions!
```

## Tips for Better Results

- Analyze candidates with 6+ months of GitHub activity
- Look for consistent contribution patterns
- Value growth potential over perfect current match
- Consider work style compatibility with team
- Review actual code samples in repositories
- Use interview questions from recommendations
- Cross-reference with portfolio/resume

## Quick Stats

- **100+** framework/tool mappings
- **10** repository deep analysis
- **12 months** of contribution history
- **4-factor** matching algorithm
- **5** bias detection categories
- **2** output formats (JSON + Markdown)

---

**Need Help?** Check the full README.md for detailed documentation.

**Found a Bug?** The tool includes comprehensive error messages and troubleshooting steps.

**Want to Extend?** All modules are well-documented and modular for easy customization.
