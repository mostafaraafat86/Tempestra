// Initialize map
const map = L.map('map').setView([30.0444, 31.2357], 6); // Default to Cairo, Egypt
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let marker = null;
let selectedArea = null;
let isSelectingArea = false;
let selectionRectangle = null;
let areaSelectionMode = false;

// Disable/enable map dragging based on mode
function updateMapInteractions() {
  if (areaSelectionMode) {
    map.dragging.disable();
    map.getContainer().style.cursor = 'crosshair';
  } else {
    map.dragging.enable();
    map.getContainer().style.cursor = '';
  }
}

// Function to add marker at coordinates
function addMarker(lat, lng) {
  if (marker) marker.remove();
  marker = L.marker([lat, lng]).addTo(map);
  
  // Clear area selection when adding marker
  clearAreaSelection();
  
  // Add a subtle animation to the marker
  marker.getElement().style.transition = 'transform 0.3s ease';
  marker.getElement().style.transform = 'scale(1.2)';
  setTimeout(() => {
    marker.getElement().style.transform = 'scale(1)';
  }, 200);
  
  // Update button state
  updateButtonState();
}

// Function to clear area selection
function clearAreaSelection() {
  if (selectionRectangle) {
    map.removeLayer(selectionRectangle);
    selectionRectangle = null;
  }
  selectedArea = null;
  isSelectingArea = false;
  updateAreaSelectionUI();
}

// Drawing functions removed - focusing on area selection only

// Function to update area selection UI
function updateAreaSelectionUI() {
  const areaInfo = document.getElementById('area-info');
  if (selectedArea) {
    const bounds = selectedArea.getBounds();
    const center = bounds.getCenter();
    const area = calculateArea(bounds);
    areaInfo.innerHTML = `
      <div class="area-selection-info">
        <strong>Selected Area:</strong><br>
        Center: ${center.lat.toFixed(4)}°, ${center.lng.toFixed(4)}°<br>
        Bounds: ${bounds.getSouthWest().lat.toFixed(4)}° to ${bounds.getNorthEast().lat.toFixed(4)}° lat,<br>
        ${bounds.getSouthWest().lng.toFixed(4)}° to ${bounds.getNorthEast().lng.toFixed(4)}° lng<br>
        Approximate Area: ${area.toFixed(2)} km²
      </div>
    `;
    areaInfo.style.display = 'block';
  } else {
    areaInfo.style.display = 'none';
  }
}

// Function to calculate approximate area in km²
function calculateArea(bounds) {
  const sw = bounds.getSouthWest();
  const ne = bounds.getNorthEast();
  
  // Convert to meters and calculate area
  const lat1 = sw.lat * Math.PI / 180;
  const lat2 = ne.lat * Math.PI / 180;
  const dLat = (ne.lat - sw.lat) * Math.PI / 180;
  const dLng = (ne.lng - sw.lng) * Math.PI / 180;
  
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
          Math.cos(lat1) * Math.cos(lat2) *
          Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  
  // Earth's radius in km
  const R = 6371;
  const area = R * R * c * Math.abs(ne.lat - sw.lat) * Math.PI / 180;
  
  return area;
}

// Selection mode toggle functionality (toggles between Point and Area)
let selectionMode = 'point'; // 'point', 'area'

document.getElementById('selection-mode-btn').addEventListener('click', function() {
  const icon = this.querySelector('.mode-icon');
  const text = this.querySelector('.mode-text');
  const drawMethod = document.getElementById('draw-method');
  
  // Toggle between point and area modes
  if (selectionMode === 'point') {
    selectionMode = 'area';
    areaSelectionMode = true;
    this.classList.add('active');
    icon.textContent = '🔷';
    text.textContent = 'Area Selection';
    drawMethod.style.display = 'none';
    
    // Clear any existing marker when switching to area mode
    if (marker) {
      map.removeLayer(marker);
      marker = null;
    }
    
    // Update map interactions for area selection mode
    updateMapInteractions();
  } else {
    selectionMode = 'point';
    areaSelectionMode = false;
    this.classList.remove('active');
    icon.textContent = '📍';
    text.textContent = 'Point Selection';
    drawMethod.style.display = 'none';
    
    // Clear any existing area selection when switching to point mode
    clearAreaSelection();
    
    // Update map interactions for point selection mode
    updateMapInteractions();
  }
  
  updateButtonState();
});

// Map click handler
map.on('click', (e) => {
  if (!areaSelectionMode) {
    addMarker(e.latlng.lat, e.latlng.lng);
    
    // Update location input with coordinates
    document.getElementById('location-input').value = `${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`;
  }
});

// Area selection functionality
let startPoint = null;
let endPoint = null;
let startLatLng = null;

