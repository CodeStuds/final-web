"""
Utility functions for HireSight
Includes error handling, caching, date calculations, and helpers
"""

import os
import pickle
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import time
from functools import wraps

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HireSight')


class CacheManager:
    """Simple file-based cache manager using pickle"""
    
    def __init__(self, cache_dir: str = '.cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, key: str, max_age_hours: int = 24) -> Optional[Any]:
        """Get cached value if it exists and is not expired"""
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        
        if not os.path.exists(cache_file):
            return None
        
        # Check age
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age > max_age_hours * 3600:
            logger.debug(f"Cache expired for {key}")
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache for {key}: {e}")
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value"""
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            logger.warning(f"Failed to save cache for {key}: {e}")


def retry_on_rate_limit(max_retries: int = 3, initial_delay: int = 60):
    """Decorator to retry function on rate limit errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if 'rate limit' in str(e).lower() or 'abuse' in str(e).lower():
                        if attempt < max_retries - 1:
                            logger.warning(f"Rate limit hit, waiting {delay}s before retry {attempt + 1}/{max_retries}")
                            time.sleep(delay)
                            delay *= 2  # Exponential backoff
                        else:
                            logger.error("Max retries reached for rate limit")
                            raise
                    else:
                        raise
            return None
        return wrapper
    return decorator


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def calculate_months_ago(date: datetime) -> int:
    """Calculate how many months ago a date was from now"""
    now = datetime.now()
    if date.tzinfo is not None:
        # Make now timezone-aware if date is
        from datetime import timezone
        now = datetime.now(timezone.utc)
    
    months = (now.year - date.year) * 12 + (now.month - date.month)
    return max(0, months)


def calculate_recency_score(date: datetime, max_months: int = 12, max_score: int = 30) -> float:
    """
    Calculate recency score based on how recent the activity is
    More recent = higher score
    """
    months_ago = calculate_months_ago(date)
    
    if months_ago >= max_months:
        return 0.0
    
    # Linear decay: max_score at 0 months, 0 at max_months
    score = max_score * (1 - (months_ago / max_months))
    return max(0.0, score)


def calculate_days_between(start_date: datetime, end_date: datetime) -> int:
    """Calculate days between two dates"""
    try:
        delta = end_date - start_date
        return abs(delta.days)
    except:
        return 0


def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value to 0-100 scale"""
    if max_val == min_val:
        return 50.0  # Default to middle if no variance
    
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return max(0.0, min(100.0, normalized))


def extract_username_from_url(input_str: str) -> str:
    """Extract GitHub username from URL or return as-is if already username"""
    input_str = input_str.strip()
    
    # Remove trailing slash
    if input_str.endswith('/'):
        input_str = input_str[:-1]
    
    # Handle various GitHub URL formats
    if 'github.com' in input_str:
        # https://github.com/username or https://github.com/username/repo
        parts = input_str.split('github.com/')
        if len(parts) > 1:
            username = parts[1].split('/')[0]
            return username
    
    # Assume it's already a username
    return input_str


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_file_extension(filename: str) -> str:
    """Get file extension"""
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def calculate_contribution_consistency(dates: list) -> float:
    """
    Calculate consistency score based on distribution of contribution dates
    Returns 0-100 where 100 is perfectly consistent
    """
    if not dates or len(dates) < 2:
        return 0.0
    
    # Sort dates
    sorted_dates = sorted(dates)
    
    # Calculate gaps between consecutive commits
    gaps = []
    for i in range(1, len(sorted_dates)):
        gap = (sorted_dates[i] - sorted_dates[i-1]).days
        gaps.append(gap)
    
    if not gaps:
        return 0.0
    
    # Calculate coefficient of variation (lower = more consistent)
    import statistics
    mean_gap = statistics.mean(gaps)
    if mean_gap == 0:
        return 100.0
    
    try:
        std_gap = statistics.stdev(gaps)
        cv = std_gap / mean_gap
        
        # Convert CV to 0-100 score (lower CV = higher score)
        # CV of 0 = 100, CV of 2+ = 0
        consistency = max(0, 100 - (cv * 50))
        return consistency
    except:
        return 50.0


def detect_conventional_commits(commit_messages: list) -> Dict[str, Any]:
    """
    Detect if commits follow conventional commit format
    Returns dict with usage percentage and examples
    """
    if not commit_messages:
        return {'usage_percentage': 0.0, 'follows_convention': False}
    
    conventional_prefixes = [
        'feat:', 'fix:', 'docs:', 'style:', 'refactor:',
        'perf:', 'test:', 'chore:', 'ci:', 'build:'
    ]
    
    conventional_count = 0
    for msg in commit_messages:
        msg_lower = msg.lower().strip()
        if any(msg_lower.startswith(prefix) for prefix in conventional_prefixes):
            conventional_count += 1
    
    usage_percentage = (conventional_count / len(commit_messages)) * 100
    
    return {
        'usage_percentage': usage_percentage,
        'follows_convention': usage_percentage >= 50,
        'total_commits': len(commit_messages),
        'conventional_commits': conventional_count
    }


def calculate_average_commit_message_length(commit_messages: list) -> float:
    """Calculate average length of commit messages"""
    if not commit_messages:
        return 0.0
    
    total_length = sum(len(msg) for msg in commit_messages)
    return total_length / len(commit_messages)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def format_number(num: float, decimals: int = 2) -> str:
    """Format number with thousands separator"""
    if num >= 1000000:
        return f"{num/1000000:.{decimals}f}M"
    elif num >= 1000:
        return f"{num/1000:.{decimals}f}K"
    else:
        return f"{num:.{decimals}f}"


def calculate_percentile(value: float, values: list) -> float:
    """Calculate percentile rank of value in list"""
    if not values:
        return 50.0
    
    sorted_values = sorted(values)
    count_below = sum(1 for v in sorted_values if v < value)
    
    percentile = (count_below / len(sorted_values)) * 100
    return percentile


class ProgressTracker:
    """Simple progress tracker for user feedback"""
    
    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0
    
    def update(self, step_name: str):
        """Update progress"""
        self.current_step += 1
        percentage = (self.current_step / self.total_steps) * 100
        logger.info(f"[{percentage:.1f}%] {step_name}")
    
    def complete(self):
        """Mark as complete"""
        logger.info("[100%] Analysis complete!")


def handle_api_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """Handle API errors gracefully"""
    error_msg = str(error)
    logger.error(f"API Error {context}: {error_msg}")
    
    return {
        'error': True,
        'message': error_msg,
        'context': context,
        'timestamp': datetime.now().isoformat()
    }


def merge_dicts_safely(dict1: dict, dict2: dict) -> dict:
    """Safely merge two dictionaries"""
    result = dict1.copy()
    result.update(dict2)
    return result
