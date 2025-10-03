from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Query, HTTPException

from app.services.power_client import fetch_daily_series
from app.utils.stats import (
    compute_exceedance_probability,
    wilson_confidence_interval,
    select_dayofyear_window,
)


router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/probability")
def probability(
    lat: float,
    lon: float,
    target_date: date,
    var: str = Query(..., description="Variable key, e.g., T2M_MAX, WS10M, PRECTOTCORR"),
    threshold: float = Query(..., description="Numeric threshold in variable units"),
    comparison: str = Query("gt", regex="^(gt|lt)$", description="gt for >, lt for <"),
    window_days: int = Query(15, ge=0, le=60, description="Half-window size in days for DOY window"),
) -> dict:
    try:
        start = date(1981, 1, 1)
        end = date.today()
        series = fetch_daily_series(lat=lat, lon=lon, start=start, end=end, parameters=[var])
        samples = select_dayofyear_window(series[var], target_date, window_days)
        prob = compute_exceedance_probability(samples, threshold, comparison)
        ci_low, ci_high = wilson_confidence_interval(int(prob * len(samples)), len(samples))
        return {
            "probability": prob,
            "n_samples": int(len(samples)),
            "ci_95": [ci_low, ci_high],
            "threshold": threshold,
            "comparison": comparison,
            "units": None,
            "source": ["NASA POWER (MERRA-2 derived)"],
            "period": f"{start.year}–{end.year}",
            "method": f"DOY ±{window_days}d; binomial proportion (Wilson CI)",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/climatology")
def climatology(
    lat: float,
    lon: float,
    var: str,
    window_days: int = 15,
) -> dict:
    try:
        start = date(1981, 1, 1)
        end = date.today()
        series = fetch_daily_series(lat=lat, lon=lon, start=start, end=end, parameters=[var])
        # Build DOY mean and simple percentiles without pandas
        from collections import defaultdict
        buckets = defaultdict(list)
        for dt, val in series[var]:
            if val is None:
                continue
            doy = dt.timetuple().tm_yday
            try:
                v = float(val)
            except Exception:
                continue
            if v == v and v != float('inf') and v != float('-inf'):  # Check for NaN and inf
                buckets[doy].append(v)
        days = sorted(buckets.keys())
        means, medians, p10s, p90s = [], [], [], []
        for d in days:
            arr = buckets[d]
            if arr:
                arr_sorted = sorted(arr)
                n = len(arr_sorted)
                means.append(sum(arr) / n)
                medians.append(arr_sorted[n//2] if n % 2 == 1 else (arr_sorted[n//2-1] + arr_sorted[n//2]) / 2)
                p10s.append(arr_sorted[int(n * 0.1)] if n > 0 else float("nan"))
                p90s.append(arr_sorted[int(n * 0.9)] if n > 0 else float("nan"))
            else:
                means.append(float("nan"))
                medians.append(float("nan"))
                p10s.append(float("nan"))
                p90s.append(float("nan"))
        return {
            "doy": days,
            "mean": [round(x, 3) if x == x and x != float('inf') and x != float('-inf') else None for x in means],
            "median": [round(x, 3) if x == x and x != float('inf') and x != float('-inf') else None for x in medians],
            "p10": [round(x, 3) if x == x and x != float('inf') and x != float('-inf') else None for x in p10s],
            "p90": [round(x, 3) if x == x and x != float('inf') and x != float('-inf') else None for x in p90s],
            "units": None,
            "source": ["NASA POWER"],
            "period": f"{start.year}–{end.year}",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/trend")
def trend(
    lat: float,
    lon: float,
    target_date: date,
    var: str,
    threshold: float,
    comparison: str = Query("gt", regex="^(gt|lt)$"),
    window_days: int = 15,
) -> dict:
    try:
        start = date(1981, 1, 1)
        end = date.today()
        series = fetch_daily_series(lat=lat, lon=lon, start=start, end=end, parameters=[var])
        center = target_date.timetuple().tm_yday
        lower = max(1, center - window_days)
        upper = min(366, center + window_days)
        from collections import defaultdict
        buckets = defaultdict(lambda: [0, 0])  # year -> [exceed_count, total]
        for dt, val in series[var]:
            doy = dt.timetuple().tm_yday
            if not (lower <= doy <= upper):
                continue
            try:
                v = float(val)
            except Exception:
                continue
            year = dt.year
            buckets[year][1] += 1
            if (comparison == "gt" and v > threshold) or (comparison == "lt" and v < threshold):
                buckets[year][0] += 1
        years = sorted(buckets.keys())
        values = []
        for y in years:
            k, n = buckets[y]
            values.append(k / n if n else 0.0)
        # Simple Sen's slope (pairwise median slope)
        slopes = []
        for i in range(len(years)):
            for j in range(i + 1, len(years)):
                if years[j] != years[i]:
                    slopes.append((values[j] - values[i]) / (years[j] - years[i]))
        slope = float(sorted(slopes)[len(slopes) // 2]) if slopes else 0.0
        # Mann-Kendall (very simplified, no ties correction)
        S = 0
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                S += 1 if values[j] > values[i] else (-1 if values[j] < values[i] else 0)
        n = len(values)
        var_s = n * (n - 1) * (2 * n + 5) / 18 if n >= 2 else 0
        z = S / (var_s ** 0.5) if var_s > 0 else 0
        return {
            "years": years,
            "values": [round(v, 4) for v in values],
            "trend_slope_per_year": round(slope, 5),
            "mann_kendall_z": round(float(z), 3),
            "source": ["NASA POWER"],
            "period": f"{start.year}–{end.year}",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