// Mouse down handler for starting area selection
map.getContainer().addEventListener('mousedown', function(e) {
  if (areaSelectionMode && e.target === map.getContainer() || e.target.classList.contains('leaflet-container') || e.target.classList.contains('leaflet-tile') || e.target.classList.contains('leaflet-tile-container')) {
    isSelectingArea = true;
    
    // Get the latlng from pixel coordinates
    const containerPoint = map.mouseEventToContainerPoint(e);
    startLatLng = map.containerPointToLatLng(containerPoint);
    
    // Clear existing area selection
    if (selectionRectangle) {
      map.removeLayer(selectionRectangle);
      selectionRectangle = null;
    }
    selectedArea = null;
    
    e.preventDefault();
    e.stopPropagation();
  }
});

// Mouse move handler for drawing selection rectangle
map.getContainer().addEventListener('mousemove', function(e) {
  if (areaSelectionMode && isSelectingArea && startLatLng) {
    // Get the latlng from pixel coordinates
    const containerPoint = map.mouseEventToContainerPoint(e);
    const endLatLng = map.containerPointToLatLng(containerPoint);
    
    // Remove existing rectangle
    if (selectionRectangle) {
      map.removeLayer(selectionRectangle);
    }
    
    // Create new rectangle
    const bounds = L.latLngBounds([startLatLng, endLatLng]);
    selectionRectangle = L.rectangle(bounds, {
      color: '#0ea5e9',
      weight: 2,
      fillColor: '#0ea5e9',
      fillOpacity: 0.2,
      dashArray: '5, 5',
      interactive: false
    }).addTo(map);
    
    e.preventDefault();
    e.stopPropagation();
  }
});

// Mouse up handler for finishing area selection
map.getContainer().addEventListener('mouseup', function(e) {
  if (areaSelectionMode && isSelectingArea && startLatLng) {
    // Get the latlng from pixel coordinates
    const containerPoint = map.mouseEventToContainerPoint(e);
    const endLatLng = map.containerPointToLatLng(containerPoint);
    
    const bounds = L.latLngBounds([startLatLng, endLatLng]);
    
    // Only create area selection if bounds are meaningful (not too small)
    const distance = bounds.getSouthWest().distanceTo(bounds.getNorthEast());
    
    if (distance > 100) { // 100m minimum
      selectedArea = selectionRectangle;
      updateAreaSelectionUI();
      updateButtonState();
      
      // Update location input with center coordinates
      const center = bounds.getCenter();
      document.getElementById('location-input').value = `${center.lat.toFixed(4)}, ${center.lng.toFixed(4)}`;
    } else {
      // Too small selection, remove rectangle
      if (selectionRectangle) {
        map.removeLayer(selectionRectangle);
        selectionRectangle = null;
      }
    }
    
    isSelectingArea = false;
    startLatLng = null;
    
    e.preventDefault();
    e.stopPropagation();
  }
});

// Handle mouse leaving the map container
map.getContainer().addEventListener('mouseleave', function(e) {
  if (areaSelectionMode && isSelectingArea) {
    isSelectingArea = false;
    startLatLng = null;
    if (selectionRectangle && !selectedArea) {
      map.removeLayer(selectionRectangle);
      selectionRectangle = null;
    }
  }
});

// City search functionality
let citySearchTimeout;
const suggestionsContainer = document.getElementById('location-suggestions');

