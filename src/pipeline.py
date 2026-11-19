from .config import GPS_FILE, NODES_FILE, EDGES_FILE, OUTPUT_PREFIX
from .gps_processing import load_and_clean_gps
from .road_network import normalize_nodes, build_graph
from .utils import read_csv_any
from .viterbi import run_viterbi_strict
from .outputs import save_outputs


def run_pipeline(gps_path=GPS_FILE, nodes_path=NODES_FILE, edges_path=EDGES_FILE, output_prefix=OUTPUT_PREFIX):
    clean = load_and_clean_gps(gps_path)
    nodes_df = normalize_nodes(read_csv_any(nodes_path))
    edges_df = read_csv_any(edges_path)
    G, edge_geom = build_graph(nodes_df, edges_df)
    gps2, path_list = run_viterbi_strict(clean, nodes_df, G)
    return save_outputs(str(output_prefix), gps2, path_list, G, edge_geom)
