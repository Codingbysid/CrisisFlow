import os
from twilio.rest import Client
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials (set in .env)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


def get_twilio_client() -> Optional[Client]:
    """Get authenticated Twilio client"""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN]):
        return None
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        return client
    except Exception as e:
        print(f"Error creating Twilio client: {e}")
        return None


def send_sms(to: str, message: str) -> bool:
    """
    Send SMS message via Twilio
    
    Args:
        to: Recipient phone number (E.164 format, e.g., +1234567890)
        message: Message text
        
    Returns:
        True if sent successfully, False otherwise
    """
    client = get_twilio_client()
    if not client or not TWILIO_PHONE_NUMBER:
        print("Twilio not configured")
        return False
    
    try:
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to
        )
        print(f"SMS sent to {to}: {message.sid}")
        return True
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False


def receive_sms_webhook(request_data: dict) -> dict:
    """
    Process incoming SMS webhook from Twilio
    
    Args:
        request_data: Webhook data from Twilio
        
    Returns:
        Dictionary with extracted report data
    """
    # Extract SMS data
    from_number = request_data.get("From", "")
    message_body = request_data.get("Body", "")
    
    return {
        "raw_text": message_body,
        "source": "sms",
        "phone_number": from_number,
        "timestamp": request_data.get("DateSent", "")
    }