// Enhanced city data with more cities and better country disambiguation
const cities = [
  { name: 'Cairo', country: 'Egypt', lat: 30.0444, lng: 31.2357 },
  { name: 'London', country: 'United Kingdom', lat: 51.5074, lng: -0.1278 },
  { name: 'New York', country: 'United States', lat: 40.7128, lng: -74.0060 },
  { name: 'Paris', country: 'France', lat: 48.8566, lng: 2.3522 },
  { name: 'Tokyo', country: 'Japan', lat: 35.6762, lng: 139.6503 },
  { name: 'Sydney', country: 'Australia', lat: -33.8688, lng: 151.2093 },
  { name: 'Dubai', country: 'UAE', lat: 25.2048, lng: 55.2708 },
  { name: 'Mumbai', country: 'India', lat: 19.0760, lng: 72.8777 },
  { name: 'Beijing', country: 'China', lat: 39.9042, lng: 116.4074 },
  { name: 'Moscow', country: 'Russia', lat: 55.7558, lng: 37.6176 },
  { name: 'Berlin', country: 'Germany', lat: 52.5200, lng: 13.4050 },
  { name: 'Rome', country: 'Italy', lat: 41.9028, lng: 12.4964 },
  { name: 'Madrid', country: 'Spain', lat: 40.4168, lng: -3.7038 },
  { name: 'Amsterdam', country: 'Netherlands', lat: 52.3676, lng: 4.9041 },
  { name: 'Barcelona', country: 'Spain', lat: 41.3851, lng: 2.1734 },
  { name: 'Istanbul', country: 'Turkey', lat: 41.0082, lng: 28.9784 },
  { name: 'Athens', country: 'Greece', lat: 37.9838, lng: 23.7275 },
  { name: 'Prague', country: 'Czech Republic', lat: 50.0755, lng: 14.4378 },
  { name: 'Vienna', country: 'Austria', lat: 48.2082, lng: 16.3738 },
  { name: 'Stockholm', country: 'Sweden', lat: 59.3293, lng: 18.0686 },
  // Additional cities with common names
  { name: 'Springfield', country: 'United States (Illinois)', lat: 39.7817, lng: -89.6501 },
  { name: 'Springfield', country: 'United States (Missouri)', lat: 37.2089, lng: -93.2923 },
  { name: 'Birmingham', country: 'United Kingdom', lat: 52.4862, lng: -1.8904 },
  { name: 'Birmingham', country: 'United States', lat: 33.5207, lng: -86.8025 },
  { name: 'Manchester', country: 'United Kingdom', lat: 53.4808, lng: -2.2426 },
  { name: 'Manchester', country: 'United States', lat: 42.9956, lng: -71.4548 },
  { name: 'Newport', country: 'United Kingdom', lat: 51.5889, lng: -2.9979 },
  { name: 'Newport', country: 'United States (Rhode Island)', lat: 41.4901, lng: -71.3128 },
  { name: 'Newport', country: 'United States (Kentucky)', lat: 39.0914, lng: -84.4958 },
  { name: 'Richmond', country: 'United States (Virginia)', lat: 37.5407, lng: -77.4360 },
  { name: 'Richmond', country: 'United States (California)', lat: 37.9358, lng: -122.3478 },
  { name: 'Richmond', country: 'Australia', lat: -37.8136, lng: 144.9631 },
  { name: 'Frankfurt', country: 'Germany', lat: 50.1109, lng: 8.6821 },
  { name: 'Frankfurt', country: 'United States', lat: 38.2009, lng: -84.8733 },
  { name: 'Victoria', country: 'Canada', lat: 48.4284, lng: -123.3656 },
  { name: 'Victoria', country: 'Australia', lat: -37.8136, lng: 144.9631 },
  { name: 'Victoria', country: 'Seychelles', lat: -4.6191, lng: 55.4513 },
  { name: 'Hamilton', country: 'Canada', lat: 43.2557, lng: -79.8711 },
  { name: 'Hamilton', country: 'New Zealand', lat: -37.7870, lng: 175.2793 },
  { name: 'Hamilton', country: 'Bermuda', lat: 32.2948, lng: -64.7814 },
  // Additional important cities
  { name: 'Washington', country: 'United States', lat: 38.9072, lng: -77.0369 },
  { name: 'Washington', country: 'United States (State)', lat: 47.7511, lng: -120.7401 },
  { name: 'Luxor', country: 'Egypt', lat: 25.6872, lng: 32.6396 },
  { name: 'Alexandria', country: 'Egypt', lat: 31.2001, lng: 29.9187 },
  { name: 'Giza', country: 'Egypt', lat: 30.0131, lng: 31.2089 },
  { name: 'Aswan', country: 'Egypt', lat: 24.0889, lng: 32.8998 },
  { name: 'Hurghada', country: 'Egypt', lat: 27.2574, lng: 33.8129 },
  { name: 'Sharm El Sheikh', country: 'Egypt', lat: 27.9158, lng: 34.3300 }
];

function showSuggestions(suggestions) {
  suggestionsContainer.innerHTML = '';
  
  if (suggestions.length === 0) {
    suggestionsContainer.style.display = 'none';
    return;
  }
  
  // Limit to 8 suggestions for better UX
  const limitedSuggestions = suggestions.slice(0, 8);
  
  limitedSuggestions.forEach(city => {
    const suggestion = document.createElement('div');
    suggestion.className = 'location-suggestion';
    
    // Highlight matching text
    const inputValue = document.getElementById('location-input').value.toLowerCase();
    const cityName = city.name.toLowerCase();
    const countryName = city.country.toLowerCase();
    
    let displayName = city.name;
    let displayCountry = city.country;
    
    // Highlight matching parts
    if (cityName.includes(inputValue)) {
      const index = cityName.indexOf(inputValue);
      displayName = city.name.substring(0, index) + 
                   '<mark>' + city.name.substring(index, index + inputValue.length) + '</mark>' + 
                   city.name.substring(index + inputValue.length);
    }
    
    suggestion.innerHTML = `
      <div class="suggestion-content">
        <span class="location-name">${displayName}</span>
        <span class="location-country">${displayCountry}</span>
      </div>
      <span class="location-coords">${city.lat.toFixed(2)}°, ${city.lng.toFixed(2)}°</span>
    `;
    
    suggestion.addEventListener('click', () => {
      selectCity(city);
    });
    
    suggestionsContainer.appendChild(suggestion);
  });
  
  suggestionsContainer.style.display = 'block';
}

