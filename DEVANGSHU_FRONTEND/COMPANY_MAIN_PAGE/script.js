// -----------------------------
// ELEMENT REFERENCES
// -----------------------------
const cgpaYes = document.getElementById("cgpa-yes");
const cgpaNo = document.getElementById("cgpa-no");
const cgpaSomewhat = document.getElementById("cgpa-somewhat");
const cgpaSliderContainer = document.getElementById("cgpaSliderContainer");
const cgpaRange = document.getElementById("cgpaRange");
const cgpaValue = document.getElementById("cgpaValue");

const experienceYes = document.getElementById("experience-yes");
const experienceNo = document.getElementById("experience-no");
const experienceSomewhat = document.getElementById("experience-somewhat");
const experienceSliderContainer = document.getElementById("experienceSliderContainer");
const experienceRange = document.getElementById("experienceRange");
const experienceValue = document.getElementById("experienceValue");

const submitBtn = document.getElementById("submitBtn");
const leaderboard = document.getElementById("leaderboard");
const formCard = document.getElementById("formCard");
const leaderboardHeader = document.getElementById("leaderboardHeader");
const resultsContainer = document.getElementById("results");
const closeLeaderboardBtn = document.getElementById("closeLeaderboard");
const logoutBtn = document.getElementById("logoutBtn");

// -----------------------------
// AUTH GUARD (redirect if not logged in)
// -----------------------------
(async () => {
  try {
    if (typeof checkAuth === 'function') {
      const session = await checkAuth();
      if (!session) {
        // Not authenticated; send to login
        window.location.href = '/COMPANY_LOGIN/index.html';
      }
    }
  } catch (err) {
    console.warn('Auth check failed:', err);
  }
})();

// -----------------------------
// CGPA SLIDER TOGGLE
// -----------------------------
function toggleCGPASlider() {
  if (cgpaYes.checked) {
    cgpaSliderContainer.style.display = "block";
  } else {
    cgpaSliderContainer.style.display = "none";
  }
}

[cgpaYes, cgpaNo, cgpaSomewhat].forEach((radio) =>
  radio.addEventListener("change", toggleCGPASlider)
);

// Update CGPA value display
cgpaRange.addEventListener("input", () => {
  cgpaValue.textContent = parseFloat(cgpaRange.value).toFixed(2);
});

// -----------------------------
// EXPERIENCE SLIDER TOGGLE
// -----------------------------
function toggleExperienceSlider() {
  if (experienceYes.checked) {
    experienceSliderContainer.style.display = "block";
  } else {
    experienceSliderContainer.style.display = "none";
  }
}

[experienceYes, experienceNo, experienceSomewhat].forEach((radio) =>
  radio.addEventListener("change", toggleExperienceSlider)
);

// Update experience value display
experienceRange.addEventListener("input", () => {
  experienceValue.textContent = `${experienceRange.value} yrs`;
});

// -----------------------------
// SUBMIT BUTTON BEHAVIOR
// -----------------------------
submitBtn.addEventListener("click", async (e) => {
  e.preventDefault();

  // Get form values
  const role = document.querySelector('input[placeholder*="Senior Software Engineer"]').value;
  const skills = document.querySelector('input[placeholder*="React, TypeScript"]').value;
  const cgpaImportance = document.querySelector('input[name="cgpa"]:checked').value;
  const cgpaValue = cgpaImportance === 'yes' ? cgpaRange.value : '';
  const experienceImportance = document.querySelector('input[name="experience"]:checked').value;
  const experienceValue = experienceImportance === 'yes' ? experienceRange.value : '';
  const additional = document.querySelector('textarea').value;
  const fileInput = document.getElementById('uploadFile');
  const file = fileInput.files[0];

  // Validate inputs
  if (!role || !skills) {
    alert('Please fill in the role and required skills');
    return;
  }

  if (!file) {
    alert('Please upload a resume file or ZIP archive');
    return;
  }

  // Show loading state
  const attributes = document.querySelector(".attributes");
  const originalButtonText = submitBtn.textContent;
  submitBtn.textContent = "Processing Resumes...";
  submitBtn.disabled = true;

  try {
    // Call the comprehensive resume parsing API
    const formData = new FormData();
    formData.append('file', file);
    formData.append('role', role);
    formData.append('skills', skills);
    formData.append('cgpa', cgpaValue);
    formData.append('experience', experienceValue);
    formData.append('additional', additional);
    formData.append('calculate_score', 'true');
    formData.append('use_ai', 'true');

    // Store job details in sessionStorage for later use (email sending)
    const jobDetails = {
      role: role,
      skills: skills,
      description: additional || `We are hiring for ${role}. Required skills: ${skills}`,
      cgpa: cgpaValue,
      experience: experienceValue
    };
    sessionStorage.setItem('currentJobDetails', JSON.stringify(jobDetails));

    const response = await fetch(`${HireSightAPI.baseUrl}/resume/parse-comprehensive`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to process resumes');
    }

    const data = await response.json();

    if (data.success && data.results && data.results.length > 0) {
      // Hide the form & show leaderboard
      attributes.style.display = "none";
      leaderboard.style.display = "block";
      leaderboardHeader.classList.add("visible");

      // Populate leaderboard with real data
      populateLeaderboard(data.results);
    } else {
      alert('No candidates found in the uploaded file(s)');
      submitBtn.textContent = originalButtonText;
      submitBtn.disabled = false;
    }

  } catch (error) {
    console.error('Error processing resumes:', error);
    alert(`Error: ${error.message}`);
    submitBtn.textContent = originalButtonText;
    submitBtn.disabled = false;
  }
});

// -----------------------------
// BACK BUTTON BEHAVIOR
// -----------------------------
closeLeaderboardBtn.addEventListener("click", () => {
  leaderboard.style.display = "none";
  leaderboardHeader.classList.remove("visible");

  const attributes = document.querySelector(".attributes");
  attributes.style.display = "block";
});

