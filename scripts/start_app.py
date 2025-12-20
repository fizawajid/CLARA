"""
Unified Startup Script for CLARA NLP
Starts both FastAPI backend and Streamlit UI
"""

import subprocess
import sys
import time
import os
import signal
import httpx
from pathlib import Path


def check_api_health(base_url: str = "http://localhost:8000", max_attempts: int = 30) -> bool:
    """
    Check if API is responsive by polling the /health endpoint

    Args:
        base_url: Base URL of the API
        max_attempts: Maximum number of attempts

    Returns:
        True if API is healthy, False otherwise
    """
    print(f"\nWaiting for API to be ready at {base_url}...")

    for attempt in range(max_attempts):
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{base_url}/health")
                if response.status_code == 200:
                    print(f"API is ready! ({attempt + 1} attempts)")
                    return True
        except:
            pass

        print(f"  Attempt {attempt + 1}/{max_attempts}...", end='\r')
        time.sleep(2)

    print(f"\nFailed to connect to API after {max_attempts} attempts")
    return False


def find_project_root() -> Path:
    """
    Find the project root directory (CLARA folder)

    Returns:
        Path to project root
    """
    current = Path(__file__).resolve()

    # Navigate up from scripts/ to CLARA/
    if current.parent.name == "scripts":
        return current.parent.parent
    else:
        # Fallback: search upwards for key files
        for parent in current.parents:
            if (parent / "src" / "api" / "main.py").exists():
                return parent

    raise FileNotFoundError("Could not find project root directory")


def main():
    """
    Main startup function
    """
    print("=" * 60)
    print(" CLARA NLP - Multi-Agent Feedback Analysis System")
    print("=" * 60)

    # Find project root
    try:
        project_root = find_project_root()
        print(f"\nProject root: {project_root}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Change to project root directory
    os.chdir(project_root)

    # Determine Python executable path
    if sys.platform == "win32":
        # Windows - check for .venv
        venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    else:
        # Linux/Mac
        venv_python = project_root / ".venv" / "bin" / "python"

    if venv_python.exists():
        python_exe = str(venv_python)
        print(f"Using virtual environment: {python_exe}")
    else:
        python_exe = sys.executable
        print(f"Using system Python: {python_exe}")

    # Start FastAPI backend
    print("\n" + "-" * 60)
    print("Starting FastAPI Backend...")
    print("-" * 60)

    api_process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=project_root
    )


    # Wait for API to be ready
    if not check_api_health():
        print("\nError: API failed to start properly")
        api_process.terminate()
        sys.exit(1)

    # Start Streamlit UI
    print("\n" + "-" * 60)
    print("Starting Streamlit UI...")
    print("-" * 60)

    streamlit_app_path = project_root / "src" / "ui" / "app.py"

    if not streamlit_app_path.exists():
        print(f"Error: Streamlit app not found at {streamlit_app_path}")
        api_process.terminate()
        sys.exit(1)

    ui_process = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", str(streamlit_app_path), "--server.headless", "true"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("\n" + "=" * 60)
    print(" CLARA NLP is now running!")
    print("=" * 60)
    print("\n  API Backend:     http://localhost:8000")
    print("  API Docs:        http://localhost:8000/docs")
    print("  Streamlit UI:    http://localhost:8501")
    print("\n  Press Ctrl+C to stop both services")
    print("=" * 60 + "\n")

    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\n\nShutting down CLARA NLP...")
        print("  Stopping Streamlit UI...")
        ui_process.terminate()
        print("  Stopping FastAPI Backend...")
        api_process.terminate()

        # Wait for processes to terminate
        ui_process.wait(timeout=5)
        api_process.wait(timeout=5)

        print("  All services stopped successfully!")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Keep the script running
    try:
        api_process.wait()
        ui_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