function selectCity(city) {
  document.getElementById('location-input').value = `${city.name}, ${city.country}`;
  addMarker(city.lat, city.lng);
  map.setView([city.lat, city.lng], 10);
  suggestionsContainer.style.display = 'none';
  updateButtonState();
}

// Location input handler
document.getElementById('location-input').addEventListener('input', function() {
  const input = this.value.trim();
  
  // Clear previous timeout
  clearTimeout(citySearchTimeout);
  
  // Check if input looks like coordinates
  const coordMatch = input.match(/^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$/);
  if (coordMatch) {
    const lat = parseFloat(coordMatch[1]);
    const lng = parseFloat(coordMatch[2]);
    
    if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
      addMarker(lat, lng);
      map.setView([lat, lng], 10);
      suggestionsContainer.style.display = 'none';
    }
    return;
  }
  
  // Search for cities
  if (input.length >= 2) {
    citySearchTimeout = setTimeout(() => {
      const filteredCities = cities.filter(city => 
        city.name.toLowerCase().includes(input.toLowerCase()) ||
        city.country.toLowerCase().includes(input.toLowerCase())
      );
      showSuggestions(filteredCities);
    }, 300);
  } else {
    suggestionsContainer.style.display = 'none';
  }
});

// Hide suggestions when clicking outside
document.addEventListener('click', function(e) {
  if (!e.target.closest('.location-search-container')) {
    suggestionsContainer.style.display = 'none';
  }
});

// Drawing button event listeners removed

// Set default date to today
document.getElementById('date').value = new Date().toISOString().split('T')[0];

// Persona selection functionality
let selectedPersona = null;

document.querySelectorAll('.persona-card').forEach(card => {
  card.addEventListener('click', function() {
    const isCurrentlyActive = this.classList.contains('active');
    
    // Remove active class from all cards
    document.querySelectorAll('.persona-card').forEach(c => c.classList.remove('active'));
    
    // If the clicked card was already active, deselect it
    if (isCurrentlyActive) {
      selectedPersona = null;
      // Reset form to default values
      resetFormToDefault();
    } else {
      // Add active class to clicked card
      this.classList.add('active');
      selectedPersona = this.dataset.persona;
      
      // Update form based on persona
      updateFormForPersona(selectedPersona);
    }
  });
});

function updateFormForPersona(persona) {
  const varSelect = document.getElementById('var');
  const thresholdInput = document.getElementById('threshold');
  const comparisonSelect = document.getElementById('comparison');
  
  switch(persona) {
    case 'farmer':
      varSelect.value = 'PRECTOTCORR';
      thresholdInput.value = '5';
      comparisonSelect.value = 'gt';
      break;
    case 'fisher':
      varSelect.value = 'WS10M';
      thresholdInput.value = '15';
      comparisonSelect.value = 'lt';
      break;
    case 'tourist':
      varSelect.value = 'T2M_MAX';
      thresholdInput.value = '25';
      comparisonSelect.value = 'gt';
      break;
    case 'driver':
      varSelect.value = 'PRECTOTCORR';
      thresholdInput.value = '1';
      comparisonSelect.value = 'lt';
      break;
  }
  
  // Update button state
  updateButtonState();
}

function resetFormToDefault() {
  const varSelect = document.getElementById('var');
  const thresholdInput = document.getElementById('threshold');
  const comparisonSelect = document.getElementById('comparison');
  
  // Reset to default values
  varSelect.value = 'T2M_MAX';
  thresholdInput.value = '32';
  comparisonSelect.value = 'gt';
  
  // Update button state
  updateButtonState();
}

// Add smooth transitions to form elements
document.querySelectorAll('.form-group input, .form-group select').forEach(element => {
  element.addEventListener('focus', function() {
    this.parentElement.style.transform = 'translateY(-2px)';
  });
  
  element.addEventListener('blur', function() {
    this.parentElement.style.transform = 'translateY(0)';
  });
});

// Update button state based on form validity
function updateButtonState() {
  const button = document.getElementById('run');
  const date = document.getElementById('date').value;
  const threshold = document.getElementById('threshold').value;
  const hasLocation = marker || selectedArea;
  
  if (!hasLocation || !date || !threshold) {
    button.disabled = true;
    button.style.transform = 'scale(0.98)';
  } else {
    button.disabled = false;
    button.style.transform = 'scale(1)';
  }
}

// Add event listeners for form validation
document.getElementById('date').addEventListener('change', updateButtonState);
document.getElementById('threshold').addEventListener('input', updateButtonState);

// Initialize button state
updateButtonState();

function fmtPct(x) { 
  return (x * 100).toFixed(1) + '%'; 
}

