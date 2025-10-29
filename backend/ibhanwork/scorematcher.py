import os
import zipfile
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv
import re

# ============ CONFIGURATION ============
ZIP_PATH = "resumes.zip"   # Your resumes zip file
DESC_PATH = "desc.txt"     # Job description text file
EXTRACT_DIR = "resumes_extracted"
# ======================================


def extract_zip(zip_path, extract_to):
    """Extract resumes zip file"""
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"✅ Extracted {len(zip_ref.namelist())} files to {extract_to}")


def read_file(file_path):
    """Read text from file safely with debugging"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            print(f"   📄 {os.path.basename(file_path)}: {len(content)} characters")
            if len(content) < 50:
                print(f"   ⚠️  Warning: File might be too short or empty")
            return content
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return ""


def get_candidate_name(filename):
    """Simple cleaned fallback from filename (used if text extraction fails)"""
    name = os.path.splitext(os.path.basename(filename))[0]
    # Remove common extraction headers like "=== EXTRACTED FROM: ... ==="
    name = re.sub(r'={2,}.*EXTRACTED\s+FROM[:\s\-]*', '', name, flags=re.I)
    # replace delimiters
    name = name.replace('_', ' ').replace('-', ' ').strip(' =._-')
    # collapse spaces
    name = re.sub(r'\s+', ' ', name).strip()
    return name or filename


def _cleanup_name_candidate(raw):
    """Normalize a raw candidate name string and reject noisy values."""
    if not raw:
        return ""
    s = raw.strip()
    # remove trailing academic/professional titles and parentheses/extra chars
    s = re.sub(r'\((?:.*)\)', '', s)
    s = re.sub(r'\b(?:Ph\.?D|PhD|MD|M\.?Sc|MSc|B\.?Sc|BSc|Chef|Manager|Sr\.?|Jr\.|III|II)\b[.,]?', '', s, flags=re.I)
    s = re.sub(r'[\|\[\];:]+', ' ', s)
    s = re.sub(r'\s{2,}', ' ', s).strip(' ,.-')
    # reject if it contains emails or phone numbers or long digit sequences
    if '@' in s or re.search(r'\d{3,}', s):
        return ""
    # limit words length (names rarely > 5 words)
    if len(s.split()) > 5:
        return ""
    return s


def extract_candidate_name_from_text(text, filename_fallback):
    """
    Robust name extractor:
    - strips common "EXTRACTED FROM" headers
    - looks for "Name:" or "Resume of" patterns (same-line or next line)
    - tries Title Case heuristic on top N lines
    - handles "Last, First" format
    - falls back to cleaned filename
    """
    if not text or not text.strip():
        return get_candidate_name(filename_fallback)

    # Remove extraction headers that some converters add
    text = re.sub(r'={2,}\s*EXTRACTED\s+FROM[:\s\-]*([^=]+)={2,}', r'\1', text, flags=re.I)
    text = re.sub(r'={2,}.*?={2,}', ' ', text)  # any leftover ==== blocks

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    top_lines = lines[:25]

    # 1) Label patterns on the same line
    same_line_patterns = [
        r'^\s*(?:name|full name|candidate name|candidate|applicant)\s*[:\-]\s*(.+)$',
        r'^\s*(?:resume of|cv of|curriculum vitae of)\s*[:\-]?\s*(.+)$',
    ]
    for pat in same_line_patterns:
        for ln in top_lines:
            m = re.match(pat, ln, flags=re.I)
            if m:
                cand = _cleanup_name_candidate(m.group(1))
                if cand:
                    return cand

    # 2) Label on one line, actual name on next line
    label_lines = re.compile(r'^\s*(?:name|full name|candidate name|candidate|applicant|resume of|cv of)\s*[:\-]?\s*$', flags=re.I)
    for i, ln in enumerate(top_lines):
        if label_lines.match(ln) and i + 1 < len(top_lines):
            cand = _cleanup_name_candidate(top_lines[i + 1])
            if cand:
                return cand

    # 3) Title case heuristic and "Last, First" handling
    for ln in top_lines:
        if '@' in ln or re.search(r'\d', ln):
            continue
        # Last, First -> First Last
        m = re.match(r'^([A-Za-z\-]+),\s*([A-Za-z\-\s]+)$', ln)
        if m:
            cand = _cleanup_name_candidate(f"{m.group(2).strip()} {m.group(1).strip()}")
            if cand:
                return cand
        # Title case words (2-4 words, each starts with uppercase then lowercase)
        words = ln.split()
        if 1 < len(words) <= 4:
            if all(re.match(r"^[A-Z][a-z]+(?:[-'][A-Z][a-z]+)?$", w) for w in words):
                cand = _cleanup_name_candidate(ln)
                if cand:
                    return cand

    # 4) Fallback to cleaned filename
    return get_candidate_name(filename_fallback)


def calculate_similarity(resume_texts, job_desc):
    """Compute cosine similarity between resumes and job description"""
    
    print(f"\n🔍 SIMILARITY ANALYSIS:")
    print(f"   📝 Job description: {len(job_desc)} characters")
    print(f"   📄 Number of resumes: {len(resume_texts)}")
    
    # Check if we have valid content
    if not job_desc.strip():
        print("❌ Job description is empty!")
        return []
    
    if not resume_texts or all(not text.strip() for text in resume_texts):
        print("❌ No valid resume text found!")
        return []
    
    # Show sample of job description
    print(f"   📋 Job desc preview: {job_desc[:100]}...")
    
    # Filter out empty resumes
    valid_resumes = []
    valid_indices = []
    for i, text in enumerate(resume_texts):
        if text.strip():  # Only include non-empty resumes
            valid_resumes.append(text)
            valid_indices.append(i)
        else:
            print(f"   ⚠️  Resume {i+1} is empty, skipping")
    
    if not valid_resumes:
        print("❌ No non-empty resumes found!")
        return []
    
    print(f"   ✅ Using {len(valid_resumes)} valid resumes for comparison")
    
    try:
        # Create corpus with job description first
        corpus = [job_desc] + valid_resumes
        
        # Use TF-IDF vectorizer with relaxed parameters
        vectorizer = TfidfVectorizer(
            stop_words="english",
            lowercase=True,
            ngram_range=(1, 2),  # Include bigrams
            min_df=1,  # Lower minimum document frequency
            max_features=5000  # Limit features
        )
        
        print(f"   🔢 Fitting TF-IDF on {len(corpus)} documents...")
        tfidf_matrix = vectorizer.fit_transform(corpus)
        print(f"   📊 TF-IDF matrix shape: {tfidf_matrix.shape}")
        
        # Calculate similarities
        job_vector = tfidf_matrix[0:1]
        resume_vectors = tfidf_matrix[1:]
        
        similarities = cosine_similarity(job_vector, resume_vectors).flatten()
        
        print(f"   🎯 Similarity scores calculated")
        
        # Map back to original indices
        full_similarities = [0.0] * len(resume_texts)
        for i, sim_score in enumerate(similarities):
            full_similarities[valid_indices[i]] = sim_score
            
        return full_similarities
        
    except Exception as e:
        print(f"❌ Error calculating similarity: {e}")
        return [0.0] * len(resume_texts)


def main():
    print("🚀 RESUME MATCHING SYSTEM")
    print("=" * 50)
    
    # Step 1: Check if files exist
    if not os.path.exists(ZIP_PATH):
        print(f"❌ Zip file '{ZIP_PATH}' not found!")
        return
    
    if not os.path.exists(DESC_PATH):
        print(f"❌ Job description file '{DESC_PATH}' not found!")
        return
    
    # Step 2: Extract resumes
    print(f"\n📦 Step 1: Extracting resumes from {ZIP_PATH}")
    extract_zip(ZIP_PATH, EXTRACT_DIR)
    
    # Step 3: Load job description
    print(f"\n📝 Step 2: Loading job description from {DESC_PATH}")
    job_description = read_file(DESC_PATH)
    
    # Step 4: Load resumes
    print(f"\n📄 Step 3: Loading resumes")
    if not os.path.exists(EXTRACT_DIR):
        print(f"❌ Extraction directory '{EXTRACT_DIR}' not found!")
        return
        
    resume_files = [f for f in os.listdir(EXTRACT_DIR) if f.endswith(".txt")]
    if not resume_files:
        print(f"❌ No .txt files found in '{EXTRACT_DIR}'!")
        return
    
    print(f"   Found {len(resume_files)} resume files:")
    for f in resume_files[:5]:  # Show first 5
        print(f"      • {f}")
    if len(resume_files) > 5:
        print(f"      ... and {len(resume_files) - 5} more")
    
    resume_texts = []
    candidate_names = []
    for f in resume_files:
        file_path = os.path.join(EXTRACT_DIR, f)
        content = read_file(file_path)
        resume_texts.append(content)
        candidate_names.append(extract_candidate_name_from_text(content, f))
    
    # Step 5: Calculate similarity
    print(f"\n🎯 Step 4: Calculating similarity scores")
    scores = calculate_similarity(resume_texts, job_description)
    
    # Step 6: Prepare and display results
    leaderboard = []
    for i, (name, score) in enumerate(zip(candidate_names, scores)):
        text_len = len(resume_texts[i]) if i < len(resume_texts) else 0
        filename = resume_files[i] if i < len(resume_files) else ""
        leaderboard.append((name, score, text_len, filename))  # Include filename and text length for CSV/debugging)
    
    # Sort by score
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    
    # Save leaderboard to CSV (only name and score)
    csv_path = "results.csv"
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Candidate", "Score"])
            for name, score, *_ in leaderboard:
                writer.writerow([name, f"{score:.6f}"])
        print(f"\n✅ Results saved to {os.path.abspath(csv_path)}")
    except Exception as e:
        print(f"\n❌ Failed to write CSV '{csv_path}': {e}")
    
    # Step 8: Display results
    print("\n" + "=" * 60)
    print("🏆 RESUME MATCH LEADERBOARD")
    print("=" * 60)
    print(f"{'Rank':<4} {'Candidate':<25} {'Score':<8} {'Text Len':<8}")
    print("-" * 60)
    
    for rank, (name, score, text_len, filename) in enumerate(leaderboard, 1):
        print(f"{rank:<4} {name:<25} {score:.3f}{'':<4} {text_len:<8}")
    
    print("=" * 60)
    print(f"📊 Summary: {len(leaderboard)} candidates processed")
    if leaderboard:
        best_score = leaderboard[0][1]
        print(f"🥇 Best match: {leaderboard[0][0]} (score: {best_score:.3f})")
        
        # Show score distribution
        scores_only = [x[1] for x in leaderboard]
        non_zero_scores = [s for s in scores_only if s > 0]
        if non_zero_scores:
            print(f"📈 Non-zero scores: {len(non_zero_scores)}/{len(scores_only)}")
        else:
            print("⚠️  All scores are zero - check content quality")


if __name__ == "__main__":
    main()
