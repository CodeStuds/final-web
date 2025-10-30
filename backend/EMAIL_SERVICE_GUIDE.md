# 📧 HireSight Email Service - Complete Guide

## Overview

The HireSight Email Service provides professional, automated interview invitation emails to shortlisted candidates. This guide covers setup, configuration, usage, and troubleshooting.

---

## 🚀 Quick Start

### 1. Configure Email Credentials

#### For Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication**
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password (without spaces)

3. **Update .env File**
   ```bash
   cd /home/srijan/Code/Hackathrone/final-web/backend
   nano .env
   ```
   
   Update these lines:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_EMAIL=your-email@gmail.com
   SMTP_PASSWORD=your_16_char_app_password
   SMTP_SENDER_NAME=Your Company Name
   ```

### 2. Test the Service

Run the test script to verify everything works:

```bash
cd /home/srijan/Code/Hackathrone/final-web/backend
python3 test_email_service.py
```

---

## 📋 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SMTP_SERVER` | SMTP server address | `smtp.gmail.com` | Yes |
| `SMTP_PORT` | SMTP port number | `587` | Yes |
| `SMTP_EMAIL` | Sender email address | - | Yes |
| `SMTP_PASSWORD` | SMTP password/app password | - | Yes |
| `SMTP_SENDER_NAME` | Display name for sender | `HireSight Recruitment Team` | No |

### Supported Email Providers

#### Gmail
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```
- **Limit**: 500 emails/day for free accounts
- **Requires**: App Password (2FA enabled)

#### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

#### Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

#### SendGrid (Production)
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_EMAIL=apikey
SMTP_PASSWORD=your_sendgrid_api_key
```
- **Limit**: 100 emails/day (free), unlimited (paid)
- **Recommended for production**

---

## 🎯 Usage

### Via API Endpoint (Frontend Integration)

The email service is automatically integrated with the API at:
```
POST /api/email/send-interview-requests
```

**Request Body:**
```json
{
  "candidates": [
    {"name": "John Doe", "email": "john@example.com"},
    {"name": "Jane Smith", "email": "jane@example.com"}
  ],
  "job_details": {
    "role": "Senior Software Engineer",
    "description": "We are looking for an experienced developer...",
    "skills": "Python, Django, PostgreSQL, Docker"
  },
  "company_info": {
    "company_name": "Tech Innovations Inc.",
    "company_email": "hr@techinnovations.com"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Interview requests sent to 2 candidate(s)",
  "sent": 2,
  "failed": 0,
  "total": 2,
  "recipients": ["john@example.com", "jane@example.com"],
  "failed_recipients": [],
  "timestamp": "2025-10-30T12:34:56.789012"
}
```

### Direct Python Usage

```python
from ibhanwork.emailsender import send_interview_invitations

# Prepare candidate list
candidates = [
    {"name": "John Doe", "email": "john@example.com"},
    {"name": "Jane Smith", "email": "jane@example.com"}
]

# Send invitations
result = send_interview_invitations(
    candidates=candidates,
    company_name="Tech Corp",
    role="Backend Developer",
    job_description="We are hiring a talented backend developer...",
    skills="Python, Django, PostgreSQL"
)

# Check results
print(f"Sent: {result['sent']}, Failed: {result['failed']}")
```

### Using EmailService Class

```python
from ibhanwork.emailsender import EmailService

# Initialize service
service = EmailService()

# Send bulk emails
result = service.send_bulk_emails(
    candidates=[...],
    company_name="Tech Corp",
    role="Backend Developer",
    job_description="...",
    skills="Python, Django"
)

# Or send single email
success, error = service.send_single_email(
    recipient_email="candidate@example.com",
    recipient_name="John Doe",
    company_name="Tech Corp",
    role="Backend Developer",
    job_description="...",
    skills="Python, Django"
)
```

---

## 📧 Email Template

### What Candidates Receive

The email service sends professional HTML emails with:

- **Subject**: 🎉 Interview Invitation for [Role] at [Company]
- **Greeting**: Personalized with candidate's name
- **Content**:
  - Congratulations message
  - Job role and description
  - Required skills (if provided)
  - Next steps
  - Call-to-action button
  - Company information
- **Footer**: HireSight branding

### Sample Email Preview

```
Subject: 🎉 Interview Invitation for Backend Developer at Tech Corp

Dear John Doe,

Congratulations! You have been shortlisted for the position of 
Backend Developer at Tech Corp.

About the Role:
We are looking for an experienced backend developer to join our team...

Required Skills:
Python, Django, PostgreSQL, Docker

Next Steps:
We were highly impressed by your profile and would like to invite you 
to the next stage of our selection process. Please reply to this email 
with your availability for an interview in the coming week.

[Confirm Your Availability Button]

We look forward to speaking with you soon!

Best regards,
HR Team
Tech Corp

---
This email was sent via HireSight - Smart Recruitment Platform
```

---

## 🔧 Troubleshooting

### Issue: "Email service not properly configured"

**Cause**: Missing or invalid SMTP credentials

**Solution**:
1. Check `.env` file exists in `/backend/` directory
2. Verify all required variables are set
3. Ensure no extra spaces or quotes around values
4. Test with: `python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('SMTP_EMAIL'))"`

### Issue: "SMTP Authentication failed"

