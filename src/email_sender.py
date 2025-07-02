"""
Email sending utilities for the PDF converter app.
"""
from datetime import datetime, timedelta
from typing import List
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import streamlit as st
import msal
import requests
import json
import base64

from config import EMAIL_CONFIG


class EmailSender:
    """Handles email composition and sending."""
    
    def __init__(self):
        self.smtp_hosts = EMAIL_CONFIG["smtp_hosts"]
        self.smtp_port = EMAIL_CONFIG["smtp_port"]
        self.sender_email = EMAIL_CONFIG["sender_email"]
        self.sender_password = EMAIL_CONFIG["sender_password"]
        self.sender_type = EMAIL_CONFIG["sender_type"]
        self.recipient_email = EMAIL_CONFIG["recipient_email"]
        # Microsoft Graph API configuration
        self.microsoft_tenant_id = EMAIL_CONFIG["microsoft_tenant_id"]
        self.microsoft_client_id = EMAIL_CONFIG["microsoft_client_id"]
        self.microsoft_client_secret = EMAIL_CONFIG["microsoft_client_secret"]
        # Configuration for Microsoft Graph attachment method
        self.use_mime_attachments = EMAIL_CONFIG.get("use_mime_attachments", True)
    
    def generate_subject(self, topic_type: str, subtopic: str) -> str:
        """Generate email subject with next Friday's date."""
        if topic_type == "":
            date = datetime.now().strftime("%Y-%m-%d")
            topic_type = ""
        elif topic_type in ["Non-Onc", "Onc"]:
            # Get next friday's date
            date = (datetime.now() + timedelta((4 - datetime.now().weekday() + 7) % 7)).strftime("%Y-%m-%d")
        elif topic_type == "No Date":
            date = ""
            topic_type = ""
        else:
            raise ValueError(f"Invalid topic type: {topic_type}")

        str_list = [date, topic_type, subtopic]
        str_list = [s for s in str_list if s]
        return " ".join(str_list)
    
    def create_email_content(self, message_body: str, image_buffers: List[BytesIO]) -> str:
        """Create HTML email content with inline images."""
        html_content = f"<html><body>{message_body}<br><br>"
        
        for i in range(len(image_buffers)):
            html_content += f'<img src="cid:image{i+1}" style="max-width: 100%; height: auto;"><br>'
            html_content += '<hr>'
        
        html_content += "</body></html>"
        return html_content
    
    def compose_email(self, subject: str, message_body: str, image_buffers: List[BytesIO]) -> MIMEMultipart:
        """Compose email with images as attachments or embedded in HTML."""
        if self.sender_type == "microsoft_graph":
            if self.use_mime_attachments:
                # For Microsoft Graph API with MIME attachments, create proper MIME message
                msg = MIMEMultipart()
                msg['From'] = self.sender_email
                msg['To'] = self.recipient_email
                msg['Subject'] = subject
                
                # Create HTML content with CID references
                html_content = self.create_html_with_cid_references(message_body, image_buffers)
                msg.attach(MIMEText(html_content, 'html'))
                
                # Add images as attachments with Content-ID headers
                for i, buffer in enumerate(image_buffers):
                    buffer.seek(0)
                    img_data = buffer.getvalue()
                    image = MIMEImage(img_data, name=f'page{i+1}.png')
                    image.add_header('Content-ID', f'<page{i+1}>')
                    msg.attach(image)
                
                return msg
            else:
                # Fallback to base64 encoding for smaller files
                msg = MIMEMultipart()
                msg['From'] = self.sender_email
                msg['To'] = self.recipient_email
                msg['Subject'] = subject
                
                # Create HTML content with embedded base64 images
                html_content = self.create_html_with_images_microsoft_graph(message_body, image_buffers)
                msg.attach(MIMEText(html_content, 'html'))
                
                return msg
        else:
            # For SMTP, use attachments
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            # Add images as attachments
            for i, buffer in enumerate(image_buffers):
                buffer.seek(0)
                img_data = buffer.getvalue()
                image = MIMEImage(img_data, name=f'image{i+1}.png')
                image.add_header('Content-ID', f'<image{i+1}>')
                msg.attach(image)
            
            # Create and attach HTML content
            html_content = self.create_email_content(message_body, image_buffers)
            msg.attach(MIMEText(html_content, 'html'))
            
            return msg
    
    def send_email(self, msg: MIMEMultipart) -> bool:
        """Send email via SMTP or Microsoft Graph API."""
        if self.sender_type == "microsoft_graph":
            # For Microsoft Graph, we need to pass the original image_buffers
            # Extract them from the MIME message for now
            image_buffers = []
            for part in msg.walk():
                if part.get_content_type().startswith('image/'):
                    buffer = BytesIO(part.get_payload(decode=True))
                    buffer.seek(0)
                    image_buffers.append(buffer)
            
            if self.use_mime_attachments:
                return self.send_email_microsoft_graph_with_attachments(msg, image_buffers)
            else:
                return self.send_email_microsoft_graph_simple(msg)
        else:
            return self.send_email_smtp(msg)
    
    def send_email_smtp(self, msg: MIMEMultipart) -> bool:
        """Send email via SMTP."""
        try:
            smtp_host = self.smtp_hosts[self.sender_type]
            
            with smtplib.SMTP(smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            st.error("Authentication failed. Please check your email credentials.")
            return False
        except smtplib.SMTPException as e:
            st.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            st.error(f"An error occurred while sending email: {e}")
            return False
    
    def send_email_microsoft_graph_with_attachments(self, msg: MIMEMultipart, image_buffers: List[BytesIO]) -> bool:
        """Send email via Microsoft Graph API using inline attachments with sendMail endpoint."""
        try:
            token = self.acquire_microsoft_graph_token()
            
            # Extract subject and body from the MIME message
            subject = msg['Subject']
            
            # Get the HTML content from the message
            html_content = ""
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_content = part.get_payload(decode=True).decode()
                    break
            
            # Prepare attachments for inline use using the original image_buffers
            attachments = []
            for i, buffer in enumerate(image_buffers):
                buffer.seek(0)
                
                attachment = {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": f"page{i+1}.png",
                    "contentType": "image/png",
                    "contentBytes": base64.b64encode(buffer.getvalue()).decode(),
                    "contentId": f"page{i+1}",
                    "isInline": True
                }
                attachments.append(attachment)
            
            payload = {
                "message": {
                    "subject": subject,
                    "body": {"contentType": "HTML", "content": html_content},
                    "toRecipients": [{"emailAddress": {"address": self.recipient_email}}],
                    "attachments": attachments
                },
                "saveToSentItems": "true",
            }

            url = f"https://graph.microsoft.com/v1.0/users/{self.sender_email}/sendMail"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            
            return True
            
        except requests.exceptions.RequestException as e:
            st.error(f"Microsoft Graph API error with attachments: {e}")
            return False
        except Exception as e:
            st.error(f"An error occurred while sending email via Microsoft Graph with attachments: {e}")
            return False
    
    def send_email_microsoft_graph_simple(self, msg: MIMEMultipart) -> bool:
        """Send email via Microsoft Graph API using simple approach (base64 encoded)."""
        try:
            # Extract subject and body from the MIME message
            subject = msg['Subject']
            
            # Get the HTML content from the message
            html_content = ""
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_content = part.get_payload(decode=True).decode()
                    break
            
            payload = {
                "message": {
                    "subject": subject,
                    "body": {"contentType": "HTML", "content": html_content},
                    "toRecipients": [{"emailAddress": {"address": self.recipient_email}}],
                },
                "saveToSentItems": "true",
            }

            url = f"https://graph.microsoft.com/v1.0/users/{self.sender_email}/sendMail"
            headers = {
                "Authorization": f"Bearer {self.acquire_microsoft_graph_token()}",
                "Content-Type": "application/json",
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            
            return True
            
        except requests.exceptions.RequestException as e:
            st.error(f"Microsoft Graph API error: {e}")
            return False
        except Exception as e:
            st.error(f"An error occurred while sending email: {e}")
            return False
    
    def preview_email(self, subject: str, message_body: str, image_buffers: List[BytesIO]) -> None:
        """Display email preview in Streamlit."""
        with st.expander("Preview of Email Content"):
            # Display subject
            st.write(f"**Subject:** {subject}")
            
            # Display message body
            st.write("**Message:**")
            st.write(message_body)
            
            # Display images
            if image_buffers:
                for i, buffer in enumerate(image_buffers):
                    buffer.seek(0)
                    st.image(buffer, caption=f"Image {i+1}", use_column_width=True)
                    if i < len(image_buffers) - 1:
                        st.markdown("---")
    
    def acquire_microsoft_graph_token(self) -> str:
        """Acquire access token for Microsoft Graph API."""
        app = msal.ConfidentialClientApplication(
            self.microsoft_client_id,
            authority=f"https://login.microsoftonline.com/{self.microsoft_tenant_id}",
            client_credential=self.microsoft_client_secret,
        )
        result = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        if "access_token" not in result:
            raise RuntimeError(
                f"Token request failed: {result.get('error')}\n{result.get('error_description')}"
            )
        return result["access_token"]
    
    def create_html_with_cid_references(self, message_body: str, image_buffers: List[BytesIO]) -> str:
        """Create HTML content with CID references for MIME attachments."""
        html_parts = [f"<p>{message_body}</p>"]
        
        for i in range(len(image_buffers)):
            html_parts.append(f'<img src="cid:page{i+1}" style="max-width: 100%; height: auto; margin: 10px 0;" alt="Page {i+1}">')
            
            if i < len(image_buffers) - 1:
                html_parts.append('<hr>')
        
        return "".join(html_parts)
    
    def create_html_with_images_microsoft_graph(self, message_body: str, image_buffers: List[BytesIO]) -> str:
        """Create HTML content with base64 encoded images for Microsoft Graph API."""
        html_parts = [f"<p>{message_body}</p>"]
        
        for i, buffer in enumerate(image_buffers):
            buffer.seek(0)
            img_data = buffer.getvalue()
            img_base64 = base64.b64encode(img_data).decode()
            html_parts.append(f'<img src="data:image/png;base64,{img_base64}" style="max-width: 100%; height: auto; margin: 10px 0;" alt="Page {i+1}">')
            
            if i < len(image_buffers) - 1:
                html_parts.append('<hr>')
        
        return "".join(html_parts)

    # ALTERNATIVE DRAFT APPROACH (COMMENTED OUT)
    # This approach requires Mail.ReadWrite permission in addition to Mail.Send
    # To use this method, you would need to update your Azure AD app registration
    # to include Mail.ReadWrite permission and get admin consent
    """
    def send_email_microsoft_graph_with_draft_attachments(self, msg: MIMEMultipart, token: str) -> bool:
        \"\"\"Send email via Microsoft Graph API using draft messages with MIME attachments.\"\"\"
        try:
            # Step 1: Create a draft message
            draft_payload = {
                "subject": msg['Subject'],
                "toRecipients": [{"emailAddress": {"address": self.recipient_email}}],
                "body": {"contentType": "HTML", "content": "<p>Loading...</p>"}
            }
            
            url = f"https://graph.microsoft.com/v1.0/users/{self.sender_email}/messages"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(draft_payload))
            response.raise_for_status()
            draft = response.json()
            
            # Step 2: Get the HTML content from the MIME message
            html_content = ""
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_content = part.get_payload(decode=True).decode()
                    break
            
            # Step 3: Update the draft with the actual HTML content
            update_payload = {
                "body": {"contentType": "HTML", "content": html_content}
            }
            
            update_url = f"https://graph.microsoft.com/v1.0/users/{self.sender_email}/messages/{draft['id']}"
            response = requests.patch(update_url, headers=headers, data=json.dumps(update_payload))
            response.raise_for_status()
            
            # Step 4: Add attachments to the draft
            for i, part in enumerate(msg.walk()):
                if part.get_content_type().startswith('image/'):
                    buffer = BytesIO(part.get_payload(decode=True))
                    buffer.seek(0)
                    
                    # Upload attachment
                    attachment_payload = {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": f"page{i+1}.png",
                        "contentType": "image/png",
                        "contentBytes": base64.b64encode(buffer.getvalue()).decode(),
                        "contentId": f"page{i+1}"
                    }
                    
                    attachment_url = f"https://graph.microsoft.com/v1.0/users/{self.sender_email}/messages/{draft['id']}/attachments"
                    response = requests.post(attachment_url, headers=headers, data=json.dumps(attachment_payload))
                    response.raise_for_status()
            
            # Step 5: Send the draft
            send_url = f"https://graph.microsoft.com/v1.0/users/{self.sender_email}/messages/{draft['id']}/send"
            response = requests.post(send_url, headers=headers)
            response.raise_for_status()
            
            return True
            
        except requests.exceptions.RequestException as e:
            st.error(f"Microsoft Graph API error with draft attachments: {e}")
            return False
        except Exception as e:
            st.error(f"An error occurred while sending email via Microsoft Graph with draft attachments: {e}")
            return False
    """