#!/usr/bin/env python3
"""
Example usage of the HireSight Leaderboard system
Demonstrates programmatic API usage
"""

from data_loader import DataLoader
from leaderboard import LeaderboardGenerator
from output_generator import OutputGenerator


def basic_example():
    """Basic usage example"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Leaderboard Generation")
    print("=" * 60)
    
    # Load data
    loader = DataLoader()
    candidates = loader.load_all_data()
    
    # Generate leaderboard with default weights (50/50)
    generator = LeaderboardGenerator(candidates)
    leaderboard = generator.calculate_scores()
    
    # Display summary
    generator.print_summary(top_n=5)
    
    # Generate output files
    output_gen = OutputGenerator(leaderboard)
    output_gen.generate_all()


def custom_weights_example():
    """Example with custom weights"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Custom Weights (GitHub 70%, LinkedIn 30%)")
    print("=" * 60)
    
    # Load data
    loader = DataLoader()
    candidates = loader.load_all_data()
    
    # Generate leaderboard with custom weights
    generator = LeaderboardGenerator(
        candidates,
        linkedin_weight=0.3,
        github_weight=0.7
    )
    leaderboard = generator.calculate_scores()
    
    # Display top 3 only
    top_3 = generator.get_top_candidates(3)
    
    print("\n🥇 Top 3 Candidates (GitHub-focused):")
    print("-" * 60)
    for candidate in top_3:
        print(f"{candidate.emoji} {candidate.rank}. {candidate.name}")
        print(f"   Combined: {candidate.combined_score*100:.2f}%")
        print(f"   GitHub: {candidate.github_score*100:.2f}% | LinkedIn: {candidate.linkedin_score*100:.2f}%")
        print(f"   Tier: {candidate.tier}\n")


def filtered_example():
    """Example with minimum score filtering"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: Filtered Leaderboard (Min Score: 0.7)")
    print("=" * 60)
    
    # Load data
    loader = DataLoader()
    candidates = loader.load_all_data()
    
    # Generate leaderboard with minimum score threshold
    generator = LeaderboardGenerator(
        candidates,
        min_score=0.7  # Only candidates scoring 70% or higher
    )
    leaderboard = generator.calculate_scores()
    
    # Get statistics
    stats = generator.get_statistics()
    
    print(f"\n📊 High-Scoring Candidates (>70%):")
    print(f"   Total: {stats['total_candidates']}")
    print(f"   Average: {stats['average_score']*100:.2f}%")
    print(f"   Range: {stats['lowest_score']*100:.2f}% - {stats['highest_score']*100:.2f}%")
    
    print(f"\n🎯 Tier Distribution:")
    for tier, count in stats['tier_distribution'].items():
        print(f"   {tier}: {count}")


def find_candidate_example():
    """Example of finding specific candidate"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 4: Find Specific Candidate")
    print("=" * 60)
    
    # Load data
    loader = DataLoader()
    candidates = loader.load_all_data()
    
    # Generate leaderboard
    generator = LeaderboardGenerator(candidates)
    generator.calculate_scores()
    
    # Find a candidate by name (replace with actual name from your data)
    # This is just an example - will return None if not found
    candidate_name = "John Doe"  # Replace with actual candidate name
    candidate = generator.get_candidate_by_name(candidate_name)
    
    if candidate:
        print(f"\n🔍 Found: {candidate.name}")
        print(f"   Rank: #{candidate.rank}")
        print(f"   Combined Score: {candidate.combined_score*100:.2f}%")
        print(f"   LinkedIn: {candidate.linkedin_score*100:.2f}%")
        print(f"   GitHub: {candidate.github_score*100:.2f}%")
        print(f"   Tier: {candidate.tier} {candidate.emoji}")
        if candidate.github_username:
            print(f"   GitHub: @{candidate.github_username}")
    else:
        print(f"\n⚠️  Candidate '{candidate_name}' not found in leaderboard")
        print("   (This is expected if you haven't replaced the example name)")


def programmatic_access_example():
    """Example of accessing data programmatically"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 5: Programmatic Data Access")
    print("=" * 60)
    
    # Load data
    loader = DataLoader()
    candidates = loader.load_all_data()
    
    # Generate leaderboard
    generator = LeaderboardGenerator(candidates)
    leaderboard = generator.calculate_scores()
    
    # Access leaderboard data programmatically
    print(f"\n📋 Accessing leaderboard data:")
    print(f"   Total candidates: {len(leaderboard)}")
    
    # Get top 3
    top_3 = leaderboard[:3]
    print(f"\n   Top 3 names: {[c.name for c in top_3]}")
    
    # Filter by tier
    excellent_matches = [c for c in leaderboard if c.tier == "Excellent Match"]
    print(f"   Excellent matches: {len(excellent_matches)}")
    
    # Calculate custom metrics
    avg_linkedin = sum(c.linkedin_score for c in leaderboard) / len(leaderboard)
    avg_github = sum(c.github_score for c in leaderboard) / len(leaderboard)
    
    print(f"\n   Average LinkedIn score: {avg_linkedin*100:.2f}%")
    print(f"   Average GitHub score: {avg_github*100:.2f}%")


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        HireSight Leaderboard - Usage Examples               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Run all examples
        basic_example()
        custom_weights_example()
        filtered_example()
        find_candidate_example()
        programmatic_access_example()
        
        print("\n\n✨ All examples completed!")
        print("Check the 'output/' directory for generated files.\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: Required data files not found.")
        print(f"   {e}")
        print("\nPlease ensure:")
        print("  1. LinkedIn data exists: ../ibhanwork/results.csv")
        print("  2. GitHub data exists: ../github-data-fetch/reports/")
        print("\nRun the respective systems first, then try again.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
