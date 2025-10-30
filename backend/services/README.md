# HireSight Backend Services

## Overview

This directory contains unified, consolidated backend services that eliminate code duplication and provide consistent interfaces for:

- **GitHub Profile Analysis** (`github_service.py`)
- **Interview Question Generation** (`interview_service.py`) 
- **Leaderboard Generation** (`leaderboard_service.py`)

## Features

### ✅ No Code Duplication
All functionality is consolidated into single-responsibility services instead of being scattered across multiple directories.

### ✅ Proper Error Handling
Each service has comprehensive error handling with meaningful error messages.

### ✅ Consistent Interfaces
All services follow the same patterns:
- Factory functions (`create_*_service()`)
- Status check methods (`get_service_status()`)
- Validation methods
- Batch processing support

### ✅ Easy Testing
Services are decoupled from Flask and can be imported and tested independently.

## Usage

### GitHub Service

```python
from services.github_service import create_github_service

# Create service
github_service = create_github_service(github_token="your_token_here")

# Analyze profile
result = github_service.analyze_profile(
    username="torvalds",
    job_requirements={
        "role": "Senior Developer",
        "required_skills": ["C", "Linux"],
        "preferred_skills": ["Kernel Development"]
    },
    max_repos=20
)

print(f"Match Score: {result['match_score']}")
```

### Interview Service

```python
from services.interview_service import create_interview_service

# Create service
interview_service = create_interview_service(api_key="your_gemini_key")

# Generate questions
result = interview_service.generate_questions(
    candidate_name="John Doe",
    candidate_profile="Software engineer with 5 years experience..."
)

print(result['interview_questions'])
```

### Leaderboard Service

```python
from services.leaderboard_service import create_leaderboard_service

# Create service
leaderboard_service = create_leaderboard_service()

# Generate leaderboard
result = leaderboard_service.generate_leaderboard(
    candidates=[
        {
            "name": "Alice",
            "linkedin_score": 85,
            "github_score": 90,
            "resume_score": 88
        },
        # ... more candidates
    ],
    weights={
        "linkedin": 0.3,
        "github": 0.4,
        "resume": 0.3
    }
)

for candidate in result['leaderboard']:
    print(f"{candidate['rank']}. {candidate['name']}: {candidate['combined_score']}")
```

## API Integration

These services are automatically integrated into the main Flask API (`api.py`). The following endpoints use these services:

- `POST /api/github/analyze` - GitHub Service
- `POST /api/interview/generate` - Interview Service
- `POST /api/leaderboard` - Leaderboard Service

## Benefits Over Old Code

1. **Single Source of Truth**: No duplicate logic in multiple places
2. **Easier Maintenance**: Changes only need to be made in one place
3. **Better Testing**: Services can be tested independently
4. **Improved Error Handling**: Consistent error handling across all services
5. **Type Safety**: Proper type hints and validation
6. **Documentation**: Comprehensive docstrings

## Migration Guide

If you were previously using the old modules directly:

**Old way** (scattered across directories):
```python
from github_data_fetch.data_fetcher import GitHubDataFetcher
from github_data_fetch.analyzer import GitHubAnalyzer
# ... multiple imports, manual coordination
```

**New way** (unified service):
```python
from services.github_service import create_github_service
service = create_github_service()
result = service.analyze_profile("username")
```

## Testing

Run the comprehensive test suite:

```bash
python test_api.py
```

Or test individual services:

```bash
python -c "from services.github_service import create_github_service; print(create_github_service().get_service_status())"
```

## Environment Variables

See `.env.example` for required configuration:

- `GITHUB_TOKEN` - For GitHub API access
- `GEMINI_API_KEY` - For interview question generation
- `API_KEYS_ENABLED` - Enable/disable API key authentication

## Status

All services are **production-ready** and actively used by the main API.
