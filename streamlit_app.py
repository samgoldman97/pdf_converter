"""
PDF to Email Converter - Streamlit App Entry Point

This is the main entry point for Streamlit Community Cloud deployment.
It imports and runs the main application from src/main.py
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main app
from main import main

if __name__ == "__main__":
    main() 