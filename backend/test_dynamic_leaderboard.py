#!/usr/bin/env python3
"""
Test Script for Dynamic Leaderboard System
Demonstrates the complete workflow
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
API_KEY = None  # Set if API keys are enabled

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def make_request(method, endpoint, **kwargs):
    """Make API request with optional API key"""
    headers = kwargs.get('headers', {})
    if API_KEY:
        headers['X-API-Key'] = API_KEY
    kwargs['headers'] = headers
    
    url = f"{BASE_URL}{endpoint}"
    response = requests.request(method, url, **kwargs)
    return response

def test_health_check():
    """Test 1: Health check"""
    print_section("Test 1: Health Check")
    
    response = make_request('GET', '/api/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_session_list():
    """Test 2: List existing sessions"""
    print_section("Test 2: List Existing Sessions")
    
    response = make_request('GET', '/api/sessions')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total sessions: {data['total']}")
        
        if data['sessions']:
            print("\nExisting sessions:")
            for session in data['sessions'][:5]:  # Show first 5
                print(f"  • {session['session_id']}")
                print(f"    Job: {session.get('job_title', 'Unknown')}")
                print(f"    Created: {session.get('created_at', 'Unknown')}")
                print(f"    Status: {session.get('status', 'Unknown')}")
        else:
            print("No existing sessions found.")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_storage_stats():
    """Test 3: Get storage statistics"""
    print_section("Test 3: Storage Statistics")
    
    response = make_request('GET', '/api/sessions/stats')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        stats = data['statistics']
        print(f"Total sessions: {stats['total_sessions']}")
        print(f"Storage used: {stats['total_size_mb']} MB")
        print(f"Base directory: {stats['base_directory']}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_session_info(session_id):
    """Test 4: Get session info"""
    print_section(f"Test 4: Get Session Info - {session_id}")
    
    response = make_request('GET', f'/api/session/{session_id}')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nMetadata:")
        for key, value in data['metadata'].items():
            print(f"  {key}: {value}")
        
        print(f"\nFiles:")
        for key, value in data['files'].items():
            print(f"  {key}: {value}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_get_leaderboard(session_id, linkedin_weight=0.5, github_weight=0.5, top_n=10):
    """Test 5: Get leaderboard for session"""
    print_section(f"Test 5: Get Leaderboard - {session_id}")
    
    params = {
        'linkedin_weight': linkedin_weight,
        'github_weight': github_weight,
        'top_n': top_n
    }
    
    response = make_request('GET', f'/api/leaderboard/{session_id}', params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTotal candidates: {data['total_candidates']}")
        print(f"Weights - LinkedIn: {data['weights']['linkedin']}, GitHub: {data['weights']['github']}")
        
        if data.get('statistics'):
            stats = data['statistics']
            print(f"\nStatistics:")
            print(f"  Mean: {stats['mean']:.4f}")
            print(f"  Median: {stats['median']:.4f}")
            print(f"  Range: {stats['min']:.4f} - {stats['max']:.4f}")
        
        print(f"\nTop {len(data['leaderboard'])} Candidates:")
        print(f"{'Rank':<6} {'Name':<25} {'Combined':<10} {'LinkedIn':<10} {'GitHub':<10} {'Tier':<20}")
        print("-" * 90)
        
        for candidate in data['leaderboard']:
            print(f"{candidate['rank']:<6} "
                  f"{candidate['name'][:24]:<25} "
                  f"{candidate['combined_score']:.4f}    "
                  f"{candidate['linkedin_score']:.4f}    "
                  f"{candidate['github_score']:.4f}    "
                  f"{candidate['emoji']} {candidate['tier']}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_cleanup_dry_run():
    """Test 6: Cleanup old sessions (dry run)"""
    print_section("Test 6: Cleanup Old Sessions (Dry Run)")
    
    payload = {
        'days': 7,
        'dry_run': True
    }
    
    response = make_request('POST', '/api/sessions/cleanup', json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Sessions that would be cleaned: {data['sessions_cleaned']}")
        if data['session_ids']:
            print("\nSessions to delete:")
            for session_id in data['session_ids']:
                print(f"  • {session_id}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "=" * 70)
    print("  DYNAMIC LEADERBOARD SYSTEM - TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: List sessions
    results.append(("List Sessions", test_session_list()))
    
    # Test 3: Storage stats
    results.append(("Storage Stats", test_storage_stats()))
    
    # Get first session for testing (if exists)
    response = make_request('GET', '/api/sessions')
    if response.status_code == 200 and response.json()['sessions']:
        session_id = response.json()['sessions'][0]['session_id']
        
        # Test 4: Session info
        results.append(("Session Info", test_session_info(session_id)))
        
        # Test 5a: Leaderboard with equal weights
        results.append(("Leaderboard (50/50)", test_get_leaderboard(session_id, 0.5, 0.5, 10)))
        
        # Test 5b: Leaderboard with LinkedIn-heavy weights
        print_section("Test 5b: Leaderboard with LinkedIn-heavy weights (60/40)")
        results.append(("Leaderboard (60/40)", test_get_leaderboard(session_id, 0.6, 0.4, 10)))
        
        # Test 5c: Leaderboard with GitHub-heavy weights
        print_section("Test 5c: Leaderboard with GitHub-heavy weights (30/70)")
        results.append(("Leaderboard (30/70)", test_get_leaderboard(session_id, 0.3, 0.7, 10)))
    else:
        print("\n⚠️  No sessions found. Upload resumes first using /api/rank-with-leaderboard")
    
    # Test 6: Cleanup dry run
    results.append(("Cleanup Dry Run", test_cleanup_dry_run()))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total

def demo_workflow():
    """Demonstrate the complete workflow with example data"""
    print_section("COMPLETE WORKFLOW DEMONSTRATION")
    
    print("""
This demo shows how to use the dynamic leaderboard system:

1. Upload resumes using POST /api/rank-with-leaderboard
2. System creates a session and processes resumes
3. Generates LinkedIn scores (results.csv)
4. Analyzes GitHub profiles (analysis_*.json files)
5. Creates leaderboard with combined scores
6. Returns session_id for future access

To test with actual data, use curl:

curl -X POST http://localhost:5000/api/rank-with-leaderboard \\
  -F "company_id=acme" \\
  -F "job_id=dev001" \\
  -F "job_title=Backend Developer" \\
  -F "role=Backend Developer" \\
  -F "skills=Python, Django, PostgreSQL" \\
  -F "experience=3+ years" \\
  -F "file=@resumes.zip"

The response will contain:
- session_id: Use this to access the leaderboard later
- results: Individual resume scores
- leaderboard: Top 20 candidates with combined scores
- statistics: Mean, median, min, max scores

Then access the leaderboard anytime:
GET /api/leaderboard/{session_id}?linkedin_weight=0.5&github_weight=0.5&top_n=20
""")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            demo_workflow()
        elif sys.argv[1] == '--session':
            if len(sys.argv) > 2:
                session_id = sys.argv[2]
                test_session_info(session_id)
                test_get_leaderboard(session_id)
            else:
                print("Usage: python test_dynamic_leaderboard.py --session <session_id>")
        else:
            print("Usage: python test_dynamic_leaderboard.py [--demo | --session <session_id>]")
    else:
        # Run all tests
        success = run_all_tests()
        sys.exit(0 if success else 1)
