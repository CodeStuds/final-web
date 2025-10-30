#!/usr/bin/env python3
"""
Email Service Test Script
Tests the HireSight email service functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_configuration():
    """Test if email service is properly configured"""
    print("\n" + "="*70)
    print("📧 EMAIL SERVICE CONFIGURATION TEST")
    print("="*70)
    
    load_dotenv()
    
    config_items = {
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'SMTP_EMAIL': os.getenv('SMTP_EMAIL'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', ''),
        'SMTP_SENDER_NAME': os.getenv('SMTP_SENDER_NAME')
    }
    
    print("\n📋 Configuration Status:")
    all_configured = True
    
    for key, value in config_items.items():
        if key == 'SMTP_PASSWORD':
            status = "✅ Set" if value else "❌ Not Set"
            display_value = "*" * len(value[:4]) + "..." if value else "Not set"
        else:
            status = "✅ Set" if value else "❌ Not Set"
            display_value = value if value else "Not set"
        
        print(f"  {key}: {display_value} - {status}")
        
        if not value:
            all_configured = False
    
    if all_configured:
        print("\n✅ All configuration variables are set!")
        return True
    else:
        print("\n❌ Some configuration variables are missing.")
        print("   Please update your .env file with the required values.")
        print("   See .env.example for reference.")
        return False


def test_import():
    """Test if email service module can be imported"""
    print("\n" + "="*70)
    print("📦 MODULE IMPORT TEST")
    print("="*70)
    
    try:
        from ibhanwork.emailsender import EmailService, EmailConfig, send_interview_invitations
        print("\n✅ Email service module imported successfully!")
        print(f"   - EmailService class: Available")
        print(f"   - EmailConfig class: Available")
        print(f"   - send_interview_invitations function: Available")
        return True
    except ImportError as e:
        print(f"\n❌ Failed to import email service module: {e}")
        return False


def test_email_config():
    """Test EmailConfig initialization"""
    print("\n" + "="*70)
    print("⚙️  EMAIL CONFIG INITIALIZATION TEST")
    print("="*70)
    
    try:
        from ibhanwork.emailsender import EmailConfig
        
        config = EmailConfig()
        print("\n✅ EmailConfig initialized successfully!")
        print(f"   - SMTP Server: {config.smtp_server}")
        print(f"   - SMTP Port: {config.smtp_port}")
        print(f"   - Sender Email: {config.sender_email}")
        print(f"   - Sender Name: {config.sender_name}")
        print(f"   - Is Configured: {config.is_configured()}")
        
        if config.is_configured():
            print("\n✅ Email configuration is valid!")
            return True
        else:
            print("\n⚠️  Email configuration is incomplete.")
            print("   SMTP_PASSWORD is not set in environment variables.")
            return False
            
    except Exception as e:
        print(f"\n❌ Failed to initialize EmailConfig: {e}")
        return False


def test_smtp_connection():
    """Test SMTP connection"""
    print("\n" + "="*70)
    print("🔌 SMTP CONNECTION TEST")
    print("="*70)
    
    try:
        from ibhanwork.emailsender import EmailService
        
        service = EmailService()
        
        if not service.config.is_configured():
            print("\n⚠️  Cannot test connection: Email service not configured")
            print("   Please set SMTP_PASSWORD in .env file")
            return False
        
        print("\n🔄 Attempting to connect to SMTP server...")
        print(f"   Server: {service.config.smtp_server}:{service.config.smtp_port}")
        print(f"   Email: {service.config.sender_email}")
        
        if service.connect():
            print("\n✅ SMTP connection successful!")
            service.disconnect()
            return True
        else:
            print("\n❌ SMTP connection failed!")
            print("   Common causes:")
            print("   - Invalid credentials")
            print("   - 2FA not enabled (for Gmail)")
            print("   - Using regular password instead of app password")
            print("   - Network/firewall issues")
            return False
            
    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        return False


def test_email_generation():
    """Test email template generation"""
    print("\n" + "="*70)
    print("📝 EMAIL TEMPLATE GENERATION TEST")
    print("="*70)
    
    try:
        from ibhanwork.emailsender import EmailService
        
        service = EmailService()
        
        # Test subject generation
        subject = service.generate_email_subject("Tech Corp", "Backend Developer")
        print(f"\n✅ Subject generated: {subject}")
        
        # Test plain text generation
        plain_text = service.generate_plain_text_body(
            candidate_name="John Doe",
            company_name="Tech Corp",
            role="Backend Developer",
            job_description="We are hiring a talented developer...",
            skills="Python, Django, PostgreSQL"
        )
        print(f"\n✅ Plain text template generated ({len(plain_text)} characters)")
        
        # Test HTML generation
        html_text = service.generate_html_body(
            candidate_name="John Doe",
            company_name="Tech Corp",
            role="Backend Developer",
            job_description="We are hiring a talented developer...",
            skills="Python, Django, PostgreSQL"
        )
        print(f"✅ HTML template generated ({len(html_text)} characters)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Template generation failed: {e}")
        return False


def test_send_single_email():
    """Test sending a single email (interactive)"""
    print("\n" + "="*70)
    print("📧 SINGLE EMAIL SEND TEST (Optional)")
    print("="*70)
    
    try:
        from ibhanwork.emailsender import EmailService
        
        service = EmailService()
        
        if not service.config.is_configured():
            print("\n⚠️  Cannot send test email: Email service not configured")
            return False
        
        response = input("\n❓ Do you want to send a test email? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            print("⏭️  Skipping email send test")
            return None
        
        test_email = input("📧 Enter recipient email address: ").strip()
        test_name = input("👤 Enter recipient name: ").strip() or "Test User"
        
        if not test_email or '@' not in test_email:
            print("❌ Invalid email address")
            return False
        
        print(f"\n🔄 Sending test email to {test_name} ({test_email})...")
        
        # Connect to SMTP
        if not service.connect():
            print("❌ Failed to connect to SMTP server")
            return False
        
        # Send email
        success, error = service.send_single_email(
            recipient_email=test_email,
            recipient_name=test_name,
            company_name="HireSight Test Company",
            role="Test Position",
            job_description="This is a test email from HireSight email service.",
            skills="Testing, Quality Assurance"
        )
        
        # Disconnect
        service.disconnect()
        
        if success:
            print(f"\n✅ Test email sent successfully to {test_email}!")
            print("   Please check your inbox (and spam folder)")
            return True
        else:
            print(f"\n❌ Failed to send test email: {error}")
            return False
            
    except Exception as e:
        print(f"\n❌ Email send test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "EMAIL SERVICE TEST SUITE" + " "*24 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        ("Configuration", test_configuration),
        ("Module Import", test_import),
        ("Email Config", test_email_config),
        ("SMTP Connection", test_smtp_connection),
        ("Template Generation", test_email_generation),
        ("Send Email", test_send_single_email)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n💥 Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for test_name, result in results:
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⏭️  SKIPPED"
        print(f"  {test_name}: {status}")
    
    print(f"\n  Total: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    
    if failed == 0 and passed > 0:
        print("\n🎉 All tests passed! Email service is ready to use!")
    elif failed > 0:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        print("   Check EMAIL_SERVICE_GUIDE.md for troubleshooting help.")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    run_all_tests()
