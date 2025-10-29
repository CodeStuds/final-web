// ===============================
// 🔐 CONFIGURATION
// ===============================

// Note: API configuration is now loaded from ../api-config.js
// Make sure to include <script src="../api-config.js"></script> before this script in HTML

// Fallback configuration if api-config.js is not loaded
if (typeof HireSightAPI === 'undefined') {
  console.warn('API config not loaded, using fallback configuration');
  window.HIRESIGHT_API_CONFIG = {
    baseURL: window.ENV?.API_BASE_URL || "http://localhost:5000/api",
    apiKey: window.ENV?.API_KEY || ""
  };
}


document.addEventListener('DOMContentLoaded', () => {
  // --- Experience slider show/hide + display ---
  const yesRadio = document.getElementById('experience-yes');
  const radios = document.querySelectorAll('input[name="experience"]');
  const sliderContainer = document.getElementById('experienceSliderContainer');
  const slider = document.getElementById('experienceRange');
  const output = document.getElementById('experienceValue');

  function updateVisibility() {
    if (yesRadio && yesRadio.checked) sliderContainer.style.display = 'block';
    else sliderContainer.style.display = 'none';
  }
  function updateOutput() {
    if (!slider || !output) return;
    const val = Math.round(Number(slider.value));
    output.textContent = `${val} ${val === 1 ? 'yr' : 'yrs'}`;
  }

  radios.forEach(r => r.addEventListener('change', updateVisibility));
  if (slider) slider.addEventListener('input', updateOutput);
  updateVisibility();
  updateOutput();

  // --- CGPA slider show/hide + display ---
  const cgpaYes = document.getElementById('cgpa-yes');
  const cgpaRadios = document.querySelectorAll('input[name="cgpa"]');
  const cgpaContainer = document.getElementById('cgpaSliderContainer');
  const cgpaSlider = document.getElementById('cgpaRange');
  const cgpaOutput = document.getElementById('cgpaValue');

  function updateCgpaVisibility() {
    if (cgpaYes && cgpaYes.checked) cgpaContainer.style.display = 'block';
    else cgpaContainer.style.display = 'none';
  }
  function updateCgpaOutput() {
    if (!cgpaSlider || !cgpaOutput) return;
    const val = Number(cgpaSlider.value);
    cgpaOutput.textContent = val.toFixed(2);
  }

  cgpaRadios.forEach(r => r.addEventListener('change', updateCgpaVisibility));
  if (cgpaSlider) cgpaSlider.addEventListener('input', updateCgpaOutput);
  updateCgpaVisibility();
  updateCgpaOutput();

  // --- File validation + submit + mock fallback rendering ---
  const submitBtn = document.getElementById('submitBtn');
  const fileInput = document.getElementById('uploadFile');
  const resultsEl = document.getElementById('results');

  function isValidFile(file) {
    if (!file) return true;
    const allowed = ['.zip', '.pdf', '.docx', '.doc'];
    const name = file.name.toLowerCase();
    return allowed.some(ext => name.endsWith(ext));
  }

  async function fetchRank(formData) {
    try {
      // Use the new API service if available
      if (typeof HireSightAPI !== 'undefined' && HireSightAPI.rankCandidates) {
        const json = await HireSightAPI.rankCandidates(formData);
        if (!json.success || !Array.isArray(json.results) || json.results.length === 0) {
          throw new Error(json.error || 'No results returned');
        }
        return { data: json.results, source: 'backend', count: json.count };
      } else {
        // Fallback to direct fetch
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 15000);
        try {
          const res = await fetch(`${HIRESIGHT_API_CONFIG.baseURL}/rank`, {
            method: 'POST',
            body: formData,
            signal: controller.signal,
            headers: HIRESIGHT_API_CONFIG.apiKey ? { 'X-API-Key': HIRESIGHT_API_CONFIG.apiKey } : {}
          });
          clearTimeout(timeout);
          if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            throw new Error(errorData.error || 'Backend error');
          }
          const json = await res.json();
          if (!json || !Array.isArray(json.results) || json.results.length === 0) {
            throw new Error('No results returned');
          }
          return { data: json.results, source: 'backend', count: json.count };
        } catch (err) {
          clearTimeout(timeout);
          throw err;
        }
      }
    } catch (err) {
      console.error('Fetch rank error:', err);
      throw err;
    }
  }

  function mockDataset() {
    return [
      { name: 'Asha Verma', score: 92, skills: ['React','TypeScript','Node.js'], note: 'Strong portfolio' },
      { name: 'Rahul Singh', score: 88, skills: ['Node.js','Databases'], note: 'Great backend fit' },
      { name: 'Maya Patel', score: 85, skills: ['React','Design'], note: 'UI-focused' },
      { name: 'Samir Khan', score: 80, skills: ['Fullstack','DevOps'], note: 'Broad experience' },
      { name: 'Priya Nair', score: 76, skills: ['TypeScript','Testing'], note: 'Reliable tests' }
    ];
  }

  function renderResults(items, meta = {}) {
    if (!resultsEl) return;
    resultsEl.innerHTML = '';
    const header = document.createElement('div');
    header.className = 'results-header';
    header.innerHTML = `<strong>Candidate Ranking (${items.length} candidates)</strong>
                        <span class="meta">${meta.source ? 'Source: ' + meta.source : ''} ${meta.fallback ? '⚠️ Fallback data used' : '✓ Live results'}</span>`;
    resultsEl.appendChild(header);

    const list = document.createElement('div');
    list.className = 'results-list';
    items.forEach((it, idx) => {
      const card = document.createElement('div');
      card.className = 'result-card';
      const skillsList = (it.skills || []).slice(0, 4).join(', ');
      const hasMoreSkills = (it.skills || []).length > 4;

      card.innerHTML = `
        <div class="rank">#${idx + 1}</div>
        <div class="info">
          <div class="name">${it.name || it.candidate || 'Candidate ' + (idx+1)}</div>
          <div class="meta-line">
            Score: <strong>${it.score ?? it.matchScore ?? '—'}</strong>
            ${skillsList ? '• ' + skillsList : ''}
            ${hasMoreSkills ? ` (+${(it.skills || []).length - 4} more)` : ''}
          </div>
          <div class="note">${it.note || it.summary || ''}</div>
        </div>
        <div class="actions" style="margin-top: 0.5rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
          <button class="action-btn github-btn" data-candidate="${it.name || 'Candidate ' + (idx+1)}" style="font-size: 0.85rem; padding: 0.4rem 0.8rem;">
            Analyze GitHub
          </button>
          <button class="action-btn interview-btn" data-candidate="${it.name || 'Candidate ' + (idx+1)}" style="font-size: 0.85rem; padding: 0.4rem 0.8rem;">
            Generate Questions
          </button>
        </div>
      `;
      list.appendChild(card);
    });
    resultsEl.appendChild(list);

    // Add event listeners for action buttons
    attachActionListeners();
  }

  function attachActionListeners() {
    // GitHub analysis buttons
    document.querySelectorAll('.github-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const candidateName = e.target.getAttribute('data-candidate');
        const username = prompt(`Enter GitHub username for ${candidateName}:`);
        if (username) {
          await analyzeGitHubProfile(username, candidateName);
        }
      });
    });

    // Interview question buttons
    document.querySelectorAll('.interview-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const candidateName = e.target.getAttribute('data-candidate');
        await generateInterviewQuestions(candidateName);
      });
    });
  }

  if (submitBtn) {
    submitBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      const file = fileInput?.files?.[0];
      if (!isValidFile(file)) {
        alert('Invalid file type. Use .zip, .pdf, .docx or .doc');
        return;
      }

      const roleInput = document.querySelector('.form-grid input[type="text"]')?.value || '';
      const skillsInput = document.querySelectorAll('.form-grid input[type="text"]')[1]?.value || '';
      
      // Get experience and CGPA values
      const expYes = document.getElementById('experience-yes');
      const expSlider = document.getElementById('experienceRange');
      const experienceValue = (expYes && expYes.checked && expSlider) ? expSlider.value : 'Not important';
      
      const cgpaYes = document.getElementById('cgpa-yes');
      const cgpaSlider = document.getElementById('cgpaRange');
      const cgpaValue = (cgpaYes && cgpaYes.checked && cgpaSlider) ? cgpaSlider.value : 'Not important';
      
      const additionalReqs = document.querySelector('textarea')?.value || '';
      
      const formData = new FormData();
      formData.append('role', roleInput);
      formData.append('skills', skillsInput);
      formData.append('experience', experienceValue);
      formData.append('cgpa', cgpaValue);
      formData.append('additional', additionalReqs);
      if (file) formData.append('file', file);

      // Show loading state
      submitBtn.disabled = true;
      submitBtn.textContent = 'Processing...';

      try {
        const res = await fetchRank(formData);
        renderResults(res.data, { source: 'backend', count: res.count });

        // Show success message
        showNotification('✓ Candidates ranked successfully!', 'success');
      } catch (err) {
        console.warn('Backend unavailable, using fallback:', err);
        showNotification(`⚠️ API unavailable: ${err.message}. Showing sample data.`, 'warning');
        const fallback = mockDataset();
        renderResults(fallback, { source: 'mock', fallback: true });
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Job Posting';
      }
    });
  }
});

