"""
PDF to Email Converter - Streamlit App

A simple application to convert PDF files to images and send them via email.
Run with: streamlit run src/main.py
"""

import streamlit as st
from pathlib import Path
import sys
import os

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_CONFIG, validate_config, EMAIL_CONFIG
from pdf_converter import PDFConverter
from email_sender import EmailSender


def setup_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title=APP_CONFIG["title"],
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def authenticate_user():
    """Authenticate user using Streamlit's built-in authentication."""
    # Check if user is already authenticated
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Authentication Required")
        st.markdown("Please log in to access the PDF to Email Converter.")
        
        # Create login form
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                # Check credentials against secrets
                if username in st.secrets["passwords"] and st.secrets["passwords"][username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        st.stop()
    
    # Show logout button in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"**Logged in as:** {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()


def show_header():
    """Display app header and description."""
    st.title(APP_CONFIG["title"])
    st.markdown(APP_CONFIG["description"])
    st.markdown("---")


def validate_environment():
    """Validate environment configuration and show errors if any."""
    config_issues = validate_config()
    
    if config_issues:
        st.error("Configuration Issues Found:")
        for issue, message in config_issues.items():
            st.error(f"• {issue}: {message}")
        st.info("Please set the required environment variables:")
        st.code("""
export SENDER_EMAIL="your-email@domain.com"
export SENDER_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="recipient@domain.com"
export SENDER_TYPE="microsoft"  # or "gmail", "yahoo", "microsoft_graph"

# For Microsoft Graph API (if SENDER_TYPE=microsoft_graph):
export MICROSOFT_TENANT_ID="your-tenant-id"
export MICROSOFT_CLIENT_ID="your-client-id"
export MICROSOFT_CLIENT_SECRET="your-client-secret"

# Optional: Control attachment method for Microsoft Graph API:
export USE_MIME_ATTACHMENTS="true"  # or "false"
        """)
        st.stop()
    
    # Show current sender type
    sender_type = EMAIL_CONFIG["sender_type"]
    if sender_type == "microsoft_graph":
        attachment_method = "Inline attachments" if EMAIL_CONFIG["use_mime_attachments"] else "Base64 encoding"
        st.info(f"📧 Using Microsoft Graph API for email sending ({attachment_method})")
    else:
        st.info(f"📧 Using {sender_type.upper()} SMTP for email sending")


def create_email_form():
    """Create the email composition form."""
    st.subheader("Email Configuration")
    
    # Recipient email dropdown - get options from config
    recipient_options = EMAIL_CONFIG["recipient_options"]
    
    # Add the default recipient from config if it's not already in the list
    default_recipient = EMAIL_CONFIG["recipient_email"]
    if default_recipient and default_recipient not in recipient_options:
        recipient_options.append(default_recipient)
    
    recipient_email = st.selectbox(
        "Select recipient email",
        recipient_options,
        help="Choose the recipient for the email"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        topic_type = st.selectbox(
            "Select topic type",
            ["", "Non-Onc", "Onc", "No Date"],
            help="Choose the topic type for the email subject"
        )
    
    with col2:
        subtopic = st.text_input(
            "Enter subtopic",
            help="Add a subtopic to the email subject"
        )
    
    message_body = st.text_area(
        "Enter the message body",
        placeholder="Type your email message here...",
        help="The main content of your email"
    )
    
    return topic_type, subtopic, message_body, recipient_email


def handle_file_upload():
    """Handle file upload and conversion."""
    st.subheader("File Upload")
    
    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=["pdf"],
        help="Select a PDF file to convert to images"
    )
    
    max_size = APP_CONFIG["max_image_size"]
    quality = APP_CONFIG["image_quality"]
    col1, col2 = st.columns(2)
    tuple_compare = lambda x, y: x[0] == y[0] and x[1] == y[1]
    size_choices = [(600, 600),(800, 800), (1024, 1024), (1280, 1280)]
    
    with col1:
        max_size = st.selectbox(
            "Select maximum image size",
            size_choices,
            index=[i for i in range(len(max_size)) if tuple_compare(size_choices[i], max_size)][0],
            help="Choose the maximum size for the converted images"
        )
    
    with col2:
        quality = st.slider(
            "Select image quality",
            min_value=10,
            max_value=100,
            value=quality,
            step=5,
            help="Adjust the quality of the converted images"
        )

    if uploaded_file is not None:
        converter = PDFConverter(quality=quality, max_size= max_size)
        
        # Validate file
        is_valid, error_message = converter.validate_file(uploaded_file)
        if not is_valid:
            st.error(error_message)
            return None
        
        # Convert PDF to images
        with st.spinner("Converting PDF to images..."):
            try:
                image_buffers = converter.convert_pdf_to_images(uploaded_file)
                st.success(f"Successfully converted {len(image_buffers)} pages")
                
                # Display images
                #converter.display_images(image_buffers)
                
                return image_buffers
                
            except Exception as e:
                st.error(f"Error converting PDF: {e}")
                return None
    
    return None


def main():
    """Main application function."""
    setup_page()
    authenticate_user()
    show_header()
    validate_environment()
    
    # Create email form
    topic_type, subtopic, message_body, recipient_email = create_email_form()
    email_sender = EmailSender(recipient_email)
    subject = email_sender.generate_subject(topic_type, subtopic)

    # Display subject
    st.info(f"**Subject:** {subject}")
    
    # Handle file upload
    image_buffers = handle_file_upload()
    
    # Send email button
    if image_buffers:
        col1, col2 = st.columns([6, 1])
        
        with col1:
            st.subheader("Send Email")
        
        with col2:
            # Send button
            send_button = st.button("Send Email", type="primary", help="Click to send the email", key="send_email_button", 
                         use_container_width=True)
            if send_button:
                with st.spinner("Sending email..."):
                    msg = email_sender.compose_email(subject, message_body, image_buffers)
                    
        # Start of Selection
        if send_button and email_sender.send_email(msg):
            st.success("✅ Email sent successfully!")
        elif send_button:
            st.error("❌ Failed to send email. Please check the error messages above.")
        else:
            pass
        
        # Generate subject
        email_sender = EmailSender(recipient_email)
        subject = email_sender.generate_subject(topic_type, subtopic)
        
        # Preview email
        email_sender.preview_email(subject, message_body, image_buffers)
    
    elif image_buffers and (not message_body or not subtopic):
        st.warning("Please fill in the message body and subtopic to send an email.")
    
    # Footer
    st.markdown("---")


if __name__ == "__main__":
    main()
