"""
Configuration file for HireSight GitHub Profile Analysis
Contains skill mappings, scoring weights, and constants
"""

# Scoring weights
SCORING_WEIGHTS = {
    'lines_of_code_max': 20,
    'repo_count_max': 30,
    'recency_max': 30,
    'complexity_max': 20,
}

# Code quality weights
QUALITY_WEIGHTS = {
    'documentation': 0.30,
    'testing': 0.25,
    'maintenance': 0.15,
    'overall': 0.30,
}

# Matching algorithm weights
MATCHING_WEIGHTS = {
    'current_fit': 0.40,
    'growth_potential': 0.30,
    'collaboration_fit': 0.20,
    'code_quality': 0.10,
}

# Work style thresholds
WORK_STYLE_THRESHOLDS = {
    'solo_developer_threshold': 0.80,  # >80% of contributions
    'high_review_ratio': 0.60,  # Review-to-PR ratio
    'mentorship_comment_length': 100,  # Average comment length for mentorship
}

# Dependency to framework/tool mapping (100+ common dependencies)
DEPENDENCY_MAPPINGS = {
    # JavaScript/Node.js
    'react': {'type': 'framework', 'category': 'Frontend', 'name': 'React'},
    'vue': {'type': 'framework', 'category': 'Frontend', 'name': 'Vue.js'},
    'angular': {'type': 'framework', 'category': 'Frontend', 'name': 'Angular'},
    'next': {'type': 'framework', 'category': 'Frontend', 'name': 'Next.js'},
    'nuxt': {'type': 'framework', 'category': 'Frontend', 'name': 'Nuxt.js'},
    'express': {'type': 'framework', 'category': 'Backend', 'name': 'Express.js'},
    'nestjs': {'type': 'framework', 'category': 'Backend', 'name': 'NestJS'},
    'koa': {'type': 'framework', 'category': 'Backend', 'name': 'Koa'},
    'fastify': {'type': 'framework', 'category': 'Backend', 'name': 'Fastify'},
    'gatsby': {'type': 'framework', 'category': 'Frontend', 'name': 'Gatsby'},
    'svelte': {'type': 'framework', 'category': 'Frontend', 'name': 'Svelte'},
    'electron': {'type': 'framework', 'category': 'Desktop', 'name': 'Electron'},
    'react-native': {'type': 'framework', 'category': 'Mobile', 'name': 'React Native'},
    'jest': {'type': 'testing', 'category': 'Testing', 'name': 'Jest'},
    'mocha': {'type': 'testing', 'category': 'Testing', 'name': 'Mocha'},
    'chai': {'type': 'testing', 'category': 'Testing', 'name': 'Chai'},
    'jasmine': {'type': 'testing', 'category': 'Testing', 'name': 'Jasmine'},
    'cypress': {'type': 'testing', 'category': 'Testing', 'name': 'Cypress'},
    'playwright': {'type': 'testing', 'category': 'Testing', 'name': 'Playwright'},
    'webpack': {'type': 'tool', 'category': 'Build', 'name': 'Webpack'},
    'vite': {'type': 'tool', 'category': 'Build', 'name': 'Vite'},
    'rollup': {'type': 'tool', 'category': 'Build', 'name': 'Rollup'},
    'babel': {'type': 'tool', 'category': 'Build', 'name': 'Babel'},
    'typescript': {'type': 'language', 'category': 'Language', 'name': 'TypeScript'},
    'eslint': {'type': 'tool', 'category': 'Quality', 'name': 'ESLint'},
    'prettier': {'type': 'tool', 'category': 'Quality', 'name': 'Prettier'},
    
    # Python
    'django': {'type': 'framework', 'category': 'Backend', 'name': 'Django'},
    'flask': {'type': 'framework', 'category': 'Backend', 'name': 'Flask'},
    'fastapi': {'type': 'framework', 'category': 'Backend', 'name': 'FastAPI'},
    'tornado': {'type': 'framework', 'category': 'Backend', 'name': 'Tornado'},
    'pyramid': {'type': 'framework', 'category': 'Backend', 'name': 'Pyramid'},
    'aiohttp': {'type': 'framework', 'category': 'Backend', 'name': 'aiohttp'},
    'pytest': {'type': 'testing', 'category': 'Testing', 'name': 'Pytest'},
    'unittest': {'type': 'testing', 'category': 'Testing', 'name': 'unittest'},
    'nose': {'type': 'testing', 'category': 'Testing', 'name': 'Nose'},
    'pytest-cov': {'type': 'testing', 'category': 'Testing', 'name': 'Pytest-Cov'},
    'celery': {'type': 'tool', 'category': 'Task Queue', 'name': 'Celery'},
    'redis': {'type': 'database', 'category': 'Database', 'name': 'Redis'},
    'sqlalchemy': {'type': 'tool', 'category': 'ORM', 'name': 'SQLAlchemy'},
    'numpy': {'type': 'library', 'category': 'Data Science', 'name': 'NumPy'},
    'pandas': {'type': 'library', 'category': 'Data Science', 'name': 'Pandas'},
    'scikit-learn': {'type': 'library', 'category': 'Machine Learning', 'name': 'Scikit-learn'},
    'tensorflow': {'type': 'framework', 'category': 'Machine Learning', 'name': 'TensorFlow'},
    'pytorch': {'type': 'framework', 'category': 'Machine Learning', 'name': 'PyTorch'},
    'keras': {'type': 'framework', 'category': 'Machine Learning', 'name': 'Keras'},
    'matplotlib': {'type': 'library', 'category': 'Visualization', 'name': 'Matplotlib'},
    'seaborn': {'type': 'library', 'category': 'Visualization', 'name': 'Seaborn'},
    'scrapy': {'type': 'framework', 'category': 'Web Scraping', 'name': 'Scrapy'},
    'beautifulsoup4': {'type': 'library', 'category': 'Web Scraping', 'name': 'BeautifulSoup'},
    'requests': {'type': 'library', 'category': 'HTTP', 'name': 'Requests'},
    'black': {'type': 'tool', 'category': 'Quality', 'name': 'Black'},
    'pylint': {'type': 'tool', 'category': 'Quality', 'name': 'Pylint'},
    'flake8': {'type': 'tool', 'category': 'Quality', 'name': 'Flake8'},
    'mypy': {'type': 'tool', 'category': 'Quality', 'name': 'MyPy'},
    
    # Go
    'gin': {'type': 'framework', 'category': 'Backend', 'name': 'Gin'},
    'echo': {'type': 'framework', 'category': 'Backend', 'name': 'Echo'},
    'fiber': {'type': 'framework', 'category': 'Backend', 'name': 'Fiber'},
    'beego': {'type': 'framework', 'category': 'Backend', 'name': 'Beego'},
    'gorm': {'type': 'tool', 'category': 'ORM', 'name': 'GORM'},
    'testify': {'type': 'testing', 'category': 'Testing', 'name': 'Testify'},
    
    # Rust
    'actix-web': {'type': 'framework', 'category': 'Backend', 'name': 'Actix-web'},
    'rocket': {'type': 'framework', 'category': 'Backend', 'name': 'Rocket'},
    'tokio': {'type': 'library', 'category': 'Async Runtime', 'name': 'Tokio'},
    'serde': {'type': 'library', 'category': 'Serialization', 'name': 'Serde'},
    
    # Ruby
    'rails': {'type': 'framework', 'category': 'Backend', 'name': 'Ruby on Rails'},
    'sinatra': {'type': 'framework', 'category': 'Backend', 'name': 'Sinatra'},
    'rspec': {'type': 'testing', 'category': 'Testing', 'name': 'RSpec'},
    
    # Java
    'spring': {'type': 'framework', 'category': 'Backend', 'name': 'Spring'},
    'spring-boot': {'type': 'framework', 'category': 'Backend', 'name': 'Spring Boot'},
    'junit': {'type': 'testing', 'category': 'Testing', 'name': 'JUnit'},
    'mockito': {'type': 'testing', 'category': 'Testing', 'name': 'Mockito'},
    'hibernate': {'type': 'tool', 'category': 'ORM', 'name': 'Hibernate'},
    
    # Databases
    'mongodb': {'type': 'database', 'category': 'Database', 'name': 'MongoDB'},
    'postgresql': {'type': 'database', 'category': 'Database', 'name': 'PostgreSQL'},
    'mysql': {'type': 'database', 'category': 'Database', 'name': 'MySQL'},
    'sqlite': {'type': 'database', 'category': 'Database', 'name': 'SQLite'},
    'cassandra': {'type': 'database', 'category': 'Database', 'name': 'Cassandra'},
    'elasticsearch': {'type': 'database', 'category': 'Database', 'name': 'Elasticsearch'},
    
    # DevOps & Cloud
    'docker': {'type': 'tool', 'category': 'DevOps', 'name': 'Docker'},
    'kubernetes': {'type': 'tool', 'category': 'DevOps', 'name': 'Kubernetes'},
    'terraform': {'type': 'tool', 'category': 'DevOps', 'name': 'Terraform'},
    'ansible': {'type': 'tool', 'category': 'DevOps', 'name': 'Ansible'},
    'jenkins': {'type': 'tool', 'category': 'CI/CD', 'name': 'Jenkins'},
    'gitlab-ci': {'type': 'tool', 'category': 'CI/CD', 'name': 'GitLab CI'},
    'github-actions': {'type': 'tool', 'category': 'CI/CD', 'name': 'GitHub Actions'},
    'circleci': {'type': 'tool', 'category': 'CI/CD', 'name': 'CircleCI'},
    'travis': {'type': 'tool', 'category': 'CI/CD', 'name': 'Travis CI'},
    'aws-sdk': {'type': 'cloud', 'category': 'Cloud', 'name': 'AWS'},
    'boto3': {'type': 'cloud', 'category': 'Cloud', 'name': 'AWS (Boto3)'},
    'google-cloud': {'type': 'cloud', 'category': 'Cloud', 'name': 'Google Cloud'},
    'azure-sdk': {'type': 'cloud', 'category': 'Cloud', 'name': 'Azure'},
    
    # Message Queues
    'rabbitmq': {'type': 'tool', 'category': 'Message Queue', 'name': 'RabbitMQ'},
    'kafka': {'type': 'tool', 'category': 'Message Queue', 'name': 'Kafka'},
    
    # GraphQL
    'graphql': {'type': 'tool', 'category': 'API', 'name': 'GraphQL'},
    'apollo': {'type': 'tool', 'category': 'API', 'name': 'Apollo GraphQL'},
    
    # Monitoring
    'prometheus': {'type': 'tool', 'category': 'Monitoring', 'name': 'Prometheus'},
    'grafana': {'type': 'tool', 'category': 'Monitoring', 'name': 'Grafana'},
    'sentry': {'type': 'tool', 'category': 'Monitoring', 'name': 'Sentry'},
}

