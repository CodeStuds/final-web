#!/usr/bin/env python3
"""
Example usage of the Unified Candidate Scoring System
Demonstrates scoring candidates with GitHub/LinkedIn and Resume data
"""

import json
from candidate_scorer import CandidateScorer

def example_single_candidate():
    """Example: Score a single candidate"""
    print("=" * 70)
    print("EXAMPLE 1: Single Candidate Scoring")
    print("=" * 70)
    
    # Define job requirements
    job_description = {
        'role': 'Backend Developer',
        'required_skills': ['Python', 'Django', 'PostgreSQL', 'REST API'],
        'preferred_skills': ['Docker', 'AWS', 'Redis'],
        'description': 'We are looking for an experienced backend developer to build scalable APIs and microservices',
        'experience': '3+ years'
    }
    
    # Initialize scorer
    scorer = CandidateScorer(job_description)
    
    # Candidate data
    candidate = {
        'name': 'John Doe',
        'resume_text': '''
            John Doe - Backend Developer
            
            Experience: 4 years
            
            Skills: Python, Django, PostgreSQL, REST APIs, Docker, Git
            
            Recent Projects:
            - Built scalable REST API handling 10M+ requests/day
            - Designed microservices architecture with Docker
            - Optimized PostgreSQL queries improving performance by 40%
            - Implemented CI/CD pipelines
        ''',
        'candidate_skills': {
            'github': ['Python', 'Django', 'Docker', 'Git', 'FastAPI'],
            'linkedin': ['Python', 'PostgreSQL', 'AWS', 'Team Leadership', 'REST API']
        }
    }
    
    # Score the candidate
    result = scorer.score_candidate(
        candidate_name=candidate['name'],
        resume_text=candidate['resume_text'],
        candidate_skills=candidate['candidate_skills']
    )
    
    # Display results
    print(f"\nCandidate: {result['candidate_name']}")
    print(f"Final Score: {result['normalized_score']:.2f}/100")
    print(f"Tier: {result['tier']}")
    
    if 'github_linkedin_compatibility' in result:
        gl = result['github_linkedin_compatibility']
        print(f"\n📊 GitHub/LinkedIn Compatibility: {gl['compatibility_score']*100:.2f}%")
        print(f"   Required Skills Matched: {', '.join(gl['required_skills_matched'])}")
        print(f"   Missing Skills: {', '.join(gl['required_skills_missing']) if gl['required_skills_missing'] else 'None'}")
        print(f"   Preferred Skills Matched: {', '.join(gl['preferred_skills_matched'])}")
        print(f"   Match Percentage: {gl['match_percentage']:.1f}%")
    
    if 'resume_compatibility' in result:
        rc = result['resume_compatibility']
        print(f"\n📄 Resume Compatibility: {rc['compatibility_score']*100:.2f}%")
        print(f"   Matched Keywords: {', '.join(rc['matched_keywords'])}")
    
    if 'final_score_data' in result:
        fs = result['final_score_data']
        print(f"\n🎯 Final Averaged Score:")
        print(f"   GitHub/LinkedIn: {fs['github_linkedin_score']*100:.2f}%")
        print(f"   Resume: {fs['resume_score']*100:.2f}%")
        print(f"   Weights: GL={fs['weights_used']['github_linkedin']}, Resume={fs['weights_used']['resume']}")
        print(f"   Final: {fs['normalized_score']:.2f}/100 {fs['emoji']}")
    
    print("\n" + "=" * 70)
    return result


def example_multiple_candidates():
    """Example: Score multiple candidates and generate leaderboard"""
    print("\nEXAMPLE 2: Multiple Candidates Leaderboard")
    print("=" * 70)
    
    # Define job requirements
    job_description = {
        'role': 'Full Stack Developer',
        'required_skills': ['JavaScript', 'React', 'Node.js', 'PostgreSQL'],
        'preferred_skills': ['TypeScript', 'Docker', 'AWS'],
        'description': 'Looking for a full stack developer with strong frontend and backend skills',
        'experience': '2+ years'
    }
    
    # Initialize scorer
    scorer = CandidateScorer(job_description)
    
    # Multiple candidates
    candidates = [
        {
            'name': 'Alice Johnson',
            'resume_text': 'Full stack developer with 3 years experience in React and Node.js. Built multiple web applications with PostgreSQL.',
            'candidate_skills': {
                'github': ['JavaScript', 'React', 'Node.js', 'TypeScript', 'Git'],
                'linkedin': ['React', 'Node.js', 'PostgreSQL', 'Docker', 'Team Lead']
            }
        },
        {
            'name': 'Bob Smith',
            'resume_text': 'Frontend developer specializing in React. Experience with REST APIs and modern JavaScript.',
            'candidate_skills': {
                'github': ['JavaScript', 'React', 'Vue', 'HTML', 'CSS'],
                'linkedin': ['JavaScript', 'React', 'TypeScript', 'UI/UX']
            }
        },
        {
            'name': 'Carol Williams',
            'resume_text': 'Backend specialist with Node.js and PostgreSQL. Built scalable microservices with Docker and AWS.',
            'candidate_skills': {
                'github': ['Node.js', 'PostgreSQL', 'Docker', 'Python', 'MongoDB'],
                'linkedin': ['Node.js', 'PostgreSQL', 'AWS', 'Kubernetes', 'DevOps']
            }
        },
        {
            'name': 'David Brown',
            'resume_text': 'Full stack developer experienced in React, Node.js, TypeScript, and PostgreSQL. AWS certified.',
            'candidate_skills': {
                'github': ['JavaScript', 'TypeScript', 'React', 'Node.js', 'Docker'],
                'linkedin': ['React', 'Node.js', 'PostgreSQL', 'AWS', 'TypeScript']
            }
        }
    ]
    
    # Score all candidates
    leaderboard = scorer.score_multiple_candidates(candidates)
    
    # Display leaderboard
    print(f"\n🏆 LEADERBOARD - {job_description['role']}")
    print("-" * 70)
    print(f"{'Rank':<6} {'Name':<20} {'Score':<10} {'Tier':<12} {'Skills Match'}")
    print("-" * 70)
    
    for candidate in leaderboard:
        name = candidate['candidate_name']
        score = candidate['normalized_score']
        tier = candidate['tier']
        rank = candidate['rank']
        
        # Get match percentage if available
        match_pct = "N/A"
        if 'github_linkedin_compatibility' in candidate:
            match_pct = f"{candidate['github_linkedin_compatibility']['match_percentage']:.0f}%"
        
        print(f"{rank:<6} {name:<20} {score:>6.2f}/100 {tier:<12} {match_pct}")
    
    print("-" * 70)
    print(f"Total Candidates: {len(leaderboard)}")
    print("\n" + "=" * 70)
    
    return leaderboard


