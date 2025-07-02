"""
Configuration settings for the PDF to Email Converter app.
"""
import os
from pathlib import Path
from typing import Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# Base directory
BASE_DIR = Path(__file__).parent

# Data directory for temporary files
DATA_DIR = BASE_DIR / "data"

# Email configuration
EMAIL_CONFIG = {
    "smtp_hosts": {
        "gmail": "smtp.gmail.com",
        "microsoft": "smtp.office365.com",
        "yahoo": "smtp.mail.yahoo.com",
    },
    "smtp_port": 587,
    "sender_email": os.getenv("SENDER_EMAIL", ""),
    "sender_password": os.getenv("SENDER_PASSWORD", ""),
    "sender_type": os.getenv("SENDER_TYPE", "microsoft"),
    "recipient_email": os.getenv("RECIPIENT_EMAIL", ""),
    # Microsoft Graph API configuration
    "microsoft_tenant_id": os.getenv("MICROSOFT_TENANT_ID", ""),
    "microsoft_client_id": os.getenv("MICROSOFT_CLIENT_ID", ""),
    "microsoft_client_secret": os.getenv("MICROSOFT_CLIENT_SECRET", ""),
    # Configuration for Microsoft Graph attachment method
    "use_mime_attachments": os.getenv("USE_MIME_ATTACHMENTS", "true").lower() == "true",
}

# App configuration
APP_CONFIG = {
    "title": "PDF to Email Converter",
    "description": "Convert PDF files to images and send via email",
    "supported_file_types": [".pdf"],
    "max_image_size": (600, 600),
    "image_quality": 75,
    "image_format": "PNG",
}

# Validation
def validate_config() -> Dict[str, Any]:
    """Validate configuration and return any issues."""
    issues = {}
    
    if not EMAIL_CONFIG["sender_email"]:
        issues["sender_email"] = "SENDER_EMAIL environment variable not set"
    
    if not EMAIL_CONFIG["recipient_email"]:
        issues["recipient_email"] = "RECIPIENT_EMAIL environment variable not set"
    
    sender_type = EMAIL_CONFIG["sender_type"]
    
    if sender_type == "microsoft_graph":
        # Validate Microsoft Graph API credentials
        if not EMAIL_CONFIG["microsoft_tenant_id"]:
            issues["microsoft_tenant_id"] = "MICROSOFT_TENANT_ID environment variable not set"
        if not EMAIL_CONFIG["microsoft_client_id"]:
            issues["microsoft_client_id"] = "MICROSOFT_CLIENT_ID environment variable not set"
        if not EMAIL_CONFIG["microsoft_client_secret"]:
            issues["microsoft_client_secret"] = "MICROSOFT_CLIENT_SECRET environment variable not set"
    elif sender_type in EMAIL_CONFIG["smtp_hosts"]:
        # Validate SMTP credentials
        if not EMAIL_CONFIG["sender_password"]:
            issues["sender_password"] = "SENDER_PASSWORD environment variable not set"
    else:
        issues["sender_type"] = f"Invalid sender type: {sender_type}. Options: microsoft, gmail, yahoo, microsoft_graph"
    
    return issues 