"""
Configuration file for HireSight Leaderboard
Contains paths, weights, and constants
"""

import os

# Paths to data sources
LINKEDIN_DATA_PATH = "../ibhanwork/results.csv"
GITHUB_DATA_PATH = "../github-data-fetch/reports"

# Output paths
OUTPUT_DIR = "output"
LEADERBOARD_JSON = "leaderboard.json"
LEADERBOARD_CSV = "leaderboard.csv"
LEADERBOARD_MD = "leaderboard.md"

# Score weights (default: equal weight)
LINKEDIN_WEIGHT = 0.5
GITHUB_WEIGHT = 0.5

# Score normalization
GITHUB_MAX_SCORE = 100  # GitHub scores are 0-100
LINKEDIN_MAX_SCORE = 1  # LinkedIn scores are 0-1

# Display settings
TOP_CANDIDATES_DISPLAY = 10  # Number of top candidates to highlight
MIN_SCORE_THRESHOLD = 0.0  # Minimum score to include in leaderboard
