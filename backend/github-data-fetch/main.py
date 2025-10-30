#!/usr/bin/env python3
"""
HireSight - Comprehensive GitHub Profile Analysis for Developer Hiring
Main entry point for the application
"""

import argparse
import sys
import os
from typing import Dict, Any, Optional

from utils import logger, extract_username_from_url, ProgressTracker, CacheManager
from data_fetcher import GitHubDataFetcher
from analyzer import GitHubAnalyzer
from matcher import CandidateMatcher
from output_generator import OutputGenerator
from config import DEFAULT_JOB_REQUIREMENTS


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='HireSight - Comprehensive GitHub Profile Analysis for Developer Hiring',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py octocat
  python main.py https://github.com/torvalds
  python main.py username --job-title "Backend Developer" --required-skills "Python,Django,PostgreSQL"
  python main.py username --top-repos 15 --no-cache
        """
    )
    
    parser.add_argument(
        'username',
        type=str,
        help='GitHub username or profile URL (e.g., "octocat" or "https://github.com/octocat")'
    )
    
    parser.add_argument(
        '--token',
        type=str,
        default=None,
        help='GitHub Personal Access Token (or set GITHUB_TOKEN env var)'
    )
    
    parser.add_argument(
        '--top-repos',
        type=int,
        default=10,
        help='Number of top repositories to analyze in detail (default: 10)'
    )
    
    parser.add_argument(
        '--job-title',
        type=str,
        default=None,
        help='Job title for matching (default: Full-Stack Developer)'
    )
    
    parser.add_argument(
        '--required-skills',
        type=str,
        default=None,
        help='Comma-separated list of required skills (e.g., "Python,React,Docker")'
    )
    
    parser.add_argument(
        '--preferred-skills',
        type=str,
        default=None,
        help='Comma-separated list of preferred skills'
    )
    
    parser.add_argument(
        '--work-style',
        type=str,
        choices=['solo', 'collaborative', 'mixed'],
        default=None,
        help='Required work style for the role'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='reports',
        help='Output directory for generated files (default: reports/)'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching (fetch fresh data)'
    )
    
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='Generate only JSON output (skip Markdown report)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )
    
    return parser.parse_args()


def build_job_requirements(args) -> Dict[str, Any]:
    """Build job requirements from command line arguments"""
    job_reqs = DEFAULT_JOB_REQUIREMENTS.copy()
    
    if args.job_title:
        job_reqs['title'] = args.job_title
    
    if args.required_skills:
        job_reqs['required_skills'] = [s.strip() for s in args.required_skills.split(',')]
    
    if args.preferred_skills:
        job_reqs['preferred_skills'] = [s.strip() for s in args.preferred_skills.split(',')]
    
    if args.work_style:
        job_reqs['work_style'] = args.work_style
    
    return job_reqs


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Set logging level
    if args.quiet:
        logger.setLevel('WARNING')
    
    # Print banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                      H I R E S I G H T                       ║
║          Comprehensive GitHub Profile Analysis              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Extract username
    username = extract_username_from_url(args.username)
    logger.info(f"Analyzing GitHub profile: {username}")
    
    # Setup progress tracker
    progress = ProgressTracker(total_steps=7)
    
    try:
        # Step 1: Initialize components
        progress.update("Initializing components")
        
        token = args.token or os.getenv('GITHUB_TOKEN')
        if not token:
            logger.warning("⚠️  No GitHub token provided. API rate limits will be restrictive (60 requests/hour).")
            logger.warning("   Set GITHUB_TOKEN environment variable or use --token for better performance.")
            print()
        
        fetcher = GitHubDataFetcher(access_token=token)
        cache = CacheManager()
        
        # Build job requirements
        job_requirements = build_job_requirements(args)
        logger.info(f"Job requirements: {job_requirements['title']}")
        
        # Step 2: Fetch data
        progress.update("Fetching GitHub data")
        
        # Check cache
        cache_key = f"{username}_data"
        if not args.no_cache:
            cached_data = cache.get(cache_key, max_age_hours=24)
            if cached_data:
                logger.info("Using cached data (less than 24 hours old)")
                data = cached_data
            else:
                data = fetcher.get_comprehensive_data(username, top_repos_count=args.top_repos)
                cache.set(cache_key, data)
        else:
            data = fetcher.get_comprehensive_data(username, top_repos_count=args.top_repos)
        
        # Check if we got data
        if not data or not data.get('profile'):
            logger.error("Failed to fetch data. Please check the username and try again.")
            sys.exit(1)
        
        # Step 3: Analyze skills
        progress.update("Analyzing skills and technologies")
        analyzer = GitHubAnalyzer(data)
        analysis = analyzer.perform_complete_analysis()
        
        # Step 4: Perform matching
        progress.update("Calculating match scores")
        matcher = CandidateMatcher(analysis, job_requirements)
        match_results = matcher.calculate_overall_match()
        
        # Step 5: Detect bias
        progress.update("Analyzing bias and fairness")
        bias_analysis = matcher.detect_bias()
        match_results['bias_analysis'] = bias_analysis
        
        # Step 6: Generate outputs
        progress.update("Generating reports")
        
        # Ensure output directory exists
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Change to output directory
        original_dir = os.getcwd()
        os.chdir(args.output_dir)
        
        generator = OutputGenerator(username, analysis, match_results)
        
        if args.json_only:
            json_file = generator.generate_json_output()
            summary = generator.generate_summary()
            print(summary)
            print(f"\n✅ JSON output saved to: {os.path.join(args.output_dir, json_file)}")
        else:
            outputs = generator.generate_all()
            print(f"\n✅ Reports generated successfully!")
            print(f"   • JSON: {os.path.join(args.output_dir, outputs['json'])}")
            print(f"   • Markdown: {os.path.join(args.output_dir, outputs['markdown'])}")
        
        # Change back to original directory
        os.chdir(original_dir)
        
        # Step 7: Complete
        progress.complete()
        
        # Display key metrics
        print("\n" + "="*60)
        print("KEY METRICS")
        print("="*60)
        print(f"Overall Match Score: {match_results['overall_score']:.1f}/100 ({match_results['tier']})")
        print(f"Skills Identified: {analysis['skills_analysis']['skill_count']}")
        print(f"Top Skill: {analysis['skills_analysis']['top_skills'][0] if analysis['skills_analysis']['top_skills'] else 'N/A'}")
        print(f"Work Style: {analysis['work_style']['primary_style']}")
        print(f"Code Quality: {analysis['code_quality']['quality_tier']}")
        print(f"Growth Potential: {analysis['learning_trajectory']['growth_potential']}")
        
        if bias_analysis['biases_found']:
            print(f"\n⚠️  {bias_analysis['bias_count']} potential bias(es) detected in job requirements")
            print("   Review the full report for details and recommendations.")
        
        print("\n" + "="*60)
        print()
        
        # Rate limit warning
        rate_limit = fetcher.check_rate_limit()
        remaining = rate_limit.get('core_remaining', 0)
        if remaining < 100:
            print(f"⚠️  GitHub API rate limit: {remaining} requests remaining")
            if not token:
                print("   Consider setting GITHUB_TOKEN for higher limits (5000/hour)")
            print()
        
        logger.info("Analysis complete!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        logger.warning("Analysis interrupted")
        return 130
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("  • Verify the GitHub username is correct")
        print("  • Check your internet connection")
        print("  • Ensure GITHUB_TOKEN is valid (if provided)")
        print("  • Check GitHub API status: https://www.githubstatus.com/")
        return 1


if __name__ == '__main__':
    sys.exit(main())
