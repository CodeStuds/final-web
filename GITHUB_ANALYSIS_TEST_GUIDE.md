# Quick Test Guide - GitHub Analysis Feature

## Prerequisites

1. **Set up GitHub Token:**
   ```bash
   export GITHUB_TOKEN="your_github_personal_access_token"
   ```

2. **Set up Gemini API Key (for interview questions):**
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key"
   ```

3. **Start the backend server:**
   ```bash
   cd backend
   python3 api.py
   ```

4. **Open the frontend:**
   Navigate to `DEVANGSHU_FRONTEND/COMPANY_MAIN_PAGE/index.html` in your browser

## Test Cases

### Test 1: View Analyse GitHub Button
**Steps:**
1. Upload resumes with GitHub URLs in them
2. Submit the form
3. Look for candidates with GitHub profiles in the leaderboard
4. Verify "🔍 Analyse GitHub" button appears next to "👤 View Full Profile"
5. Verify button has purple gradient styling

**Expected Result:**
- Button only shows for candidates with GitHub profiles
- Button is styled consistently with other buttons
- Button is clickable

### Test 2: Analyze GitHub Profile
**Steps:**
1. Click "🔍 Analyse GitHub" button for a candidate
2. Observe loading state
3. Wait for analysis to complete

**Expected Result:**
- Modal appears immediately with loading spinner
- Loading message shows "Fetching data from GitHub for [username]..."
- After loading, modal displays:
  - Summary stats (repos, stars, forks, followers)
  - Top languages as tags
  - Top 3 projects with full details
  - Each project shows: name, description, stars, forks, language, topics, link

**Test with these GitHub users:**
- `torvalds` (Linus Torvalds - popular profile)
- `gvanrossum` (Guido van Rossum - Python creator)
- `octocat` (GitHub mascot - simple profile)

### Test 3: Error Handling
**Steps:**
1. Manually modify a candidate's GitHub username to invalid value
2. Click "🔍 Analyse GitHub" button

**Expected Result:**
- Error modal appears
- Clear error message displayed
- "Close" button works

### Test 4: Generate Interview Questions WITH GitHub Data
**Steps:**
1. Select a candidate with a GitHub profile
2. Click "✨ Generate Questions" button
3. Observe the process
4. Review generated questions

**Expected Result:**
- Button shows "Analyzing GitHub..." first
- Then shows "Generating AI Questions..."
- Questions are more specific to candidate's projects
- Questions reference actual technologies from GitHub repos
- Questions mention specific projects or patterns

### Test 5: Generate Interview Questions WITHOUT GitHub Data
**Steps:**
1. Select a candidate without a GitHub profile
2. Click "✨ Generate Questions" button
3. Review generated questions

**Expected Result:**
- No GitHub analysis phase
- Questions generated based on resume data only
- Still relevant and personalized

### Test 6: Modal Interactions
**Steps:**
1. Open GitHub analysis modal
2. Try each close method:
   - Click X button
   - Click outside modal
   - Press Escape key
3. Click project links

**Expected Result:**
- All close methods work
- Project links open in new tab
- Links go to correct GitHub repositories

### Test 7: Mobile Responsiveness
**Steps:**
1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select mobile device (e.g., iPhone 12)
4. Test all features

**Expected Result:**
- Buttons stack vertically on mobile
- Modal fits screen
- Stats grid shows 2 columns on mobile
- Project cards are readable
- All interactions work on touch

### Test 8: Multiple Candidates
**Steps:**
1. Analyze GitHub profiles for 3-4 different candidates
2. Compare results
3. Generate questions for each

**Expected Result:**
- Each analysis is unique
- Data doesn't mix between candidates
- Questions reflect individual GitHub projects
- No caching issues

## API Testing (Optional)

### Test GitHub Analysis API Directly

```bash
# Test with curl
curl -X POST http://localhost:5000/api/github/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "username": "torvalds"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "username": "torvalds",
  "analysis": {
    "total_repos": 5,
    "total_stars": 150000,
    "total_forks": 50000,
    "followers": 180000,
    "top_languages": ["C", "Shell", "Makefile"],
    "bio": "..."
  },
  "top_projects": [
    {
      "name": "linux",
      "description": "Linux kernel source tree",
      "stars": 150000,
      ...
    }
  ],
  "timestamp": "2025-10-30T..."
}
```

### Test Interview Questions API

```bash
curl -X POST http://localhost:5000/api/interview/generate \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "John Doe",
    "candidate_profile": "Full stack developer with 5 years experience..."
  }'
```

## Common Issues & Solutions

### Issue 1: "GitHub analysis module not available"
**Solution:** 
```bash
cd backend/github-data-fetch
pip install -r requirements.txt
```

### Issue 2: Rate limit exceeded
**Solution:**
- Wait for rate limit to reset (check response header)
- Use authenticated GitHub token with higher limits
- Reduce number of repos fetched

### Issue 3: No projects shown
**Possible Causes:**
- User has no public repositories
- All repositories are forks
- API token doesn't have permission
**Solution:** Test with a different GitHub user

### Issue 4: Questions not including GitHub data
**Check:**
1. GitHub analysis succeeded (check browser console)
2. Projects data exists in response
3. No errors in backend logs
4. Gemini API key is valid

### Issue 5: Modal doesn't close
**Solution:**
- Check browser console for JavaScript errors
- Verify event listeners are attached
- Try hard refresh (Ctrl+Shift+R)

## Performance Benchmarks

Expected response times:
- GitHub profile analysis: 2-5 seconds
- Interview question generation (with GitHub): 8-15 seconds
- Interview question generation (without GitHub): 5-10 seconds

## Browser Console Checks

Open browser console (F12 > Console) and look for:
- ✅ No errors in red
- ✅ Successful API calls (200 status)
- ✅ "GitHub data fetched successfully" (if implemented)
- ❌ CORS errors (should not appear)
- ❌ 404 or 500 errors (should not appear)

## Success Criteria

✅ All 8 test cases pass
✅ No console errors
✅ Mobile responsive
✅ Professional UI/UX
✅ Error handling works
✅ Performance is acceptable
✅ GitHub data enhances interview questions

## Demo Script

**For presentation:**

1. "I'll show you our new GitHub analysis feature"
2. Upload sample resumes with GitHub profiles
3. "Notice the purple 'Analyse GitHub' button for candidates with GitHub"
4. Click button, show loading state
5. "Here we see comprehensive GitHub statistics"
6. Point out: repos count, stars, top languages
7. "These are the candidate's top 3 projects"
8. Click a project link to show it opens on GitHub
9. Close modal
10. "Now let's generate interview questions"
11. Click generate questions
12. "Notice it's analyzing GitHub first"
13. Show generated questions
14. "See how questions reference actual projects and technologies"
15. "This gives us much better insight into real coding abilities"

## Troubleshooting Log

Keep notes while testing:
- [ ] All buttons visible ✓/✗
- [ ] GitHub analysis works ✓/✗
- [ ] Projects display correctly ✓/✗
- [ ] Questions enhanced with GitHub ✓/✗
- [ ] Error handling works ✓/✗
- [ ] Mobile responsive ✓/✗
- [ ] Performance acceptable ✓/✗

## Next Steps After Testing

1. Document any bugs found
2. Note performance issues
3. Gather user feedback
4. Plan improvements
5. Update documentation