# Package file patterns
PACKAGE_FILES = {
    'package.json': 'javascript',
    'requirements.txt': 'python',
    'Pipfile': 'python',
    'pyproject.toml': 'python',
    'go.mod': 'go',
    'Cargo.toml': 'rust',
    'Gemfile': 'ruby',
    'pom.xml': 'java',
    'build.gradle': 'java',
    'composer.json': 'php',
}

# Testing framework indicators
TESTING_FRAMEWORKS = [
    'jest', 'mocha', 'chai', 'jasmine', 'cypress', 'playwright', 'pytest',
    'unittest', 'nose', 'testify', 'rspec', 'junit', 'mockito', 'karma',
    'ava', 'tape', 'qunit', 'vitest'
]

# CI/CD indicators (file patterns)
CICD_FILES = [
    '.github/workflows',
    '.gitlab-ci.yml',
    '.travis.yml',
    'Jenkinsfile',
    '.circleci/config.yml',
    'azure-pipelines.yml',
    'buildspec.yml'
]

# Default sample job description (configurable)
DEFAULT_JOB_REQUIREMENTS = {
    'title': 'Full-Stack Developer',
    'required_skills': ['JavaScript', 'React', 'Python', 'Docker', 'PostgreSQL'],
    'preferred_skills': ['TypeScript', 'AWS', 'GraphQL', 'Redis'],
    'experience_level': 'mid',  # junior, mid, senior
    'team_size': 'medium',  # solo, small, medium, large
    'work_style': 'collaborative',  # solo, collaborative, mixed
}

# Tier classification thresholds
MATCH_TIERS = {
    'top': 85,      # 85-100
    'high': 70,     # 70-84
    'moderate': 50, # 50-69
    'low': 0,       # 0-49
}

# Bias detection keywords
BIAS_KEYWORDS = {
    'education': ['university', 'degree', 'phd', 'masters', 'college', 'ivy league'],
    'location': ['bay area', 'silicon valley', 'san francisco', 'new york', 'us only', 'usa'],
    'experience': ['years of experience', 'senior', '5+ years', '10+ years'],
    'keyword': ['ninja', 'rockstar', 'guru', 'wizard'],
}

# Recency decay factor (for skill scoring)
RECENCY_DECAY_MONTHS = 12  # Consider last 12 months

# API rate limits
GITHUB_API_RATE_LIMIT = 5000  # per hour for authenticated users
