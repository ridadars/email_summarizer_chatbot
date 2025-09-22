#!/usr/bin/env python3
"""
Launcher script for Gmail Q&A Chatbot Web App
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Gmail Q&A Chatbot Web App...")
    print("=" * 50)
    
    # Change to the project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run Streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/streamlit_app.py", 
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down web app...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running web app: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