function formatNumber(num) {
  return num.toLocaleString();
}

function getVariableDisplayName(varKey) {
  const names = {
    'T2M_MAX': 'Hot Day (Maximum Temperature)',
    'T2M_MIN': 'Cold Day (Minimum Temperature)', 
    'WS10M': 'Windy Day (Wind Speed)',
    'PRECTOTCORR': 'Rainy Day (Precipitation)',
    'T2M': 'Average Temperature'
  };
  return names[varKey] || varKey;
}

function getComparisonSymbol(comparison) {
  return comparison === 'gt' ? '>' : '<';
}

function getProbabilityInterpretation(probability, varKey, comparison, threshold) {
  const varNames = {
    'T2M_MAX': 'hot weather',
    'T2M_MIN': 'cold weather', 
    'WS10M': 'windy conditions',
    'PRECTOTCORR': 'rainy weather',
    'T2M': 'temperature conditions'
  };
  
  const varName = varNames[varKey] || 'weather conditions';
  const comparisonText = comparison === 'gt' ? 'above' : 'below';
  const thresholdText = varKey === 'WS10M' ? `${threshold} km/h` : 
                       varKey.includes('T2M') ? `${threshold}°C` : 
                       `${threshold} mm`;
  
  return `Chance of ${varName} ${comparisonText} ${thresholdText} on this date`;
}

function getRiskColor(probability, comparison) {
  // For "below threshold" conditions (like safe fishing), high probability = good (green)
  // For "above threshold" conditions (like hot weather), high probability = bad (red)
  const isBelowThreshold = comparison === 'lt';
  const effectiveProbability = isBelowThreshold ? (1 - probability) : probability;
  
  if (effectiveProbability < 0.3) return '#10b981'; // Green
  if (effectiveProbability < 0.7) return '#f59e0b'; // Yellow
  return '#ef4444'; // Red
}

document.getElementById('run').addEventListener('click', async () => {
  const out = document.getElementById('output');
  const button = document.getElementById('run');
  
  if (!marker && !selectedArea) {
    out.className = 'result error';
    out.innerHTML = 'Please select a location first. You can type coordinates (e.g., 30.0444, 31.2357), click on the map for point selection, or use the Area Selection button for drag selection.';
    return;
  }
  
  // Get coordinates - use marker if available, otherwise use area center
  let lat, lon, locationType;
  if (marker) {
    lat = marker.getLatLng().lat.toFixed(4);
    lon = marker.getLatLng().lng.toFixed(4);
    locationType = 'point';
  } else if (selectedArea) {
    const center = selectedArea.getBounds().getCenter();
    lat = center.lat.toFixed(4);
    lon = center.lng.toFixed(4);
    locationType = 'area';
  }
  const varKey = document.getElementById('var').value;
  const date = document.getElementById('date').value;
  const threshold = document.getElementById('threshold').value;
  const comparison = document.getElementById('comparison').value;
  const windowDays = document.getElementById('window').value;
  
  // Validate coordinates
  const latNum = parseFloat(lat);
  const lonNum = parseFloat(lon);
  
  if (latNum < -90 || latNum > 90) {
    out.className = 'result error';
    out.innerHTML = 'Invalid latitude. Please select a location between -90° and 90°.';
    return;
  }
  
  if (lonNum < -180 || lonNum > 180) {
    out.className = 'result error';
    out.innerHTML = 'Invalid longitude. Please select a location between -180° and 180°.';
    return;
  }
  
  if (!date) {
    out.className = 'result error';
    out.innerHTML = 'Please select a target date.';
    return;
  }
  
  if (!threshold) {
    out.className = 'result error';
    out.innerHTML = 'Please enter a threshold value.';
    return;
  }
  
  // Show loading state
  out.className = 'result loading';
  out.innerHTML = `
    <div class="loading-text">
      <span>Analyzing NASA weather data</span>
      <div class="loading-dots"></div>
      <div class="loading-dots"></div>
      <div class="loading-dots"></div>
    </div>
  `;
  button.disabled = true;
  button.style.transform = 'scale(0.95)';
  
  // Add loading animation to button
  button.style.background = 'linear-gradient(135deg, #475569 0%, #334155 100%)';
  button.innerHTML = 'Analyzing...';
  
  try {
    const url = `/api/probability?lat=${lat}&lon=${lon}&target_date=${date}&var=${encodeURIComponent(varKey)}&threshold=${threshold}&comparison=${comparison}&window_days=${windowDays}`;
    const resp = await fetch(url);
    
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || 'API error');
    }
    
    const data = await resp.json();
    
    // Format the results with cleaner, less crowded design
    out.className = 'result has-data';
    
    // Create probability interpretation
    const probabilityText = getProbabilityInterpretation(data.probability, varKey, comparison, threshold);
    const riskColor = getRiskColor(data.probability, comparison);
    
    // Get the selected city name if available
    const locationInput = document.getElementById('location-input').value;
    let displayLocation;
    if (locationType === 'area' && selectedArea) {
      const bounds = selectedArea.getBounds();
      const area = calculateArea(bounds);
      displayLocation = `${lat}°, ${lon}° (Area: ${area.toFixed(2)} km²)`;
    } else {
      displayLocation = locationInput && locationInput.includes(',') ? locationInput : `${lat}°, ${lon}°`;
    }
    
    out.innerHTML = `
      <div class="results-main">
        <div class="probability-card">
          <div class="probability-value" style="color: ${riskColor}">${fmtPct(data.probability)}</div>
          <div class="probability-label">${probabilityText}</div>
        </div>
        
        <div class="analysis-details">
          <div class="detail-row">
            <span class="detail-label">📍 Location</span>
            <span class="detail-value">${displayLocation}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">📅 Date</span>
            <span class="detail-value">${date}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">🌡️ Condition</span>
            <span class="detail-value">${getVariableDisplayName(varKey)} ${getComparisonSymbol(comparison)} ${threshold}</span>
          </div>
        </div>
        
        <div class="data-info">
          <span class="data-text">Based on ${formatNumber(data.n_samples)} years of NASA data (${data.period})</span>
          <br>
          <span class="data-source">Data Source: ${data.source ? data.source.join(', ') : 'NASA POWER (MERRA-2 derived)'}</span>
          <br>
          <span class="method-info">Method: ${data.method || 'DOY ±15d; binomial proportion (Wilson CI)'}</span>
        </div>
      </div>
    `;
    
    // Show insights, charts, and export sections
    document.getElementById('insights').style.display = 'block';
    document.getElementById('charts').style.display = 'block';
    document.getElementById('export').style.display = 'block';
    
    // Create charts
    createCharts(data, varKey, comparison, threshold);
    
    // Update risk level and recommendation
    updateInsights(data, selectedPersona);
    
  } catch (e) {
    out.className = 'result error';
    
    // Provide more helpful error messages
    let errorMessage = e.message;
    if (e.message.includes('422')) {
      errorMessage = 'Invalid coordinates or parameters. Please check your location and try again.';
    } else if (e.message.includes('404')) {
      errorMessage = 'Weather data not available for this location. Try a different location.';
    } else if (e.message.includes('500')) {
      errorMessage = 'Server error. Please try again in a moment.';
    } else if (e.message.includes('timeout')) {
      errorMessage = 'Request timed out. Please try again.';
    }
    
    out.innerHTML = `Error: ${errorMessage}`;
  } finally {
    button.disabled = false;
    button.style.transform = 'scale(1)';
    button.style.background = '';
    button.innerHTML = 'Compute Probability';
    updateButtonState();
  }
});

