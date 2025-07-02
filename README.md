# PDF to Email Converter

A simple Streamlit application that converts PDF files to images and sends them via email with support for multiple email providers including Microsoft Graph API.

## Features

- 📄 Convert PDF files to high-quality images
- 📧 Send images via email with custom message
- 🎨 Automatic image resizing and optimization
- 📅 Automatic subject line generation with next Friday's date
- 🔒 Secure credential management using Streamlit secrets
- 📱 Responsive web interface
- ☁️ **Microsoft Graph API support** with inline attachments
- 🔧 **Configurable image quality and size** via UI controls
- 📎 **Multiple attachment methods** for optimal file handling

## Prerequisites

- Python 3.9 or higher
- Poppler (for PDF processing)
- Email account with SMTP access or Microsoft Graph API credentials

### Installing Poppler

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/)

## Installation

### Option 1: Using pip (Recommended for deployment)

1. **Clone the repository:**
```bash
git clone <repository-url>
cd pdf_converter
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up configuration:**
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` file with your credentials:
```toml
[passwords]
admin = "your-secure-password-here"
cbardon = "another-secure-password"

# Email Configuration
sender_email = "your-email@domain.com"
recipient_email = "recipient@domain.com"
recipient_options = ["recipient1@domain.com", "recipient2@domain.com", "recipient3@domain.com"]
sender_type = "microsoft_graph"  # Options: microsoft, gmail, yahoo, microsoft_graph

# Required if SENDER_TYPE=microsoft_graph
microsoft_tenant_id = "your-tenant-id"
microsoft_client_id = "your-client-id"
microsoft_client_secret = "your-client-secret"
use_mime_attachments = false

# Required if SENDER_TYPE in [microsoft, gmail, yahoo]
# sender_password = "your-app-password"
```

### Option 2: Using conda (Recommended for local development)

1. **Clone the repository:**
```bash
git clone <repository-url>
cd pdf_converter
```

2. **Create conda environment:**
```bash
conda env create -f environment.yml
conda activate pdf_email_app
```

3. **Set up configuration:**
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` file with your credentials (same as above).

## Deployment

### Streamlit Community Cloud Deployment

This app is configured for easy deployment to Streamlit Community Cloud.

#### 1. Prepare Your Repository

- ✅ Ensure `streamlit_app.py` exists in the root directory (entry point)
- ✅ Verify `requirements.txt` contains all dependencies
- ✅ Check that `packages.txt` includes system dependencies (Poppler)
- ✅ Commit the template file `.streamlit/secrets.toml.template`

#### 2. Deploy to Streamlit Community Cloud

1. **Push your code to GitHub:**
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

2. **Go to [Streamlit Community Cloud](https://share.streamlit.io/)**

3. **Connect your repository:**
   - Click "New app"
   - Connect your GitHub account
   - Select your repository
   - Set the main file path to: `streamlit_app.py`

4. **Configure secrets:**
   - In your app settings, go to "Secrets"
   - Add the contents of your `.streamlit/secrets.toml` file
   - **Never commit the actual secrets file to GitHub!**

#### 3. Secrets Configuration for Streamlit Cloud

Add this to your Streamlit Cloud secrets (in the web interface):

```toml
[passwords]
admin = "your-actual-secure-password"
cbardon = "your-actual-secure-password"

# Email Configuration
sender_email = "your-actual-email@domain.com"
recipient_email = "your-actual-recipient@domain.com"
recipient_options = ["actual1@domain.com", "actual2@domain.com", "actual3@domain.com"]
sender_type = "microsoft_graph"

# Microsoft Graph API (if using)
microsoft_tenant_id = "your-actual-tenant-id"
microsoft_client_id = "your-actual-client-id"
microsoft_client_secret = "your-actual-client-secret"
use_mime_attachments = false

# SMTP Password (if using SMTP)
# sender_password = "your-actual-app-password"
```

#### 4. Deployment Files

The following files are used for deployment:

- **`streamlit_app.py`** - Main entry point for Streamlit Cloud
- **`requirements.txt`** - Python dependencies
- **`packages.txt`** - System dependencies (Poppler)
- **`.streamlit/config.toml`** - Streamlit configuration
- **`.streamlit/secrets.toml.template`** - Template for secrets (committed)

#### 5. Security Best Practices for Deployment

- ✅ **Never commit** `.streamlit/secrets.toml` to GitHub
- ✅ Use strong, unique passwords for authentication
- ✅ Store all sensitive credentials in Streamlit Cloud secrets
- ✅ Regularly rotate passwords and API keys
- ✅ Use environment-specific configurations

## Dependency Management

This project includes multiple dependency files for different use cases:

- **`requirements.txt`** - For pip installation (used by Streamlit Cloud)
- **`packages.txt`** - System dependencies for Streamlit Cloud (installs Poppler)
- **`environment.yml`** - For conda installation (includes Poppler automatically)

**For local development:** Use `environment.yml` with conda for easier setup
**For deployment:** Streamlit Cloud uses `requirements.txt` + `packages.txt`

## Usage

1. **Activate the conda environment (if using conda):**
```bash
conda activate pdf_email_app
```

2. **Run the application:**
```bash
streamlit run streamlit_app.py
```

3. **Open your browser** and navigate to the provided URL (usually `http://localhost:8501`)