// -----------------------------
// POPULATE LEADERBOARD
// -----------------------------
function populateLeaderboard(candidatesData = null) {
  resultsContainer.innerHTML = "";

  // Use provided data or fall back to mock data for testing
  const mockCandidates = [
    {
      name: "Ananya Sharma",
      score: 96,
      cgpa: 9.2,
      exp: "3 yrs",
      note: "Strong React + Node expertise",
      email: "ananya.sharma@email.com",
      phone: "+91 98765 43210",
      location: "Mumbai, India",
      skills: ["React", "Node.js", "TypeScript", "MongoDB", "GraphQL", "AWS"],
      education: "B.Tech in Computer Science",
      university: "IIT Bombay",
      projects: 12,
      github: "ananya-dev",
      linkedin: "ananya-sharma"
    },
    {
      name: "Rohit Mehta",
      score: 92,
      cgpa: 8.8,
      exp: "2 yrs",
      note: "Excellent problem-solving and team skills",
      email: "rohit.mehta@email.com",
      phone: "+91 98765 43211",
      location: "Bangalore, India",
      skills: ["Python", "Django", "PostgreSQL", "Docker", "Redis", "CI/CD"],
      education: "B.Tech in Software Engineering",
      university: "BITS Pilani",
      projects: 9,
      github: "rohit-codes",
      linkedin: "rohit-mehta"
    },
    {
      name: "Isha Verma",
      score: 88,
      cgpa: 9.0,
      exp: "1 yr",
      note: "Proficient in TypeScript and system design",
      email: "isha.verma@email.com",
      phone: "+91 98765 43212",
      location: "Delhi, India",
      skills: ["TypeScript", "Angular", "NestJS", "MySQL", "Microservices"],
      education: "B.Tech in Information Technology",
      university: "DTU Delhi",
      projects: 7,
      github: "isha-dev",
      linkedin: "isha-verma"
    },
  ];

  const candidates = candidatesData || mockCandidates;

  candidates.forEach((c, i) => {
    // Ensure all fields have default values
    const candidate = {
      name: c.name || 'Unknown Candidate',
      score: c.score || c.matchScore || 0,
      cgpa: c.cgpa || 0,
      exp: c.exp || (c.experience_years ? `${c.experience_years} yrs` : '0 yrs'),
      note: c.note || c.summary || 'No summary available',
      email: c.email || '',
      phone: c.phone || '',
      location: c.location || '',
      skills: Array.isArray(c.skills) ? c.skills : [],
      education: c.education || '',
      university: c.university || '',
      projects: c.projects || c.projects_count || 0,
      github: c.github || '',
      linkedin: c.linkedin || ''
    };

    // Format GitHub and LinkedIn as full URLs for display
    const githubDisplay = candidate.github ? `github.com/${candidate.github}` : '';
    const linkedinDisplay = candidate.linkedin ? `linkedin.com/in/${candidate.linkedin}` : '';

    const card = document.createElement("div");
    card.classList.add("result-card");
    card.innerHTML = `
      <div class="card-header">
        <input type="checkbox" class="candidate-checkbox" data-index="${i}" data-email="${candidate.email}" data-name="${candidate.name}">
        <div class="rank">#${i + 1}</div>
        <div class="info">
          <div class="name">${candidate.name}</div>
          <div class="meta-line">Score: <b>${candidate.score}</b> | CGPA: <b>${candidate.cgpa.toFixed(1)}</b> | Exp: <b>${candidate.exp}</b> | Projects: <b>${candidate.projects}</b></div>
          <div class="note">${candidate.note}</div>
        </div>
      </div>

      <div class="card-actions">
        <button class="details-btn" data-index="${i}">
          📋 Show Details
        </button>
        <button class="view-full-btn" data-index="${i}">
          👤 View Full Profile
        </button>
        <button class="analyse-github-btn" data-index="${i}" data-github="${candidate.github || ''}">
          🔍 Analyse GitHub
        </button>
      </div>

      <div class="card-details" id="details-${i}">
        <div class="detail-section">
          <h4>📞 Contact Information</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">Email</span>
              <span class="detail-value">${candidate.email || 'Not provided'}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Phone</span>
              <span class="detail-value">${candidate.phone || 'Not provided'}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Location</span>
              <span class="detail-value">${candidate.location || 'Not provided'}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4>🎓 Education</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">Degree</span>
              <span class="detail-value">${candidate.education || 'Not provided'}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">University</span>
              <span class="detail-value">${candidate.university || 'Not provided'}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">CGPA</span>
              <span class="detail-value">${candidate.cgpa > 0 ? candidate.cgpa.toFixed(2) + '/10' : 'Not provided'}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4>💻 Technical Skills</h4>
          <div class="skills-list">
            ${candidate.skills.length > 0
              ? candidate.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')
              : '<span style="color: #64748b;">No skills listed</span>'}
          </div>
        </div>

        <div class="detail-section">
          <h4>💼 Experience & Projects</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">Experience</span>
              <span class="detail-value">${candidate.exp}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Projects</span>
              <span class="detail-value">${candidate.projects} completed</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4>🔗 Professional Links</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">GitHub</span>
              <span class="detail-value">${githubDisplay || 'Not provided'}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">LinkedIn</span>
              <span class="detail-value">${linkedinDisplay || 'Not provided'}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Interview Questions Generator Section -->
      <div class="question-gen-section">
        <div class="question-gen-header">
          <span style="font-size: 1.5rem;">🎯</span>
          <h4>Interview Questions Generator</h4>
        </div>
        <p class="question-gen-description">
          Generate AI-powered interview questions tailored for ${candidate.name}
        </p>
        <button class="generate-questions-btn" data-index="${i}" data-name="${candidate.name}">
          ✨ Generate Questions
        </button>
        <div class="generated-questions" id="generated-questions-${i}" style="display: none;"></div>
      </div>
    `;
    resultsContainer.appendChild(card);
  });

  // Add Send Request button container
  const sendRequestContainer = document.createElement("div");
  sendRequestContainer.className = "send-request-container";
  sendRequestContainer.innerHTML = `
    <div class="selection-info">
      Selected: <span class="selection-count">0</span> candidate(s)
    </div>
    <button class="send-request-btn" id="sendRequestBtn" disabled>
      📧 Send Interview Request
    </button>
  `;
  resultsContainer.appendChild(sendRequestContainer);

  // Attach event listeners
  attachCardEventListeners(candidates);
  attachCheckboxListeners();
}

// -----------------------------
// ATTACH CHECKBOX LISTENERS
// -----------------------------
function attachCheckboxListeners() {
  const checkboxes = document.querySelectorAll('.candidate-checkbox');
  const sendBtn = document.getElementById('sendRequestBtn');
  const selectionCount = document.querySelector('.selection-count');

  function updateSelectionCount() {
    const checkedCount = document.querySelectorAll('.candidate-checkbox:checked').length;
    selectionCount.textContent = checkedCount;
    sendBtn.disabled = checkedCount === 0;
  }

  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', updateSelectionCount);
  });

  // Send request button handler
  sendBtn.addEventListener('click', sendInterviewRequests);
}