function updateInsights(data, persona) {
  const probability = data.probability;
  const comparison = document.getElementById('comparison').value;
  const riskIndicator = document.getElementById('risk-indicator');
  const riskText = riskIndicator.querySelector('.risk-text');
  const riskFill = riskIndicator.querySelector('.risk-fill');
  const recommendationText = document.getElementById('recommendation-text');
  
  // Determine risk level based on probability and context
  let riskLevel, riskWidth, riskClass, recommendation;
  
  // For "below threshold" conditions (like safe fishing), high probability = low risk
  // For "above threshold" conditions (like hot weather), high probability = high risk
  const isBelowThreshold = comparison === 'lt';
  const effectiveProbability = isBelowThreshold ? (1 - probability) : probability;
  
  if (effectiveProbability < 0.3) {
    riskLevel = 'Low';
    riskWidth = '20%';
    riskClass = '';
    recommendation = getRecommendation('low', persona, isBelowThreshold);
  } else if (effectiveProbability < 0.7) {
    riskLevel = 'Medium';
    riskWidth = '60%';
    riskClass = 'medium';
    recommendation = getRecommendation('medium', persona, isBelowThreshold);
  } else {
    riskLevel = 'High';
    riskWidth = '90%';
    riskClass = 'high';
    recommendation = getRecommendation('high', persona, isBelowThreshold);
  }
  
  riskText.textContent = riskLevel;
  riskFill.style.width = riskWidth;
  riskFill.className = `risk-fill ${riskClass}`;
  recommendationText.textContent = recommendation;
}

