"""Launcher script to avoid sys.path conflicts with Hermes agent."""
import sys
import os

# Ensure backend dir is first in path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir in sys.path:
    sys.path.remove(backend_dir)
sys.path.insert(0, backend_dir)

# Remove any hermes paths that could shadow our utils
sys.path = [p for p in sys.path if '/home/huayue/.hermes/hermes-agent' not in p]

# Add site-packages back (last)
import site
for p in site.getsitepackages():
    if p not in sys.path:
        sys.path.append(p)

import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
