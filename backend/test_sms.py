#!/usr/bin/env python3
"""
SMS System Test Script
Tests the SMS notification functionality directly from .env file
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Read configuration from .env
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
SMS_RECIPIENTS = os.getenv('SMS_RECIPIENTS', '')
SMS_RISK_THRESHOLD = float(os.getenv('SMS_RISK_THRESHOLD', '75.0'))


def print_status():
    """Print SMS system configuration status"""
    print("\n" + "="*60)
    print("📱 SMS SYSTEM CONFIGURATION STATUS")
    print("="*60)
    
    print(f"\n🔧 Twilio Configuration (from .env):")
    print(f"   Account SID: {'✅ Set' if TWILIO_ACCOUNT_SID else '❌ Not Set'}")
    if TWILIO_ACCOUNT_SID:
        print(f"   Account SID Value: {TWILIO_ACCOUNT_SID[:8]}...{TWILIO_ACCOUNT_SID[-4:] if len(TWILIO_ACCOUNT_SID) > 12 else ''}")
    
    print(f"   Auth Token: {'✅ Set' if TWILIO_AUTH_TOKEN else '❌ Not Set'}")
    if TWILIO_AUTH_TOKEN:
        print(f"   Auth Token Value: {TWILIO_AUTH_TOKEN[:8]}...{TWILIO_AUTH_TOKEN[-4:] if len(TWILIO_AUTH_TOKEN) > 12 else ''}")
    
    print(f"   Phone Number: {TWILIO_PHONE_NUMBER or '❌ Not Set'}")
    
    print(f"\n📋 Recipients:")
    recipients = [r.strip() for r in SMS_RECIPIENTS.split(',') if r.strip()]
    if recipients:
        print(f"   Count: {len(recipients)}")
        for i, recipient in enumerate(recipients, 1):
            print(f"   {i}. {recipient}")
    else:
        print(f"   ❌ No recipients configured")
    
    print(f"\n⚙️ Settings:")
    print(f"   SMS Risk Threshold: {SMS_RISK_THRESHOLD}%")
    print(f"   .env file location: {env_path}")
    
    # Check if fully configured
    is_configured = bool(
        TWILIO_ACCOUNT_SID and
        TWILIO_AUTH_TOKEN and
        TWILIO_PHONE_NUMBER and
        recipients
    )
    
    print(f"\n📊 Overall Status: {'✅ READY' if is_configured else '❌ NOT CONFIGURED'}")
    print("="*60 + "\n")
    
    return is_configured


def send_test_sms():
    """Send a test SMS alert to all configured recipients"""
    print("📱 Sending test SMS alert...\n")
    
    recipients = [r.strip() for r in SMS_RECIPIENTS.split(',') if r.strip()]
    
    if not recipients:
        print("❌ No recipients configured in .env file")
        return
    
    try:
        from twilio.rest import Client
        
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Create test message
        test_message = (
            "🚨 FIRE ALERT: Test Alert\n"
            "Risk: 85% | Temp: 39.2°C | Smoke: 3200\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}\n"
            "ID: TEST-ALERT"
        )
        
        print(f"📤 Sending to {len(recipients)} recipient(s)...\n")
        
        sent_count = 0
        failed_count = 0
        
        for recipient in recipients:
            try:
                message = client.messages.create(
                    body=test_message,
                    from_=TWILIO_PHONE_NUMBER,
                    to=recipient
                )
                
                if message.sid:
                    print(f"✅ SMS sent to {recipient}")
                    print(f"   Message SID: {message.sid}")
                    print(f"   Status: {message.status}\n")
                    sent_count += 1
                else:
                    print(f"⚠️ SMS failed for {recipient}\n")
                    failed_count += 1
                    
            except Exception as recipient_error:
                print(f"❌ Failed to send SMS to {recipient}: {recipient_error}\n")
                failed_count += 1
        
        print(f"\n📊 SMS Alert Summary: {sent_count} sent, {failed_count} failed")
        print(f"✅ Test completed!")
        print(f"   Check your phone for the test message")
        print(f"   Also check Twilio console at: https://console.twilio.com/\n")
    
    except ImportError:
        print("❌ Twilio library not installed!")
        print("   Run: pip install twilio\n")
    except Exception as e:
        print(f"❌ Error sending SMS: {e}\n")
        print("   Possible causes:")
        print("   - Invalid Twilio credentials in .env file")
        print("   - Twilio account issues")
        print("   - Network connectivity problems\n")


def send_single_sms(phone_number: str):
    """Test sending to a single phone number"""
    if not phone_number.startswith('+'):
        print(f"❌ Error: Phone number must start with '+' (country code)")
        print(f"   Example: +919876543210")
        return
    
    print(f"📱 Sending test SMS to: {phone_number}\n")
    
    try:
        from twilio.rest import Client
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body="🔥 TEST: Forest Fire Prevention System is active and monitoring.",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        print(f"✅ SMS Sent Successfully!")
        print(f"   Message SID: {message.sid}")
        print(f"   To: {phone_number}")
        print(f"   Status: {message.status}")
        print(f"   From: {TWILIO_PHONE_NUMBER}\n")
        
    except ImportError:
        print("❌ Twilio library not installed!")
        print("   Run: pip install twilio\n")
    except Exception as e:
        print(f"❌ Error sending SMS: {e}\n")
        print("   Possible causes:")
        print("   - Invalid Twilio credentials in .env file")
        print("   - Invalid phone number format")
        print("   - Unverified number (for trial accounts)")
        print("   - Insufficient Twilio credit\n")


def show_help():
    """Show usage instructions"""
    print("\n" + "="*60)
    print("📱 SMS TEST SCRIPT - USAGE")
    print("="*60)
    print("\nCommands:")
    print("  python test_sms.py status          - Check configuration status")
    print("  python test_sms.py test            - Send test alert to all recipients")
    print("  python test_sms.py send <number>   - Send test to specific number")
    print("  python test_sms.py help            - Show this help message")
    print("\nExamples:")
    print("  python test_sms.py status")
    print("  python test_sms.py send +919876543210")
    print("  python test_sms.py test")
    print("\nConfiguration:")
    print("  All settings are read from backend/.env file")
    print("  Required variables:")
    print("    TWILIO_ACCOUNT_SID")
    print("    TWILIO_AUTH_TOKEN")
    print("    TWILIO_PHONE_NUMBER")
    print("    SMS_RECIPIENTS")
    print("\nPhone Number Format:")
    print("  ✅ Correct: +919876543210")
    print("  ❌ Wrong: 9876543210 (missing country code)")
    print("  ❌ Wrong: +91 9876 543 210 (no spaces)")
    print("\n" + "="*60 + "\n")


def main():
    """Main test function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        print_status()
    
    elif command == "test":
        is_configured = print_status()
        if not is_configured:
            print("❌ Cannot send test: System not fully configured")
            print("   Please set environment variables in .env file\n")
            return
        
        send_test_sms()
    
    elif command == "send":
        if len(sys.argv) < 3:
            print("❌ Error: Phone number required")
            print("   Usage: python test_sms.py send +919876543210\n")
            return
        
        is_configured = print_status()
        if not is_configured:
            print("❌ Cannot send: Twilio not configured")
            print("   Please set TWILIO_* environment variables in .env file\n")
            return
        
        phone_number = sys.argv[2]
        send_single_sms(phone_number)
    
    elif command == "help":
        show_help()
    
    else:
        print(f"❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