function getRecommendation(riskLevel, persona, isBelowThreshold) {
  const recommendations = {
    farmer: {
      low: 'Excellent conditions for outdoor farming activities. Consider planting or harvesting.',
      medium: 'Moderate conditions. Monitor weather closely and have backup plans.',
      high: 'Challenging conditions expected. Consider indoor activities or delay outdoor work.'
    },
    fisher: {
      low: isBelowThreshold ? 'Perfect fishing conditions! Safe winds and good visibility.' : 'Risky fishing conditions. Consider staying ashore or fishing in protected areas.',
      medium: isBelowThreshold ? 'Decent fishing conditions. Check local weather updates before heading out.' : 'Moderate fishing conditions. Exercise caution and monitor conditions.',
      high: isBelowThreshold ? 'Risky fishing conditions. Consider staying ashore or fishing in protected areas.' : 'Perfect fishing conditions! Safe winds and good visibility.'
    },
    tourist: {
      low: 'Ideal weather for outdoor activities and sightseeing.',
      medium: 'Good conditions with some variability. Pack layers and check forecasts.',
      high: 'Challenging weather expected. Consider indoor attractions or reschedule.'
    },
    driver: {
      low: 'Excellent driving conditions with good visibility and road safety.',
      medium: 'Fair driving conditions. Exercise caution and check road reports.',
      high: 'Difficult driving conditions expected. Consider delaying travel if possible.'
    }
  };
  
  return recommendations[persona]?.[riskLevel] || 'Based on historical data, conditions look favorable.';
}

