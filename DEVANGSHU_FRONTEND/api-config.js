// ======== HIRESIGHT API CONFIGURATION ========
// Centralized API configuration for HireSight backend
// IMPORTANT: Set these values in your environment or build configuration
// DO NOT commit actual API keys to version control

const HIRESIGHT_API_CONFIG = {
  // Base API URL - defaults to localhost for development
  baseURL: window.ENV?.API_BASE_URL || "http://localhost:5000/api",

  // Optional API key for authenticated requests
  apiKey: window.ENV?.API_KEY || "",

  // Timeout for API requests (in milliseconds)
  timeout: 30000,

  // Endpoints
  endpoints: {
    health: "/health",
    rank: "/rank",
    analyze: "/analyze",
    githubAnalyze: "/github/analyze",
    interviewGenerate: "/interview/generate",
    leaderboard: "/leaderboard",
    sendInterviewRequests: "/email/send-interview-requests"
  }
};

// Helper function to get headers for API requests
function getAPIHeaders(isJSON = true) {
  const headers = {};

  if (isJSON) {
    headers['Content-Type'] = 'application/json';
  }

  // Add API key if configured
  if (HIRESIGHT_API_CONFIG.apiKey) {
    headers['X-API-Key'] = HIRESIGHT_API_CONFIG.apiKey;
  }

  return headers;
}

// Helper function to build full API URL
function getAPIUrl(endpoint) {
  return `${HIRESIGHT_API_CONFIG.baseURL}${HIRESIGHT_API_CONFIG.endpoints[endpoint] || endpoint}`;
}

// API Service Object with all API methods
const HireSightAPI = {
  // Export base URL for direct use
  baseUrl: HIRESIGHT_API_CONFIG.baseURL,

  /**
   * Check API health status
   */
  async checkHealth() {
    try {
      const response = await fetch(getAPIUrl('health'), {
        method: 'GET',
        headers: getAPIHeaders()
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  },

  /**
   * Rank candidates based on resumes and job requirements
   * @param {FormData} formData - Form data with role, skills, experience, cgpa, additional, and file
   */
  async rankCandidates(formData) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), HIRESIGHT_API_CONFIG.timeout);

      const response = await fetch(getAPIUrl('rank'), {
        method: 'POST',
        body: formData,
        headers: HIRESIGHT_API_CONFIG.apiKey ? { 'X-API-Key': HIRESIGHT_API_CONFIG.apiKey } : {},
        signal: controller.signal
      });

      clearTimeout(timeout);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Rank candidates error:', error);
      throw error;
    }
  },

  /**
   * Analyze a single resume
   * @param {File} resumeFile - Resume file (PDF, DOCX, DOC)
   */
  async analyzeResume(resumeFile) {
    try {
      const formData = new FormData();
      formData.append('resume', resumeFile);

      const response = await fetch(getAPIUrl('analyze'), {
        method: 'POST',
        body: formData,
        headers: HIRESIGHT_API_CONFIG.apiKey ? { 'X-API-Key': HIRESIGHT_API_CONFIG.apiKey } : {}
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Analyze resume error:', error);
      throw error;
    }
  },

  /**
   * Analyze a GitHub profile
   * @param {string} username - GitHub username
   * @param {object} jobRequirements - Optional job requirements for matching
   */
  async analyzeGitHub(username, jobRequirements = null) {
    try {
      const body = {
        username: username
      };

      if (jobRequirements) {
        body.job_requirements = jobRequirements;
      }

      const response = await fetch(getAPIUrl('githubAnalyze'), {
        method: 'POST',
        headers: getAPIHeaders(),
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('GitHub analysis error:', error);
      throw error;
    }
  },

  /**
   * Generate interview questions based on candidate profile
   * @param {string} candidateName - Candidate's name
   * @param {string} candidateProfile - Combined profile text from GitHub/LinkedIn
   * @param {string} apiKey - Optional Gemini API key (if not set in env)
   */
  async generateInterviewQuestions(candidateName, candidateProfile, apiKey = null) {
    try {
      const body = {
        candidate_name: candidateName,
        candidate_profile: candidateProfile
      };

      if (apiKey) {
        body.api_key = apiKey;
      }

      const response = await fetch(getAPIUrl('interviewGenerate'), {
        method: 'POST',
        headers: getAPIHeaders(),
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Interview generation error:', error);
      throw error;
    }
  },

  /**
   * Generate leaderboard from candidate scores
   * @param {Array} candidates - Array of candidate objects with scores
   * @param {object} weights - Optional weights for different score types
   */
  async generateLeaderboard(candidates, weights = null) {
    try {
      const body = {
        candidates: candidates
      };

      if (weights) {
        body.weights = weights;
      }

      const response = await fetch(getAPIUrl('leaderboard'), {
        method: 'POST',
        headers: getAPIHeaders(),
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Leaderboard generation error:', error);
      throw error;
    }
  },

  /**
   * Send interview requests to selected candidates
   * @param {Array} candidates - Array of candidate objects with name and email
   * @param {Array} questions - Optional array of interview questions
   */
  async sendInterviewRequests(candidates, questions = null) {
    try {
      const body = {
        candidates: candidates
      };

      if (questions) {
        body.questions = questions;
      }

      const response = await fetch(getAPIUrl('sendInterviewRequests'), {
        method: 'POST',
        headers: getAPIHeaders(),
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Send interview requests error:', error);
      throw error;
    }
  }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { HIRESIGHT_API_CONFIG, HireSightAPI, getAPIHeaders, getAPIUrl };
}
