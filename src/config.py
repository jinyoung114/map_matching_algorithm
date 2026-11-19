from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "input"
OUTPUT_DIR = BASE_DIR / "data" / "output"

GPS_FILE = INPUT_DIR / "충남70자1265_0430_filtered.csv"
NODES_FILE = INPUT_DIR / "mm_nodes_dense_27_33.csv"
EDGES_FILE = INPUT_DIR / "mm_edges_dense_27_33.csv"

OUTPUT_PREFIX = OUTPUT_DIR / "strict_matched"

# candidate search
BASE_RADIUS_M = 10
CURVE_RADIUS_M = 15
BASE_K = 4
CURVE_K = 6
CURVE_THRESHOLD_DEG = 30

# emission
EMIT_SIGMA = 40.0

# gps cleaning
SPEED_THRESHOLD_MPS = 40.0
HEADING_JUMP_DIST_M = 3.0
HEADING_JUMP_THRESHOLD_DEG = 120.0
HAMPEL_WINDOW = 9
HAMPEL_MULT = 4.0
