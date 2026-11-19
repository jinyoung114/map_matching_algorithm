import numpy as np
from sklearn.neighbors import BallTree

from .config import BASE_RADIUS_M, CURVE_RADIUS_M, BASE_K, CURVE_K, CURVE_THRESHOLD_DEG
from .utils import bearing_deg


def is_curve_point(prev, curr, nxt, threshold=CURVE_THRESHOLD_DEG):
    a1 = bearing_deg(prev, curr)
    a2 = bearing_deg(curr, nxt)
    diff = (a2 - a1 + 180) % 360 - 180
    return abs(diff) > threshold


def build_balltree(nodes_df):
    return BallTree(np.radians(nodes_df[["Latitude", "Longitude"]].values), metric="haversine")


def get_candidates(i, gps_df, nodes_df, tree, base_radius=BASE_RADIUS_M, curve_radius=CURVE_RADIUS_M, base_k=BASE_K, curve_k=CURVE_K):
    lat, lon = gps_df.iloc[i][["Latitude", "Longitude"]]
    prev_pt = gps_df.iloc[i - 1][["Latitude", "Longitude"]].values if i > 0 else None
    next_pt = gps_df.iloc[i + 1][["Latitude", "Longitude"]].values if i < len(gps_df) - 1 else None

    curved = False
    if prev_pt is not None and next_pt is not None:
        curved = is_curve_point(prev_pt, [lat, lon], next_pt)

    radius = curve_radius if curved else base_radius
    max_k = curve_k if curved else base_k

    q = np.radians([[lat, lon]])
    inds = tree.query_radius(q, r=radius / 6371000.0, return_distance=True)

    idxs = inds[0][0] if len(inds[0]) > 0 else np.array([])
    dists = inds[1][0] * 6371000.0 if len(inds[0]) > 0 else np.array([])

    if len(idxs) == 0:
        d, idx = tree.query(q, k=min(max_k, len(nodes_df)))
        dists = d[0] * 6371000.0
        idxs = idx[0]

    pairs = sorted(zip(dists, idxs), key=lambda x: x[0])[:max_k]
    return [
        {
            "Node_ID": int(nodes_df.iloc[int(idx)]["Node_ID"]),
            "Latitude": float(nodes_df.iloc[int(idx)]["Latitude"]),
            "Longitude": float(nodes_df.iloc[int(idx)]["Longitude"]),
            "Distance": float(dist),
        }
        for dist, idx in pairs
    ]
