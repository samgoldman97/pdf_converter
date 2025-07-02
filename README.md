# PDF Converter

Simple PDF to image converter with email functionality.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Poppler:
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils
```

3. Configure secrets:
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` with your email credentials.

## Usage

```bash
streamlit run streamlit_app.py
```

Upload a PDF, configure settings, and send via email.