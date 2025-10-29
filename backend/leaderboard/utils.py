"""
Utility functions for score normalization and matching
"""

from typing import Dict, Tuple
import re


def normalize_github_score(score: float) -> float:
    """
    Normalize GitHub score from 0-100 scale to 0-1 scale
    
    Args:
        score: GitHub match score (0-100)
    
    Returns:
        Normalized score (0-1)
    """
    if score < 0:
        return 0.0
    if score > 100:
        return 1.0
    return score / 100.0


def normalize_linkedin_score(score: float) -> float:
    """
    Normalize LinkedIn score (should already be 0-1)
    
    Args:
        score: LinkedIn similarity score (0-1)
    
    Returns:
        Normalized score (0-1)
    """
    if score < 0:
        return 0.0
    if score > 1:
        return 1.0
    return score


def calculate_combined_score(
    linkedin_score: float,
    github_score: float,
    linkedin_weight: float = 0.5,
    github_weight: float = 0.5
) -> float:
    """
    Calculate weighted average of LinkedIn and GitHub scores
    
    Args:
        linkedin_score: Normalized LinkedIn score (0-1)
        github_score: Normalized GitHub score (0-1)
        linkedin_weight: Weight for LinkedIn score (default: 0.5)
        github_weight: Weight for GitHub score (default: 0.5)
    
    Returns:
        Combined score (0-1)
    """
    # Normalize weights to sum to 1
    total_weight = linkedin_weight + github_weight
    if total_weight == 0:
        return 0.0
    
    normalized_linkedin_weight = linkedin_weight / total_weight
    normalized_github_weight = github_weight / total_weight
    
    combined = (linkedin_score * normalized_linkedin_weight + 
                github_score * normalized_github_weight)
    
    return round(combined, 6)


def normalize_name(name: str) -> str:
    """
    Normalize candidate name for matching
    - Convert to lowercase
    - Remove extra spaces
    - Remove special characters
    
    Args:
        name: Raw candidate name
    
    Returns:
        Normalized name
    """
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove special characters except spaces and hyphens
    name = re.sub(r'[^a-z0-9\s\-]', '', name)
    
    # Replace multiple spaces with single space
    name = re.sub(r'\s+', ' ', name)
    
    # Strip leading/trailing spaces
    name = name.strip()
    
    return name


def fuzzy_name_match(name1: str, name2: str) -> float:
    """
    Calculate fuzzy match score between two names
    
    Args:
        name1: First candidate name
        name2: Second candidate name
    
    Returns:
        Match score (0-1)
    """
    if not name1 or not name2:
        return 0.0
    
    # Normalize names
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    # Exact match
    if norm1 == norm2:
        return 1.0
    
    # Check if one is contained in the other
    if norm1 in norm2 or norm2 in norm1:
        return 0.8
    
    # Check word overlap
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    # Jaccard similarity
    jaccard = len(intersection) / len(union) if union else 0.0
    
    return jaccard


def extract_github_username(name_or_url: str) -> str:
    """
    Extract GitHub username from name or URL
    
    Args:
        name_or_url: GitHub username or profile URL
    
    Returns:
        Username string
    """
    if not name_or_url:
        return ""
    
    # Check if it's a GitHub URL
    url_patterns = [
        r'github\.com/([^/\s]+)',
        r'@([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in url_patterns:
        match = re.search(pattern, name_or_url)
        if match:
            return match.group(1).lower()
    
    # Otherwise, return as-is (assumed to be username)
    return name_or_url.strip().lower()


def classify_score(score: float) -> Tuple[str, str]:
    """
    Classify combined score into tier and color
    
    Args:
        score: Combined score (0-1)
    
    Returns:
        Tuple of (tier_name, emoji)
    """
    if score >= 0.85:
        return ("Excellent Match", "🥇")
    elif score >= 0.75:
        return ("Very Good Match", "🥈")
    elif score >= 0.65:
        return ("Good Match", "🥉")
    elif score >= 0.50:
        return ("Moderate Match", "✅")
    elif score >= 0.35:
        return ("Fair Match", "⚠️")
    else:
        return ("Low Match", "❌")


def format_score(score: float, as_percentage: bool = True) -> str:
    """
    Format score for display
    
    Args:
        score: Score value (0-1)
        as_percentage: Whether to format as percentage
    
    Returns:
        Formatted string
    """
    if as_percentage:
        return f"{score * 100:.2f}%"
    else:
        return f"{score:.4f}"