// ===============================
// 🔔 NOTIFICATION HELPER
// ===============================
function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    background: ${type === 'success' ? '#10b981' : type === 'warning' ? '#f59e0b' : type === 'error' ? '#ef4444' : '#3b82f6'};
    color: white;
    font-weight: 500;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 9999;
    animation: slideIn 0.3s ease-out;
    max-width: 400px;
  `;
  notification.textContent = message;

  document.body.appendChild(notification);

  // Remove after 5 seconds
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => notification.remove(), 300);
  }, 5000);
}

// ===============================
// 🐙 GITHUB ANALYSIS
// ===============================
async function analyzeGitHubProfile(username, candidateName) {
  try {
    showNotification(`Analyzing GitHub profile for ${username}...`, 'info');

    // Use API service
    if (typeof HireSightAPI !== 'undefined' && HireSightAPI.analyzeGitHub) {
      const result = await HireSightAPI.analyzeGitHub(username);

      if (result.success) {
        // Display results in a modal or new section
        displayGitHubAnalysis(candidateName, username, result.analysis, result.match_score);
        showNotification(`✓ GitHub analysis complete for ${username}`, 'success');
      } else {
        throw new Error(result.error || 'Analysis failed');
      }
    } else {
      throw new Error('API service not available');
    }
  } catch (error) {
    console.error('GitHub analysis error:', error);
    showNotification(`✗ Failed to analyze GitHub profile: ${error.message}`, 'error');
  }
}

function displayGitHubAnalysis(candidateName, username, analysis, matchScore) {
  // Create modal for displaying results
  const modal = document.createElement('div');
  modal.className = 'analysis-modal';
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    padding: 20px;
  `;

  const modalContent = document.createElement('div');
  modalContent.style.cssText = `
    background: white;
    padding: 2rem;
    border-radius: 12px;
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
  `;

  modalContent.innerHTML = `
    <button class="close-modal" style="position: absolute; top: 1rem; right: 1rem; background: #ef4444; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">✕ Close</button>
    <h2 style="margin-bottom: 1rem;">GitHub Analysis: ${candidateName}</h2>
    <p style="margin-bottom: 1rem;"><strong>Username:</strong> <a href="https://github.com/${username}" target="_blank" style="color: #3b82f6;">${username}</a></p>
    ${matchScore !== null && matchScore !== undefined ? `<p style="margin-bottom: 1rem;"><strong>Match Score:</strong> ${matchScore}/100</p>` : ''}
    <div style="margin-top: 1.5rem;">
      <h3 style="margin-bottom: 0.5rem;">Analysis Results:</h3>
      <pre style="background: #f3f4f6; padding: 1rem; border-radius: 6px; overflow-x: auto; white-space: pre-wrap;">${JSON.stringify(analysis, null, 2)}</pre>
    </div>
  `;

  modal.appendChild(modalContent);
  document.body.appendChild(modal);

  // Close modal on click
  modal.querySelector('.close-modal').addEventListener('click', () => modal.remove());
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.remove();
  });
}

