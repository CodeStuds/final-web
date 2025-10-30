import re
#this verification takes place during the company registration if non company domains are ysed it will just show a red bannner that is given in function below however it wont block any action of registration process
def check_company_email(email):
    # Common personal domains
    personal_domains = [
        "gmail.com", "yahoo.com", "outlook.com",
        "hotmail.com", "icloud.com", "aol.com"
    ]
    
    # Extract domain
    match = re.search(r'@([\w.-]+)$', email)
    if match:
        domain = match.group(1).lower()
        if domain in personal_domains:
            print("\033[91m⚠️ Please use an official company email address (not a personal one like Gmail/Yahoo).\033[0m")
        else:
            print("✅ Company email detected.")
    else:
        print("\033[91m❌ Invalid email format.\033[0m")


# Example usage
check_company_email("john.doe@gmail.com")
check_company_email("hr@openai.com")
