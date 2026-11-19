import pandas as pd
import numpy as np
from pathlib import Path
from geopy.distance import geodesic


def read_csv_any(path: Path):
    for enc in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue
    raise RuntimeError(f"CSV 읽기 실패: {path}")


def need_scale(series: pd.Series) -> bool:
    v = pd.to_numeric(series.dropna().astype(str).str.replace(",", "", regex=False), errors="coerce")
    if v.empty:
        return False
    return v.median() > 1000


def haversine_m(a, b) -> float:
    return geodesic(a, b).meters


def bearing_deg(p1, p2) -> float:
    lat1, lon1 = np.radians(p1[0]), np.radians(p1[1])
    lat2, lon2 = np.radians(p2[0]), np.radians(p2[1])
    dlon = lon2 - lon1
    y = np.sin(dlon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    brng = np.degrees(np.arctan2(y, x))
    return (brng + 360) % 360


def angle_diff(a, b) -> float:
    return (a - b + 180) % 360 - 180
