Tempestra - NASA Weather Likelihood (Hackathon MVP)

Run
```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints
- GET /api/health
- GET /api/probability?lat&lon&target_date=YYYY-MM-DD&var=T2M_MAX&threshold=32&comparison=gt&window_days=15
- GET /api/climatology?lat&lon&var=T2M_MAX&window_days=15
- GET /api/trend?lat&lon&target_date=YYYY-MM-DD&var=T2M_MAX&threshold=32&comparison=gt&window_days=15

Variables (POWER)
- Temperature: T2M_MAX, T2M_MIN, T2M
- Humidity: RH2M
- Wind: WS10M
- Precipitation: PRECTOTCORR

How probabilities are computed
- Day-of-year window (±N days) across all years (1981–present)
- Exceedance probability for > or < threshold; Wilson 95% CI
- Trends from annual exceedance rate (Sen’s slope, Mann–Kendall Z)

What I need from you
- Default thresholds: hot (°C/°F), cold, windy (m/s or mph), wet (mm or in), uncomfortable (Heat Index)
- Preferred units: metric or imperial
- Window size: default 15 days ok?
- UI: use pin only now? polygon later?

Data sources
- NASA POWER (MERRA‑2 derived): https://power.larc.nasa.gov
- Stretch: GPM IMERG, MERRA‑2 via GES DISC OPeNDAP/Harmony; Giovanni for subsets

Notes
- Historical probability, not a forecast; leap days handled; missing dropped.

