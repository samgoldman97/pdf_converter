#!/usr/bin/env python3
"""
Test script to verify the new src structure works correctly.

This script tests that:
1. All required files exist in the correct locations
2. All modules can be imported successfully (both as package and direct imports)
3. Configuration objects have expected attributes

Run from the project root directory:
    conda activate pdf_email_app
    python tests/test_structure.py
"""

import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_package_imports():
    """Test that all modules can be imported as a package."""
    try:
        # Test importing the package
        from src import main, config, pdf_converter, email_sender
        print("✅ All src modules imported as package successfully!")
        
        # Test that config has expected attributes
        assert hasattr(config, 'APP_CONFIG'), "APP_CONFIG not found in config"
        assert hasattr(config, 'EMAIL_CONFIG'), "EMAIL_CONFIG not found in config"
        print("✅ Config module has expected attributes!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Package import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_direct_imports():
    """Test that modules can be imported directly (for Streamlit compatibility)."""
    try:
        # Add src to path and test direct imports
        src_path = os.path.join(project_root, 'src')
        sys.path.insert(0, src_path)
        
        from config import APP_CONFIG, EMAIL_CONFIG
        from pdf_converter import PDFConverter
        from email_sender import EmailSender
        from main import main
        
        print("✅ All src modules imported directly successfully!")
        
        # Test that config has expected keys
        assert 'title' in APP_CONFIG, "APP_CONFIG['title'] not found"
        assert 'sender_type' in EMAIL_CONFIG, "EMAIL_CONFIG['sender_type'] not found"
        print("✅ Direct imports have expected keys!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Direct import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_structure():
    """Test that the directory structure is correct."""
    expected_files = [
        'src/__init__.py',
        'src/main.py',
        'src/config.py',
        'src/pdf_converter.py',
        'src/email_sender.py'
    ]
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

if __name__ == "__main__":
    print("Testing PDF Converter project structure...")
    print("=" * 50)
    
    structure_ok = test_structure()
    package_imports_ok = test_package_imports()
    direct_imports_ok = test_direct_imports()
    
    print("=" * 50)
    if structure_ok and package_imports_ok and direct_imports_ok:
        print("🎉 All tests passed! The project structure is working correctly.")
        print("\nTo run the application:")
        print("  conda activate pdf_email_app")
        print("  streamlit run src/main.py")
    else:
        print("❌ Some tests failed. Please check the structure.") 