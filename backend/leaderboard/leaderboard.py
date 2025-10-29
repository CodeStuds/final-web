"""
Leaderboard generator module
Calculates combined scores and ranks candidates
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass

from data_loader import CandidateScore
from utils import calculate_combined_score, classify_score, format_score
from config import LINKEDIN_WEIGHT, GITHUB_WEIGHT, MIN_SCORE_THRESHOLD


@dataclass
class RankedCandidate:
    """Data class for ranked candidate with combined score"""
    rank: int
    name: str
    combined_score: float
    linkedin_score: float
    github_score: float
    tier: str
    emoji: str
    github_username: str = None
    
    # Raw scores for reference
    linkedin_raw_score: float = None
    github_raw_score: float = None


class LeaderboardGenerator:
    """Generates ranked leaderboard from candidate scores"""
    
    def __init__(
        self,
        candidates: Dict[str, CandidateScore],
        linkedin_weight: float = None,
        github_weight: float = None,
        min_score: float = None
    ):
        """
        Initialize leaderboard generator
        
        Args:
            candidates: Dictionary of candidate scores
            linkedin_weight: Weight for LinkedIn score (default from config)
            github_weight: Weight for GitHub score (default from config)
            min_score: Minimum score threshold (default from config)
        """
        self.candidates = candidates
        self.linkedin_weight = linkedin_weight or LINKEDIN_WEIGHT
        self.github_weight = github_weight or GITHUB_WEIGHT
        self.min_score = min_score if min_score is not None else MIN_SCORE_THRESHOLD
        
        self.leaderboard: List[RankedCandidate] = []
    
    def calculate_scores(self) -> List[RankedCandidate]:
        """
        Calculate combined scores for all candidates
        
        Returns:
            List of ranked candidates
        """
        scored_candidates = []
        
        for norm_name, candidate in self.candidates.items():
            # Handle missing scores
            linkedin_score = candidate.linkedin_score if candidate.linkedin_score is not None else 0.0
            github_score = candidate.github_score if candidate.github_score is not None else 0.0
            
            # Skip if both scores are 0
            if linkedin_score == 0.0 and github_score == 0.0:
                continue
            
            # Calculate combined score with weights
            # If only one score available, use it with full weight
            if linkedin_score > 0 and github_score == 0:
                combined_score = linkedin_score
            elif github_score > 0 and linkedin_score == 0:
                combined_score = github_score
            else:
                combined_score = calculate_combined_score(
                    linkedin_score,
                    github_score,
                    self.linkedin_weight,
                    self.github_weight
                )
            
            # Apply minimum score threshold
            if combined_score < self.min_score:
                continue
            
            # Classify score
            tier, emoji = classify_score(combined_score)
            
            scored_candidates.append({
                'name': candidate.name,
                'combined_score': combined_score,
                'linkedin_score': linkedin_score,
                'github_score': github_score,
                'tier': tier,
                'emoji': emoji,
                'github_username': candidate.github_username,
                'linkedin_raw_score': candidate.linkedin_raw_score,
                'github_raw_score': candidate.github_raw_score
            })
        
        # Sort by combined score (descending)
        scored_candidates.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Add ranks
        self.leaderboard = []
        for rank, candidate_data in enumerate(scored_candidates, start=1):
            self.leaderboard.append(RankedCandidate(
                rank=rank,
                **candidate_data
            ))
        
        return self.leaderboard
    
    def get_top_candidates(self, n: int = 10) -> List[RankedCandidate]:
        """
        Get top N candidates
        
        Args:
            n: Number of candidates to return
        
        Returns:
            List of top N ranked candidates
        """
        if not self.leaderboard:
            self.calculate_scores()
        
        return self.leaderboard[:n]
    
    def get_candidate_by_name(self, name: str) -> RankedCandidate:
        """
        Get specific candidate by name
        
        Args:
            name: Candidate name
        
        Returns:
            Ranked candidate or None
        """
        if not self.leaderboard:
            self.calculate_scores()
        
        for candidate in self.leaderboard:
            if candidate.name.lower() == name.lower():
                return candidate
        
        return None
    
    def get_statistics(self) -> Dict:
        """
        Calculate leaderboard statistics
        
        Returns:
            Dictionary of statistics
        """
        if not self.leaderboard:
            self.calculate_scores()
        
        if not self.leaderboard:
            return {
                'total_candidates': 0,
                'average_score': 0,
                'median_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
                'tier_distribution': {}
            }
        
        scores = [c.combined_score for c in self.leaderboard]
        
        # Tier distribution
        tier_counts = {}
        for candidate in self.leaderboard:
            tier = candidate.tier
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        return {
            'total_candidates': len(self.leaderboard),
            'average_score': sum(scores) / len(scores),
            'median_score': sorted(scores)[len(scores) // 2],
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'tier_distribution': tier_counts,
            'linkedin_weight': self.linkedin_weight,
            'github_weight': self.github_weight
        }
    
    def print_summary(self, top_n: int = 10):
        """
        Print leaderboard summary to console
        
        Args:
            top_n: Number of top candidates to display
        """
        if not self.leaderboard:
            self.calculate_scores()
        
        stats = self.get_statistics()
        top_candidates = self.get_top_candidates(top_n)
        
        print("\n" + "=" * 80)
        print("🏆 CANDIDATE LEADERBOARD - TOP COMPATIBLE CANDIDATES")
        print("=" * 80)
        
        print(f"\n📊 Statistics:")
        print(f"   Total Candidates: {stats['total_candidates']}")
        print(f"   Average Score: {format_score(stats['average_score'])}")
        print(f"   Median Score: {format_score(stats['median_score'])}")
        print(f"   Score Range: {format_score(stats['lowest_score'])} - {format_score(stats['highest_score'])}")
        
        print(f"\n⚖️  Weights:")
        print(f"   LinkedIn: {self.linkedin_weight * 100:.0f}%")
        print(f"   GitHub: {self.github_weight * 100:.0f}%")
        
        print(f"\n🎯 Tier Distribution:")
        for tier, count in sorted(stats['tier_distribution'].items(), 
                                  key=lambda x: x[1], reverse=True):
            print(f"   {tier}: {count} candidates")
        
        print(f"\n🥇 Top {min(top_n, len(top_candidates))} Candidates:")
        print("-" * 80)
        print(f"{'Rank':<6} {'Name':<25} {'Combined':<12} {'LinkedIn':<12} {'GitHub':<12} {'Tier':<10}")
        print("-" * 80)
        
        for candidate in top_candidates:
            print(
                f"{candidate.emoji} {candidate.rank:<3} "
                f"{candidate.name:<25} "
                f"{format_score(candidate.combined_score):<12} "
                f"{format_score(candidate.linkedin_score):<12} "
                f"{format_score(candidate.github_score):<12} "
                f"{candidate.tier}"
            )
        
        print("=" * 80)