// -----------------------------
// SEND INTERVIEW REQUESTS
// -----------------------------
async function sendInterviewRequests() {
  const selectedCheckboxes = document.querySelectorAll('.candidate-checkbox:checked');

  if (selectedCheckboxes.length === 0) {
    alert('Please select at least one candidate.');
    return;
  }

  const selectedCandidates = Array.from(selectedCheckboxes).map(cb => ({
    name: cb.getAttribute('data-name'),
    email: cb.getAttribute('data-email')
  }));

  const sendBtn = document.getElementById('sendRequestBtn');
  const originalText = sendBtn.textContent;
  sendBtn.disabled = true;
  sendBtn.textContent = '📤 Sending...';

  try {
    // Get stored job details
    const jobDetails = JSON.parse(sessionStorage.getItem('currentJobDetails') || '{}');
    
    // Get company info from Supabase auth
    let companyInfo = {
      company_name: 'HireSight Partner Company',
      company_email: 'hr@company.com'
    };
    
    try {
      const user = await getCurrentUser();
      if (user && user.user_metadata) {
        companyInfo = {
          company_name: user.user_metadata.company_name || companyInfo.company_name,
          company_email: user.email || companyInfo.company_email
        };
      }
    } catch (authError) {
      console.warn('Could not fetch user info, using default company info:', authError);
    }

    // Call the real API with complete data
    const response = await HireSightAPI.sendInterviewRequests(
      selectedCandidates,
      jobDetails,
      companyInfo
    );

    if (response.success) {
      // Show Lottie animation with success message
      showEmailSentAnimation(selectedCandidates);

      // Uncheck all checkboxes
      selectedCheckboxes.forEach(cb => cb.checked = false);

      // Update count
      document.querySelector('.selection-count').textContent = '0';
      
      // Show detailed success message
      if (response.sent > 0) {
        console.log(`✅ Successfully sent ${response.sent} email(s)`);
        if (response.failed > 0) {
          console.warn(`⚠️ Failed to send ${response.failed} email(s)`);
        }
      }
    } else {
      throw new Error(response.error || 'Failed to send interview requests');
    }

  } catch (error) {
    console.error('Error sending requests:', error);
    alert(`❌ Failed to send interview requests: ${error.message}`);
    sendBtn.disabled = false;
    sendBtn.textContent = originalText;
  } finally {
    // Re-enable button after animation is shown
    setTimeout(() => {
      sendBtn.disabled = false;
      sendBtn.textContent = originalText;
    }, 3000);
  }
}

// -----------------------------
// SHOW EMAIL SENT LOTTIE ANIMATION
// -----------------------------
function showEmailSentAnimation(candidates) {
  // Check if Lottie is loaded
  if (typeof lottie === 'undefined') {
    console.error('Lottie library not loaded');
    alert(`✅ Interview requests sent successfully to:\n\n${candidates.map(c => `${c.name} (${c.email})`).join('\n')}`);
    addQuestionGenerationSections(candidates);
    return;
  }

  // Create modal if it doesn't exist
  let lottieModal = document.getElementById('lottieModal');
  if (!lottieModal) {
    lottieModal = document.createElement('div');
    lottieModal.id = 'lottieModal';
    lottieModal.classList.add('lottie-modal-overlay');
    document.body.appendChild(lottieModal);
  }

  // Create candidate list HTML
  const candidateListHTML = candidates.map(c => 
    `<li>${c.name} <span style="color: #94a3b8;">(${c.email})</span></li>`
  ).join('');

  lottieModal.innerHTML = `
    <div class="lottie-animation-container" id="lottieAnimationContainer">
      <div class="thumbs-up-emoji">👍</div>
    </div>
    <div class="lottie-message">
      <h3>✅ Requests Sent Successfully!</h3>
      <p>Interview requests have been sent to the following candidates:</p>
      <div class="lottie-candidate-list">
        <strong>Recipients (${candidates.length}):</strong>
        <ul>
          ${candidateListHTML}
        </ul>
      </div>
      <button class="lottie-close-btn" id="closeLottieModal">Got it!</button>
    </div>
  `;

  lottieModal.classList.add('active');

  // Initialize Lottie animation
  const animationContainer = document.getElementById('lottieAnimationContainer');
  
  // Try loading animation with error handling
  try {
    const animation = lottie.loadAnimation({
      container: animationContainer,
      renderer: 'svg',
      loop: false,
      autoplay: true,
      path: 'Email_Sent_by_Todd_Rocheford[1].json'
    });

    // Slow down the animation speed
    animation.setSpeed(0.4);

    animation.addEventListener('DOMLoaded', () => {
      console.log('Animation loaded successfully');
    });

    animation.addEventListener('error', (err) => {
      console.error('Animation error:', err);
      animationContainer.innerHTML = '<div class="thumbs-up-emoji">👍</div>';
    });

    // Close button handler
    const closeBtn = document.getElementById('closeLottieModal');
    closeBtn.addEventListener('click', () => {
      lottieModal.classList.remove('active');
      if (animation) animation.destroy();
      
      // Add question generation sections to candidate cards
      addQuestionGenerationSections(candidates);
    });

    // Click outside to close
    lottieModal.addEventListener('click', (e) => {
      if (e.target === lottieModal) {
        lottieModal.classList.remove('active');
        if (animation) animation.destroy();
      }
    });

    // Escape key to close
    const escapeHandler = (e) => {
      if (e.key === 'Escape' && lottieModal.classList.contains('active')) {
        lottieModal.classList.remove('active');
        if (animation) animation.destroy();
        document.removeEventListener('keydown', escapeHandler);
      }
    };
    document.addEventListener('keydown', escapeHandler);

  } catch (error) {
    console.error('Failed to load animation:', error);
    animationContainer.innerHTML = '<div class="thumbs-up-emoji">👍</div>';
    
    const closeBtn = document.getElementById('closeLottieModal');
    closeBtn.addEventListener('click', () => {
      lottieModal.classList.remove('active');
      addQuestionGenerationSections(candidates);
    });
  }
}

// -----------------------------
// ATTACH EVENT LISTENERS FOR CARDS
// -----------------------------
function attachCardEventListeners(candidates) {
  // Details toggle buttons
  document.querySelectorAll('.details-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const index = e.target.getAttribute('data-index');
      const detailsDiv = document.getElementById(`details-${index}`);
      const isOpen = detailsDiv.classList.contains('open');
      
      // Close all details first
      document.querySelectorAll('.card-details').forEach(d => d.classList.remove('open'));
      
      // Toggle current
      if (!isOpen) {
        detailsDiv.classList.add('open');
        e.target.textContent = '📋 Hide Details';
      } else {
        e.target.textContent = '📋 Show Details';
      }
    });
  });

  // View full profile buttons
  document.querySelectorAll('.view-full-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const index = e.target.getAttribute('data-index');
      showFullProfileModal(candidates[index]);
    });
  });

  // Analyse GitHub buttons
  document.querySelectorAll('.analyse-github-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const index = e.target.getAttribute('data-index');
      const github = e.target.getAttribute('data-github');
      analyseGitHubProfile(candidates[index], github);
    });
  });

  // Generate questions buttons
  document.querySelectorAll('.generate-questions-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const index = parseInt(e.target.getAttribute('data-index'));
      generateQuestionsForCandidate(index, candidates[index]);
    });
  });
}

