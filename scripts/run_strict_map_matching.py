from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.pipeline import run_pipeline


if __name__ == "__main__":
    outputs = run_pipeline()
    print("DONE")
    print(outputs)
