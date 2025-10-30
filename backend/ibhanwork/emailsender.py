#!/usr/bin/env python3
"""
HireSight Email Service Module
Professional email service for sending interview invitations to candidates
Integrated with the HireSight recruitment platform
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailConfig:
    """Email configuration management"""
    
    def __init__(self):
        """Initialize email configuration from environment variables"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SMTP_EMAIL', 'teamhiresight@gmail.com')
        self.sender_password = os.getenv('SMTP_PASSWORD', '')
        self.sender_name = os.getenv('SMTP_SENDER_NAME', 'HireSight Recruitment Team')
        
        # Validate configuration
        if not self.sender_password:
            logger.warning("SMTP_PASSWORD not set in environment variables")
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(self.sender_email and self.sender_password)


class EmailService:
    """
    Professional email service for sending interview invitations
    Handles SMTP connection, template generation, and bulk email sending
    """
    
    def __init__(self, config: Optional[EmailConfig] = None):
        """
        Initialize email service
        
        Args:
            config: EmailConfig instance (creates default if None)
        """
        self.config = config or EmailConfig()
        self.smtp_connection = None
        
        if not self.config.is_configured():
            logger.error("Email service not properly configured. Check environment variables.")
    
    def connect(self) -> bool:
        """
        Establish SMTP connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to SMTP server {self.config.smtp_server}:{self.config.smtp_port}")
            self.smtp_connection = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            self.smtp_connection.starttls()
            self.smtp_connection.login(self.config.sender_email, self.config.sender_password)
            logger.info("✅ Successfully connected to SMTP server")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP Authentication failed: {e}")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"❌ Failed to connect to SMTP server: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to SMTP: {e}")
            return False
    
    def disconnect(self):
        """Close SMTP connection"""
        if self.smtp_connection:
            try:
                self.smtp_connection.quit()
                logger.info("Disconnected from SMTP server")
            except Exception as e:
                logger.warning(f"Error disconnecting from SMTP: {e}")
            finally:
                self.smtp_connection = None
    
    def generate_email_subject(self, company_name: str, role: str) -> str:
        """
        Generate email subject line
        
        Args:
            company_name: Name of the company
            role: Job role/position
            
        Returns:
            str: Email subject line
        """
        return f"🎉 Interview Invitation for {role} at {company_name}"
    
    def generate_plain_text_body(
        self,
        candidate_name: str,
        company_name: str,
        role: str,
        job_description: str,
        skills: Optional[str] = None
    ) -> str:
        """
        Generate plain text email body
        
        Args:
            candidate_name: Name of the candidate
            company_name: Name of the company
            role: Job role/position
            job_description: Job description text
            skills: Required skills (optional)
            
        Returns:
            str: Plain text email body
        """
        skills_section = f"\n\nRequired Skills:\n{skills}" if skills else ""
        
        return f"""Dear {candidate_name},

Congratulations! We are delighted to inform you that you have been shortlisted for the position of {role} at {company_name}.

About the Role:
{job_description}{skills_section}

Next Steps:
We were highly impressed by your profile and would like to invite you to the next stage of our selection process. Please reply to this email with your availability for an interview in the coming week.

We look forward to speaking with you soon!

Best regards,
HR Team
{company_name}