// ===============================
// 💼 INTERVIEW QUESTION GENERATION
// ===============================
async function generateInterviewQuestions(candidateName) {
  try {
    // Prompt for candidate profile or GitHub username
    const profileSource = confirm('Do you want to use GitHub profile? Click OK for GitHub, Cancel to enter profile text manually.');

    let candidateProfile = '';

    if (profileSource) {
      // Get from GitHub
      const username = prompt(`Enter GitHub username for ${candidateName}:`);
      if (!username) return;

      showNotification(`Fetching GitHub profile for ${username}...`, 'info');

      if (typeof HireSightAPI !== 'undefined' && HireSightAPI.analyzeGitHub) {
        const result = await HireSightAPI.analyzeGitHub(username);
        if (result.success) {
          candidateProfile = JSON.stringify(result.analysis);
        } else {
          throw new Error('Failed to fetch GitHub profile');
        }
      }
    } else {
      // Manual entry
      candidateProfile = prompt('Enter candidate profile (skills, experience, projects):');
      if (!candidateProfile) return;
    }

    showNotification(`Generating interview questions for ${candidateName}...`, 'info');

    // Generate questions
    if (typeof HireSightAPI !== 'undefined' && HireSightAPI.generateInterviewQuestions) {
      const result = await HireSightAPI.generateInterviewQuestions(candidateName, candidateProfile);

      if (result.success) {
        displayInterviewQuestions(candidateName, result.interview_questions);
        showNotification(`✓ Interview questions generated for ${candidateName}`, 'success');
      } else {
        throw new Error(result.error || 'Question generation failed');
      }
    } else {
      throw new Error('API service not available');
    }
  } catch (error) {
    console.error('Interview generation error:', error);
    showNotification(`✗ Failed to generate questions: ${error.message}`, 'error');
  }
}

