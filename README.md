# PDF to Email Converter

A simple Streamlit application that converts PDF files to images and sends them via email with support for multiple email providers including Microsoft Graph API.

## Features

- 📄 Convert PDF files to high-quality images
- 📧 Send images via email with custom message
- 🎨 Automatic image resizing and optimization
- 📅 Automatic subject line generation with next Friday's date
- 🔒 Secure credential management using environment variables
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

3. **Set up environment variables:**
```bash
cp .env.example .env
```

Edit `.env` file with your email credentials:
```bash
SENDER_EMAIL=your-email@domain.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@domain.com
SENDER_TYPE=microsoft  # or gmail, yahoo, microsoft_graph

# For Microsoft Graph API (if SENDER_TYPE=microsoft_graph):
MICROSOFT_TENANT_ID=your-tenant-id
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret

# Optional: Control attachment method for Microsoft Graph API:
USE_MIME_ATTACHMENTS=true  # or false
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

3. **Set up environment variables:**
```bash
cp .env.example .env
```

Edit `.env` file with your email credentials (same as above).

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
streamlit run src/main.py
```

3. **Open your browser** and navigate to the provided URL (usually `http://localhost:8501`)

4. **Configure your email:**
   - Select topic type (Non-ONC, ONC, or No Date)
   - Enter a subtopic
   - Write your message body

5. **Customize image settings:**
   - Select maximum image size (600x600 to 1280x1280)
   - Adjust image quality (10-100)

6. **Upload a PDF file** and wait for conversion

7. **Preview the email** and click "Send Email"

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
- ✅ Temporary file cleanup
- ✅ Error handling and validation
- ✅ Microsoft Graph API token management
- ✅ Secure attachment handling

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

## Troubleshooting

### Common Issues

1. **"Poppler not found" error:**
   - Ensure Poppler is installed and in your PATH
   - On Windows, add Poppler's bin directory to PATH

2. **Email authentication failed:**
   - Check your email credentials
   - Ensure app passwords are used (not regular passwords)
   - Verify SMTP settings for your email provider

3. **Microsoft Graph API errors:**
   - Verify Azure AD app registration is correct
   - Check that Mail.Send permission is granted
   - Ensure admin consent is provided
   - Verify tenant ID, client ID, and client secret

4. **File upload issues:**
   - Check file size (max 50MB)
   - Ensure file is a valid PDF
   - Check file permissions

5. **Image quality issues:**
   - Adjust image size and quality settings in the UI
   - Try different quality levels (10-100)
   - Experiment with different maximum sizes

### Getting Help

If you encounter issues:
1. Check the error messages in the Streamlit interface
2. Verify your environment variables are set correctly
3. Ensure all dependencies are installed
4. Check your email provider's settings
5. For Microsoft Graph API issues, verify Azure AD configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the GitHub repository.
