# GitHub Analysis with Gemini AI - Setup Guide

## Overview
The GitHub Analysis feature now uses **Gemini 2.0 Flash Exp** AI to provide intelligent insights about candidates based on their resume data and GitHub profiles.

## What's New

### ✨ AI-Powered Insights
Instead of just showing raw GitHub statistics, the system now:
1. Fetches GitHub profile data (repos, stars, projects)
2. Combines it with resume/profile data
3. Sends everything to Gemini AI for analysis
4. Displays comprehensive AI-generated insights including:
   - Overall Assessment
   - Key Strengths
   - Technical Expertise Analysis
   - Project Quality Evaluation
   - Growth Potential
   - Red Flags / Areas for Investigation
   - Recommended Interview Focus Areas
   - Hiring Recommendation

### 🔘 Button Always Visible
- The "🔍 Analyse GitHub" button now shows for **all candidates**
- Even without a GitHub username, AI can analyze resume data
- If GitHub data is available, it enriches the analysis

## Setup Instructions

### 1. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

### 2. Configure the API Key

**Option A: Direct Configuration (Quick)**

Edit `DEVANGSHU_FRONTEND/COMPANY_MAIN_PAGE/index.html`:

```html
<script>
  window.ENV = {
    API_BASE_URL: 'http://localhost:5000/api',
    GEMINI_API_KEY: 'YOUR_ACTUAL_GEMINI_API_KEY_HERE', // Paste your key here
    API_KEY: ''
  };
</script>
```

**Option B: Environment Variables (Production)**

Create a `.env` file or set environment variables:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

Then modify the script to read from environment:

```javascript
window.ENV = {
  GEMINI_API_KEY: process.env.GEMINI_API_KEY || 'fallback_key'
};
```

### 3. Start the Application

```bash
# Backend
cd backend
python3 api.py

# Frontend
# Open DEVANGSHU_FRONTEND/COMPANY_MAIN_PAGE/index.html in browser
```

## How It Works

### User Flow

1. **User clicks "🔍 Analyse GitHub" button** for any candidate
2. **System fetches GitHub data** (if username available):
   - Public repositories count
   - Stars, forks, followers
   - Top 3 projects with details
   - Languages used
3. **System builds comprehensive profile**:
   - Resume data (education, experience, skills)
   - GitHub statistics
   - Project details
4. **Gemini AI analyzes the profile**:
   - Evaluates technical expertise
   - Assesses project quality
   - Identifies strengths and concerns
   - Provides hiring recommendation
5. **Results displayed in modal**:
   - GitHub statistics (if available)
   - AI-generated insights
   - Top projects with links

### Technical Architecture

```
User Action
    ↓
[Analyse GitHub Button]
    ↓
[Fetch GitHub Data via Backend API] (optional)
    ↓
[Combine with Candidate Profile Data]
    ↓
[Send to Gemini 2.0 Flash API]
    ↓
[Parse AI Response]
    ↓
[Display in Modal]
```

## API Calls Made

### 1. GitHub Analysis (Optional)
```javascript
POST http://localhost:5000/api/github/analyze
{
  "username": "github_username"
}
```

### 2. Gemini AI Analysis (Always)
```javascript
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=API_KEY
{
  "contents": [{
    "parts": [{ 
      "text": "Analyze this candidate profile..." 
    }]
  }]
}
```

## Example AI Output

```markdown
## Overall Assessment
John is a strong full-stack developer with 3 years of experience and a solid 
GitHub portfolio. His projects demonstrate practical problem-solving skills 
and modern technology adoption.

## Key Strengths
- Proficient in React, Node.js, and TypeScript
- Active GitHub contributor with consistent commit history
- Strong educational background (9.2 CGPA from IIT)
- Experience with cloud platforms (AWS)
- Good documentation practices in projects

## Technical Expertise
John shows deep understanding of modern web development stack. His GitHub 
projects reveal hands-on experience with microservices architecture, database 
design, and API development. Code quality appears above average based on 
project structure.

## Project Quality
The top 3 GitHub projects show:
1. Real-world problem solving (e-commerce platform)
2. Good use of CI/CD practices
3. Active maintenance (recent commits)
Stars and forks indicate community value.

## Growth Potential
Consistent learning trajectory evident from diverse tech stack. Recent projects 
show adoption of newer technologies like GraphQL and Docker. Good potential 
for senior roles.

## Red Flags / Areas for Investigation
- Verify actual role in team projects (solo vs collaborative)
- Assess system design experience in interview
- Check production deployment experience

## Recommended Interview Focus Areas
- Microservices architecture decisions
- Database scaling strategies
- CI/CD pipeline implementation
- Team collaboration examples

## Hiring Recommendation
**Strong Hire** - Candidate demonstrates both theoretical knowledge and 
practical skills. Good cultural fit indicators. Recommend for senior 
developer position.
```

