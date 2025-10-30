"""
Example script demonstrating how to use the GitHub Leaderboard API.
"""
import requests
import json

# API endpoint
API_URL = "http://localhost:8000/analyze"

# Example request payload
# NOTE: GitHub token is now loaded from .env file, not passed in request
payload = {
    "github_profiles": [
        "torvalds",
        "gvanrossum",
        "https://github.com/defunkt",
        "sindresorhus",
        "tj"
    ],
    "job_description": """
        We are looking for a Senior Python Developer with the following qualifications:

        Required Skills:
        - 5+ years of Python development experience
        - Strong experience with FastAPI or Django
        - Docker and containerization
        - RESTful API design and development
        - Git version control
        - CI/CD pipelines (GitHub Actions, Jenkins)

        Nice to Have:
        - AWS or cloud platform experience
        - PostgreSQL or database optimization
        - Machine learning or data science background
        - Open source contributions
        - TypeScript/JavaScript experience

        The ideal candidate will have a strong GitHub presence with well-documented
        projects and active contributions to the community.
    """,
    "top_n_repos": 5,
    "use_gemini": True  # Enable Gemini AI analysis (requires GEMINI_API_KEY in .env)
}

def analyze_profiles():
    """Send request to API and display results."""

    print("Sending request to GitHub Leaderboard API...")
    print(f"Analyzing {len(payload['github_profiles'])} profiles\n")

    try:
        # Make POST request
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()

        # Parse response
        result = response.json()

        # Display results
        print("="*80)
        print("GITHUB PROFILE LEADERBOARD")
        print("="*80)
        print()

        # Summary
        summary = result['analysis_summary']
        print(f"Total Candidates Analyzed: {summary['total_candidates']}")
        print(f"Average Score: {summary['average_score']}")
        print(f"Top Score: {summary['top_score']}")
        print(f"Required Skills: {', '.join(summary['required_skills_identified'][:10])}")
        print()

        # Leaderboard
        print("-"*80)
        print("RANKINGS")
        print("-"*80)

        for candidate in result['candidates']:
            print(f"\n#{candidate['ranking']} - {candidate['name']} (@{candidate['username']})")
            print(f"   Profile: {candidate['profile_url']}")
            print(f"   Total Score: {candidate['total_score']}/100")

            metrics = candidate['metrics']
            print(f"\n   Score Breakdown:")
            print(f"   - Skill Match: {metrics['skill_match_score']}/100")
            print(f"   - Semantic Similarity: {metrics['semantic_similarity_score']}/100")
            print(f"   - Activity: {metrics['activity_score']}/100")
            print(f"   - Community: {metrics['community_score']}/100")
            print(f"   - Code Quality: {metrics['code_quality_score']}/100")

            print(f"\n   GitHub Stats:")
            print(f"   - Stars: {metrics['total_stars']}")
            print(f"   - Commits: {metrics['total_commits']}")
            print(f"   - Public Repos: {metrics['public_repos']}")
            print(f"   - Followers: {metrics['followers']}")

            if candidate['matching_skills']:
                print(f"\n   Matching Skills: {', '.join(candidate['matching_skills'][:10])}")

            if candidate['bio']:
                print(f"   Bio: {candidate['bio'][:100]}...")

            print(f"\n   Top Repositories:")
            for repo in candidate['top_repositories'][:3]:
                print(f"   - {repo['name']} ({repo['stars']} ⭐) - {repo['languages']}")
                # Show Gemini analysis if available
                if 'gemini_analysis' in repo:
                    gemini = repo['gemini_analysis']
                    print(f"     Gemini Quality Score: {gemini.get('quality_score', 'N/A')}/100")
                    print(f"     Complexity: {gemini.get('technical_complexity', 'N/A')}")

            # Show Gemini candidate fit analysis if available
            if 'gemini_fit_analysis' in candidate:
                fit = candidate['gemini_fit_analysis']
                print(f"\n   Gemini AI Candidate Fit Analysis:")
                print(f"   - Overall Fit Score: {fit.get('overall_fit_score', 'N/A')}/100")
                print(f"   - Recommendation: {fit.get('recommendation', 'N/A')}")
                if fit.get('standout_qualities'):
                    print(f"   - Standout Qualities: {', '.join(fit['standout_qualities'][:3])}")

            print()

        print("="*80)

        # Save to file
        with open('leaderboard_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("\nFull results saved to 'leaderboard_result.json'")

    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("NOTE: Make sure you have set GITHUB_TOKEN in your .env file!")
    print("Get one at: https://github.com/settings/tokens")
    print("\nFor Gemini AI analysis, also set GEMINI_API_KEY in .env")
    print("Get one at: https://makersuite.google.com/app/apikey")
    print("\n" + "="*80 + "\n")
    analyze_profiles()
