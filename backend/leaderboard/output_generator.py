"""
Output generator for leaderboard results
Generates JSON, CSV, and Markdown reports
"""

import os
import json
import csv
from typing import List
from datetime import datetime

from leaderboard import RankedCandidate
from utils import format_score
from config import OUTPUT_DIR, LEADERBOARD_JSON, LEADERBOARD_CSV, LEADERBOARD_MD


class OutputGenerator:
    """Generates output files for leaderboard"""
    
    def __init__(self, leaderboard: List[RankedCandidate], output_dir: str = None):
        """
        Initialize output generator
        
        Args:
            leaderboard: List of ranked candidates
            output_dir: Output directory (default from config)
        """
        self.leaderboard = leaderboard
        self.output_dir = output_dir or OUTPUT_DIR
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_json(self, filename: str = None) -> str:
        """
        Generate JSON output
        
        Args:
            filename: Output filename (default from config)
        
        Returns:
            Path to generated file
        """
        filename = filename or LEADERBOARD_JSON
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare data
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_candidates': len(self.leaderboard),
            'candidates': []
        }
        
        for candidate in self.leaderboard:
            data['candidates'].append({
                'rank': candidate.rank,
                'name': candidate.name,
                'combined_score': candidate.combined_score,
                'linkedin_score': candidate.linkedin_score,
                'github_score': candidate.github_score,
                'tier': candidate.tier,
                'github_username': candidate.github_username,
                'scores': {
                    'combined_percentage': f"{candidate.combined_score * 100:.2f}%",
                    'linkedin_percentage': f"{candidate.linkedin_score * 100:.2f}%",
                    'github_percentage': f"{candidate.github_score * 100:.2f}%",
                    'linkedin_raw': candidate.linkedin_raw_score,
                    'github_raw': candidate.github_raw_score
                }
            })
        
        # Write JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON saved to: {filepath}")
        return filepath
    
    def generate_csv(self, filename: str = None) -> str:
        """
        Generate CSV output
        
        Args:
            filename: Output filename (default from config)
        
        Returns:
            Path to generated file
        """
        filename = filename or LEADERBOARD_CSV
        filepath = os.path.join(self.output_dir, filename)
        
        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Rank',
                'Name',
                'Combined Score',
                'LinkedIn Score',
                'GitHub Score',
                'Tier',
                'GitHub Username'
            ])
            
            # Data
            for candidate in self.leaderboard:
                writer.writerow([
                    candidate.rank,
                    candidate.name,
                    f"{candidate.combined_score:.6f}",
                    f"{candidate.linkedin_score:.6f}",
                    f"{candidate.github_score:.6f}",
                    candidate.tier,
                    candidate.github_username or ''
                ])
        
        print(f"✅ CSV saved to: {filepath}")
        return filepath
    
    def generate_markdown(self, filename: str = None, top_n: int = None) -> str:
        """
        Generate Markdown report
        
        Args:
            filename: Output filename (default from config)
            top_n: Number of top candidates to include (None = all)
        
        Returns:
            Path to generated file
        """
        filename = filename or LEADERBOARD_MD
        filepath = os.path.join(self.output_dir, filename)
        
        candidates_to_show = self.leaderboard[:top_n] if top_n else self.leaderboard
        
        # Generate markdown content
        md_content = f"""# 🏆 Candidate Leaderboard

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Total Candidates:** {len(self.leaderboard)}
{f"**Showing Top:** {top_n}" if top_n else ""}

---

## 📊 Rankings

| Rank | Name | Combined Score | LinkedIn Score | GitHub Score | Tier |
|------|------|----------------|----------------|--------------|------|
"""
        
        for candidate in candidates_to_show:
            md_content += (
                f"| {candidate.emoji} **#{candidate.rank}** | "
                f"{candidate.name} | "
                f"**{format_score(candidate.combined_score)}** | "
                f"{format_score(candidate.linkedin_score)} | "
                f"{format_score(candidate.github_score)} | "
                f"{candidate.tier} |\n"
            )
        
        # Add tier distribution
        tier_counts = {}
        for candidate in self.leaderboard:
            tier_counts[candidate.tier] = tier_counts.get(candidate.tier, 0) + 1
        
        md_content += "\n---\n\n## 🎯 Tier Distribution\n\n"
        
        for tier, count in sorted(tier_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.leaderboard)) * 100
            md_content += f"- **{tier}**: {count} candidates ({percentage:.1f}%)\n"
        
        # Add score statistics
        scores = [c.combined_score for c in self.leaderboard]
        avg_score = sum(scores) / len(scores)
        median_score = sorted(scores)[len(scores) // 2]
        
        md_content += f"""
---

## 📈 Statistics

- **Average Score:** {format_score(avg_score)}
- **Median Score:** {format_score(median_score)}
- **Highest Score:** {format_score(max(scores))}
- **Lowest Score:** {format_score(min(scores))}

---

## 📝 Notes

- **Combined Score**: Weighted average of LinkedIn and GitHub scores
- **LinkedIn Score**: Based on resume-job description similarity (0-100%)
- **GitHub Score**: Based on comprehensive profile analysis (0-100%)
- Scores are normalized to 0-1 scale before averaging

---

*Generated by HireSight Leaderboard System*
"""
        
        # Write markdown
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ Markdown saved to: {filepath}")
        return filepath
    
    def generate_all(self) -> dict:
        """
        Generate all output formats
        
        Returns:
            Dictionary with paths to all generated files
        """
        return {
            'json': self.generate_json(),
            'csv': self.generate_csv(),
            'markdown': self.generate_markdown()
        }
