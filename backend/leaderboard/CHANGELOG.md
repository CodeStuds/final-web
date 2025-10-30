# Changelog

All notable changes to the HireSight Leaderboard system will be documented in this file.

## [1.0.0] - 2025-10-29

### Added
- Initial release of HireSight Leaderboard system
- **Data Loading**
  - LinkedIn CSV score loader
  - GitHub JSON report loader
  - Automatic candidate name matching and merging
  - Handles missing scores gracefully
  
- **Score Processing**
  - Normalize GitHub scores (0-100 → 0-1)
  - Normalize LinkedIn scores (maintain 0-1)
  - Configurable weighted averaging
  - Minimum score threshold filtering
  
- **Ranking System**
  - Sort candidates by combined score
  - 6-tier classification system
  - Rank assignment
  - Statistical analysis
  
- **Output Generation**
  - JSON format with full details
  - CSV format for spreadsheets
  - Markdown format with tables
  - Console summary display
  
- **Command Line Interface**
  - Custom weight configuration
  - Minimum score filtering
  - Top N display limit
  - Custom data paths
  - Output format selection
  
- **Utilities**
  - Score normalization functions
  - Fuzzy name matching
  - Tier classification
  - Score formatting helpers
  
- **Documentation**
  - Complete README with examples
  - Quick start guide
  - Project overview and architecture
  - Implementation summary
  - Usage examples
  
- **Scripts**
  - `run.sh` for quick setup
  - `example.py` with code samples
  - `.gitignore` for output files

### Features
- Configurable weights (default 50/50 split)
- Handles candidates with only LinkedIn or only GitHub scores
- Automatic tier classification with emojis
- Statistics: average, median, min, max scores
- Tier distribution analysis
- Multiple output formats
- Comprehensive error handling

### Technical Details
- Pure Python implementation
- No external dependencies required
- Modular architecture
- Clean separation of concerns
- Dataclasses for type safety
- Extensive documentation

## [Unreleased]

### Planned Features
- [ ] Web dashboard interface
- [ ] Real-time data watching
- [ ] Advanced ML-based name matching
- [ ] Score visualization charts
- [ ] PDF report generation
- [ ] REST API server
- [ ] Database persistence
- [ ] Unit test suite
- [ ] Integration tests
- [ ] Performance optimizations
- [ ] Caching system
- [ ] Progress bars for large datasets
- [ ] Multi-job leaderboards
- [ ] Customizable tier thresholds
- [ ] Email notifications
- [ ] Slack/Discord integration

### Possible Improvements
- [ ] Add type hints throughout
- [ ] Implement async data loading
- [ ] Support for additional data sources
- [ ] Export to Excel with formatting
- [ ] Interactive CLI with prompts
- [ ] Configuration file support (YAML/JSON)
- [ ] Logging system
- [ ] Comprehensive error recovery
- [ ] Input validation improvements
- [ ] Better name matching algorithms

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2025-10-29 | Initial release with core functionality |

---

*Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)*