def example_custom_weights():
    """Example: Using custom scoring weights"""
    print("\nEXAMPLE 3: Custom Scoring Weights")
    print("=" * 70)
    
    job_description = {
        'role': 'Senior Backend Developer',
        'required_skills': ['Python', 'Django', 'PostgreSQL'],
        'preferred_skills': ['Redis', 'Celery'],
        'description': 'Senior role requiring proven GitHub contributions'
    }
    
    scorer = CandidateScorer(job_description)
    
    candidate_data = {
        'candidate_name': 'Senior Dev',
        'resume_text': 'Senior Python developer with Django and PostgreSQL experience',
        'candidate_skills': {
            'github': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Celery'],
            'linkedin': ['Python', 'Leadership', 'Mentoring']
        }
    }
    
    # Default weights (50/50)
    print("\n📊 Scoring with DEFAULT weights (50/50):")
    result_default = scorer.score_candidate(**candidate_data)
    print(f"   Final Score: {result_default['normalized_score']:.2f}/100")
    
    # GitHub/LinkedIn focused (70/30)
    print("\n📊 Scoring with GITHUB/LINKEDIN focus (70/30):")
    result_github_focus = scorer.score_candidate(
        **candidate_data,
        weights={'github_linkedin': 0.7, 'resume': 0.3}
    )
    print(f"   Final Score: {result_github_focus['normalized_score']:.2f}/100")
    
    # Resume focused (30/70)
    print("\n📊 Scoring with RESUME focus (30/70):")
    result_resume_focus = scorer.score_candidate(
        **candidate_data,
        weights={'github_linkedin': 0.3, 'resume': 0.7}
    )
    print(f"   Final Score: {result_resume_focus['normalized_score']:.2f}/100")
    
    print("\n💡 Insight: Adjust weights based on role requirements")
    print("   - Technical roles: Higher GitHub/LinkedIn weight")
    print("   - Traditional roles: Higher resume weight")
    print("\n" + "=" * 70)


def example_partial_data():
    """Example: Scoring with partial data (only resume or only skills)"""
    print("\nEXAMPLE 4: Scoring with Partial Data")
    print("=" * 70)
    
    job_description = {
        'role': 'Data Scientist',
        'required_skills': ['Python', 'Machine Learning', 'Pandas'],
        'preferred_skills': ['TensorFlow', 'PyTorch']
    }
    
    scorer = CandidateScorer(job_description)
    
    # Only resume, no GitHub/LinkedIn
    print("\n📄 Candidate with ONLY RESUME:")
    result_resume_only = scorer.score_candidate(
        candidate_name='Resume Only Person',
        resume_text='Data scientist with Python, Pandas, and machine learning experience'
    )
    print(f"   Score: {result_resume_only['normalized_score']:.2f}/100")
    print(f"   Tier: {result_resume_only['tier']}")
    
    # Only GitHub/LinkedIn, no resume
    print("\n💻 Candidate with ONLY GITHUB/LINKEDIN:")
    result_skills_only = scorer.score_candidate(
        candidate_name='GitHub Star',
        candidate_skills={
            'github': ['Python', 'Machine Learning', 'TensorFlow', 'Pandas'],
            'linkedin': ['Python', 'Data Science']
        }
    )
    print(f"   Score: {result_skills_only['normalized_score']:.2f}/100")
    print(f"   Tier: {result_skills_only['tier']}")
    
    # Both available
    print("\n🎯 Candidate with BOTH:")
    result_both = scorer.score_candidate(
        candidate_name='Complete Profile',
        resume_text='Data scientist with Python, Pandas, and machine learning experience',
        candidate_skills={
            'github': ['Python', 'Machine Learning', 'TensorFlow', 'Pandas'],
            'linkedin': ['Python', 'Data Science']
        }
    )
    print(f"   Score: {result_both['normalized_score']:.2f}/100")
    print(f"   Tier: {result_both['tier']}")
    
    print("\n💡 System adapts to available data automatically")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n")
    print("🚀 UNIFIED CANDIDATE SCORING SYSTEM - EXAMPLES")
    print("=" * 70)
    print("Demonstrates integration of GitHub/LinkedIn and Resume scoring")
    print("=" * 70)
    
    # Run examples
    example_single_candidate()
    example_multiple_candidates()
    example_custom_weights()
    example_partial_data()
    
    print("\n✅ All examples completed!")
    print("\nFor API usage, see UNIFIED_SCORING_GUIDE.md")
    print("For integration, check backend/api.py endpoints:")
    print("  - POST /api/candidate/score-unified")
    print("  - POST /api/candidates/score-batch")
    print()
