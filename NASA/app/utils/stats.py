from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, Tuple, List, Tuple as Tup

# import numpy as np  # Removed for Windows compatibility


def select_dayofyear_window(series: List[Tup[datetime, float]], center_date: date, window_days: int) -> List[float]:
    center = center_date.timetuple().tm_yday
    lower = max(1, center - window_days)
    upper = min(366, center + window_days)
    vals: List[float] = []
    for dt, val in series:
        doy = dt.timetuple().tm_yday
        if lower <= doy <= upper and val is not None:
            try:
                v = float(val)
            except Exception:
                continue
            if v == v and v != float('inf') and v != float('-inf'):  # Check for NaN and inf
                vals.append(v)
    return vals


def compute_exceedance_probability(samples: Iterable[float], threshold: float, comparison: str = "gt") -> float:
    samples_list = list(samples)
    n = len(samples_list)
    if n == 0:
        return float("nan")
    if comparison == "gt":
        k = sum(1 for x in samples_list if x > threshold)
    else:
        k = sum(1 for x in samples_list if x < threshold)
    return k / n


def wilson_confidence_interval(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    from math import sqrt

    # 95% two-sided z
    if confidence == 0.95:
        z = 1.959963984540054
    else:
        # Fallback approximate
        z = 1.959963984540054
    phat = k / n
    denom = 1 + z ** 2 / n
    center = (phat + z ** 2 / (2 * n)) / denom
    margin = z * sqrt((phat * (1 - phat) + z ** 2 / (4 * n)) / n) / denom
    low = max(0.0, center - margin)
    high = min(1.0, center + margin)
    return (low, high)


