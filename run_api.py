"""
SUVI Assistant FastAPI Server Runner
Runs the FastAPI backend connected to the JARVIS unified engine.
"""
import sys
from pathlib import Path
import uvicorn

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if __name__ == "__main__":
    print("=" * 60)
    print("      STARTING SUVI UNIFIED API SERVER (PORT 8000)")
    print("=" * 60)
    print("Health check: http://127.0.0.1:8000/health")
    print("API docs:     http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False)
