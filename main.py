import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ariba_mcp.server import mcp

if __name__ == "__main__":
    mcp.run()