# GitHub Leaderboard Prompt Templates

This document contains prompt templates to help structure job descriptions for better GitHub profile analysis and ranking.

## Basic Prompt Template

```
Role: [Job Title]
Required Skills: [Comma-separated list of must-have skills]
Minimum CGPA: [If applicable, e.g., 7.5]
Required Experience: [If applicable, e.g., 3 years]

Additional Requirements:
- [Specific technology or framework experience]
- [Project type experience]
- [Soft skills or team requirements]
- [Domain knowledge requirements]
```

## Example Prompts

### Example 1: Senior Backend Developer

```
Role: Senior Backend Developer
Required Skills: Python, Django, PostgreSQL, Redis, Docker, AWS

Minimum CGPA: 7.5
Required Experience: 3 years

Additional Requirements:
- Strong experience with RESTful API design and implementation
- Experience with microservices architecture
- Familiarity with CI/CD pipelines
- Previous work on scalable, high-traffic applications
- Knowledge of caching strategies and database optimization
- Strong problem-solving and debugging skills
```

### Example 2: Full Stack Engineer

```
Role: Full Stack Engineer
Required Skills: React, TypeScript, Node.js, Express, MongoDB, GraphQL

Minimum CGPA: 7.0
Required Experience: 2 years

Additional Requirements:
- Experience building responsive web applications
- Knowledge of modern frontend build tools (Webpack, Vite)
- Understanding of state management (Redux, Context API)
- Experience with testing frameworks (Jest, Cypress)
- Good understanding of UI/UX principles
- Experience with Agile development methodologies
```

### Example 3: Machine Learning Engineer

```
Role: Machine Learning Engineer
Required Skills: Python, TensorFlow, PyTorch, scikit-learn, pandas, numpy

Minimum CGPA: 8.0
Required Experience: 2 years

Additional Requirements:
- Strong foundation in statistics and linear algebra
- Experience with deep learning architectures (CNN, RNN, Transformers)
- Knowledge of MLOps practices and tools
- Experience with data preprocessing and feature engineering
- Familiarity with cloud ML platforms (AWS SageMaker, Google AI Platform)
- Published research papers or contributions to ML open-source projects (bonus)
```

### Example 4: DevOps Engineer

```
Role: DevOps Engineer
Required Skills: Docker, Kubernetes, Jenkins, Terraform, AWS, Linux

Minimum CGPA: 7.0
Required Experience: 3 years

Additional Requirements:
- Strong scripting skills (Bash, Python)
- Experience with infrastructure as code (IaC)
- Knowledge of monitoring and logging tools (Prometheus, Grafana, ELK)
- Experience with GitOps workflows
- Understanding of networking and security best practices
- Experience with multi-cloud environments
```

### Example 5: Frontend Developer

```
Role: Frontend Developer
Required Skills: React, JavaScript, HTML5, CSS3, Tailwind CSS, REST API

Minimum CGPA: 6.5
Required Experience: 1 year

Additional Requirements:
- Strong understanding of responsive design principles
- Experience with modern JavaScript (ES6+)
- Knowledge of browser compatibility issues
- Experience with version control (Git)
- Understanding of web performance optimization
- Portfolio of previous web projects
```

## Tips for Better Results

### 1. Be Specific About Technologies
Instead of "web development", specify "React, Next.js, TypeScript"

### 2. Include Context
Mention the type of projects or domain:
- "E-commerce platform development"
- "Real-time data processing systems"
- "Mobile-first web applications"

### 3. Prioritize Skills
List the most important skills first in the required skills section

### 4. Mention Preferred Qualifications
Add optional but valuable skills:
```
Preferred Qualifications:
- Open source contributions
- Technical blog posts or articles
- Speaking at conferences or meetups
- Certifications in relevant technologies
```

### 5. Include Team Culture Fit
```
Team Culture:
- Collaborative development environment
- Code review practices
- Agile/Scrum methodology
- Remote-first team
```

## Structured Format for API Calls

When calling the GitHub leaderboard API, structure your prompt like this:

```javascript
const jobDescription = `
Role: ${roleName}
Required Skills: ${skillsList}
${cgpaRequired ? `Minimum CGPA: ${cgpaValue}` : ''}
${experienceRequired ? `Required Experience: ${experienceYears} years` : ''}

${additionalRequirements ? `
Additional Requirements:
${additionalRequirements}` : ''}

${preferredQualifications ? `
Preferred Qualifications:
${preferredQualifications}` : ''}
`.trim();
```

## Analysis Optimization

### For Better Skill Matching
- Use standard technology names (e.g., "React" not "ReactJS")
- Include both frameworks and languages (e.g., "Django, Python" not just "Django")
- Mention specific versions if critical (e.g., "Python 3.9+")

### For Better Semantic Analysis
- Describe the type of work: "building microservices", "data analysis", "UI development"
- Mention scale: "high-traffic applications", "real-time systems", "large-scale databases"
- Include industry context: "fintech", "healthcare", "e-commerce", "gaming"

### For Better Repository Matching
- Mention project types: "CLI tools", "web applications", "libraries", "APIs"
- Include architecture patterns: "MVC", "microservices", "serverless", "monorepo"
- Specify development practices: "test-driven development", "documentation", "CI/CD"

## Sample API Call

```javascript
// Complete example with all fields
const response = await HireSightAPI.generateGitHubLeaderboard(
  ['username1', 'username2', 'username3'],
  `
Role: Senior Full Stack Developer
Required Skills: React, Node.js, TypeScript, PostgreSQL, Docker, AWS

Minimum CGPA: 7.5
Required Experience: 3 years

Additional Requirements:
- Experience with microservices architecture
- Strong understanding of RESTful API design
- Knowledge of CI/CD pipelines and DevOps practices
- Experience with test-driven development
- Previous work on SaaS products

Preferred Qualifications:
- Open source contributions
- Experience with GraphQL
- Knowledge of WebSocket and real-time features
- Familiarity with monitoring and observability tools
  `.trim(),
  5,  // analyze top 5 repos per candidate
  true // use Gemini AI enhancement
);
```

## Response Interpretation

The API returns candidates ranked by:

1. **Skill Match Score (30%)**: Direct match with required skills
2. **Semantic Similarity (25%)**: Contextual understanding of job fit
3. **Activity Score (20%)**: Development activity and engagement
4. **Community Score (15%)**: Stars, forks, followers
5. **Code Quality (10%)**: Repository quality indicators

Use the detailed metrics to understand:
- Which candidates best match your technical requirements
- Who has the most active development history
- Which profiles have strong community engagement
- Overall quality and maintainability of their code

---

**Best Practice**: Combine the structured prompt with the AI analysis feature for the most accurate candidate rankings!