// -----------------------------
// SHOW FULL PROFILE MODAL
// -----------------------------
function showFullProfileModal(candidate) {
  // Create modal if it doesn't exist
  let modal = document.getElementById('profileModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'profileModal';
    modal.classList.add('modal-overlay');
    document.body.appendChild(modal);
  }

  // Format GitHub and LinkedIn
  const githubDisplay = candidate.github ? `github.com/${candidate.github}` : 'Not provided';
  const linkedinDisplay = candidate.linkedin ? `linkedin.com/in/${candidate.linkedin}` : 'Not provided';

  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <h3>${candidate.name}</h3>
        <button class="close-modal-btn">&times;</button>
      </div>

      <div class="modal-body">
        <div class="modal-section">
          <h4>📊 Overview</h4>
          <div class="modal-detail-grid">
            <div class="modal-detail-item">
              <span class="modal-detail-label">Match Score</span>
              <span class="modal-detail-value">${candidate.score}/100</span>
            </div>
            <div class="modal-detail-item">
              <span class="modal-detail-label">CGPA</span>
              <span class="modal-detail-value">${candidate.cgpa > 0 ? candidate.cgpa.toFixed(2) + '/10' : 'Not provided'}</span>
            </div>
            <div class="modal-detail-item">
              <span class="modal-detail-label">Experience</span>
              <span class="modal-detail-value">${candidate.exp}</span>
            </div>
            <div class="modal-detail-item">
              <span class="modal-detail-label">Projects</span>
              <span class="modal-detail-value">${candidate.projects} completed</span>
            </div>
          </div>
        </div>

        <div class="modal-section">
          <h4>📞 Contact Information</h4>
          <div class="modal-detail-grid">
            <div class="modal-detail-item">
              <span class="modal-detail-label">Email</span>
              <span class="modal-detail-value">${candidate.email || 'Not provided'}</span>
            </div>
            <div class="modal-detail-item">
              <span class="modal-detail-label">Phone</span>
              <span class="modal-detail-value">${candidate.phone || 'Not provided'}</span>
            </div>
            <div class="modal-detail-item">
              <span class="modal-detail-label">Location</span>
              <span class="modal-detail-value">${candidate.location || 'Not provided'}</span>
            </div>
          </div>
        </div>

        <div class="modal-section">
          <h4>🎓 Education</h4>
          <div class="modal-detail-grid">
            <div class="modal-detail-item">
              <span class="modal-detail-label">Degree</span>
              <span class="modal-detail-value">${candidate.education || 'Not provided'}</span>
            </div>
            <div class="modal-detail-item">
              <span class="modal-detail-label">University</span>
              <span class="modal-detail-value">${candidate.university || 'Not provided'}</span>
            </div>
          </div>
        </div>

        <div class="modal-section">
          <h4>💻 Technical Skills</h4>
          <div class="modal-skills">
            ${Array.isArray(candidate.skills) && candidate.skills.length > 0
              ? candidate.skills.map(skill => `<span class="modal-skill-tag">${skill}</span>`).join('')
              : '<span style="color: #94a3b8;">No skills listed</span>'}
          </div>
        </div>

        <div class="modal-section">
          <h4>🔗 Professional Links</h4>
          <div class="modal-detail-grid">
            <div class="modal-detail-item">
              <span class="modal-detail-label">GitHub</span>
              <span class="modal-detail-value">${githubDisplay}</span>
            </div>
            <div class="modal-detail-item">
              <span class="modal-detail-label">LinkedIn</span>
              <span class="modal-detail-value">${linkedinDisplay}</span>
            </div>
          </div>
        </div>

        <div class="modal-section">
          <h4>📝 Summary</h4>
          <p style="color: #475569; line-height: 1.6;">${candidate.note || 'No summary available'}</p>
        </div>
      </div>
    </div>
  `;

  modal.classList.add('active');

  // Close modal handlers
  const closeBtn = modal.querySelector('.close-modal-btn');
  closeBtn.addEventListener('click', () => {
    modal.classList.remove('active');
  });

  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.classList.remove('active');
    }
  });

  // Escape key to close
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      modal.classList.remove('active');
    }
  });
}

// -----------------------------
// ANALYSE GITHUB PROFILE
// -----------------------------
async function analyseGitHubProfile(candidate, githubUsername) {
  // Create modal if it doesn't exist
  let modal = document.getElementById('githubAnalysisModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'githubAnalysisModal';
    modal.classList.add('modal-overlay');
    document.body.appendChild(modal);
  }

  // Show loading state
  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <h3>🔍 Analyzing GitHub Profile with AI</h3>
        <button class="close-modal-btn">&times;</button>
      </div>
      <div class="modal-body" style="text-align: center; padding: 3rem;">
        <div class="question-loading-spinner" style="margin: 0 auto 1rem;"></div>
        <p>Fetching data from GitHub${githubUsername ? ` for <strong>${githubUsername}</strong>` : ''}...</p>
        <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">Using Gemini AI to generate insights</p>
      </div>
    </div>
  `;

  modal.classList.add('active');

  try {
    let githubData = null;
    let aiInsights = '';
    
    // Try to fetch GitHub data if username is provided
    if (githubUsername && githubUsername.trim()) {
      try {
        const response = await HireSightAPI.analyzeGitHub(githubUsername);
        if (response.success) {
          githubData = response;
        }
      } catch (githubError) {
        console.warn('GitHub API error:', githubError);
        // Continue without GitHub data
      }
    }

    // Update loading message for AI analysis
    modal.querySelector('.modal-body p').innerHTML = 
      'Generating AI insights about the candidate...';

    // Prepare profile data for AI analysis
    let profileText = `
CANDIDATE ANALYSIS REQUEST
==========================
Name: ${candidate.name}
Email: ${candidate.email || 'Not provided'}
Location: ${candidate.location || 'Not provided'}

EDUCATION
---------
Degree: ${candidate.education || 'Not specified'}
University: ${candidate.university || 'Not specified'}
CGPA: ${candidate.cgpa > 0 ? candidate.cgpa + '/10' : 'Not provided'}

PROFESSIONAL BACKGROUND
-----------------------
Experience: ${candidate.exp}
Projects Completed: ${candidate.projects}
Match Score: ${candidate.score}/100

TECHNICAL SKILLS
----------------
${candidate.skills && candidate.skills.length > 0 ? candidate.skills.join(', ') : 'Not specified'}
`;

    // Add GitHub data if available
    if (githubData && githubData.top_projects && githubData.top_projects.length > 0) {
      profileText += `\n\nGITHUB PROFILE ANALYSIS
-----------------------
Username: ${githubUsername}
Public Repositories: ${githubData.analysis?.total_repos || 0}
Total Stars: ${githubData.analysis?.total_stars || 0}
Total Forks: ${githubData.analysis?.total_forks || 0}
Followers: ${githubData.analysis?.followers || 0}

TOP PROGRAMMING LANGUAGES
-------------------------
${githubData.analysis?.top_languages ? githubData.analysis.top_languages.join(', ') : 'N/A'}

TOP 3 GITHUB PROJECTS
---------------------
`;
      githubData.top_projects.forEach((project, idx) => {
        profileText += `
${idx + 1}. ${project.name}
   Description: ${project.description || 'No description'}
   Stars: ${project.stars} | Forks: ${project.forks}
   Language: ${project.language || 'Unknown'}
   Technologies: ${Object.keys(project.languages || {}).join(', ') || 'N/A'}
   Topics: ${project.topics && project.topics.length > 0 ? project.topics.join(', ') : 'None'}
   URL: ${project.url}
`;
      });
    } else if (githubUsername && githubUsername.trim()) {
      profileText += `\n\nGITHUB PROFILE
--------------
Username: ${githubUsername}
Note: Limited or no public repository data available
`;
    } else {
      profileText += `\n\nGITHUB PROFILE
--------------
GitHub username not provided in resume
`;
    }

    profileText += `\n\nPROFESSIONAL SUMMARY
-------------------
${candidate.note || 'No summary provided'}
`;

    // Call Gemini AI for insights
    const aiPrompt = `You are an expert technical recruiter and software engineering analyst.

Analyze the following candidate profile and provide a comprehensive assessment in a structured format:

${profileText}

Please provide:
1. **Overall Assessment** (2-3 sentences): A brief evaluation of the candidate's profile
2. **Key Strengths** (3-5 bullet points): What stands out positively
3. **Technical Expertise** (2-3 sentences): Assessment of their technical skills and depth
4. **Project Quality** (2-3 sentences): If GitHub projects are available, evaluate their quality, relevance, and impact
5. **Growth Potential** (2-3 sentences): Candidate's learning trajectory and potential
6. **Red Flags / Areas for Investigation** (2-3 bullet points): Any concerns or areas to probe in interview
7. **Recommended Interview Focus Areas** (3-4 bullet points): What to emphasize in the interview
8. **Hiring Recommendation** (1-2 sentences): Strong hire / Hire / Maybe / Pass and why

Format your response in clean markdown with proper headings and bullet points.`;

    try {
      const geminiResponse = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${window.ENV?.GEMINI_API_KEY || ''}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{
              parts: [{ text: aiPrompt }]
            }]
          })
        }
      );

      if (!geminiResponse.ok) {
        throw new Error('Failed to get AI insights');
      }

      const geminiData = await geminiResponse.json();
      aiInsights = geminiData.candidates?.[0]?.content?.parts?.[0]?.text || 'No insights generated';
    } catch (aiError) {
      console.error('AI insights error:', aiError);
      aiInsights = `**Unable to generate AI insights.** Please check if Gemini API key is configured.

However, here's what we know about ${candidate.name}:

**Profile Summary:**
- Match Score: ${candidate.score}/100
- Experience: ${candidate.exp}
- Projects: ${candidate.projects}
- Skills: ${candidate.skills.join(', ')}

**GitHub:** ${githubUsername || 'Not provided'}
${githubData ? `- ${githubData.analysis?.total_repos || 0} public repositories
- ${githubData.analysis?.total_stars || 0} stars received
- ${githubData.analysis?.followers || 0} followers` : ''}`;
    }

    // Convert markdown to HTML (simple conversion)
    const formatMarkdown = (text) => {
      return text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/^### (.+)$/gm, '<h5 style="color: #1e293b; margin-top: 1.5rem; margin-bottom: 0.5rem;">$1</h5>')
        .replace(/^## (.+)$/gm, '<h4 style="color: #1e293b; margin-top: 1.5rem; margin-bottom: 0.5rem;">$1</h4>')
        .replace(/^# (.+)$/gm, '<h3 style="color: #1e293b; margin-top: 1rem; margin-bottom: 0.5rem;">$1</h3>')
        .replace(/^- (.+)$/gm, '<li style="margin-left: 1.5rem; color: #475569;">$1</li>')
        .replace(/\n\n/g, '</p><p style="color: #475569; line-height: 1.6; margin: 0.5rem 0;">')
        .replace(/\n/g, '<br>');
    };

    const formattedInsights = formatMarkdown(aiInsights);

    // Build GitHub stats section if data available
    let githubStatsHTML = '';
    if (githubData && githubData.analysis) {
      githubStatsHTML = `
        <div class="modal-section" style="background: linear-gradient(135deg, #f8fafc, #f1f5f9); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;">
          <h4 style="margin-bottom: 1rem;">📊 GitHub Statistics</h4>
          <div class="github-analysis-summary">
            <div class="analysis-stat">
              <span class="stat-label">Public Repos</span>
              <span class="stat-value">${githubData.analysis.total_repos || 0}</span>
            </div>
            <div class="analysis-stat">
              <span class="stat-label">Total Stars</span>
              <span class="stat-value">${githubData.analysis.total_stars || 0}</span>
            </div>
            <div class="analysis-stat">
              <span class="stat-label">Total Forks</span>
              <span class="stat-value">${githubData.analysis.total_forks || 0}</span>
            </div>
            <div class="analysis-stat">
              <span class="stat-label">Followers</span>
              <span class="stat-value">${githubData.analysis.followers || 0}</span>
            </div>
          </div>
        </div>
      `;
    }

    // Build top projects section if available
    let projectsHTML = '';
    if (githubData && githubData.top_projects && githubData.top_projects.length > 0) {
      const projectCards = githubData.top_projects.map((project, idx) => `
        <div class="github-project-card">
          <div class="project-header">
            <h5>${idx + 1}. ${project.name}</h5>
            <div class="project-stats">
              <span>⭐ ${project.stars}</span>
              <span>🔀 ${project.forks}</span>
            </div>
          </div>
          <p class="project-description">${project.description || 'No description'}</p>
          <div class="project-meta">
            <span class="project-language">📝 ${project.language || 'N/A'}</span>
            ${project.topics && project.topics.length > 0 
              ? `<div class="project-topics">${project.topics.slice(0, 3).map(t => `<span class="topic-tag">${t}</span>`).join('')}</div>` 
              : ''}
          </div>
          <a href="${project.url}" target="_blank" class="project-link">View on GitHub →</a>
        </div>
      `).join('');

      projectsHTML = `
        <div class="modal-section">
          <h4>🚀 Top GitHub Projects</h4>
          <div class="github-projects-list">
            ${projectCards}
          </div>
        </div>
      `;
    }

    // Update modal with AI insights and data
    modal.innerHTML = `
      <div class="modal-content" style="max-width: 1000px;">
        <div class="modal-header">
          <h3>🤖 AI-Powered Analysis: ${candidate.name}</h3>
          <button class="close-modal-btn">&times;</button>
        </div>

        <div class="modal-body">
          ${githubStatsHTML}

          <div class="modal-section" style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
              <span style="font-size: 1.5rem;">🤖</span>
              <h4 style="margin: 0;">Gemini AI Insights</h4>
            </div>
            <div class="ai-insights-content">
              <p style="color: #475569; line-height: 1.6; margin: 0.5rem 0;">${formattedInsights}</p>
            </div>
          </div>

          ${projectsHTML}
        </div>
      </div>
    `;

    modal.classList.add('active');

  } catch (error) {
    console.error('Error analyzing profile:', error);
    
    // Show error in modal
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>🔍 Analysis Error</h3>
          <button class="close-modal-btn">&times;</button>
        </div>
        <div class="modal-body" style="text-align: center; padding: 2rem;">
          <p style="color: #ef4444; font-size: 1.1rem; margin-bottom: 1rem;">❌ Failed to analyze profile</p>
          <p style="color: #64748b;">${error.message}</p>
          <p style="color: #64748b; font-size: 0.9rem; margin-top: 1rem;">
            Make sure Gemini API key is configured in window.ENV.GEMINI_API_KEY
          </p>
          <button onclick="document.getElementById('githubAnalysisModal').classList.remove('active')" 
                  style="margin-top: 1rem; padding: 0.5rem 1.5rem; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer;">
            Close
          </button>
        </div>
      </div>
    `;
  }

  // Close modal handlers
  const closeBtn = modal.querySelector('.close-modal-btn');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      modal.classList.remove('active');
    });
  }

  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.classList.remove('active');
    }
  });

  // Escape key to close
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      modal.classList.remove('active');
    }
  });
}

// -----------------------------
// ADD QUESTION GENERATION SECTIONS
// -----------------------------
function addQuestionGenerationSections(candidates) {
  // Get full candidate data from mockCandidates
  const allCandidates = [
    {
      name: "Ananya Sharma",
      score: 96,
      cgpa: 9.2,
      exp: "3 yrs",
      note: "Strong React + Node expertise",
      email: "ananya.sharma@email.com",
      phone: "+91 98765 43210",
      location: "Mumbai, India",
      skills: ["React", "Node.js", "TypeScript", "MongoDB", "GraphQL", "AWS"],
      education: "B.Tech in Computer Science",
      university: "IIT Bombay",
      projects: 12,
      github: "github.com/ananya-dev",
      linkedin: "linkedin.com/in/ananya-sharma"
    },
    {
      name: "Rohit Mehta",
      score: 92,
      cgpa: 8.8,
      exp: "2 yrs",
      note: "Excellent problem-solving and team skills",
      email: "rohit.mehta@email.com",
      phone: "+91 98765 43211",
      location: "Bangalore, India",
      skills: ["Python", "Django", "PostgreSQL", "Docker", "Redis", "CI/CD"],
      education: "B.Tech in Software Engineering",
      university: "BITS Pilani",
      projects: 9,
      github: "github.com/rohit-codes",
      linkedin: "linkedin.com/in/rohit-mehta"
    },
    {
      name: "Isha Verma",
      score: 88,
      cgpa: 9.0,
      exp: "1 yr",
      note: "Proficient in TypeScript and system design",
      email: "isha.verma@email.com",
      phone: "+91 98765 43212",
      location: "Delhi, India",
      skills: ["TypeScript", "Angular", "NestJS", "MySQL", "Microservices"],
      education: "B.Tech in Information Technology",
      university: "DTU Delhi",
      projects: 7,
      github: "github.com/isha-dev",
      linkedin: "linkedin.com/in/isha-verma"
    }
  ];

  candidates.forEach((selectedCandidate) => {
    // Find the full candidate data
    const fullCandidate = allCandidates.find(c => c.email === selectedCandidate.email);
    if (!fullCandidate) return;

    // Find the index in the displayed cards
    const allCards = document.querySelectorAll('.result-card');
    let targetIndex = -1;
    allCards.forEach((card, idx) => {
      const checkbox = card.querySelector('.candidate-checkbox');
      if (checkbox && checkbox.getAttribute('data-email') === selectedCandidate.email) {
        targetIndex = idx;
      }
    });

    if (targetIndex === -1) return;

    const candidateCard = allCards[targetIndex];

    // Check if section already exists
    if (candidateCard.querySelector('.question-gen-section')) return;

    const questionSection = document.createElement('div');
    questionSection.className = 'question-gen-section';
    questionSection.innerHTML = `
      <div class="question-gen-header">
        <span style="font-size: 1.5rem;">🎯</span>
        <h4>Interview Questions Generator</h4>
      </div>
      <p class="question-gen-description">
        Generate AI-powered interview questions tailored for ${fullCandidate.name}
      </p>
      <button class="generate-questions-btn" data-index="${targetIndex}" data-name="${fullCandidate.name}">
        ✨ Generate Questions
      </button>
      <div class="generated-questions" id="generated-questions-${targetIndex}" style="display: none;"></div>
    `;

    candidateCard.appendChild(questionSection);

    // Attach event listener
    const generateBtn = questionSection.querySelector('.generate-questions-btn');
    generateBtn.addEventListener('click', () => generateQuestionsForCandidate(targetIndex, fullCandidate));
  });
}

// -----------------------------
// GENERATE QUESTIONS FOR CANDIDATE
// -----------------------------
async function generateQuestionsForCandidate(index, candidate) {
  const btn = document.querySelector(`.generate-questions-btn[data-index="${index}"]`);
  const questionsContainer = document.getElementById(`generated-questions-${index}`);

  const originalHTML = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<span class="question-loading-spinner"></span> <span>Generating AI Questions...</span>';

  try {
    // First, fetch GitHub data if available
    let githubProjectsInfo = '';
    if (candidate.github) {
      try {
        btn.innerHTML = '<span class="question-loading-spinner"></span> <span>Analyzing GitHub...</span>';
        const githubData = await HireSightAPI.analyzeGitHub(candidate.github);
        
        if (githubData.success && githubData.top_projects && githubData.top_projects.length > 0) {
          githubProjectsInfo = '\n\nTOP 3 GITHUB PROJECTS\n---------------------\n';
          githubData.top_projects.forEach((project, idx) => {
            githubProjectsInfo += `\n${idx + 1}. ${project.name}\n`;
            githubProjectsInfo += `   Description: ${project.description}\n`;
            githubProjectsInfo += `   Languages: ${Object.keys(project.languages || {}).join(', ') || project.language || 'N/A'}\n`;
            githubProjectsInfo += `   Stars: ${project.stars}, Forks: ${project.forks}\n`;
            if (project.topics && project.topics.length > 0) {
              githubProjectsInfo += `   Topics: ${project.topics.join(', ')}\n`;
            }
            githubProjectsInfo += `   URL: ${project.url}\n`;
          });
        }
      } catch (githubError) {
        console.warn('Could not fetch GitHub data:', githubError);
        // Continue without GitHub data
      }
    }

    btn.innerHTML = '<span class="question-loading-spinner"></span> <span>Generating AI Questions...</span>';

    // Build comprehensive candidate profile text from their data
    const candidateProfile = `
CANDIDATE PROFILE
==================
Name: ${candidate.name}
Email: ${candidate.email || 'Not provided'}
Phone: ${candidate.phone || 'Not provided'}
Location: ${candidate.location || 'Not provided'}

EDUCATION
---------
Degree: ${candidate.education || 'Not specified'}
University: ${candidate.university || 'Not specified'}
CGPA: ${candidate.cgpa > 0 ? candidate.cgpa + '/10' : 'Not provided'}

PROFESSIONAL EXPERIENCE
-----------------------
Years of Experience: ${candidate.exp}
Projects Completed: ${candidate.projects}

TECHNICAL SKILLS
----------------
${candidate.skills && candidate.skills.length > 0 ? candidate.skills.join(', ') : 'Not specified'}

PROFESSIONAL LINKS
------------------
GitHub: ${candidate.github ? 'github.com/' + candidate.github : 'Not provided'}
LinkedIn: ${candidate.linkedin ? 'linkedin.com/in/' + candidate.linkedin : 'Not provided'}

SUMMARY
-------
${candidate.note || candidate.summary || 'No summary provided'}
${githubProjectsInfo}
    `.trim();

    // Call the real API
    const response = await HireSightAPI.generateInterviewQuestions(
      candidate.name,
      candidateProfile
    );

    // Extract questions from API response
    let questions = [];

    if (response.success && response.interview_questions) {
      // Parse AI-generated questions from text
      const questionsText = response.interview_questions;

      // Split by numbered patterns (1., 2., etc.) or question marks
      const questionLines = questionsText.split(/\n+/)
        .map(line => line.trim())
        .filter(line => {
          // Keep lines that look like questions or have content
          return line.length > 10 && (
            line.includes('?') ||
            /^\d+\./.test(line) ||
            /^-/.test(line) ||
            /^Q\d+/i.test(line)
          );
        })
        .map(line => {
          // Clean up numbering and formatting
          return line
            .replace(/^\d+\.\s*/, '')
            .replace(/^-\s*/, '')
            .replace(/^Q\d+[:\s]*/i, '')
            .trim();
        })
        .filter(line => line.length > 15); // Filter out very short lines

      if (questionLines.length > 0) {
        questions = questionLines;
      } else {
        // Try alternate parsing - split by question marks
        questions = questionsText
          .split('?')
          .map(q => q.trim() + '?')
          .filter(q => q.length > 20 && q.length < 300);
      }
    }

    // Fallback to mock questions only if parsing completely failed
    if (questions.length === 0) {
      questions = [
        `Tell me about a ${candidate.skills?.[0] || 'technical'} project you've worked on recently.`,
        `How do you approach problem-solving when faced with a difficult bug in ${candidate.skills?.[1] || 'your code'}?`,
        `Describe your experience with the technologies mentioned in your profile, particularly ${candidate.skills?.[2] || 'modern frameworks'}.`,
        `With ${candidate.exp} of experience, what has been your most challenging project?`,
        `How do you stay updated with the latest trends in ${candidate.skills?.[0] || 'technology'}?`,
        `Tell me about a time when you had to work with a difficult team member.`,
        `What's your approach to code reviews and ensuring quality in ${candidate.skills?.[1] || 'your work'}?`,
        `How do you prioritize tasks when working on multiple projects simultaneously?`
      ];
    }

    // Store questions for later use (copy/download)
    questionsContainer.dataset.questions = JSON.stringify(questions);
    questionsContainer.dataset.candidateName = candidate.name;

    // Display questions
    questionsContainer.innerHTML = `
      <h5>📝 Generated Questions:</h5>
      <div class="question-list">
        ${questions.map((q, i) => `
          <div class="question-card">
            <span class="question-number">Q${i + 1}:</span>
            <span class="question-text">${q}</span>
          </div>
        `).join('')}
      </div>
      <div class="questions-actions">
        <button class="copy-questions-btn" onclick="copyQuestions(${index}, event)">
          📋 Copy Questions
        </button>
        <button class="download-questions-btn" onclick="downloadQuestions(${index}, '${candidate.name}', event)">
          💾 Download PDF
        </button>
      </div>
    `;

    questionsContainer.style.display = 'block';
    btn.innerHTML = '✓ Questions Generated';
    btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
    btn.disabled = true;

    // Smooth scroll to questions
    questionsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  } catch (error) {
    console.error('Error generating questions:', error);

    // Fallback to mock questions on error
    const mockQuestions = [
      `Tell me about a ${candidate.skills?.[0] || 'technical'} project you've worked on recently.`,
      `How do you approach problem-solving when faced with a difficult bug in ${candidate.skills?.[1] || 'your code'}?`,
      `Describe your experience with the technologies mentioned in your profile, particularly ${candidate.skills?.[2] || 'modern frameworks'}.`,
      `With ${candidate.exp} of experience, what has been your most challenging project?`,
      `How do you stay updated with the latest trends in ${candidate.skills?.[0] || 'technology'}?`,
      `Tell me about a time when you had to work with a difficult team member.`,
      `What's your approach to code reviews and ensuring quality in ${candidate.skills?.[1] || 'your work'}?`,
      `How do you prioritize tasks when working on multiple projects simultaneously?`
    ];

    questionsContainer.dataset.questions = JSON.stringify(mockQuestions);
    questionsContainer.dataset.candidateName = candidate.name;

    questionsContainer.innerHTML = `
      <h5>📝 Generated Questions:</h5>
      <div class="question-list">
        ${mockQuestions.map((q, i) => `
          <div class="question-card">
            <span class="question-number">Q${i + 1}:</span>
            <span class="question-text">${q}</span>
          </div>
        `).join('')}
      </div>
      <div class="questions-actions">
        <button class="copy-questions-btn" onclick="copyQuestions(${index}, event)">
          📋 Copy Questions
        </button>
        <button class="download-questions-btn" onclick="downloadQuestions(${index}, '${candidate.name}', event)">
          💾 Download PDF
        </button>
      </div>
    `;

    questionsContainer.style.display = 'block';
    btn.innerHTML = '✓ Questions Generated';
    btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
    btn.disabled = true;

    console.warn('Using fallback questions due to API error');
  }
}

