import numpy as np
import pandas as pd

from .config import SPEED_THRESHOLD_MPS, HEADING_JUMP_DIST_M, HEADING_JUMP_THRESHOLD_DEG, HAMPEL_MULT, HAMPEL_WINDOW
from .utils import read_csv_any, need_scale, haversine_m, bearing_deg, angle_diff


def load_and_clean_gps(gps_path):
    gps_raw = read_csv_any(gps_path).copy()

    if "PosX" in gps_raw.columns and "PosY" in gps_raw.columns:
        gps_raw["_lon"] = pd.to_numeric(gps_raw["PosX"], errors="coerce")
        gps_raw["_lat"] = pd.to_numeric(gps_raw["PosY"], errors="coerce")
    else:
        lon_c = next((c for c in gps_raw.columns if c.lower() in ["longitude", "lon", "x", "경도"]), None)
        lat_c = next((c for c in gps_raw.columns if c.lower() in ["latitude", "lat", "y", "위도"]), None)
        if lon_c is None or lat_c is None:
            raise RuntimeError("GPS 컬럼을 찾을 수 없음 (PosX/PosY 또는 Latitude/Longitude)")
        gps_raw["_lon"] = pd.to_numeric(gps_raw[lon_c], errors="coerce")
        gps_raw["_lat"] = pd.to_numeric(gps_raw[lat_c], errors="coerce")

    scale = 1e6 if (need_scale(gps_raw["_lon"]) or need_scale(gps_raw["_lat"])) else 1.0
    gps_raw["Longitude"] = gps_raw["_lon"] / scale
    gps_raw["Latitude"] = gps_raw["_lat"] / scale

    ts_col = next((c for c in ["Timestamp", "정보 발생 일시", "time", "datetime"] if c in gps_raw.columns), None)
    if ts_col:
        t = pd.to_datetime(gps_raw[ts_col].astype(str), errors="coerce", format="%Y%m%d%H%M%S")
        if t.isna().all():
            t = pd.to_datetime(gps_raw[ts_col].astype(str), errors="coerce", format="%y%m%d%H%M%S")
        gps_raw["_t"] = t
        if gps_raw["_t"].notna().any():
            gps_raw = gps_raw.sort_values("_t").reset_index(drop=True)
    else:
        gps_raw["_t"] = pd.NaT

    gps = gps_raw[gps_raw["Latitude"].between(32, 39) & gps_raw["Longitude"].between(124, 132)].reset_index(drop=True)

    d_m, dt_s, head = [0.0], [1.0], [np.nan]
    for i in range(1, len(gps)):
        a = (gps.loc[i - 1, "Latitude"], gps.loc[i - 1, "Longitude"])
        b = (gps.loc[i, "Latitude"], gps.loc[i, "Longitude"])
        d_m.append(haversine_m(a, b))
        head.append(bearing_deg(a, b))
        if gps["_t"].notna().all():
            dt = (gps.loc[i, "_t"] - gps.loc[i - 1, "_t"]).total_seconds()
            dt_s.append(dt if (dt and dt > 0) else 1.0)
        else:
            dt_s.append(1.0)

    gps["_dist"] = d_m
    gps["_dt"] = dt_s
    gps["_speed_mps"] = np.array(d_m) / np.array(dt_s)
    gps["_heading"] = head

    mask_speed = gps["_speed_mps"] <= SPEED_THRESHOLD_MPS

    mh = [True]
    for i in range(1, len(gps)):
        if gps.loc[i, "_dist"] < HEADING_JUMP_DIST_M:
            prev_h, cur_h = gps.loc[i - 1, "_heading"], gps.loc[i, "_heading"]
            if not np.isnan(prev_h) and not np.isnan(cur_h):
                if abs(angle_diff(cur_h, prev_h)) > HEADING_JUMP_THRESHOLD_DEG:
                    mh.append(False)
                    continue
        mh.append(True)
    mask_heading = pd.Series(mh, index=gps.index)

    s = gps["_speed_mps"].copy()
    med = s.rolling(HAMPEL_WINDOW, center=True, min_periods=1).median()
    mad = (s - med).abs().rolling(HAMPEL_WINDOW, center=True, min_periods=1).median() + 1e-6
    mask_hampel = (s - med).abs() <= HAMPEL_MULT * mad

    clean = gps[mask_speed & mask_heading & mask_hampel].reset_index(drop=True)

    d2, h2, dt2 = [0.0], [np.nan], [1.0]
    for i in range(1, len(clean)):
        a = (clean.loc[i - 1, "Latitude"], clean.loc[i - 1, "Longitude"])
        b = (clean.loc[i, "Latitude"], clean.loc[i, "Longitude"])
        d2.append(haversine_m(a, b))
        h2.append(bearing_deg(a, b))
        if clean["_t"].notna().all():
            dt = (clean.loc[i, "_t"] - clean.loc[i - 1, "_t"]).total_seconds()
            dt2.append(dt if (dt and dt > 0) else 1.0)
        else:
            dt2.append(1.0)

    clean["_dist"] = d2
    clean["_dt"] = dt2
    clean["_heading"] = h2
    return clean
