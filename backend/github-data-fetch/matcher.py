"""
Matcher Module for HireSight
Implements four-factor matching algorithm and bias detection
"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict

from utils import logger, safe_divide
from config import (
    MATCHING_WEIGHTS, MATCH_TIERS, DEFAULT_JOB_REQUIREMENTS, BIAS_KEYWORDS
)


class CandidateMatcher:
    """Matches candidates against job requirements"""
    
    def __init__(self, analysis: Dict[str, Any], job_requirements: Dict[str, Any] = None):
        """
        Initialize matcher with analysis results and job requirements
        """
        self.analysis = analysis
        self.job_requirements = job_requirements or DEFAULT_JOB_REQUIREMENTS
        
        # Extract key data
        self.skills = analysis['skills_analysis']['skills']
        self.top_skills = analysis['skills_analysis']['top_skills']
        self.work_style = analysis['work_style']
        self.code_quality = analysis['code_quality']
        self.learning = analysis['learning_trajectory']
        self.contribution = analysis['contribution_patterns']
    
    def calculate_current_fit(self) -> Dict[str, Any]:
        """
        Calculate current fit score (40% of total)
        Based on: skill overlap, experience level, tech stack
        """
        logger.info("Calculating current fit...")
        
        required_skills = set(s.lower() for s in self.job_requirements.get('required_skills', []))
        preferred_skills = set(s.lower() for s in self.job_requirements.get('preferred_skills', []))
        candidate_skills = set(s.lower() for s in self.skills.keys())
        
        # 1. Required Skills Match (60% of current fit)
        required_matches = required_skills & candidate_skills
        required_score = safe_divide(len(required_matches), len(required_skills), 0) * 60
        
        # 2. Preferred Skills Match (30% of current fit)
        preferred_matches = preferred_skills & candidate_skills
        preferred_score = safe_divide(len(preferred_matches), len(preferred_skills), 0) * 30 if preferred_skills else 0
        
        # 3. Overall Skill Depth (10% of current fit)
        # Average confidence of matching skills
        matching_skills = required_matches | preferred_matches
        if matching_skills:
            skill_depths = []
            for skill in matching_skills:
                # Find original skill name (case-insensitive)
                for orig_skill, data in self.skills.items():
                    if orig_skill.lower() == skill:
                        skill_depths.append(data['confidence'])
                        break
            
            avg_depth = sum(skill_depths) / len(skill_depths) if skill_depths else 0
            depth_score = (avg_depth / 100) * 10
        else:
            depth_score = 0
        
        # Total current fit score
        current_fit_score = required_score + preferred_score + depth_score
        
        # Identify gaps
        skill_gaps = list(required_skills - candidate_skills)
        
        return {
            'score': round(current_fit_score, 2),
            'required_skills_match': list(required_matches),
            'required_skills_missing': list(required_skills - required_matches),
            'preferred_skills_match': list(preferred_matches),
            'skill_gaps': skill_gaps,
            'match_percentage': round(safe_divide(len(required_matches), len(required_skills), 0) * 100, 2),
            'skill_gap_count': len(skill_gaps)
        }
    
    def calculate_growth_potential(self) -> Dict[str, Any]:
        """
        Calculate growth potential score (30% of total)
        Based on: learning ability, adaptability, skill acquisition velocity
        """
        logger.info("Calculating growth potential...")
        
        # Use learning trajectory data
        adaptability = self.learning['adaptability_score']
        learning_velocity = self.learning['learning_velocity']
        new_skills_count = self.learning['new_skills_last_year']
        diversification = self.learning['diversification_score']
        
        # 1. Adaptability (40% of growth potential)
        adaptability_score = (adaptability / 100) * 40
        
        # 2. Learning Velocity (30% of growth potential)
        # Normalize learning velocity (assume 0.5 skills/month is good)
        velocity_normalized = min(100, (learning_velocity / 0.5) * 100)
        velocity_score = (velocity_normalized / 100) * 30
        
        # 3. Recent Learning Activity (30% of growth potential)
        # Normalize new skills (assume 6 new skills/year is good)
        recent_learning_normalized = min(100, (new_skills_count / 6) * 100)
        recent_score = (recent_learning_normalized / 100) * 30
        
        growth_potential_score = adaptability_score + velocity_score + recent_score
        
        # Estimate ramp-up time for skill gaps
        ramp_up_estimates = {}
        skill_gaps = self.calculate_current_fit()['skill_gaps']
        
        for gap in skill_gaps:
            # Estimate based on learning velocity and skill similarity
            # Fast learner (velocity > 0.5): 1-2 months
            # Medium learner (velocity 0.2-0.5): 2-4 months
            # Slower learner (velocity < 0.2): 4-6 months
            
            if learning_velocity > 0.5:
                estimate = "1-2 months"
            elif learning_velocity > 0.2:
                estimate = "2-4 months"
            else:
                estimate = "4-6 months"
            
            ramp_up_estimates[gap] = estimate
        
        return {
            'score': round(growth_potential_score, 2),
            'adaptability_score': round(adaptability, 2),
            'learning_velocity': round(learning_velocity, 3),
            'new_skills_last_year': new_skills_count,
            'growth_classification': self.learning['growth_potential'],
            'ramp_up_estimates': ramp_up_estimates
        }
    
    def calculate_collaboration_fit(self) -> Dict[str, Any]:
        """
        Calculate collaboration fit score (20% of total)
        Based on: work style, communication patterns, team dynamics
        """
        logger.info("Calculating collaboration fit...")
        
        # Get job requirements
        required_style = self.job_requirements.get('work_style', 'collaborative')
        team_size = self.job_requirements.get('team_size', 'medium')
        
        # Get candidate work style
        primary_style = self.work_style['primary_style'].lower()
        all_styles = [s['style'].lower() for s in self.work_style['all_styles']]
        
        # Get contribution patterns
        pr_activity = self.contribution['pull_request_activity']
        review_activity = self.contribution['code_review_behavior']
        commit_activity = self.contribution['commit_behavior']
        
        # 1. Work Style Match (50% of collaboration fit)
        style_match = 0
        if required_style.lower() in primary_style or required_style.lower() in ' '.join(all_styles):
            style_match = 50
        elif 'collaborative' in all_styles and required_style == 'collaborative':
            style_match = 50
        elif 'solo' in primary_style and required_style == 'solo':
            style_match = 50
        else:
            # Partial match based on overlap
            style_match = 25
        
        # 2. Communication Quality (30% of collaboration fit)
        comm_score = 0
        
        # Conventional commits (good communication)
        if commit_activity['uses_conventional_commits']:
            comm_score += 10
        
        # Good commit messages
        if commit_activity['avg_message_length'] > 40:
            comm_score += 10
        
        # Active in discussions
        if pr_activity['avg_comments_per_pr'] > 2:
            comm_score += 10
        
        # 3. Team Dynamics (20% of collaboration fit)
        team_score = 0
        
        # Review engagement
        if review_activity['total_reviews_given'] > 0:
            team_score += 10
        
        # Positive sentiment
        if review_activity['sentiment_classification'] == 'positive':
            team_score += 10
        
        collaboration_score = style_match + comm_score + team_score
        
        return {
            'score': round(collaboration_score, 2),
            'work_style_match': primary_style,
            'required_style': required_style,
            'communication_quality': round(comm_score / 30 * 100, 2),
            'team_dynamics_score': round(team_score / 20 * 100, 2),
            'async_friendly': 'async' in ' '.join(all_styles),
            'mentorship_capable': 'mentorship' in ' '.join(all_styles)
        }
    
    def calculate_code_quality_score(self) -> Dict[str, Any]:
        """
        Calculate code quality score (10% of total)
        Based on: documentation, testing, maintenance
        """
        logger.info("Calculating code quality score...")
        
        aggregate = self.code_quality['aggregate_scores']
        
        # Already normalized to 0-100
        quality_score = aggregate['overall']
        
        return {
            'score': round(quality_score, 2),
            'documentation_score': aggregate['documentation'],
            'testing_score': aggregate['testing'],
            'maintenance_score': aggregate['maintenance'],
            'quality_tier': self.code_quality['quality_tier']
        }
    
    def calculate_overall_match(self) -> Dict[str, Any]:
        """
        Calculate overall match score using four-factor algorithm
        Returns: Complete match analysis
        """
        logger.info("Calculating overall match score...")
        
        # Calculate individual components
        current_fit = self.calculate_current_fit()
        growth_potential = self.calculate_growth_potential()
        collaboration_fit = self.calculate_collaboration_fit()
        code_quality = self.calculate_code_quality_score()
        
        # Apply weights
        overall_score = (
            current_fit['score'] * MATCHING_WEIGHTS['current_fit'] +
            growth_potential['score'] * MATCHING_WEIGHTS['growth_potential'] +
            collaboration_fit['score'] * MATCHING_WEIGHTS['collaboration_fit'] +
            code_quality['score'] * MATCHING_WEIGHTS['code_quality']
        )
        
        # Classify into tier
        tier = self._classify_tier(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            current_fit, growth_potential, collaboration_fit, code_quality, overall_score
        )
        
        return {
            'overall_score': round(overall_score, 2),
            'tier': tier,
            'components': {
                'current_fit': current_fit,
                'growth_potential': growth_potential,
                'collaboration_fit': collaboration_fit,
                'code_quality': code_quality
            },
            'recommendations': recommendations,
            'job_requirements': self.job_requirements
        }
    
    def _classify_tier(self, score: float) -> str:
        """Classify match score into tier"""
        if score >= MATCH_TIERS['top']:
            return 'Top Match'
        elif score >= MATCH_TIERS['high']:
            return 'High Match'
        elif score >= MATCH_TIERS['moderate']:
            return 'Moderate Match'
        else:
            return 'Low Match'
    
    def _generate_recommendations(
        self,
        current_fit: Dict,
        growth_potential: Dict,
        collaboration_fit: Dict,
        code_quality: Dict,
        overall_score: float
    ) -> Dict[str, List[str]]:
        """
        Generate hiring recommendations and interview questions
        """
        strengths = []
        considerations = []
        interview_questions = []
        
        # Analyze strengths
        if current_fit['match_percentage'] >= 80:
            strengths.append(f"Strong skill match ({current_fit['match_percentage']:.0f}% of required skills)")
        
        if growth_potential['score'] >= 70:
            strengths.append(f"High growth potential with {growth_potential['growth_classification'].lower()} adaptability")
        
        if collaboration_fit['score'] >= 70:
            strengths.append("Excellent collaboration and communication skills")
        
        if code_quality['quality_tier'] in ['Excellent', 'Good']:
            strengths.append(f"{code_quality['quality_tier']} code quality standards")
        
        # Analyze considerations
        if current_fit['skill_gap_count'] > 0:
            considerations.append(f"Missing {current_fit['skill_gap_count']} required skills: {', '.join(current_fit['skill_gaps'][:3])}")
        
        if growth_potential['score'] < 50:
            considerations.append("Limited recent learning activity - may need structured onboarding")
        
        if collaboration_fit['score'] < 50:
            considerations.append("Work style may not align perfectly with team dynamics")
        
        if code_quality['score'] < 60:
            considerations.append("Code quality practices could be improved")
        
        # Generate interview questions
        if current_fit['skill_gaps']:
            interview_questions.append(
                f"Can you discuss your experience or interest in learning {current_fit['skill_gaps'][0]}?"
            )
        
        if collaboration_fit['work_style_match'] != collaboration_fit['required_style']:
            interview_questions.append(
                f"How do you adapt your work style when joining a {collaboration_fit['required_style']} team?"
            )
        
        interview_questions.append("Walk us through your approach to learning new technologies")
        interview_questions.append("Describe a recent technical challenge and how you solved it")
        
        if collaboration_fit['mentorship_capable']:
            interview_questions.append("Tell us about your experience mentoring or helping other developers")
        
        return {
            'strengths': strengths,
            'considerations': considerations,
            'interview_questions': interview_questions
        }
    
    def detect_bias(self) -> Dict[str, Any]:
        """
        Detect potential biases in job requirements and matching
        Returns: Bias analysis
        """
        logger.info("Detecting potential biases...")
        
        biases_detected = []
        
        job_desc = str(self.job_requirements).lower()
        
        # Check for education bias
        education_keywords = [k for k in BIAS_KEYWORDS['education'] if k in job_desc]
        if education_keywords:
            biases_detected.append({
                'type': 'Education Bias',
                'severity': 'medium',
                'description': f"Job requirements emphasize educational credentials: {', '.join(education_keywords)}",
                'recommendation': 'Consider skills-based evaluation over formal education'
            })
        
        # Check for location bias
        location_keywords = [k for k in BIAS_KEYWORDS['location'] if k in job_desc]
        if location_keywords:
            biases_detected.append({
                'type': 'Geographic Bias',
                'severity': 'high',
                'description': f"Job requirements specify restrictive locations: {', '.join(location_keywords)}",
                'recommendation': 'Consider remote candidates to expand talent pool'
            })
        
        # Check for experience bias
        experience_keywords = [k for k in BIAS_KEYWORDS['experience'] if k in job_desc]
        if len(experience_keywords) > 1:
            biases_detected.append({
                'type': 'Experience Bias',
                'severity': 'medium',
                'description': 'Job requirements over-emphasize years of experience',
                'recommendation': 'Focus on demonstrated skills and project quality'
            })
        
        # Check for problematic keywords
        keyword_issues = [k for k in BIAS_KEYWORDS['keyword'] if k in job_desc]
        if keyword_issues:
            biases_detected.append({
                'type': 'Keyword Bias',
                'severity': 'low',
                'description': f"Job description uses potentially exclusionary terms: {', '.join(keyword_issues)}",
                'recommendation': 'Use inclusive, professional language in job descriptions'
            })
        
        # Analyze skill requirements balance
        required_count = len(self.job_requirements.get('required_skills', []))
        if required_count > 8:
            biases_detected.append({
                'type': 'Unrealistic Expectations',
                'severity': 'medium',
                'description': f'Job requires {required_count} skills, which may be overly restrictive',
                'recommendation': 'Prioritize truly essential skills vs. nice-to-have'
            })
        
        return {
            'biases_found': len(biases_detected) > 0,
            'bias_count': len(biases_detected),
            'biases': biases_detected,
            'fairness_score': round(max(0, 100 - len(biases_detected) * 15), 2)
        }
    
    def analyze_equity(self, candidate_pool: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze equity and diversity in candidate evaluation
        Note: This is for candidate pools, but we'll provide framework for single candidate
        """
        logger.info("Analyzing equity considerations...")
        
        # For single candidate, provide framework
        equity_analysis = {
            'note': 'Full equity analysis requires multiple candidates',
            'single_candidate_considerations': [
                'Evaluate based on demonstrated skills, not proxies',
                'Consider non-traditional backgrounds and self-taught developers',
                'Weight growth potential alongside current skills',
                'Ensure interview process is accessible and bias-free'
            ],
            'recommended_metrics': [
                'Skill diversity in candidate pool',
                'Geographic distribution',
                'Experience level distribution',
                'Learning path diversity (formal education vs. self-taught)'
            ]
        }
        
        return equity_analysis