// -----------------------------
// COPY QUESTIONS TO CLIPBOARD
// -----------------------------
function copyQuestions(index, evt) {
  const questionsContainer = document.getElementById(`generated-questions-${index}`);
  const questions = Array.from(questionsContainer.querySelectorAll('.question-card'))
    .map(card => card.textContent.trim())
    .join('\n\n');

  navigator.clipboard.writeText(questions).then(() => {
    const btn = evt ? evt.target : document.querySelector(`.copy-questions-btn[data-index="${index}"]`);
    if (btn) {
      const originalText = btn.innerHTML;
      btn.innerHTML = '✓ Copied!';
      setTimeout(() => {
        btn.innerHTML = originalText;
      }, 2000);
    }
  }).catch(err => {
    console.error('Failed to copy:', err);
    alert('❌ Failed to copy questions');
  });
}

// -----------------------------
// DOWNLOAD QUESTIONS AS PDF
// -----------------------------
function downloadQuestions(index, candidateName, evt) {
  const questionsContainer = document.getElementById(`generated-questions-${index}`);
  const questionsData = questionsContainer.dataset.questions;

  let questions = [];
  try {
    questions = JSON.parse(questionsData);
  } catch (error) {
    // Fallback: extract from DOM
    questions = Array.from(questionsContainer.querySelectorAll('.question-text'))
      .map(el => el.textContent.trim());
  }

  // Get button reference
  const btn = evt ? evt.target : document.querySelector(`.download-questions-btn[data-index="${index}"]`);

  try {
    // Create PDF using jsPDF
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Set document properties
    doc.setProperties({
      title: `Interview Questions for ${candidateName}`,
      subject: 'AI-Generated Interview Questions',
      author: 'HireSight',
      keywords: 'interview, questions, hiring',
      creator: 'HireSight Platform'
    });

    // Add header
    doc.setFontSize(20);
    doc.setTextColor(37, 99, 235); // Blue color
    doc.text('Interview Questions', 20, 20);

    doc.setFontSize(14);
    doc.setTextColor(71, 85, 105); // Gray color
    doc.text(`Candidate: ${candidateName}`, 20, 30);

    // Add date
    doc.setFontSize(10);
    doc.setTextColor(100, 116, 139);
    const today = new Date().toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
    doc.text(`Generated on: ${today}`, 20, 38);

    // Add a line separator
    doc.setDrawColor(226, 232, 240);
    doc.setLineWidth(0.5);
    doc.line(20, 42, 190, 42);

    // Add questions
    doc.setFontSize(12);
    doc.setTextColor(30, 41, 59); // Dark gray

    let yPosition = 52;
    const pageHeight = doc.internal.pageSize.height;
    const marginBottom = 20;
    const lineHeight = 7;

    questions.forEach((question, i) => {
      // Check if we need a new page
      if (yPosition > pageHeight - marginBottom) {
        doc.addPage();
        yPosition = 20;
      }

      // Question number
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(37, 99, 235);
      doc.text(`Q${i + 1}:`, 20, yPosition);

      // Question text - with word wrap
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(51, 65, 85);
      const questionLines = doc.splitTextToSize(question, 160);
      doc.text(questionLines, 33, yPosition);

      yPosition += (questionLines.length * lineHeight) + 5;
    });

    // Add footer on last page
    const totalPages = doc.internal.pages.length - 1;
    for (let i = 1; i <= totalPages; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(148, 163, 184);
      doc.text(
        `Page ${i} of ${totalPages} | Generated by HireSight`,
        doc.internal.pageSize.width / 2,
        doc.internal.pageSize.height - 10,
        { align: 'center' }
      );
    }

    // Download the PDF
    const filename = `${candidateName.replace(/\s+/g, '_')}_Interview_Questions.pdf`;
    doc.save(filename);

    // Show success message
    if (btn) {
      const originalText = btn.innerHTML;
      btn.innerHTML = '✓ Downloaded!';
      setTimeout(() => {
        btn.innerHTML = originalText;
      }, 2000);
    }

  } catch (error) {
    console.error('PDF generation error:', error);

    // Fallback to text file if PDF fails
    const questionsText = questions.map((q, i) => `Q${i + 1}: ${q}`).join('\n\n');
    const blob = new Blob(
      [`Interview Questions for ${candidateName}\n\n${questionsText}`],
      { type: 'text/plain' }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${candidateName.replace(/\s+/g, '_')}_Interview_Questions.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    if (btn) {
      const originalText = btn.innerHTML;
      btn.innerHTML = '✓ Downloaded (TXT)!';
      setTimeout(() => {
        btn.innerHTML = originalText;
      }, 2000);
    }
  }
}

// -----------------------------
// LOGOUT BUTTON (Supabase)
// -----------------------------
logoutBtn.addEventListener("click", async () => {
  if (!window.supabase || typeof signOut !== 'function') {
    // Fallback if supabase isn't loaded for any reason
    console.warn('Supabase not initialized; redirecting to login as fallback.');
    window.location.href = '/COMPANY_LOGIN/index.html';
    return;
  }

  const originalText = logoutBtn.textContent;
  logoutBtn.disabled = true;
  logoutBtn.textContent = 'Logging out…';

  try {
    const ok = await signOut();
    if (!ok) throw new Error('Sign out failed');
    // Redirect to login after successful sign out
    window.location.href = '/COMPANY_LOGIN/index.html';
  } catch (e) {
    console.error('Logout error:', e);
    alert('Failed to log out. Please try again.');
    logoutBtn.disabled = false;
    logoutBtn.textContent = originalText;
  }
});
