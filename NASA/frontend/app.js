const map = L.map('map').setView([20, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let marker = null;
map.on('click', (e) => {
  if (marker) marker.remove();
  marker = L.marker(e.latlng).addTo(map);
});

function fmtPct(x) { return (x * 100).toFixed(1) + '%'; }

document.getElementById('run').addEventListener('click', async () => {
  const out = document.getElementById('output');
  if (!marker) {
    out.textContent = 'Please drop a pin on the map first.';
    return;
  }
  const lat = marker.getLatLng().lat.toFixed(4);
  const lon = marker.getLatLng().lng.toFixed(4);
  const varKey = document.getElementById('var').value;
  const date = document.getElementById('date').value;
  const threshold = document.getElementById('threshold').value;
  const comparison = document.getElementById('comparison').value;
  const windowDays = document.getElementById('window').value;
  if (!date) {
    out.textContent = 'Please select a date.';
    return;
  }
  out.textContent = 'Computing...';
  try {
    const url = `/api/probability?lat=${lat}&lon=${lon}&target_date=${date}&var=${encodeURIComponent(varKey)}&threshold=${threshold}&comparison=${comparison}&window_days=${windowDays}`;
    const resp = await fetch(url);
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || 'API error');
    }
    const data = await resp.json();
    out.innerHTML = `Probability: <b>${fmtPct(data.probability)}</b><br/>Samples: ${data.n_samples}<br/>95% CI: ${fmtPct(data.ci_95[0])} - ${fmtPct(data.ci_95[1])}<br/>Method: ${data.method}`;
  } catch (e) {
    out.textContent = 'Error: ' + e.message;
  }
});