function displayInterviewQuestions(candidateName, questions) {
  // Create modal for displaying questions
  const modal = document.createElement('div');
  modal.className = 'questions-modal';
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    padding: 20px;
  `;

  const modalContent = document.createElement('div');
  modalContent.style.cssText = `
    background: white;
    padding: 2rem;
    border-radius: 12px;
    max-width: 900px;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
  `;

  modalContent.innerHTML = `
    <button class="close-modal" style="position: absolute; top: 1rem; right: 1rem; background: #ef4444; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">✕ Close</button>
    <h2 style="margin-bottom: 1rem;">Interview Questions: ${candidateName}</h2>
    <div style="margin-top: 1.5rem; line-height: 1.8;">
      <pre style="white-space: pre-wrap; font-family: inherit;">${questions}</pre>
    </div>
    <button class="copy-btn" style="margin-top: 1.5rem; background: #3b82f6; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; cursor: pointer;">Copy to Clipboard</button>
  `;

  modal.appendChild(modalContent);
  document.body.appendChild(modal);

  // Close modal
  modal.querySelector('.close-modal').addEventListener('click', () => modal.remove());
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.remove();
  });

  // Copy to clipboard
  modal.querySelector('.copy-btn').addEventListener('click', () => {
    navigator.clipboard.writeText(questions).then(() => {
      showNotification('✓ Copied to clipboard!', 'success');
    }).catch(err => {
      console.error('Copy failed:', err);
      showNotification('✗ Failed to copy', 'error');
    });
  });
}

// ===============================
// 🎯 DOM ELEMENTS
// ===============================
const uploadSection = document.getElementById("upload-section");
const loadingSection = document.getElementById("loading-section");
const resultsSection = document.getElementById("results-section");
const calculateBtn = document.getElementById("calculate-btn");
const dropArea = document.getElementById("drop-area");
const resumeUpload = document.getElementById("resume-upload");


// ===============================
// 📊 UI UPDATE HELPERS
// ===============================
function updateScoreUI(scores) {
  document.getElementById("main-score").textContent = scores.mainScore;
  document.getElementById("keyword-score").textContent = `${scores.keywordScore}/100`;
  document.getElementById("achievement-score").textContent = `${scores.achievementScore}/100`;
  document.getElementById("formatting-score").textContent = `${scores.formattingScore}/100`;
  document.getElementById("length-score").textContent = `${scores.lengthScore}/100`;

  document.getElementById("keyword-bar").style.width = `${scores.keywordScore}%`;
  document.getElementById("achievement-bar").style.width = `${scores.achievementScore}%`;
  document.getElementById("formatting-bar").style.width = `${scores.formattingScore}%`;
  document.getElementById("length-bar").style.width = `${scores.lengthScore}%`;

  let gradeText, gradeColor;
  if (scores.mainScore >= 90) {
    gradeText = "Excellent – Recruiters Will Love This";
    gradeColor = "text-secondary";
  } else if (scores.mainScore >= 80) {
    gradeText = "Great – Minor Improvements Needed";
    gradeColor = "text-secondary";
  } else if (scores.mainScore >= 70) {
    gradeText = "Good – Some Key Fixes Required";
    gradeColor = "text-warning";
  } else {
    gradeText = "Needs Work – Critical Improvements Needed";
    gradeColor = "text-danger";
  }

  const gradeElement = document.getElementById("score-grade");
  gradeElement.textContent = gradeText;
  gradeElement.className = `text-xl font-semibold ${gradeColor} mb-2`;
}


// ===============================
// ⚙️ SCORE GENERATION (API CALL)
// ===============================
async function getResumeScore(file) {
  try {
    let data;

    // Use the new API service if available
    if (typeof HireSightAPI !== 'undefined' && HireSightAPI.analyzeResume) {
      const result = await HireSightAPI.analyzeResume(file);
      if (result.success) {
        data = result;
      } else {
        throw new Error(result.error || 'Analysis failed');
      }
    } else {
      // Fallback to direct fetch
      const formData = new FormData();
      formData.append("resume", file);

      const response = await fetch(`${HIRESIGHT_API_CONFIG.baseURL}/analyze`, {
        method: "POST",
        body: formData,
        headers: HIRESIGHT_API_CONFIG.apiKey ? { 'X-API-Key': HIRESIGHT_API_CONFIG.apiKey } : {}
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API Error: ${response.statusText}`);
      }

      data = await response.json();
    }

    // Expected response structure:
    // {
    //   success: true,
    //   mainScore: 84,
    //   keywordScore: 78,
    //   achievementScore: 88,
    //   formattingScore: 90,
    //   lengthScore: 76
    // }

    updateScoreUI(data);
    showNotification('✓ Resume analyzed successfully!', 'success');

  } catch (error) {
    console.error("❌ Resume analysis failed:", error);
    showNotification(`✗ Resume analysis failed: ${error.message}`, 'error');
    throw error;
  }
}