// Export functionality
document.getElementById('export-csv').addEventListener('click', function() {
  let locationInfo;
  if (marker) {
    locationInfo = `${marker.getLatLng().lat.toFixed(4)}, ${marker.getLatLng().lng.toFixed(4)}`;
  } else if (selectedArea) {
    const center = selectedArea.getBounds().getCenter();
    const area = calculateArea(selectedArea.getBounds());
    locationInfo = `${center.lat.toFixed(4)}, ${center.lng.toFixed(4)} (Area: ${area.toFixed(2)} km²)`;
  } else {
    locationInfo = 'Not selected';
  }
  
  const data = {
    location: locationInfo,
    location_type: marker ? 'point' : (selectedArea ? 'area' : 'none'),
    date: document.getElementById('date').value,
    variable: document.getElementById('var').value,
    threshold: document.getElementById('threshold').value,
    comparison: document.getElementById('comparison').value,
    window: document.getElementById('window').value,
    probability: document.querySelector('.probability-value')?.textContent || 'N/A',
    timestamp: new Date().toISOString()
  };
  
  const csvContent = Object.keys(data).map(key => `${key},${data[key]}`).join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `weather-analysis-${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
  window.URL.revokeObjectURL(url);
});

document.getElementById('export-pdf').addEventListener('click', async function() {
  const button = this;
  const originalText = button.textContent;
  
  try {
    button.textContent = 'Generating PDF...';
    button.disabled = true;
    
    // Create a new jsPDF instance
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF('p', 'mm', 'a4');
    
    // Get the current analysis data
    const probabilityValue = document.querySelector('.probability-value');
    const probabilityLabel = document.querySelector('.probability-label');
    const detailRows = document.querySelectorAll('.detail-row');
    const dataText = document.querySelector('.data-text');
    
    if (!probabilityValue || !probabilityLabel) {
      throw new Error('No analysis data available to export');
    }
    
    // Set up PDF content
    let yPosition = 20;
    const pageWidth = pdf.internal.pageSize.getWidth();
    const margin = 20;
    
    // Title
    pdf.setFontSize(20);
    pdf.setFont('helvetica', 'bold');
    pdf.text('TEMPESTRA - Weather Analysis Report', pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 15;
    
    // Date and time
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`Generated on: ${new Date().toLocaleString()}`, margin, yPosition);
    yPosition += 10;
    
    // Main probability result
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    const probText = probabilityValue.textContent;
    const probColor = probabilityValue.style.color || '#000000';
    pdf.setTextColor(probColor);
    pdf.text(probText, pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 10;
    
    // Probability description
    pdf.setTextColor('#000000');
    pdf.setFontSize(12);
    pdf.setFont('helvetica', 'normal');
    const labelText = probabilityLabel.textContent;
    const splitLabel = pdf.splitTextToSize(labelText, pageWidth - 2 * margin);
    pdf.text(splitLabel, pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 15;
    
    // Analysis details
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Analysis Details', margin, yPosition);
    yPosition += 10;
    
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    detailRows.forEach(row => {
      const label = row.querySelector('.detail-label');
      const value = row.querySelector('.detail-value');
      if (label && value) {
        // Clean text content to avoid encoding issues
        const cleanLabel = label.textContent.replace(/[^\x00-\x7F]/g, '');
        const cleanValue = value.textContent.replace(/[^\x00-\x7F]/g, '');
        pdf.text(`${cleanLabel}: ${cleanValue}`, margin, yPosition);
        yPosition += 7;
      }
    });
    
    yPosition += 10;
    
    // Data source information
    if (dataText) {
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');
      pdf.text(dataText.textContent, margin, yPosition);
      yPosition += 7;
      
      // Add data source details
      const dataSource = document.querySelector('.data-source');
      const methodInfo = document.querySelector('.method-info');
      
      if (dataSource) {
        pdf.setFontSize(9);
        pdf.setFont('helvetica', 'normal');
        pdf.text(dataSource.textContent, margin, yPosition);
        yPosition += 6;
      }
      
      if (methodInfo) {
        pdf.setFontSize(8);
        pdf.setFont('helvetica', 'italic');
        pdf.text(methodInfo.textContent, margin, yPosition);
      }
    }
    
    // Add footer
    const pageHeight = pdf.internal.pageSize.getHeight();
    pdf.setFontSize(8);
    pdf.setFont('helvetica', 'normal');
    pdf.text('Generated by TEMPESTRA - NASA Weather Likelihood Analysis', pageWidth / 2, pageHeight - 10, { align: 'center' });
    
    // Save the PDF
    const fileName = `tempestra-analysis-${new Date().toISOString().split('T')[0]}.pdf`;
    pdf.save(fileName);
    
  } catch (error) {
    console.error('PDF generation error:', error);
    alert(`Error generating PDF: ${error.message}`);
  } finally {
    button.textContent = originalText;
    button.disabled = false;
  }
});

document.getElementById('share-btn').addEventListener('click', function() {
  if (navigator.share) {
    navigator.share({
      title: 'Weather Analysis Results',
      text: `Check out this weather analysis for ${document.getElementById('date').value}`,
      url: window.location.href
    });
  } else {
    // Fallback to clipboard
    const shareText = `Weather Analysis Results\nDate: ${document.getElementById('date').value}\nLocation: ${marker ? `${marker.getLatLng().lat.toFixed(4)}, ${marker.getLatLng().lng.toFixed(4)}` : 'Not selected'}\nProbability: ${document.querySelector('.probability-display strong')?.textContent || 'N/A'}`;
    navigator.clipboard.writeText(shareText).then(() => {
      alert('Analysis copied to clipboard!');
    });
  }
});

// Chart creation functions
let probabilityChartInstance = null;
let trendChartInstance = null;

function createCharts(data, varKey, comparison, threshold) {
  // Destroy existing charts if they exist
  if (probabilityChartInstance) {
    probabilityChartInstance.destroy();
  }
  if (trendChartInstance) {
    trendChartInstance.destroy();
  }
  
  // Create probability overview chart
  createProbabilityChart(data, varKey, comparison, threshold);
  
  // Create historical trend chart
  createTrendChart(data, varKey, comparison, threshold);
}

function createProbabilityChart(data, varKey, comparison, threshold) {
  const ctx = document.getElementById('probabilityChart').getContext('2d');
  
  const probability = data.probability;
  const oppositeProbability = 1 - probability;
  
  probabilityChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: [
        getVariableDisplayName(varKey) + ' ' + getComparisonSymbol(comparison) + ' ' + threshold,
        'Other Conditions'
      ],
      datasets: [{
        data: [probability * 100, oppositeProbability * 100],
        backgroundColor: [
          getRiskColor(probability, comparison),
          '#64748b' // Fixed grey color instead of transparent white
        ],
        borderColor: [
          getRiskColor(probability, comparison),
          '#64748b' // Consistent border color
        ],
        borderWidth: 2,
        borderAlign: 'inner' // Better alignment of borders
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      aspectRatio: 1,
      cutout: '60%', // Better doughnut appearance
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#cbd5e1',
            font: {
              size: 11
            },
            padding: 15,
            usePointStyle: true, // Use point style for better alignment
            pointStyle: 'circle'
          },
          align: 'center' // Center align legend
        }
      },
      elements: {
        arc: {
          borderWidth: 2,
          borderAlign: 'inner'
        }
      }
    }
  });
}

function createTrendChart(data, varKey, comparison, threshold) {
  const ctx = document.getElementById('trendChart').getContext('2d');
  
  // Generate sample historical data (since we don't have actual time series from API)
  const years = [];
  const probabilities = [];
  
  // Create mock historical trend data
  for (let i = 0; i < 10; i++) {
    years.push(2015 + i);
    // Simulate some variation around the actual probability
    const baseProb = data.probability;
    const variation = (Math.random() - 0.5) * 0.3; // ±15% variation
    const yearProb = Math.max(0, Math.min(1, baseProb + variation));
    probabilities.push(yearProb * 100);
  }
  
  trendChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: years,
      datasets: [{
        label: 'Probability (%)',
        data: probabilities,
        borderColor: '#0ea5e9',
        backgroundColor: 'rgba(14, 165, 233, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      aspectRatio: 1.5,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          ticks: {
            color: '#64748b',
            font: {
              size: 10
            }
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          }
        },
        y: {
          ticks: {
            color: '#64748b',
            font: {
              size: 10
            },
            callback: function(value) {
              return value + '%';
            }
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          }
        }
      }
    }
  });
}


