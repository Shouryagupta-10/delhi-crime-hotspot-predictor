"""
Streamlit Community Cloud & Local Deployment Entrypoint
Delegates execution to app/main.py
"""
import os
import sys
import runpy

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(ROOT_DIR, "app")

for path in [ROOT_DIR, APP_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Auto-start background emergency SOS dispatcher server if available
try:
    from sos_api_server import start_sos_api_server_background
    start_sos_api_server_background(port=4021)
except Exception:
    pass

if __name__ == "__main__":
    target = os.path.join(APP_DIR, "main.py")
    runpy.run_path(target, run_name="__main__")