// ===============================
// 🧮 FALLBACK (MOCK SCORES)
// ===============================
function generateMockScores() {
  const scores = {
    mainScore: Math.floor(Math.random() * 16) + 70,
    keywordScore: Math.floor(Math.random() * 26) + 65,
    achievementScore: Math.floor(Math.random() * 26) + 65,
    formattingScore: Math.floor(Math.random() * 26) + 65,
    lengthScore: Math.floor(Math.random() * 26) + 65,
  };
  updateScoreUI(scores);
}


// ===============================
// 🚀 ZIP SUPPORT HELPERS
// ===============================

// Acceptable resume file extensions inside ZIPs
const SUPPORTED_EXTS = ['.pdf', '.docx', '.doc', '.txt', '.rtf'];

function isZipFile(file) {
  return file && (file.type === 'application/zip' || file.name.toLowerCase().endsWith('.zip'));
}

function extFromName(name) {
  return (name.match(/\.[^/.]+$/) || [''])[0].toLowerCase();
}

function mimeFromExt(ext) {
  switch (ext) {
    case '.pdf': return 'application/pdf';
    case '.docx': return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
    case '.doc': return 'application/msword';
    case '.txt': return 'text/plain';
    case '.rtf': return 'application/rtf';
    default: return 'application/octet-stream';
  }
}

