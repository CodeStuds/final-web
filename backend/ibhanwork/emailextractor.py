# ============================================================
# 🧩 Step 1: Upload ZIP of text resumes
# ============================================================
from google.colab import files
import zipfile, os, re, csv

uploaded = files.upload()
if not uploaded:
    raise SystemExit("❌ No file uploaded!")

zip_name = list(uploaded.keys())[0]
extract_folder = "resumes_text"
os.makedirs(extract_folder, exist_ok=True)

# Unzip uploaded file
with zipfile.ZipFile(zip_name, "r") as zip_ref:
    zip_ref.extractall(extract_folder)

print(f"✅ Extracted resumes to: {extract_folder}")

# ============================================================
# 🔍 Step 2: Define regex patterns
# ============================================================
email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
phone_pattern = re.compile(r'(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4,6})')
linkedin_pattern = re.compile(r'(https?://(www\.)?linkedin\.com/[a-zA-Z0-9_/.\-]+)')
github_pattern = re.compile(r'(https?://(www\.)?github\.com/[a-zA-Z0-9_/.\-]+)')

# ============================================================
# 🧠 Step 3: Extract info from each text file
# ============================================================
results = []
all_emails = []  # 👈 new list to collect all emails in order

for root, _, files_list in os.walk(extract_folder):
    for file in files_list:
        if file.endswith(".txt"):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            emails = list(dict.fromkeys(email_pattern.findall(text)))  # keeps order & removes duplicates
            phones = list(dict.fromkeys(phone_pattern.findall(text)))
            linkedins = list(dict.fromkeys(linkedin_pattern.findall(text)))
            githubs = list(dict.fromkeys(github_pattern.findall(text)))

            if emails:
                all_emails.extend(emails)  # 👈 store in master list

            results.append({
                "filename": file,
                "emails": ", ".join(emails),
                "phones": ", ".join(phones),
                "linkedin": ", ".join([l[0] for l in linkedins]),
                "github": ", ".join([g[0] for g in githubs])
            })

            print(f"✅ {file}: {len(emails)} email(s), {len(phones)} phone(s)")

# ============================================================
# 💾 Step 4: Save extracted data to CSV
# ============================================================
csv_path = "resume_contacts.csv"

with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["filename", "emails", "phones", "linkedin", "github"])
    writer.writeheader()
    for item in results:
        writer.writerow(item)

print(f"\n📂 Extracted info saved to: {csv_path}")

# ============================================================
# ⬇️ Step 5: Download the CSV
# ============================================================
files.download(csv_path)

# ============================================================
# 📋 Step 6: Print & return all email addresses in order
# ============================================================
print("\n📧 ALL EMAILS (in order of extraction):")
for i, email in enumerate(all_emails, 1):
    print(f"{i}. {email}")

# If you need to use it later in the notebook:
all_emails  # 👈 this variable now holds all extracted emails as a Python list
