import os
import sys
from pathlib import Path

# Add the parent directory to PYTHONPATH so we can import repogather
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root)) 