**Cause**: Invalid credentials or incorrect app password

**Solution for Gmail**:
1. Verify 2FA is enabled on your Google account
2. Generate a new App Password
3. Copy password without spaces
4. Update `SMTP_PASSWORD` in `.env`
5. Restart the API server

### Issue: "Failed to connect to SMTP server"

**Cause**: Network issues or wrong server/port

**Solution**:
1. Check your internet connection
2. Verify firewall isn't blocking port 587
3. Try alternative port 465 with SSL
4. Test connection: `telnet smtp.gmail.com 587`

### Issue: "Emails going to spam"

**Cause**: Email authentication issues

**Solution**:
1. Set up SPF records for your domain
2. Configure DKIM signing
3. Use a verified sender address
4. Avoid spam trigger words in content
5. Consider using SendGrid or AWS SES for production

### Issue: "Rate limit exceeded"

**Cause**: Too many emails sent too quickly

**Solution**:
- Gmail free: Max 500/day
- Add delays between batches
- Upgrade to Google Workspace (2000/day)
- Use SendGrid (unlimited with paid plan)

---

## 🧪 Testing

### Test Email Service

```bash
cd /home/srijan/Code/Hackathrone/final-web/backend
python3 test_email_service.py
```

### Manual Test via API

```bash
curl -X POST http://localhost:5000/api/email/send-interview-requests \
  -H "Content-Type: application/json" \
  -d '{
    "candidates": [{"name": "Test User", "email": "your-test-email@gmail.com"}],
    "job_details": {
      "role": "Test Position",
      "description": "This is a test email",
      "skills": "Testing"
    },
    "company_info": {
      "company_name": "Test Company",
      "company_email": "test@company.com"
    }
  }'
```

### Test with Frontend

1. Start the backend server:
   ```bash
   cd /home/srijan/Code/Hackathrone/final-web/backend
   python3 api.py
   ```

2. Open COMPANY_MAIN_PAGE in browser

3. Upload resumes and generate leaderboard

4. Select candidates and click "Send Interview Request"

5. Check logs for email sending status

---

## 📊 Monitoring & Logging

### Log Files

Emails sending is logged to:
- Console output
- `hiresight.log` file

### Log Format

```
2025-10-30 12:34:56 - emailsender - INFO - 📧 Starting bulk email send to 5 candidates
2025-10-30 12:34:57 - emailsender - INFO - ✅ Email sent successfully to John Doe (john@example.com)
2025-10-30 12:34:58 - emailsender - INFO - ✅ Email sent successfully to Jane Smith (jane@example.com)
2025-10-30 12:34:59 - emailsender - ERROR - ❌ Failed to send email to invalid@: Invalid email address
2025-10-30 12:35:00 - emailsender - INFO - 📊 Email sending complete: 4 sent, 1 failed
```

### Check Logs

```bash
# View recent logs
tail -f backend/hiresight.log

# Search for email-related logs
grep "emailsender" backend/hiresight.log

# Count successful sends
grep "✅ Email sent" backend/hiresight.log | wc -l
```

---

## 🔒 Security Best Practices

### DO ✅

- Use environment variables for credentials
- Enable 2FA and use app passwords
- Rotate passwords regularly
- Use different credentials for dev/prod
- Keep `.env` in `.gitignore`
- Use SendGrid/AWS SES for production
- Implement rate limiting
- Validate email addresses before sending
- Log all email activity

### DON'T ❌

- Commit `.env` file to git
- Share SMTP credentials
- Use personal email in production
- Send without user consent
- Hard-code credentials in code
- Ignore bounce rates
- Send to unverified addresses

---

## 🚀 Production Deployment

### Recommended Setup

1. **Use Professional Email Service**
   - SendGrid (recommended)
   - AWS SES
   - Mailgun
   - Postmark

2. **Configure Domain Authentication**
   - Set up SPF records
   - Configure DKIM
   - Implement DMARC

3. **Monitor Deliverability**
   - Track bounce rates
   - Monitor spam reports
   - Review engagement metrics

4. **Scale Considerations**
   - Use email queues (Celery + Redis)
   - Implement retry logic
   - Add batch processing
   - Set up monitoring alerts

### Example SendGrid Setup

```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_EMAIL=apikey
SMTP_PASSWORD=SG.your_actual_sendgrid_api_key_here
SMTP_SENDER_NAME=Your Company Name
```

---

## 📞 Support

### Need Help?

1. Check troubleshooting section above
2. Review logs for error messages
3. Test with `test_email_service.py`
4. Verify environment variables
5. Check SMTP server status

### Common Resources

- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [SendGrid Documentation](https://docs.sendgrid.com/)
- [SMTP Error Codes](https://www.mailgun.com/blog/email/smtp-error-codes/)
- [Email Best Practices](https://postmarkapp.com/guides/email-best-practices)

---

## 📝 Changelog

### Version 1.0.0 (2025-10-30)

- ✅ Initial release
- ✅ SMTP email sending with Gmail support
- ✅ Professional HTML email templates
- ✅ Plain text fallback
- ✅ Bulk sending capability
- ✅ Comprehensive error handling
- ✅ Detailed logging
- ✅ Environment-based configuration
- ✅ Frontend integration

---

**Made with ❤️ by the HireSight Team**
