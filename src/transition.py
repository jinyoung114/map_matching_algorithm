import math
import numpy as np
import networkx as nx
from geopy.distance import geodesic

from .config import EMIT_SIGMA
from .utils import bearing_deg, angle_diff


def emit_prob(distance_m: float, sigma=EMIT_SIGMA) -> float:
    return math.exp(-distance_m / sigma)


def edge_heading(G: nx.DiGraph, u: int, v: int) -> float:
    a = (G.nodes[u]["lat"], G.nodes[u]["lon"])
    b = (G.nodes[v]["lat"], G.nodes[v]["lon"])
    return bearing_deg(a, b)


def trans_prob_strict(G: nx.DiGraph, n1: dict, n2: dict, g1: tuple, g2: tuple, dt: float, obs_heading: float) -> float:
    if not G.has_node(n1["Node_ID"]) or not G.has_node(n2["Node_ID"]):
        return 1e-12

    if not nx.has_path(G, n1["Node_ID"], n2["Node_ID"]):
        return 1e-12

    try:
        rd = nx.shortest_path_length(G, n1["Node_ID"], n2["Node_ID"], weight="weight")
    except Exception:
        return 1e-12

    gd = geodesic(g1, g2).meters

    if gd > 5.0:
        if (rd / gd) > 3.0 and (rd - gd) > 30.0:
            return 1e-12
    else:
        if rd > 40.0:
            return 1e-12

    if dt and dt > 0:
        road_speed = rd / dt
        obs_speed = gd / dt
        if road_speed > 45.0:
            return 1e-12
        if obs_speed < 15.0 and road_speed > max(25.0, 2.5 * max(obs_speed, 1.0)):
            return 1e-12

    head_term = 1.0
    try:
        road_head = edge_heading(G, n1["Node_ID"], n2["Node_ID"])
    except Exception:
        road_head = np.nan

    if not np.isnan(obs_heading) and not np.isnan(road_head):
        diff = abs(angle_diff(road_head, obs_heading))
        if diff >= 150:
            return 1e-12
        elif diff >= 90:
            head_term = math.exp(-((diff - 90) / 12.0)) * 0.2
        else:
            head_term = math.exp(-(diff / 25.0))

    dist_term = math.exp(-abs(rd - gd) / 40.0)
    return max(dist_term * head_term, 1e-12)
