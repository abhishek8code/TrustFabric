import uvicorn
import sys
from pathlib import Path

# Add project root directory to python path
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

if __name__ == "__main__":
    print("Starting TrustFabric backend uvicorn...")
    sys.stdout.flush()
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, log_level="info")
