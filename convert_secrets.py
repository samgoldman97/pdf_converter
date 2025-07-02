#!/usr/bin/env python3
"""
Convert .streamlit/secrets.toml to Railway environment variables
Run this script to generate the environment variables for Railway deployment
"""

import toml
import json
from pathlib import Path

def convert_secrets_to_env():
    """Convert secrets.toml to Railway environment variables format."""
    
    # Read the secrets file
    secrets_path = Path(".streamlit/secrets.toml")
    
    if not secrets_path.exists():
        print("❌ .streamlit/secrets.toml not found!")
        return
    
    try:
        with open(secrets_path, 'r') as f:
            secrets = toml.load(f)
    except Exception as e:
        print(f"❌ Error reading secrets.toml: {e}")
        return
    
    print("🔧 Converting secrets.toml to Railway environment variables...")
    print("=" * 60)
    
    # Convert to Railway format
    env_vars = {}
    
    # Handle passwords section (nested structure - needs STREAMLIT_PASSWORDS_ prefix)
    if 'passwords' in secrets:
        for username, password in secrets['passwords'].items():
            env_key = f"STREAMLIT_PASSWORDS_{username.upper()}"
            env_vars[env_key] = password
            print(f"{env_key}={password}")
    
    # Handle all other keys (direct mapping - no prefix needed)
    for key, value in secrets.items():
        # Skip the passwords section since we already handled it
        if key == 'passwords':
            continue
            
        # Convert lists to JSON strings
        if isinstance(value, list):
            value = json.dumps(value)
        # Convert booleans to strings
        elif isinstance(value, bool):
            value = str(value).lower()
        
        env_key = key.upper()
        env_vars[env_key] = value
        print(f"{env_key}={value}")
    
    print("=" * 60)
    print("✅ Conversion complete!")
    print("\n📋 Copy these environment variables to Railway:")
    print("- Go to your Railway project")
    print("- Click on your service")
    print("- Go to 'Variables' tab")
    print("- Add each variable above")
    
    # Save to file for easy copying
    output_file = "railway_env_vars.txt"
    with open(output_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"\n💾 Environment variables also saved to: {output_file}")
    print("You can copy-paste from this file into Railway!")
    
    # Also show the exact format for Railway
    print("\n🚀 For Railway Variables tab, use this format:")
    print("- Key: STREAMLIT_PASSWORDS_ADMIN")
    print("- Value: [your-admin-password]")
    print("- Key: SENDER_EMAIL")
    print("- Value: [your-sender-email]")
    print("(etc...)")

if __name__ == "__main__":
    convert_secrets_to_env() 