// Lazy-load JSZip (so you don't need to add a <script> tag manually)
function loadJSZip() {
  return new Promise((resolve, reject) => {
    if (window.JSZip) return resolve(window.JSZip);
    const s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
    s.onload = () => resolve(window.JSZip);
    s.onerror = reject;
    document.head.appendChild(s);
  });
}

// Extract first supported file from ZIP and return a File object suitable for upload
async function handleZipFile(zipFile) {
  try {
    const JSZip = await loadJSZip();
    const arrayBuffer = await zipFile.arrayBuffer();
    const zip = await JSZip.loadAsync(arrayBuffer);

    let found = null;
    // Iterate files to find first supported entry
    zip.forEach((relativePath, zipEntry) => {
      if (found) return;
      const name = zipEntry.name;
      const ext = extFromName(name);
      if (!zipEntry.dir && SUPPORTED_EXTS.includes(ext)) {
        found = { name, entry: zipEntry, ext };
      }
    });

    if (!found) {
      alert('No supported resume file found in the ZIP. Supported: pdf, docx, doc, txt, rtf.');
      throw new Error('No supported file in zip');
    }

    const blob = await found.entry.async('blob');
    const mime = mimeFromExt(found.ext);
    const typedBlob = blob.slice(0, blob.size, mime);
    // Create a File so the rest of the pipeline can treat it like a normal upload
    const extractedFile = new File([typedBlob], found.name, { type: mime });
    return extractedFile;

  } catch (err) {
    console.error('Error extracting zip:', err);
    alert('Failed to extract ZIP file.');
    throw err;
  }
}


// ===============================
// 🚀 EVENT HANDLERS (updated to support ZIPs)
// ===============================
calculateBtn.addEventListener("click", async () => {
  let file = resumeUpload.files[0];

  if (!file) {
    alert("Please upload a resume file first.");
    return;
  }

  uploadSection.classList.add("hidden");
  loadingSection.classList.remove("hidden");

  try {
    if (isZipFile(file)) {
      // extract first supported file from zip and use it
      file = await handleZipFile(file);
    }

    // Try API call, fallback to mock if API fails
    try {
      await getResumeScore(file);
    } catch {
      generateMockScores();
    }
  } catch (outerErr) {
    // extraction failed or no supported file - show upload section again
    uploadSection.classList.remove("hidden");
    resultsSection.classList.add("hidden");
    console.error('Processing halted:', outerErr);
  } finally {
    loadingSection.classList.add("hidden");
    resultsSection.classList.remove("hidden");
  }
});


// ===============================
// 🖱️ DRAG & DROP HANDLING
// ===============================
["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
  dropArea.addEventListener(eventName, e => {
    e.preventDefault();
    e.stopPropagation();
  }, false);
});

["dragenter", "dragover"].forEach(eventName => {
  dropArea.addEventListener(eventName, () => {
    dropArea.classList.add("border-primary", "bg-primary/5");
  }, false);
});

["dragleave", "drop"].forEach(eventName => {
  dropArea.addEventListener(eventName, () => {
    dropArea.classList.remove("border-primary", "bg-primary/5");
  }, false);
});

dropArea.addEventListener("drop", e => {
  const dt = e.dataTransfer;
  const files = dt.files;
  if (files.length) {
    resumeUpload.files = files;
    calculateBtn.click();
  }
});

resumeUpload.addEventListener("change", () => {
  if (resumeUpload.files.length) calculateBtn.click();
});
document.getElementById("submitBtn").addEventListener("click", () => {
  alert("✅ Job posting submitted successfully!");
});

