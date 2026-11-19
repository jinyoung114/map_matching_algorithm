import networkx as nx
import pandas as pd
from geopy.distance import geodesic
from shapely import wkt


def normalize_nodes(nodes: pd.DataFrame) -> pd.DataFrame:
    nid_col = next((c for c in nodes.columns if c.lower() in ["node_id", "id", "idx", "node"]), None) or "Node_ID"
    if nid_col not in nodes.columns and "Node_ID" in nodes.columns:
        nid_col = "Node_ID"
    nlat_col = next((c for c in nodes.columns if c.lower() in ["lat", "latitude", "y"]), None) or "Latitude"
    nlon_col = next((c for c in nodes.columns if c.lower() in ["lon", "longitude", "x", "lng"]), None) or "Longitude"

    out = nodes.rename(columns={nid_col: "Node_ID", nlat_col: "Latitude", nlon_col: "Longitude"})[
        ["Node_ID", "Latitude", "Longitude"]
    ].copy()
    out["Node_ID"] = out["Node_ID"].astype(int)
    out["Latitude"] = pd.to_numeric(out["Latitude"], errors="coerce")
    out["Longitude"] = pd.to_numeric(out["Longitude"], errors="coerce")
    return out


def build_graph(nodes_df: pd.DataFrame, edges_df: pd.DataFrame):
    G = nx.DiGraph()
    for _, r in nodes_df.iterrows():
        G.add_node(int(r["Node_ID"]), lat=float(r["Latitude"]), lon=float(r["Longitude"]))

    from_col = next((c for c in edges_df.columns if c.lower() in ["from", "u", "src", "source"]), None)
    to_col = next((c for c in edges_df.columns if c.lower() in ["to", "v", "dst", "target"]), None)
    geom_col = next((c for c in edges_df.columns if c.lower() in ["geometry", "wkt", "geom"]), None)

    if not from_col or not to_col:
        raise RuntimeError("엣지 CSV에 from/to(u/v) 컬럼이 필요합니다.")

    def edge_len(row):
        if geom_col and isinstance(row[geom_col], str):
            try:
                line = wkt.loads(row[geom_col])
                cs = list(line.coords)
                if len(cs) < 2:
                    return 1.0
                total = 0.0
                for i in range(len(cs) - 1):
                    lon1, lat1 = cs[i]
                    lon2, lat2 = cs[i + 1]
                    total += geodesic((lat1, lon1), (lat2, lon2)).meters
                return total
            except Exception:
                pass
        u, v = int(row[from_col]), int(row[to_col])
        if u in G.nodes and v in G.nodes:
            a = (G.nodes[u]["lat"], G.nodes[u]["lon"])
            b = (G.nodes[v]["lat"], G.nodes[v]["lon"])
            return geodesic(a, b).meters
        return 1.0

    edges_df = edges_df.copy()
    edges_df["_len"] = edges_df.apply(edge_len, axis=1)
    edge_geom = {}

    if geom_col and geom_col in edges_df.columns:
        for _, r in edges_df.iterrows():
            u = int(r[from_col])
            v = int(r[to_col])
            if isinstance(r[geom_col], str):
                try:
                    edge_geom[(u, v)] = wkt.loads(r[geom_col])
                except Exception:
                    pass

    for _, r in edges_df.iterrows():
        u = int(r[from_col])
        v = int(r[to_col])
        w = float(r["_len"])
        G.add_edge(u, v, weight=w)
        G.add_edge(v, u, weight=w)

    return G, edge_geom