## Features

### ✅ Works Without GitHub
If candidate doesn't have a GitHub profile:
- AI analyzes resume data alone
- Provides insights based on education, skills, experience
- Still gives hiring recommendations

### ✅ Enhanced with GitHub
If GitHub data is available:
- Richer technical analysis
- Project quality assessment
- Code activity patterns
- Community engagement metrics

### ✅ Comprehensive Insights
AI provides 8 key sections:
1. Overall Assessment
2. Key Strengths
3. Technical Expertise
4. Project Quality
5. Growth Potential
6. Red Flags
7. Interview Focus Areas
8. Hiring Recommendation

### ✅ Professional UI
- Loading states with spinners
- Formatted markdown-to-HTML conversion
- GitHub statistics cards
- Project cards with links
- Responsive design

## Troubleshooting

### Issue: "Failed to get AI insights"

**Cause:** Gemini API key not configured or invalid

**Solution:**
1. Check API key in `index.html`
2. Verify key is valid at [Google AI Studio](https://makersuite.google.com/)
3. Check browser console for detailed error

### Issue: "GitHub data not available"

**Cause:** GitHub username not in resume or invalid

**Solution:**
- Analysis still works without GitHub data
- AI provides insights based on resume alone
- Ensure resumes include GitHub usernames if needed

### Issue: Button doesn't appear

**Cause:** Browser cache or JavaScript error

**Solution:**
1. Hard refresh (Ctrl+Shift+R)
2. Check browser console for errors
3. Verify script.js is loaded

### Issue: API rate limit exceeded

**Cause:** Too many Gemini API calls

**Solution:**
- Free tier: 15 requests per minute
- Paid tier: Higher limits
- Wait a minute and try again

## Cost Considerations

### Gemini 2.0 Flash Pricing (as of 2024)
- **Free Tier:** 15 RPM, 1 million tokens/day
- **Paid Tier:** $0.075 per 1M input tokens, $0.30 per 1M output tokens

### Estimated Costs
- Per analysis: ~$0.001 - $0.003
- 1000 analyses: ~$1-3
- Very cost-effective for hiring use case

## Testing

### Test Case 1: Candidate with GitHub
1. Upload resume with GitHub username
2. Click "🔍 Analyse GitHub"
3. Verify GitHub stats display
4. Verify AI insights appear
5. Check project links work

### Test Case 2: Candidate without GitHub
1. Upload resume without GitHub
2. Click "🔍 Analyse GitHub"
3. Verify AI insights still generate
4. Check insights based on resume data

### Test Case 3: Invalid GitHub Username
1. Manually set invalid username
2. Click button
3. Verify graceful fallback
4. AI insights still work

## Security Notes

⚠️ **Important:**
- Never commit API keys to version control
- Use environment variables in production
- Implement server-side API key management
- Add rate limiting to prevent abuse
- Monitor API usage and costs

## Future Enhancements

### Planned Features
- [ ] Cache AI insights for 24 hours
- [ ] Export insights as PDF report
- [ ] Compare multiple candidates
- [ ] Custom analysis prompts
- [ ] Integration with ATS systems
- [ ] Sentiment analysis of GitHub comments
- [ ] Code quality metrics

## Support

For issues or questions:
1. Check browser console for errors
2. Verify API key configuration
3. Check network tab for failed requests
4. Review this documentation

## Model Information

**Model Used:** `gemini-2.0-flash-exp`
- Latest experimental flash model
- Fast responses (~2-5 seconds)
- High quality analysis
- Context window: 1M tokens
- Multimodal capable

**Why This Model:**
- Optimized for speed
- Cost-effective
- Excellent for structured analysis
- Reliable for professional use cases

## Example Integration

```javascript
// Quick test in browser console
const testAnalysis = async () => {
  const candidate = {
    name: "Test User",
    skills: ["JavaScript", "Python"],
    exp: "3 yrs",
    score: 85
  };
  
  await analyseGitHubProfile(candidate, "test-username");
};

testAnalysis();
```

## Conclusion

The GitHub Analysis feature now provides AI-powered insights that help recruiters make better hiring decisions. By combining resume data with GitHub activity and using Gemini AI for analysis, the system offers comprehensive candidate assessments that go beyond simple statistics.

The button is now visible for all candidates, ensuring consistent user experience and making the feature more accessible.
