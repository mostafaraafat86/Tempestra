from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Tuple

import requests


BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def _build_params(parameters: List[str]) -> str:
    return ",".join(parameters)


def fetch_daily_series(
    lat: float,
    lon: float,
    start: date,
    end: date,
    parameters: List[str],
) -> Dict[str, List[Tuple[datetime, float]]]:
    query = {
        "parameters": _build_params(parameters),
        "community": "RE",
        "latitude": lat,
        "longitude": lon,
        "start": start.strftime("%Y%m%d"),
        "end": end.strftime("%Y%m%d"),
        "format": "JSON",
    }
    resp = requests.get(BASE_URL, params=query, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # POWER JSON shape: properties.parameter.{VAR}.{YYYYMMDD: value}
    param_obj: Dict[str, Dict[str, float]] = data["properties"]["parameter"]
    series: Dict[str, List[Tuple[datetime, float]]] = {}
    for var in parameters:
        series_map = param_obj.get(var)
        if series_map is None:
            raise ValueError(f"Variable {var} not available in POWER response")
        items: List[Tuple[datetime, float]] = []
        for ymd, val in series_map.items():
            try:
                dt = datetime.strptime(ymd, "%Y%m%d")
                items.append((dt, float(val)))
            except Exception:
                continue
        items.sort(key=lambda x: x[0])
        series[var] = items
    return series