4. **Login with your credentials** (configured in secrets)

5. **Configure your email:**
   - Select topic type (Non-ONC, ONC, or No Date)
   - Enter a subtopic
   - Write your message body

6. **Customize image settings:**
   - Select maximum image size (600x600 to 1280x1280)
   - Adjust image quality (10-100)

7. **Upload a PDF file** and wait for conversion

8. **Preview the email** and click "Send Email"

## Email Provider Setup

### Microsoft Graph API (Recommended)
- **Best for large files** and enterprise environments
- **Inline attachments** for better email client compatibility
- **No additional permissions** required beyond Mail.Send
- Set `SENDER_TYPE=microsoft_graph`
- Configure Azure AD app registration with Mail.Send permission

### Microsoft 365 (SMTP)
- Use your Microsoft 365 email address
- Generate an app password in your Microsoft account settings
- Set `SENDER_TYPE=microsoft`

### Gmail
- Use your Gmail address
- Enable 2-factor authentication
- Generate an app password
- Set `SENDER_TYPE=gmail`

### Yahoo
- Use your Yahoo email address
- Generate an app password
- Set `SENDER_TYPE=yahoo`

## Microsoft Graph API Configuration

### Azure AD App Registration

1. **Create an app registration** in Azure AD
2. **Add API permissions:**
   - Microsoft Graph → Application permissions → Mail.Send
3. **Grant admin consent** for the permissions
4. **Create a client secret** and note the values:
   - Tenant ID
   - Client ID
   - Client Secret

### Environment Variables

```bash
SENDER_TYPE=microsoft_graph
MICROSOFT_TENANT_ID=your-tenant-id
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret
USE_MIME_ATTACHMENTS=true  # Use inline attachments (recommended)
```

### Attachment Methods

The app supports two methods for Microsoft Graph API:

1. **Inline Attachments (Default)** - Uses `/sendMail` with proper MIME attachments
   - Better for large files
   - Standard email format
   - No additional permissions needed

2. **Base64 Encoding** - Embeds images directly in HTML
   - Simpler implementation
   - Works well for small files
   - Set `USE_MIME_ATTACHMENTS=false` to use this method

## Security Features

- ✅ Credentials stored in environment variables
- ✅ No hardcoded passwords in source code
- ✅ File size limits (50MB max)
- ✅ File type validation
- ✅ **User authentication** with secure login system

## Authentication Setup

The app now includes built-in authentication to protect access to the PDF converter.

### 1. Configure Users

Edit `.streamlit/secrets.toml` and add your users:
```toml
[passwords]
admin = "your-secure-password-here"
user1 = "another-secure-password"
user2 = "third-secure-password"
```

**Note:** Use strong, unique passwords. You can generate secure passwords using:
```bash
openssl rand -base64 32
```

### 2. Security Best Practices

- ✅ **Never commit** `.streamlit/secrets.toml` to version control
- ✅ Use strong, unique passwords for each user
- ✅ Regularly rotate passwords
- ✅ Limit access to authorized users only
- ✅ Monitor login attempts

### 3. Streamlit Cloud Deployment

When deploying to Streamlit Cloud:

1. **Add secrets** in the Streamlit Cloud dashboard:
   - Go to your app settings
   - Navigate to "Secrets"
   - Add the contents of your `secrets.toml` file

2. **Example secrets configuration:**
```toml
[passwords]
admin = "your-secure-password"
user1 = "another-secure-password"
```

### 4. Authentication Features

- 🔐 **Secure login** with username/password
- 👤 **Session management** - users stay logged in
- 🚪 **Logout functionality** in sidebar
- ⚠️ **Access control** - unauthenticated users cannot access the app
- 🔄 **Automatic redirect** to login page

## Project Structure

```
pdf_converter/
├── src/                  # Source code package
│   ├── __init__.py      # Package initialization
│   ├── main.py          # Main Streamlit application
│   ├── config.py        # Configuration and settings
│   ├── pdf_converter.py # PDF processing utilities
│   └── email_sender.py  # Email composition and sending
├── tests/               # Test files
│   ├── __init__.py      # Test package initialization
│   └── test_structure.py # Structure validation tests
├── requirements.txt     # Python dependencies (pip)
├── packages.txt         # System dependencies (Streamlit Cloud)
├── environment.yml      # Conda environment (local development)
├── .env.example         # Environment variables template
├── README.md           # This file
├── scratch/            # Development/experimental files (git ignored)
└── .streamlit/         # Streamlit configuration
```

## Configuration

The application can be customized by modifying `config.py`:

- **Image settings**: Size, quality, format
- **File limits**: Maximum file size, supported types
- **Email settings**: SMTP hosts, ports, Microsoft Graph API settings