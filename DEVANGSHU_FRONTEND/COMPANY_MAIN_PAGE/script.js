// ===============================
// 🔐 AUTHENTICATION CHECK
// ===============================
// Check authentication on page load
(async function initAuth() {
  const session = await checkAuth();
  if (!session) {
    // Not authenticated, redirect to login
    alert("Please log in to access this page.");
    window.location.href = "../COMPANY_LOGIN/index.html";
    return;
  }

  // Get user data and display company name
  const user = await getCurrentUser();
  if (user && user.user_metadata) {
    const companyName = user.user_metadata.company_name || "Company";
    document.getElementById("user-name").textContent = `Welcome, ${companyName}!`;
  }

  // Setup logout button
  document.getElementById("logout-btn").addEventListener("click", async () => {
    const success = await signOut();
    if (success) {
      alert("Logged out successfully.");
      window.location.href = "../COMPANY_LOGIN/index.html";
    }
  });
})();

// ===============================
// 🔐 CONFIGURATION
// ===============================

// TODO: Replace these placeholders with your actual backend details
const API_BASE_URL = "https://your-backend-domain.com/api"; // Example: https://api.myresumescore.ai/api
const API_KEY = "YOUR_API_KEY_HERE"; // Securely store this (not hardcoded in production)


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
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
      },
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
