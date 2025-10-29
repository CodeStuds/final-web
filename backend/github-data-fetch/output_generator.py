"""
Output Generator Module for HireSight
Formats analysis results into JSON and Markdown reports
"""

import json
from datetime import datetime
from typing import Dict, Any

from utils import logger, sanitize_filename, format_number


class OutputGenerator:
    """Generates formatted output files"""
    
    def __init__(self, username: str, analysis: Dict[str, Any], match_results: Dict[str, Any]):
        """
        Initialize with analysis and matching results
        """
        self.username = username
        self.analysis = analysis
        self.match_results = match_results
    
    def generate_json_output(self, filename: str = None) -> str:
        """
        Generate comprehensive JSON output
        Returns: filename of created file
        """
        if filename is None:
            safe_username = sanitize_filename(self.username)
            filename = f"analysis_{safe_username}.json"
        
        logger.info(f"Generating JSON output: {filename}")
        
        output_data = {
            'candidate': {
                'username': self.username,
                'profile': self.analysis['profile_metadata']
            },
            'analysis': {
                'skills': self.analysis['skills_analysis'],
                'contribution_patterns': self.analysis['contribution_patterns'],
                'work_style': self.analysis['work_style'],
                'code_quality': self.analysis['code_quality'],
                'learning_trajectory': self.analysis['learning_trajectory']
            },
            'matching': self.match_results,
            'metadata': {
                'analyzed_at': self.analysis['analyzed_at'],
                'tool': 'HireSight',
                'version': '1.0.0'
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON output saved to {filename}")
        return filename
    
    def generate_markdown_report(self, filename: str = None) -> str:
        """
        Generate human-readable Markdown report
        Returns: filename of created file
        """
        if filename is None:
            safe_username = sanitize_filename(self.username)
            filename = f"report_{safe_username}.md"
        
        logger.info(f"Generating Markdown report: {filename}")
        
        md = []
        
        # Header
        md.append("# HireSight GitHub Profile Analysis Report")
        md.append("")
        md.append(f"**Candidate:** {self.username}")
        md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append("")
        md.append("---")
        md.append("")
        
        # Executive Summary
        md.append("## 📊 Executive Summary")
        md.append("")
        profile = self.analysis['profile_metadata']
        match = self.match_results
        
        md.append(f"**Overall Match Score:** {match['overall_score']:.1f}/100 ({match['tier']})")
        md.append(f"**Account Age:** {profile.get('account_age_months', 0)} months")
        md.append(f"**Public Repositories:** {profile.get('public_repos', 0)}")
        md.append(f"**Followers:** {profile.get('followers', 0)}")
        md.append("")
        
        # Profile Information
        md.append("## 👤 Profile Information")
        md.append("")
        if profile.get('name'):
            md.append(f"**Name:** {profile['name']}")
        if profile.get('bio'):
            md.append(f"**Bio:** {profile['bio']}")
        if profile.get('location'):
            md.append(f"**Location:** {profile['location']}")
        if profile.get('company'):
            md.append(f"**Company:** {profile['company']}")
        if profile.get('email'):
            md.append(f"**Email:** {profile['email']}")
        md.append("")
        
        # Match Results
        md.append("## 🎯 Matching Results")
        md.append("")
        md.append(f"### Overall Score: {match['overall_score']:.1f}/100")
        md.append(f"**Classification:** {match['tier']}")
        md.append("")
        
        # Component Scores
        md.append("#### Component Breakdown")
        md.append("")
        components = match['components']
        md.append(f"- **Current Fit:** {components['current_fit']['score']:.1f}/100 (Weight: 40%)")
        md.append(f"- **Growth Potential:** {components['growth_potential']['score']:.1f}/100 (Weight: 30%)")
        md.append(f"- **Collaboration Fit:** {components['collaboration_fit']['score']:.1f}/100 (Weight: 20%)")
        md.append(f"- **Code Quality:** {components['code_quality']['score']:.1f}/100 (Weight: 10%)")
        md.append("")
        
        # Skills Analysis
        md.append("## 💻 Skills Analysis")
        md.append("")
        skills = self.analysis['skills_analysis']
        md.append(f"**Total Skills Identified:** {skills['skill_count']}")
        md.append("")
        
        md.append("### Top 10 Skills (by Confidence)")
        md.append("")
        md.append("| Skill | Confidence | Category | Last Used | Repos |")
        md.append("|-------|------------|----------|-----------|-------|")
        
        for skill_name in skills['top_skills'][:10]:
            skill_data = skills['skills'][skill_name]
            last_used = skill_data.get('last_used', 'N/A')
            if last_used != 'N/A' and last_used:
                last_used = last_used.split('T')[0]  # Just date
            md.append(
                f"| {skill_name} | {skill_data['confidence']:.1f}/100 | "
                f"{skill_data['category']} | {last_used} | {skill_data['repo_count']} |"
            )
        md.append("")
        
        # Current Fit Details
        md.append("### 🎯 Current Fit Analysis")
        md.append("")
        current_fit = components['current_fit']
        md.append(f"**Required Skills Match:** {current_fit['match_percentage']:.1f}%")
        md.append("")
        
        if current_fit['required_skills_match']:
            md.append("**✅ Matching Required Skills:**")
            for skill in current_fit['required_skills_match']:
                md.append(f"- {skill}")
            md.append("")
        
        if current_fit['skill_gaps']:
            md.append("**❌ Missing Required Skills:**")
            for skill in current_fit['skill_gaps']:
                md.append(f"- {skill}")
            md.append("")
        
        if current_fit.get('preferred_skills_match'):
            md.append("**⭐ Matching Preferred Skills:**")
            for skill in current_fit['preferred_skills_match']:
                md.append(f"- {skill}")
            md.append("")
        
        # Growth Potential
        md.append("## 📈 Growth Potential")
        md.append("")
        growth = components['growth_potential']
        md.append(f"**Classification:** {growth['growth_classification']}")
        md.append(f"**Adaptability Score:** {growth['adaptability_score']:.1f}/100")
        md.append(f"**Learning Velocity:** {growth['learning_velocity']:.3f} skills/month")
        md.append(f"**New Skills (Last Year):** {growth['new_skills_last_year']}")
        md.append("")
        
        if growth.get('ramp_up_estimates'):
            md.append("### ⏱️ Estimated Ramp-up Time for Missing Skills")
            md.append("")
            for skill, estimate in growth['ramp_up_estimates'].items():
                md.append(f"- **{skill}:** {estimate}")
            md.append("")
        
        # Learning Trajectory
        learning = self.analysis['learning_trajectory']
        if learning.get('recent_skills'):
            md.append("### 🆕 Recent Skills (Last 6 Months)")
            md.append("")
            for skill in learning['recent_skills'][:5]:
                md.append(f"- {skill}")
            md.append("")
        
        # Work Style
        md.append("## 🤝 Work Style & Collaboration")
        md.append("")
        work_style = self.analysis['work_style']
        collab = components['collaboration_fit']
        
        md.append(f"**Primary Work Style:** {work_style['primary_style']}")
        md.append(f"**Required Style:** {collab['required_style'].title()}")
        md.append(f"**Collaboration Score:** {collab['score']:.1f}/100")
        md.append("")
        
        md.append("### Work Style Indicators")
        md.append("")
        for style_info in work_style['all_styles']:
            md.append(f"**{style_info['style']}** (Confidence: {style_info['confidence']:.1f}/100)")
            for indicator in style_info['indicators']:
                md.append(f"  - {indicator}")
            md.append("")
        
        # Contribution Patterns
        md.append("## 📊 Contribution Patterns")
        md.append("")
        contrib = self.analysis['contribution_patterns']
        
        # Commits
        commit_data = contrib['commit_behavior']
        md.append("### Commit Behavior")
        md.append("")
        md.append(f"- **Total Commits (12mo):** {commit_data['total_commits']}")
        md.append(f"- **Code Changes:** +{format_number(commit_data['total_additions'])} / -{format_number(commit_data['total_deletions'])}")
        md.append(f"- **Avg Message Length:** {commit_data['avg_message_length']:.1f} characters")
        md.append(f"- **Conventional Commits:** {commit_data['conventional_commit_percentage']:.1f}%")
        md.append(f"- **Consistency Score:** {commit_data['consistency_score']:.1f}/100")
        md.append("")
        
        # Pull Requests
        pr_data = contrib['pull_request_activity']
        md.append("### Pull Request Activity")
        md.append("")
        md.append(f"- **PRs Created:** {pr_data['total_prs_created']}")
        md.append(f"- **PRs Merged:** {pr_data['total_prs_merged']}")
        md.append(f"- **Merge Rate:** {pr_data['merge_rate_percentage']:.1f}%")
        md.append(f"- **Avg Comments/PR:** {pr_data['avg_comments_per_pr']:.1f}")
        md.append(f"- **Avg PR Size:** {format_number(pr_data['avg_pr_size'])} lines")
        md.append("")
        
        # Code Reviews
        review_data = contrib['code_review_behavior']
        md.append("### Code Review Behavior")
        md.append("")
        md.append(f"- **Reviews Given:** {review_data['total_reviews_given']}")
        md.append(f"- **Avg Review Length:** {format_number(review_data['avg_review_length'])} characters")
        md.append(f"- **Sentiment:** {review_data['sentiment_classification'].title()}")
        md.append(f"- **Review/PR Ratio:** {review_data['review_to_pr_ratio']:.2f}")
        md.append("")
        
        # Code Quality
        md.append("## ✨ Code Quality Assessment")
        md.append("")
        quality = self.analysis['code_quality']
        aggregate = quality['aggregate_scores']
        
        md.append(f"**Overall Quality:** {aggregate['overall']:.1f}/100 ({quality['quality_tier']})")
        md.append("")
        md.append("### Quality Metrics")
        md.append("")
        md.append(f"- **Documentation:** {aggregate['documentation']:.1f}/100")
        md.append(f"- **Testing Practices:** {aggregate['testing']:.1f}/100")
        md.append(f"- **Maintenance:** {aggregate['maintenance']:.1f}/100")
        md.append("")
        
        # Recommendations
        md.append("## 💡 Recommendations")
        md.append("")
        recs = match['recommendations']
        
        if recs['strengths']:
            md.append("### ✅ Strengths")
            md.append("")
            for strength in recs['strengths']:
                md.append(f"- {strength}")
            md.append("")
        
        if recs['considerations']:
            md.append("### ⚠️ Considerations")
            md.append("")
            for consideration in recs['considerations']:
                md.append(f"- {consideration}")
            md.append("")
        
        if recs['interview_questions']:
            md.append("### ❓ Suggested Interview Questions")
            md.append("")
            for i, question in enumerate(recs['interview_questions'], 1):
                md.append(f"{i}. {question}")
            md.append("")
        
        # Bias Detection
        if 'bias_analysis' in match:
            bias = match['bias_analysis']
            md.append("## ⚖️ Bias & Fairness Analysis")
            md.append("")
            md.append(f"**Fairness Score:** {bias['fairness_score']:.1f}/100")
            md.append("")
            
            if bias['biases_found']:
                md.append(f"**⚠️ {bias['bias_count']} Potential Bias(es) Detected**")
                md.append("")
                for bias_item in bias['biases']:
                    md.append(f"### {bias_item['type']} (Severity: {bias_item['severity'].upper()})")
                    md.append(f"- **Issue:** {bias_item['description']}")
                    md.append(f"- **Recommendation:** {bias_item['recommendation']}")
                    md.append("")
            else:
                md.append("✅ No significant biases detected in job requirements.")
                md.append("")
        
        # Footer
        md.append("---")
        md.append("")
        md.append("*Generated by HireSight - Comprehensive GitHub Profile Analysis for Developer Hiring*")
        md.append("")
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md))
        
        logger.info(f"Markdown report saved to {filename}")
        return filename
    
    def generate_summary(self) -> str:
        """
        Generate a quick text summary for console output
        Returns: summary string
        """
        match = self.match_results
        skills = self.analysis['skills_analysis']
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║              HIRESIGHT ANALYSIS SUMMARY                      ║
╚══════════════════════════════════════════════════════════════╝

Candidate: {self.username}
Overall Match: {match['overall_score']:.1f}/100 ({match['tier']})

Skills: {skills['skill_count']} identified
Top Skills: {', '.join(skills['top_skills'][:5])}

Components:
  • Current Fit:        {match['components']['current_fit']['score']:.1f}/100
  • Growth Potential:   {match['components']['growth_potential']['score']:.1f}/100
  • Collaboration Fit:  {match['components']['collaboration_fit']['score']:.1f}/100
  • Code Quality:       {match['components']['code_quality']['score']:.1f}/100

Work Style: {self.analysis['work_style']['primary_style']}
Quality Tier: {self.analysis['code_quality']['quality_tier']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return summary
    
    def generate_all(self) -> Dict[str, str]:
        """
        Generate all output formats
        Returns: dict of filenames
        """
        logger.info("Generating all output formats...")
        
        json_file = self.generate_json_output()
        md_file = self.generate_markdown_report()
        summary = self.generate_summary()
        
        print(summary)
        
        return {
            'json': json_file,
            'markdown': md_file,
            'summary': summary
        }
