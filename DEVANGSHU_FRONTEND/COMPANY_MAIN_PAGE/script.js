// ===============================
// 🔐 CONFIGURATION
// ===============================

// API Configuration - Uses environment variables when available
// For local development, defaults to localhost
// For production, set window.ENV.API_BASE_URL and window.ENV.API_KEY
const API_BASE_URL = window.ENV?.API_BASE_URL || "http://localhost:5000/api";
const API_KEY = window.ENV?.API_KEY || ""; // Optional: API key for authenticated requests

// Helper function to add API key to requests
function getHeaders() {
  const headers = {
    'Content-Type': 'application/json'
  };
  if (API_KEY) {
    headers['X-API-Key'] = API_KEY;
  }
  return headers;
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
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000); // Increased timeout
    try {
      const res = await fetch(`${API_BASE_URL}/rank`, { 
        method: 'POST', 
        body: formData, 
        signal: controller.signal 
      });
      clearTimeout(timeout);
      if (!res.ok) throw new Error('backend error');
      const json = await res.json();
      if (!json || !Array.isArray(json.results) || json.results.length === 0) throw new Error('empty results');
      return { data: json.results, source: 'backend' };
    } catch (err) {
      clearTimeout(timeout);
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
    header.innerHTML = `<strong>Ranking (${items.length})</strong>
                        <span class="meta">${meta.source ? 'Source: ' + meta.source : ''} ${meta.fallback ? '(fallback used)' : ''}</span>`;
    resultsEl.appendChild(header);

    const list = document.createElement('div');
    list.className = 'results-list';
    items.forEach((it, idx) => {
      const card = document.createElement('div');
      card.className = 'result-card';
      card.innerHTML = `
        <div class="rank">#${idx + 1}</div>
        <div class="info">
          <div class="name">${it.name || it.candidate || 'Candidate ' + (idx+1)}</div>
          <div class="meta-line">Score: <strong>${it.score ?? it.matchScore ?? '—'}</strong> • ${(it.skills||[]).slice(0,4).join(', ')}</div>
          <div class="note">${it.note || it.summary || ''}</div>
        </div>
      `;
      list.appendChild(card);
    });
    resultsEl.appendChild(list);
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
        renderResults(res.data, { source: 'backend' });
      } catch (err) {
        console.warn('Backend unavailable, using fallback:', err);
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
    // Prepare form data
    const formData = new FormData();
    formData.append("resume", file);

    // Call your backend API
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    const data = await response.json();

    // Expected response structure:
    // {
    //   mainScore: 84,
    //   keywordScore: 78,
    //   achievementScore: 88,
    //   formattingScore: 90,
    //   lengthScore: 76
    // }

    updateScoreUI(data);

  } catch (error) {
    console.error("❌ Resume analysis failed:", error);
    alert("Something went wrong while analyzing your resume. Please try again.");
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

