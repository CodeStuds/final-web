#!/usr/bin/env python3
"""
HireSight Leaderboard System
Combines LinkedIn and GitHub scores to rank candidates
"""

import argparse
import sys
import os

from data_loader import DataLoader
from leaderboard import LeaderboardGenerator
from output_generator import OutputGenerator
from config import (
    LINKEDIN_DATA_PATH, GITHUB_DATA_PATH, OUTPUT_DIR,
    LINKEDIN_WEIGHT, GITHUB_WEIGHT, TOP_CANDIDATES_DISPLAY
)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='HireSight Leaderboard - Rank candidates by combined LinkedIn and GitHub scores',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --linkedin-weight 0.6 --github-weight 0.4
  python main.py --top 20 --min-score 0.5
  python main.py --linkedin-path ../ibhanwork/results.csv --github-path ../github-data-fetch/reports
        """
    )
    
    parser.add_argument(
        '--linkedin-path',
        type=str,
        default=LINKEDIN_DATA_PATH,
        help=f'Path to LinkedIn results CSV (default: {LINKEDIN_DATA_PATH})'
    )
    
    parser.add_argument(
        '--github-path',
        type=str,
        default=GITHUB_DATA_PATH,
        help=f'Path to GitHub reports directory (default: {GITHUB_DATA_PATH})'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=OUTPUT_DIR,
        help=f'Output directory for generated files (default: {OUTPUT_DIR})'
    )
    
    parser.add_argument(
        '--linkedin-weight',
        type=float,
        default=LINKEDIN_WEIGHT,
        help=f'Weight for LinkedIn score (default: {LINKEDIN_WEIGHT})'
    )
    
    parser.add_argument(
        '--github-weight',
        type=float,
        default=GITHUB_WEIGHT,
        help=f'Weight for GitHub score (default: {GITHUB_WEIGHT})'
    )
    
    parser.add_argument(
        '--min-score',
        type=float,
        default=0.0,
        help='Minimum combined score threshold (default: 0.0)'
    )
    
    parser.add_argument(
        '--top',
        type=int,
        default=TOP_CANDIDATES_DISPLAY,
        help=f'Number of top candidates to display (default: {TOP_CANDIDATES_DISPLAY})'
    )
    
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='Generate only JSON output (skip CSV and Markdown)'
    )
    
    parser.add_argument(
        '--no-output',
        action='store_true',
        help='Skip generating output files (console only)'
    )
    
    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Print banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              H I R E S I G H T  L E A D E R B O A R D        ║
║           Rank Best Compatible Candidates                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Step 1: Load data
        print("📥 Loading candidate data...")
        loader = DataLoader(
            linkedin_path=args.linkedin_path,
            github_path=args.github_path
        )
        candidates = loader.load_all_data()
        
        if not candidates:
            print("\n❌ No candidate data found!")
            print("\nPlease ensure:")
            print(f"  • LinkedIn data exists at: {args.linkedin_path}")
            print(f"  • GitHub data exists at: {args.github_path}")
            return 1
        
        # Step 2: Generate leaderboard
        print(f"\n⚙️  Generating leaderboard...")
        print(f"   LinkedIn weight: {args.linkedin_weight * 100:.0f}%")
        print(f"   GitHub weight: {args.github_weight * 100:.0f}%")
        
        generator = LeaderboardGenerator(
            candidates=candidates,
            linkedin_weight=args.linkedin_weight,
            github_weight=args.github_weight,
            min_score=args.min_score
        )
        
        leaderboard = generator.calculate_scores()
        
        if not leaderboard:
            print("\n⚠️  No candidates meet the minimum score threshold!")
            print(f"   Try lowering --min-score (current: {args.min_score})")
            return 1
        
        # Step 3: Display summary
        generator.print_summary(top_n=args.top)
        
        # Step 4: Generate output files
        if not args.no_output:
            print(f"\n📝 Generating output files...")
            
            output_gen = OutputGenerator(
                leaderboard=leaderboard,
                output_dir=args.output_dir
            )
            
            if args.json_only:
                output_gen.generate_json()
            else:
                outputs = output_gen.generate_all()
                print(f"\n✅ All reports generated successfully!")
                print(f"   Output directory: {os.path.abspath(args.output_dir)}")
        
        print("\n✨ Leaderboard generation complete!\n")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 130
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        print("\nTroubleshooting:")
        print("  • Verify data paths are correct")
        print("  • Check that data files are properly formatted")
        print("  • Ensure you have read/write permissions")
        return 1


if __name__ == '__main__':
    sys.exit(main())
