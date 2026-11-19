import json
from pathlib import Path

import folium
import numpy as np
import pandas as pd
from shapely.geometry import LineString, mapping
import networkx as nx


def build_full_node_path(G: nx.DiGraph, dedup_nodes):
    full_path = []
    for i in range(len(dedup_nodes) - 1):
        u, v = dedup_nodes[i], dedup_nodes[i + 1]
        try:
            sp = nx.shortest_path(G, u, v, weight="weight")
            if full_path:
                full_path.extend(sp[1:])
            else:
                full_path.extend(sp)
        except nx.NetworkXNoPath:
            if not full_path:
                full_path.append(u)
            full_path.append(v)
    return full_path


def stitch_coords_from_edges(G: nx.DiGraph, edge_geom: dict, node_path: list):
    coords = []
    for i in range(len(node_path) - 1):
        u, v = node_path[i], node_path[i + 1]
        geom = edge_geom.get((u, v)) or edge_geom.get((v, u))
        if geom is not None:
            seg = [(y, x) for (x, y) in list(geom.coords)]
            if coords and coords[-1] == seg[0]:
                coords.extend(seg[1:])
            else:
                coords.extend(seg)
        else:
            a = (G.nodes[u]["lat"], G.nodes[u]["lon"])
            b = (G.nodes[v]["lat"], G.nodes[v]["lon"])
            if not coords or coords[-1] != a:
                coords.append(a)
            coords.append(b)
    return coords


def save_outputs(prefix: str, clean_df, path_list: list, G: nx.DiGraph, edge_geom: dict):
    prefix_path = Path(prefix)
    prefix_path.parent.mkdir(parents=True, exist_ok=True)

    out_clean = Path(f"{prefix}_gps_cleaned.csv")
    clean_df.to_csv(out_clean, index=False, encoding="utf-8-sig")

    out_raw = Path(f"{prefix}_strict_raw.csv")
    pd.DataFrame(path_list).to_csv(out_raw, index=False, encoding="utf-8-sig")

    seq_nodes = [int(p["Node_ID"]) for p in path_list]
    dedup = []
    for n in seq_nodes:
        if not dedup or dedup[-1] != n:
            dedup.append(n)

    full_node_path = build_full_node_path(G, dedup)
    pd.DataFrame({"node_id": full_node_path}).to_csv(f"{prefix}_path_nodes.csv", index=False, encoding="utf-8-sig")

    coords = stitch_coords_from_edges(G, edge_geom, full_node_path)
    gj_path = Path(f"{prefix}_route.geojson")

    if len(coords) >= 2:
        line = LineString([(lon, lat) for (lat, lon) in coords])
        gj = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "geometry": mapping(line), "properties": {"name": "matched_route"}}],
        }
        with open(gj_path, "w", encoding="utf-8") as f:
            json.dump(gj, f, ensure_ascii=False)
    else:
        with open(gj_path, "w", encoding="utf-8") as f:
            json.dump({"type": "FeatureCollection", "features": []}, f, ensure_ascii=False)

    if len(coords) >= 2:
        lat_med = np.median([p[0] for p in coords])
        lon_med = np.median([p[1] for p in coords])
    else:
        lat_med = clean_df["Latitude"].median()
        lon_med = clean_df["Longitude"].median()

    m = folium.Map(location=[lat_med, lon_med], zoom_start=13, control_scale=True)
    if len(coords) >= 2:
        folium.PolyLine(coords, weight=5, tooltip="Matched (strict)").add_to(m)
    m.save(f"{prefix}_map_only.html")

    return {
        "gps_cleaned_csv": str(out_clean),
        "viterbi_raw_csv": str(out_raw),
        "path_nodes_csv": f"{prefix}_path_nodes.csv",
        "route_geojson": str(gj_path),
        "map_only_html": f"{prefix}_map_only.html",
    }
