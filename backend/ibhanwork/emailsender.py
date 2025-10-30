# ===============================
#  Bulk Interview Invitation Sender (Colab Ready - Simplified)
# ===============================
#keep in mind instead of upload csv will not be there after the email for selected user is generated after the user clicks finalize immidiatly a csv file containing emails of selected user from the leaderboard
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from getpass import getpass
from google.colab import files

print(" Upload your candidates.csv file below (columns: name,email)")
uploaded = files.upload()
csv_file = list(uploaded.keys())[0]
candidates = pd.read_csv(csv_file)
display(candidates.head())

# ============  COMPANY INPUTS ============
company_name = input(" Enter your Company Name: ").strip() # this will be fetched from company registration form when a company registers to use our website
role = input(" Enter the Job Role: ").strip() #this will be fetched from the time company selects job role while givingin job description in main_frontend
job_description = input(" Paste your Job Description: ").strip()#this will be fetched from the time company selects job description in main_frontendb role whil

# ============  EMAIL SETUP ============
sender_email = "teamhiresight@gmail.com"
app_password = "flit gapp bbqx jdsg"
#and generate a better template as well please
# ============ ✉️ TEMPLATE GENERATOR ============
def generate_invite_template(company_name, role, job_description):
    subject = f" Interview Invitation for {role} at {company_name}"
    body = f"""
Dear {{candidate_name}},

We are pleased to inform you that you have been shortlisted for the position of **{role}** at **{company_name}**.

**Job Description:**
{job_description}

We were impressed by your profile and would like to invite you to the next stage of our selection process.

Please reply to this email to confirm your availability.

Best regards,  
HR Team  
{company_name}
"""
    return subject, body

# ============  EMAIL SENDER ============
def send_bulk_emails(sender_email, app_password, company_name, role, job_description, candidates_df):
    subject, template = generate_invite_template(company_name, role, job_description)
    smtp_server, smtp_port = "smtp.gmail.com", 587

    # Connect to Gmail SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, app_password)
    print("\n Logged in successfully!\n")

    sent, failed = 0, 0

    for _, row in candidates_df.iterrows():
        name = row["name"]
        email = row["email"]

        # Personalize body
        body = template.replace("{candidate_name}", name)

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            server.sendmail(sender_email, email, msg.as_string())
            print(f" Sent to {name} ({email})")
            sent += 1
        except Exception as e:
            print(f" Failed for {email}: {e}")
            failed += 1

    server.quit()
    print(f"\n Summary: {sent} sent , {failed} failed ")
#connect it to out project make it work pls
# ============  RUN ============
send_bulk_emails(sender_email, app_password, company_name, role, job_description, candidates)
