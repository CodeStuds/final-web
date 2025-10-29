#!/usr/bin/env python3
"""
Example script demonstrating HireSight usage
This can also be used as a quick test of the installation
"""

import os
import sys

# Test imports
try:
    from data_fetcher import GitHubDataFetcher
    from analyzer import GitHubAnalyzer
    from matcher import CandidateMatcher
    from output_generator import OutputGenerator
    from utils import logger
    from config import DEFAULT_JOB_REQUIREMENTS
    print("✅ All modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nPlease install dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

# Test basic functionality
def test_basic_functionality():
    """Test basic HireSight functionality"""
    print("\n" + "="*60)
    print("HIRESIGHT FUNCTIONALITY TEST")
    print("="*60)
    
    # Check for GitHub token
    token = os.getenv('GITHUB_TOKEN')
    if token:
        print("✅ GitHub token found (GITHUB_TOKEN env var)")
    else:
        print("⚠️  No GitHub token found")
        print("   Analysis will work but with limited rate limits")
        print("   Set GITHUB_TOKEN environment variable for better performance")
    
    # Test configuration
    print("\n📋 Testing Configuration...")
    print(f"  - Default job: {DEFAULT_JOB_REQUIREMENTS['title']}")
    print(f"  - Required skills: {', '.join(DEFAULT_JOB_REQUIREMENTS['required_skills'][:3])}...")
    print(f"  - Scoring weights configured: ✅")
    
    # Test data fetcher initialization
    print("\n🔌 Testing GitHub API Connection...")
    try:
        fetcher = GitHubDataFetcher(access_token=token)
        rate_limit = fetcher.check_rate_limit()
        print(f"  - API connection: ✅")
        print(f"  - Rate limit: {rate_limit['core_remaining']}/{rate_limit['core_limit']}")
    except Exception as e:
        print(f"  - API connection: ❌ ({e})")
        return False
    
    print("\n" + "="*60)
    print("All systems operational! Ready to analyze GitHub profiles.")
    print("="*60)
    print("\nTry running:")
    print("  python main.py octocat")
    print("\nOr with a real username:")
    print("  python main.py <github-username>")
    print()
    
    return True


def example_custom_job():
    """Show example of custom job requirements"""
    print("\n" + "="*60)
    print("EXAMPLE: Custom Job Requirements")
    print("="*60)
    
    custom_job = {
        'title': 'Senior Backend Engineer',
        'required_skills': ['Python', 'Django', 'PostgreSQL', 'Docker', 'AWS'],
        'preferred_skills': ['Redis', 'GraphQL', 'Kubernetes', 'Terraform'],
        'experience_level': 'senior',
        'team_size': 'large',
        'work_style': 'collaborative',
    }
    
    print("\nTo analyze with these requirements:")
    print(f"""
python main.py <username> \\
    --job-title "{custom_job['title']}" \\
    --required-skills "{','.join(custom_job['required_skills'])}" \\
    --preferred-skills "{','.join(custom_job['preferred_skills'])}" \\
    --work-style {custom_job['work_style']}
    """)


def example_batch_analysis():
    """Show example of batch analysis"""
    print("\n" + "="*60)
    print("EXAMPLE: Batch Analysis of Multiple Candidates")
    print("="*60)
    
    print("\nCreate a shell script for batch analysis:")
    print("""
#!/bin/bash
CANDIDATES=("candidate1" "candidate2" "candidate3")

for candidate in "${CANDIDATES[@]}"; do
    echo "Analyzing $candidate..."
    python main.py "$candidate" --output-dir "./reports/$candidate"
done

echo "Batch analysis complete! Check ./reports/ directory"
    """)


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                      H I R E S I G H T                       ║
║                    Installation Test                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run basic tests
    success = test_basic_functionality()
    
    if success:
        # Show examples
        example_custom_job()
        example_batch_analysis()
        
        print("\n" + "="*60)
        print("For more information, see README.md")
        print("="*60)
        print()
