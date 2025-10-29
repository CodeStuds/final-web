import os
import requests
import zipfile
from tqdm import tqdm

# =============================================================
# 🔑 CONFIGURATION
# =============================================================
# Get your free Gemini API key at: https://aistudio.google.com/app/apikey
API_KEY = "AIzaSyDg73KGgHkLntpyI_S9Dbho93zfu4EJOxg"   # 👈 REPLACE with your actual Gemini API key
MODEL = "gemini-2.5-flash"  # Use gemini-2.5-flash or gemini-2.0-flash (free tier supported)

ZIP_FILE = "resumes.zip"        # 👈this  zip file will contain text files combining the text from github and resumes given by the textract each test file will have combined github and resumes one text file per candidate
EXTRACT_DIR = "resumes"
OUTPUT_DIR = "interview_outputs"



# =============================================================
# 🤖 Function to generate interview questions
# =============================================================
def generate_interview_questions(candidate_name, candidate_text):
    prompt = f"""
You are an expert technical interviewer and HR assistant.

You will receive one text file for a candidate. The file contains combined text extracted from their GitHub and LinkedIn profiles — including project details, skills, experiences, and technical achievements.

Now generate one output text file named '{candidate_name}_interview_questions.txt' with:
- A 3–4 line thesis summary of the candidate’s expertise.
- 8–10 technical questions based on their projects and skills.
- 3–5 behavioral/HR questions.
- 2–3 follow-up questions connecting their technical work to real-world use.

Make questions personalized and specific.

Candidate Profile:
{candidate_text}
"""

    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )

        if response.status_code != 200:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return None

        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print(f"⚠️ Error generating for {candidate_name}: {e}")
        return None


# =============================================================
# 📂 Extract resumes from ZIP
# =============================================================
def extract_zip(zip_path, extract_dir):
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"❌ ZIP file '{zip_path}' not found.")
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    print(f"✅ Extracted files to: {extract_dir}")


# =============================================================
# 🧩 Main process
# =============================================================
def main():
    # Step 1 — Extract ZIP
    extract_zip(ZIP_FILE, EXTRACT_DIR)

    # Step 2 — Make output folder
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 3 — Loop through candidate text files
    files = [f for f in os.listdir(EXTRACT_DIR) if f.endswith(".txt")]
    if not files:
        print("⚠️ No .txt files found inside the ZIP.")
        return

    for file in tqdm(files, desc="Processing candidates"):
        candidate_name = os.path.splitext(file)[0]
        candidate_path = os.path.join(EXTRACT_DIR, file)

        with open(candidate_path, "r", encoding="utf-8") as f:
            candidate_text = f.read()

        print(f"\n🧾 Generating interview questions for: {candidate_name}...")
        output = generate_interview_questions(candidate_name, candidate_text)

        if output:
            out_path = os.path.join(OUTPUT_DIR, f"{candidate_name}_interview_questions.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"✅ Saved: {out_path}")
        else:
            print(f"⚠️ Skipped: {candidate_name}")

    print("\n🎯 All done! Generated interview questions are in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
