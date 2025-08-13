import subprocess
import sys
import config

def run_streamlit():
    port = getattr(config, 'STREAMLIT_PORT', 8501)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py", 
            "--server.port", str(port),
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\nStreamlit server stopped")

if __name__ == "__main__":
    run_streamlit()