---
This email was sent via HireSight - Smart Recruitment Platform
If you have any questions, please reply to this email.
"""
    
    def generate_html_body(
        self,
        candidate_name: str,
        company_name: str,
        role: str,
        job_description: str,
        skills: Optional[str] = None
    ) -> str:
        """
        Generate HTML email body with professional styling
        
        Args:
            candidate_name: Name of the candidate
            company_name: Name of the company
            role: Job role/position
            job_description: Job description text
            skills: Required skills (optional)
            
        Returns:
            str: HTML email body
        """
        skills_section = f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #495057; margin-top: 0;">🎯 Required Skills</h3>
            <p style="color: #6c757d; margin: 0;">{skills}</p>
        </div>
        """ if skills else ""
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 28px;">🎉 Interview Invitation</h1>
    </div>
    
    <div style="background-color: white; padding: 30px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 10px 10px;">
        <p style="font-size: 16px; color: #333;">Dear <strong>{candidate_name}</strong>,</p>
        
        <div style="background-color: #e8f5e9; padding: 20px; border-left: 4px solid #4caf50; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                <strong>Congratulations!</strong> You have been shortlisted for the position of <strong>{role}</strong> at <strong>{company_name}</strong>.
            </p>
        </div>
        
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">📋 About the Role</h2>
        <p style="color: #555; white-space: pre-line;">{job_description}</p>
        
        {skills_section}
        
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">🚀 Next Steps</h2>
        <p style="color: #555;">
            We were highly impressed by your profile and would like to invite you to the next stage of our selection process. 
            Please reply to this email with your availability for an interview in the coming week.
        </p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="mailto:{self.config.sender_email}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                📧 Confirm Your Availability
            </a>
        </div>
        
        <p style="color: #555;">We look forward to speaking with you soon!</p>
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
            <p style="color: #888; font-size: 14px; margin: 5px 0;">Best regards,</p>
            <p style="color: #555; font-weight: bold; margin: 5px 0;">HR Team</p>
            <p style="color: #667eea; font-weight: bold; margin: 5px 0;">{company_name}</p>
        </div>
        
        <div style="margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; text-align: center;">
            <p style="color: #6c757d; font-size: 12px; margin: 0;">
                This email was sent via <strong>HireSight</strong> - Smart Recruitment Platform<br>
                If you have any questions, please reply to this email.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    def send_single_email(
        self,
        recipient_email: str,
        recipient_name: str,
        company_name: str,
        role: str,
        job_description: str,
        skills: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Send email to a single candidate
        
        Args:
            recipient_email: Candidate's email address
            recipient_name: Candidate's name
            company_name: Name of the company
            role: Job role/position
            job_description: Job description text
            skills: Required skills (optional)
            
        Returns:
            Tuple[bool, Optional[str]]: (Success status, Error message if any)
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config.sender_name} <{self.config.sender_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = self.generate_email_subject(company_name, role)
            msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            
            # Generate both plain text and HTML versions
            plain_text = self.generate_plain_text_body(
                recipient_name, company_name, role, job_description, skills
            )
            html_text = self.generate_html_body(
                recipient_name, company_name, role, job_description, skills
            )
            
            # Attach both versions (email clients will choose which to display)
            part1 = MIMEText(plain_text, 'plain')
            part2 = MIMEText(html_text, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            self.smtp_connection.sendmail(
                self.config.sender_email,
                recipient_email,
                msg.as_string()
            )
            
            logger.info(f"✅ Email sent successfully to {recipient_name} ({recipient_email})")
            return True, None
            
        except Exception as e:
            error_msg = f"Failed to send email to {recipient_email}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def send_bulk_emails(
        self,
        candidates: List[Dict[str, str]],
        company_name: str,
        role: str,
        job_description: str,
        skills: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Send interview invitations to multiple candidates
        
        Args:
            candidates: List of candidate dicts with 'name' and 'email' keys
            company_name: Name of the company
            role: Job role/position
            job_description: Job description text
            skills: Required skills (optional)
            
        Returns:
            Dict containing success/failure statistics and details
        """
        if not candidates:
            return {
                'success': False,
                'error': 'No candidates provided',
                'sent': 0,
                'failed': 0,
                'total': 0
            }
        
        # Connect to SMTP server
        if not self.connect():
            return {
                'success': False,
                'error': 'Failed to connect to SMTP server',
                'sent': 0,
                'failed': 0,
                'total': len(candidates)
            }
        
        sent_count = 0
        failed_count = 0
        sent_to = []
        failed_to = []
        
        logger.info(f"📧 Starting bulk email send to {len(candidates)} candidates")
        
        try:
            for candidate in candidates:
                name = candidate.get('name', 'Candidate')
                email = candidate.get('email', '')
                
                if not email:
                    logger.warning(f"⚠️ Skipping candidate {name}: No email address")
                    failed_count += 1
                    failed_to.append({'name': name, 'email': email, 'error': 'No email address'})
                    continue
                
                success, error = self.send_single_email(
                    recipient_email=email,
                    recipient_name=name,
                    company_name=company_name,
                    role=role,
                    job_description=job_description,
                    skills=skills
                )
                
                if success:
                    sent_count += 1
                    sent_to.append({'name': name, 'email': email})
                else:
                    failed_count += 1
                    failed_to.append({'name': name, 'email': email, 'error': error})
        
        finally:
            # Always disconnect
            self.disconnect()
        
        logger.info(f"📊 Email sending complete: {sent_count} sent, {failed_count} failed")
        
        return {
            'success': sent_count > 0,
            'sent': sent_count,
            'failed': failed_count,
            'total': len(candidates),
            'sent_to': sent_to,
            'failed_to': failed_to,
            'timestamp': datetime.now().isoformat()
        }


# Convenience function for quick usage
def send_interview_invitations(
    candidates: List[Dict[str, str]],
    company_name: str,
    role: str,
    job_description: str,
    skills: Optional[str] = None
) -> Dict[str, any]:
    """
    Convenience function to send interview invitations
    
    Args:
        candidates: List of candidate dicts with 'name' and 'email' keys
        company_name: Name of the company
        role: Job role/position
        job_description: Job description text
        skills: Required skills (optional)
        
    Returns:
        Dict containing send results
    """
    service = EmailService()
    return service.send_bulk_emails(
        candidates=candidates,
        company_name=company_name,
        role=role,
        job_description=job_description,
        skills=skills
    )
