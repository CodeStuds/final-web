# 🧠 HireSight
### _AI-Powered Talent Intelligence Platform_

HireSight is an AI-driven recruitment assistant that helps companies find, evaluate, and interview the best candidates — faster and smarter.

---

## 🚀 Features

### 🏢 For Companies / Recruiters
- **Smart Registration**
  - Companies register and define hiring needs through an interactive setup.
  - The system asks:
    1. What role are you recruiting for?  
    2. Which skills are mandatory?  
    3. Is CGPA important?  
    4. How many years of experience are required?  
    5. Describe your ideal candidate.  

  All responses are combined into an internal “Job Profile Document” (labeled as *Requirement 9*).

- **Resume Intelligence**
  - Upload resumes individually or as a ZIP batch.
  - AI extracts text from PDFs or DOCX files.
  - Parses and structures candidate information (skills, education, experience, etc.).

- **GitHub & LinkedIn Integration**
  - Fetches candidates’ public GitHub repositories, programming languages, and contributions.
  - Optionally retrieves LinkedIn data for recent achievements, endorsements, and soft skills.

- **AI-Based Candidate Ranking**
  - Compares every candidate’s resume and GitHub/LinkedIn profile to the company’s job description.
  - Produces a **leaderboard (0–1 score)** representing candidate–role fit.

- **Automated Interview Generation**
  - For the top candidates, the system generates:
    - 8–10 personalized technical questions  
    - 3–5 behavioral/HR questions  
    - 2–3 project-related follow-ups  
  - Uses GitHub + LinkedIn insights to make questions realistic and specific.

- **AI-Powered Interview Monitoring** *(Future Feature)*
  - Uses webcam feed to analyze:
    - Eye movement (detecting reading/cheating)
    - Body posture and confidence
    - Real-time voice-to-text transcription
  - Gives live feedback to interviewers.

- **Automated Shortlisting & Notifications**
  - Once recruiters select top candidates, HireSight automatically:
    - Sends branded email invitations to shortlisted candidates.
    - Includes the company’s name and interview details in the email template.

---

## 👥 For Candidates
- Personalized job recommendations based on your uploaded resume and GitHub activity.
- “Jobs near you” and “Role fit” suggestions powered by AI.
- Continuous skill feedback to improve match scores for future roles.

---

## 🧩 Tech Stack

| Layer | Tools Used |
|-------|-------------|
| **Frontend** | React.js / Tailwind CSS |
| **Backend** | Python (FastAPI / Flask) |
| **Database** | MongoDB / Firebase |
| **AI / ML** | OpenAI / Gemini / OpenRouter APIs, Scikit-learn, HuggingFace Transformers |
| **Document Parsing** | PyPDF2, pdfplumber, python-docx |
| **Webcam / Video Analysis** | OpenCV, Mediapipe, DeepFace |
| **Deployment** | Google Cloud / AWS / Vercel |

---

## 🧠 How It Works

1. **Company Registers** → Defines hiring role and preferences.  
2. **Upload Resumes** → Extracts and parses data automatically.  
3. **Data Enrichment** → Fetches GitHub & LinkedIn info.  
4. **AI Leaderboard** → Ranks candidates based on skill match.  
5. **Interview Generation** → Creates smart question sets.  
6. **Finalization** → Sends email to shortlisted candidates.  

---

## 🧰 Setup (For Developers)

```bash
# Clone the repository
git clone https://github.com/<your-username>/HireSight.git
cd HireSight

# Create virtual environment
python -m venv venv
source venv/bin/activate   # (Windows: venv\Scripts\activate)

# Install dependencies
pip install -r requirements.txt

# Run the backend
python app.py
