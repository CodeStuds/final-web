"""
HireSight Backend Utilities
Utility modules for resume processing, scoring, and leaderboard generation
"""

__version__ = "1.0.0"

# Core utilities
from . import contact_extractor
from . import resume_text_extractor
from . import resume_scorer

# Dynamic leaderboard system
try:
    from . import session_manager
    from . import linkedin_score_generator
    from . import github_analysis_generator
    from . import dynamic_leaderboard
    DYNAMIC_LEADERBOARD_AVAILABLE = True
except ImportError as e:
    DYNAMIC_LEADERBOARD_AVAILABLE = False

__all__ = [
    'contact_extractor',
    'resume_text_extractor',
    'resume_scorer',
    'session_manager',
    'linkedin_score_generator',
    'github_analysis_generator',
    'dynamic_leaderboard',
]
