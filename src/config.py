"""
Configuration settings for the PDF to Email Converter app.
"""
import streamlit as st
from pathlib import Path
from typing import Dict, Any

# Base directory
BASE_DIR = Path(__file__).parent

# Data directory for temporary files
DATA_DIR = BASE_DIR / "data"

def get_secret(key: str, default: str = "") -> str:
    """Get value from st.secrets."""
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    return default

def get_secret_list(key: str, default: list = None) -> list:
    """Get list value from st.secrets."""
    if default is None:
        default = []
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    return default

def get_secret_bool(key: str, default: bool = True) -> bool:
    """Get boolean value from st.secrets."""
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    return default

# Email configuration
EMAIL_CONFIG = {
    "smtp_hosts": {
        "gmail": "smtp.gmail.com",
        "microsoft": "smtp.office365.com",
        "yahoo": "smtp.mail.yahoo.com",
    },
    "smtp_port": 587,
    "sender_email": get_secret("sender_email", ""),
    "sender_password": get_secret("sender_password", ""),
    "sender_type": get_secret("sender_type", "microsoft"),
    "recipient_email": get_secret("recipient_email", ""),
    # Recipient options for dropdown
    "recipient_options": get_secret_list("recipient_options", ["sgoldman@mpmcapital.com"]),
    # Microsoft Graph API configuration
    "microsoft_tenant_id": get_secret("microsoft_tenant_id", ""),
    "microsoft_client_id": get_secret("microsoft_client_id", ""),
    "microsoft_client_secret": get_secret("microsoft_client_secret", ""),
    # Configuration for Microsoft Graph attachment method
    "use_mime_attachments": get_secret_bool("use_mime_attachments", True),
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
        issues["sender_email"] = "sender_email not set in secrets"
    
    if not EMAIL_CONFIG["recipient_email"]:
        issues["recipient_email"] = "recipient_email not set in secrets"
    
    sender_type = EMAIL_CONFIG["sender_type"]
    
    if sender_type == "microsoft_graph":
        # Validate Microsoft Graph API credentials
        if not EMAIL_CONFIG["microsoft_tenant_id"]:
            issues["microsoft_tenant_id"] = "microsoft_tenant_id not set in secrets"
        if not EMAIL_CONFIG["microsoft_client_id"]:
            issues["microsoft_client_id"] = "microsoft_client_id not set in secrets"
        if not EMAIL_CONFIG["microsoft_client_secret"]:
            issues["microsoft_client_secret"] = "microsoft_client_secret not set in secrets"
    elif sender_type in EMAIL_CONFIG["smtp_hosts"]:
        # Validate SMTP credentials
        if not EMAIL_CONFIG["sender_password"]:
            issues["sender_password"] = "sender_password not set in secrets"
    else:
        issues["sender_type"] = f"Invalid sender type: {sender_type}. Options: microsoft, gmail, yahoo, microsoft_graph"
    
    return issues 