"""
Analyzer Module for HireSight
Core analysis logic for skills, work style, code quality, and learning trajectory
"""

from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import statistics
from textblob import TextBlob

from utils import (
    logger, safe_divide, calculate_recency_score, calculate_months_ago,
    calculate_contribution_consistency, detect_conventional_commits,
    calculate_average_commit_message_length, normalize_score
)
from config import (
    DEPENDENCY_MAPPINGS, TESTING_FRAMEWORKS, SCORING_WEIGHTS,
    QUALITY_WEIGHTS, WORK_STYLE_THRESHOLDS, RECENCY_DECAY_MONTHS
)


class GitHubAnalyzer:
    """Performs comprehensive analysis on GitHub data"""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize with fetched GitHub data"""
        self.data = data
        self.profile = data.get('profile', {})
        self.all_repos = data.get('all_repositories', [])
        self.top_repos = data.get('top_repositories', [])
    
    def analyze_skills(self) -> Dict[str, Any]:
        """
        Analyze and score skills based on evidence from repos
        Returns: Skill inventory with confidence scores (0-100)
        """
        logger.info("Analyzing skills...")
        
        skills = defaultdict(lambda: {
            'confidence': 0,
            'lines_of_code': 0,
            'repo_count': 0,
            'last_used': None,
            'complexity_score': 0,
            'evidence': []
        })
        
        # 1. Analyze languages from GitHub stats
        for repo in self.top_repos:
            languages = repo.get('languages', {})
            total_bytes = sum(languages.values())
            
            for lang, bytes_count in languages.items():
                if lang:
                    skills[lang]['lines_of_code'] += bytes_count
                    skills[lang]['repo_count'] += 1
                    skills[lang]['evidence'].append(f"Used in {repo['name']}")
                    
                    # Update last used date
                    pushed_at = repo.get('pushed_at')
                    if pushed_at:
                        pushed_date = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
                        if not skills[lang]['last_used'] or pushed_date > skills[lang]['last_used']:
                            skills[lang]['last_used'] = pushed_date
                    
                    # Complexity based on repo size and stars
                    complexity = (
                        repo.get('size', 0) / 1000 +  # Size in MB
                        repo.get('stargazers_count', 0) * 2 +
                        (bytes_count / max(1, total_bytes)) * 10
                    )
                    skills[lang]['complexity_score'] += complexity
        
        # 2. Analyze frameworks and tools from dependencies
        for repo in self.top_repos:
            dependencies = repo.get('dependencies', [])
            
            for dep in dependencies:
                dep_lower = dep.lower().replace('-', '').replace('_', '')
                
                # Match against known frameworks/tools
                for known_dep, info in DEPENDENCY_MAPPINGS.items():
                    known_lower = known_dep.lower().replace('-', '').replace('_', '')
                    
                    if known_lower in dep_lower or dep_lower in known_lower:
                        skill_name = info['name']
                        skills[skill_name]['repo_count'] += 1
                        skills[skill_name]['evidence'].append(f"Used in {repo['name']}")
                        
                        # Update last used
                        pushed_at = repo.get('pushed_at')
                        if pushed_at:
                            pushed_date = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
                            if not skills[skill_name]['last_used'] or pushed_date > skills[skill_name]['last_used']:
                                skills[skill_name]['last_used'] = pushed_date
                        
                        # Complexity score
                        complexity = repo.get('stargazers_count', 0) + repo.get('size', 0) / 1000
                        skills[skill_name]['complexity_score'] += complexity
        
        # 3. Detect testing frameworks
        for repo in self.top_repos:
            dependencies = repo.get('dependencies', [])
            
            for test_framework in TESTING_FRAMEWORKS:
                if any(test_framework.lower() in dep.lower() for dep in dependencies):
                    skill_name = f"{test_framework.title()} Testing"
                    skills[skill_name]['repo_count'] += 1
                    skills[skill_name]['evidence'].append(f"Testing in {repo['name']}")
        
        # 4. Detect CI/CD tools
        for repo in self.top_repos:
            cicd_tools = repo.get('cicd_tools', {})
            for tool, present in cicd_tools.items():
                if present:
                    tool_name = tool.replace('_', ' ').title()
                    skills[tool_name]['repo_count'] += 1
                    skills[tool_name]['evidence'].append(f"CI/CD in {repo['name']}")
        
        # 5. Calculate confidence scores for each skill
        max_loc = max([s['lines_of_code'] for s in skills.values()] + [1])
        max_repos = max([s['repo_count'] for s in skills.values()] + [1])
        max_complexity = max([s['complexity_score'] for s in skills.values()] + [1])
        
        scored_skills = {}
        for skill_name, skill_data in skills.items():
            # Lines of code score (0-20)
            loc_score = (skill_data['lines_of_code'] / max_loc) * SCORING_WEIGHTS['lines_of_code_max']
            
            # Repository count score (0-30)
            repo_score = (skill_data['repo_count'] / max_repos) * SCORING_WEIGHTS['repo_count_max']
            
            # Recency score (0-30)
            if skill_data['last_used']:
                recency_score = calculate_recency_score(
                    skill_data['last_used'],
                    max_months=RECENCY_DECAY_MONTHS,
                    max_score=SCORING_WEIGHTS['recency_max']
                )
            else:
                recency_score = 0
            
            # Complexity score (0-20)
            complexity_score = (skill_data['complexity_score'] / max_complexity) * SCORING_WEIGHTS['complexity_max']
            
            # Total confidence (0-100)
            total_confidence = loc_score + repo_score + recency_score + complexity_score
            
            scored_skills[skill_name] = {
                'confidence': round(total_confidence, 2),
                'repo_count': skill_data['repo_count'],
                'last_used': skill_data['last_used'].isoformat() if skill_data['last_used'] else None,
                'category': self._categorize_skill(skill_name),
                'evidence': skill_data['evidence'][:3]  # Top 3 evidence
            }
        
        # Sort by confidence
        sorted_skills = dict(sorted(scored_skills.items(), key=lambda x: x[1]['confidence'], reverse=True))
        
        logger.info(f"Identified {len(sorted_skills)} skills")
        return {
            'skills': sorted_skills,
            'top_skills': list(sorted_skills.keys())[:10],
            'skill_count': len(sorted_skills)
        }
    
    def _categorize_skill(self, skill_name: str) -> str:
        """Categorize a skill into type"""
        skill_lower = skill_name.lower()
        
        # Check in mappings
        for dep, info in DEPENDENCY_MAPPINGS.items():
            if info['name'].lower() == skill_lower:
                return info['category']
        
        # Default categories based on keywords
        if any(lang in skill_lower for lang in ['python', 'javascript', 'java', 'go', 'rust', 'ruby', 'php', 'typescript']):
            return 'Language'
        elif 'testing' in skill_lower or 'test' in skill_lower:
            return 'Testing'
        elif any(tool in skill_lower for tool in ['docker', 'kubernetes', 'ci', 'cd', 'jenkins']):
            return 'DevOps'
        elif any(db in skill_lower for db in ['sql', 'mongo', 'redis', 'database']):
            return 'Database'
        else:
            return 'Tool'
    
    def analyze_contribution_patterns(self) -> Dict[str, Any]:
        """
        Analyze commit behavior, PR activity, and code review patterns
        Returns: Contribution pattern analysis
        """
        logger.info("Analyzing contribution patterns...")
        
        all_commits = []
        all_prs = []
        all_reviews = []
        
        for repo in self.top_repos:
            all_commits.extend(repo.get('commits', []))
            all_prs.extend(repo.get('pull_requests', []))
            all_reviews.extend(repo.get('code_reviews', []))
        
        # 1. Commit behavior analysis
        commit_dates = []
        commit_messages = []
        total_additions = 0
        total_deletions = 0
        
        for commit in all_commits:
            if commit.get('date'):
                commit_dates.append(datetime.fromisoformat(commit['date'].replace('Z', '+00:00')))
            commit_messages.append(commit.get('message', ''))
            total_additions += commit.get('additions', 0)
            total_deletions += commit.get('deletions', 0)
        
        # Commit frequency
        commit_frequency = len(all_commits)
        
        # Consistency score
        consistency_score = calculate_contribution_consistency(commit_dates)
        
        # Message quality
        avg_message_length = calculate_average_commit_message_length(commit_messages)
        conventional_commits = detect_conventional_commits(commit_messages)
        
        commit_analysis = {
            'total_commits': commit_frequency,
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'avg_message_length': round(avg_message_length, 2),
            'uses_conventional_commits': conventional_commits['follows_convention'],
            'conventional_commit_percentage': round(conventional_commits['usage_percentage'], 2),
            'consistency_score': round(consistency_score, 2),
        }
        
        # 2. Pull Request analysis
        pr_created = len(all_prs)
        pr_merged = sum(1 for pr in all_prs if pr.get('merged'))
        pr_merge_rate = safe_divide(pr_merged, pr_created, 0) * 100
        
        avg_pr_comments = safe_divide(
            sum(pr.get('comments_count', 0) + pr.get('review_comments_count', 0) for pr in all_prs),
            len(all_prs),
            0
        )
        
        avg_pr_size = safe_divide(
            sum(pr.get('additions', 0) + pr.get('deletions', 0) for pr in all_prs),
            len(all_prs),
            0
        )
        
        pr_analysis = {
            'total_prs_created': pr_created,
            'total_prs_merged': pr_merged,
            'merge_rate_percentage': round(pr_merge_rate, 2),
            'avg_comments_per_pr': round(avg_pr_comments, 2),
            'avg_pr_size': round(avg_pr_size, 2),
        }
        
        # 3. Code Review analysis
        review_count = len(all_reviews)
        
        # Review thoroughness (based on comment length)
        review_bodies = [r.get('body', '') for r in all_reviews if r.get('body')]
        avg_review_length = safe_divide(sum(len(body) for body in review_bodies), len(review_bodies), 0)
        
        # Sentiment analysis on reviews
        sentiments = []
        for review in all_reviews:
            body = review.get('body', '')
            if body:
                try:
                    blob = TextBlob(body)
                    sentiments.append(blob.sentiment.polarity)  # -1 to 1
                except:
                    pass
        
        avg_sentiment = safe_divide(sum(sentiments), len(sentiments), 0)
        
        # Classify sentiment
        if avg_sentiment > 0.1:
            sentiment_classification = 'positive'
        elif avg_sentiment < -0.1:
            sentiment_classification = 'critical'
        else:
            sentiment_classification = 'neutral'
        
        review_analysis = {
            'total_reviews_given': review_count,
            'avg_review_length': round(avg_review_length, 2),
            'avg_sentiment': round(avg_sentiment, 3),
            'sentiment_classification': sentiment_classification,
            'review_to_pr_ratio': round(safe_divide(review_count, pr_created, 0), 2),
        }
        
        return {
            'commit_behavior': commit_analysis,
            'pull_request_activity': pr_analysis,
            'code_review_behavior': review_analysis,
        }
    
    def classify_work_style(self, contribution_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify work style based on contribution patterns
        Returns: Work style classification with confidence
        """
        logger.info("Classifying work style...")
        
        # Extract relevant metrics
        pr_activity = contribution_patterns['pull_request_activity']
        review_activity = contribution_patterns['code_review_behavior']
        commit_activity = contribution_patterns['commit_behavior']
        
        # Calculate ownership percentage (simplified - we don't have full contributor data)
        # Instead, use PR merge rate as proxy for ownership
        merge_rate = pr_activity['merge_rate_percentage'] / 100
        
        # Review-to-PR ratio
        review_ratio = review_activity['review_to_pr_ratio']
        
        # Conventional commits usage (indicates async-friendly)
        conventional_usage = commit_activity['conventional_commit_percentage'] / 100
        
        # Review sentiment
        sentiment = review_activity['sentiment_classification']
        
        # Classification logic
        work_styles = []
        
        # Solo Developer
        if merge_rate > WORK_STYLE_THRESHOLDS['solo_developer_threshold']:
            work_styles.append({
                'style': 'Solo Developer',
                'confidence': round(merge_rate * 100, 2),
                'indicators': [
                    f"High merge rate ({pr_activity['merge_rate_percentage']:.1f}%)",
                    "Independent project ownership",
                    "Self-directed work patterns"
                ]
            })
        
        # Collaborative
        if review_ratio > WORK_STYLE_THRESHOLDS['high_review_ratio'] or pr_activity['avg_comments_per_pr'] > 3:
            collaboration_score = min(100, (review_ratio * 100 + pr_activity['avg_comments_per_pr'] * 10))
            work_styles.append({
                'style': 'Collaborative',
                'confidence': round(collaboration_score, 2),
                'indicators': [
                    f"Active in code discussions ({pr_activity['avg_comments_per_pr']:.1f} comments/PR)",
                    f"High review engagement (ratio: {review_ratio:.2f})",
                    "Balanced merge rates"
                ]
            })
        
        # Mentorship
        if (review_activity['avg_review_length'] > WORK_STYLE_THRESHOLDS['mentorship_comment_length'] and
            sentiment == 'positive'):
            mentorship_score = min(100, review_activity['avg_review_length'] / 3)
            work_styles.append({
                'style': 'Mentorship',
                'confidence': round(mentorship_score, 2),
                'indicators': [
                    f"Detailed reviews ({review_activity['avg_review_length']:.0f} chars avg)",
                    f"Positive feedback sentiment ({sentiment})",
                    "Knowledge sharing patterns"
                ]
            })
        
        # Async-Friendly
        if conventional_usage > 0.5 or commit_activity['avg_message_length'] > 50:
            async_score = min(100, conventional_usage * 100 + (commit_activity['avg_message_length'] / 2))
            work_styles.append({
                'style': 'Async-Friendly',
                'confidence': round(async_score, 2),
                'indicators': [
                    f"Conventional commit usage ({commit_activity['conventional_commit_percentage']:.1f}%)",
                    f"Detailed commit messages ({commit_activity['avg_message_length']:.1f} chars)",
                    "Clear communication patterns"
                ]
            })
        
        # Default if no styles detected
        if not work_styles:
            work_styles.append({
                'style': 'Independent Contributor',
                'confidence': 50.0,
                'indicators': ["Standard contribution patterns"]
            })
        
        # Sort by confidence
        work_styles.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'primary_style': work_styles[0]['style'] if work_styles else 'Unknown',
            'all_styles': work_styles,
            'style_count': len(work_styles)
        }
    
    def assess_code_quality(self) -> Dict[str, Any]:
        """
        Assess code quality across multiple dimensions
        Returns: Code quality scores
        """
        logger.info("Assessing code quality...")
        
        quality_scores = []
        
        for repo in self.top_repos:
            # Skip forks
            if repo.get('is_fork'):
                continue
            
            repo_quality = {
                'repo_name': repo['name'],
                'documentation_score': 0,
                'testing_score': 0,
                'maintenance_score': 0,
                'overall_score': 0
            }
            
            # 1. Documentation Quality (30%)
            doc_score = 0
            
            # Has README (assume true if public)
            doc_score += 25
            
            # Has description
            if repo.get('description'):
                doc_score += 25
            
            # Has topics
            topics_count = len(repo.get('topics', []))
            doc_score += min(25, topics_count * 5)
            
            # Has license
            if repo.get('license'):
                doc_score += 25
            
            repo_quality['documentation_score'] = doc_score
            
            # 2. Testing Practices (25%)
            test_score = 0
            
            # Has testing framework
            dependencies = repo.get('dependencies', [])
            has_test_framework = any(
                tf.lower() in dep.lower()
                for tf in TESTING_FRAMEWORKS
                for dep in dependencies
            )
            if has_test_framework:
                test_score += 40
            
            # Has CI/CD
            cicd_tools = repo.get('cicd_tools', {})
            if any(cicd_tools.values()):
                test_score += 40
            
            # Has test-related files (approximation)
            # We'd need to check for test directories, but we'll give partial credit
            test_score += 20  # Assume some test coverage
            
            repo_quality['testing_score'] = test_score
            
            # 3. Maintenance Score (15%)
            maint_score = 0
            
            # Recent activity
            pushed_at = repo.get('pushed_at')
            if pushed_at:
                pushed_date = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
                months_ago = calculate_months_ago(pushed_date)
                if months_ago < 3:
                    maint_score += 40
                elif months_ago < 6:
                    maint_score += 30
                elif months_ago < 12:
                    maint_score += 20
            
            # Repository age (mature projects)
            created_at = repo.get('created_at')
            if created_at:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                age_months = calculate_months_ago(created_date)
                if age_months > 12:
                    maint_score += 30
                elif age_months > 6:
                    maint_score += 20
            
            # Not a fork (original work)
            if not repo.get('is_fork'):
                maint_score += 30
            
            repo_quality['maintenance_score'] = maint_score
            
            # 4. Overall Quality (weighted average)
            overall = (
                repo_quality['documentation_score'] * QUALITY_WEIGHTS['documentation'] +
                repo_quality['testing_score'] * QUALITY_WEIGHTS['testing'] +
                repo_quality['maintenance_score'] * QUALITY_WEIGHTS['maintenance']
            )
            repo_quality['overall_score'] = round(overall, 2)
            
            quality_scores.append(repo_quality)
        
        # Calculate aggregate scores
        if quality_scores:
            avg_doc = statistics.mean([q['documentation_score'] for q in quality_scores])
            avg_test = statistics.mean([q['testing_score'] for q in quality_scores])
            avg_maint = statistics.mean([q['maintenance_score'] for q in quality_scores])
            avg_overall = statistics.mean([q['overall_score'] for q in quality_scores])
        else:
            avg_doc = avg_test = avg_maint = avg_overall = 0
        
        return {
            'repository_scores': quality_scores,
            'aggregate_scores': {
                'documentation': round(avg_doc, 2),
                'testing': round(avg_test, 2),
                'maintenance': round(avg_maint, 2),
                'overall': round(avg_overall, 2)
            },
            'quality_tier': self._classify_quality_tier(avg_overall)
        }
    
    def _classify_quality_tier(self, score: float) -> str:
        """Classify quality into tiers"""
        if score >= 75:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Fair'
        else:
            return 'Needs Improvement'
    
    def analyze_learning_trajectory(self, skills_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze learning patterns and growth potential
        Returns: Learning trajectory analysis
        """
        logger.info("Analyzing learning trajectory...")
        
        skills = skills_analysis['skills']
        
        # 1. Skill Acquisition Analysis
        # Group skills by last used date
        recent_skills = []  # Last 6 months
        older_skills = []   # 6-12 months
        
        now = datetime.now()
        for skill_name, skill_data in skills.items():
            last_used = skill_data.get('last_used')
            if last_used:
                last_used_date = datetime.fromisoformat(last_used.replace('Z', '+00:00'))
                months_ago = calculate_months_ago(last_used_date)
                
                if months_ago <= 6:
                    recent_skills.append(skill_name)
                elif months_ago <= 12:
                    older_skills.append(skill_name)
        
        # Skills acquired in last year
        new_skills_count = len(recent_skills)
        
        # 2. Technology Diversification
        # Count unique categories
        categories = set()
        for skill_name, skill_data in skills.items():
            categories.add(skill_data.get('category', 'Unknown'))
        
        diversification_score = min(100, len(categories) * 20)  # Max 5 categories = 100
        
        # 3. Complexity Progression
        # Compare recent vs older skills complexity (using confidence as proxy)
        recent_confidence = []
        older_confidence = []
        
        for skill_name in recent_skills:
            if skill_name in skills:
                recent_confidence.append(skills[skill_name]['confidence'])
        
        for skill_name in older_skills:
            if skill_name in skills:
                older_confidence.append(skills[skill_name]['confidence'])
        
        if recent_confidence and older_confidence:
            avg_recent = statistics.mean(recent_confidence)
            avg_older = statistics.mean(older_confidence)
            complexity_trend = 'increasing' if avg_recent > avg_older else 'stable'
        else:
            complexity_trend = 'insufficient_data'
        
        # 4. Learning Velocity
        # Skills per month
        account_age_months = self.profile.get('account_age_months', 1)
        learning_velocity = safe_divide(len(skills), max(1, account_age_months), 0)
        
        # 5. Adaptability Score
        # Based on skill count, diversification, and recent activity
        adaptability = min(100, (
            (len(skills) / 20) * 30 +  # Skill count (max 20 skills = 30 points)
            diversification_score * 0.4 +  # Diversification (40 points)
            (new_skills_count / 10) * 30  # Recent learning (max 10 new = 30 points)
        ))
        
        return {
            'total_skills': len(skills),
            'recent_skills': recent_skills[:10],  # Top 10
            'new_skills_last_year': new_skills_count,
            'skill_categories': list(categories),
            'diversification_score': round(diversification_score, 2),
            'complexity_trend': complexity_trend,
            'learning_velocity': round(learning_velocity, 3),
            'adaptability_score': round(adaptability, 2),
            'growth_potential': self._classify_growth_potential(adaptability)
        }
    
    def _classify_growth_potential(self, adaptability_score: float) -> str:
        """Classify growth potential"""
        if adaptability_score >= 75:
            return 'High'
        elif adaptability_score >= 50:
            return 'Moderate'
        else:
            return 'Developing'
    
    def perform_complete_analysis(self) -> Dict[str, Any]:
        """
        Run all analysis modules
        Returns: Complete analysis results
        """
        logger.info("Starting complete analysis...")
        
        # Run all analyses
        skills_analysis = self.analyze_skills()
        contribution_patterns = self.analyze_contribution_patterns()
        work_style = self.classify_work_style(contribution_patterns)
        code_quality = self.assess_code_quality()
        learning_trajectory = self.analyze_learning_trajectory(skills_analysis)
        
        # Compile complete profile
        complete_analysis = {
            'profile_metadata': self.profile,
            'skills_analysis': skills_analysis,
            'contribution_patterns': contribution_patterns,
            'work_style': work_style,
            'code_quality': code_quality,
            'learning_trajectory': learning_trajectory,
            'analyzed_at': datetime.now().isoformat()
        }
        
        logger.info("Complete analysis finished!")
        return complete_analysis
