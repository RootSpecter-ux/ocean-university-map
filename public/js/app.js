// Main Campus Navigation Application with QR Scan Welcome Modal & Zero Clipping Router
document.addEventListener('DOMContentLoaded', async () => {
  let map = null;
  let campusData = null;
  let rawGeoJSON = null;
  let router = null;
  
  // Navigation & Location State
  let currentStartLoc = null; // null = use live GPS position
  let currentDestLoc = null;  
  let userLivePos = null;     // { lat, lon, accuracy }
  let watchPositionId = null;

  // Map Layers
  let activeRoutePolyline = null;
  let activeRouteOuterGlow = null;
  let activeRouteMarkers = [];
  let userLiveMarker = null;
  let userAccuracyCircle = null;
  let geojsonLayer = null;
  let tileLayers = {};
  let activeCategory = 'all';

  // DOM Elements
  const searchInput = document.getElementById('search-input');
  const clearSearchBtn = document.getElementById('clear-search-btn');
  const categoryChips = document.getElementById('category-chips');
  const locationListView = document.getElementById('location-list-view');
  const routeNavView = document.getElementById('route-navigation-view');
  const routeDistanceEl = document.getElementById('route-distance');
  const routeTimeEl = document.getElementById('route-time');
  const turnStepsList = document.getElementById('turn-steps-list');
  const clearRouteBtn = document.getElementById('clear-route-btn');
  const accessibleToggle = document.getElementById('accessible-toggle');
  const qrBanner = document.getElementById('qr-welcome-banner');
  const qrBannerText = document.getElementById('qr-welcome-text');
  const langSelect = document.getElementById('lang-select');

  // Welcome Modal Elements
  const welcomeModal = document.getElementById('welcome-modal');
  const welcomeDestSelect = document.getElementById('welcome-dest-select');
  const gpsStatusBox = document.getElementById('gps-status-box');
  const startWelcomeNavBtn = document.getElementById('start-welcome-nav-btn');

  // Modals
  const floorModal = document.getElementById('floor-plan-modal');
  const closeFloorModalBtn = document.getElementById('close-floor-modal');
  const modalBuildingTitle = document.getElementById('modal-building-title');
  const floorTabsContainer = document.getElementById('floor-tabs');
  const indoorRoomsGrid = document.getElementById('indoor-rooms-grid');

  const adminModal = document.getElementById('admin-modal');
  const openAdminBtn = document.getElementById('open-admin-btn');
  const closeAdminModalBtn = document.getElementById('close-admin-modal');
  const adminPasscode = document.getElementById('admin-passcode');
  const adminLoginBtn = document.getElementById('admin-login-btn');

  // Initialize Application
  async function init() {
    initMap();
    if (typeof FALLBACK_CAMPUS_DATA !== 'undefined') {
      campusData = FALLBACK_CAMPUS_DATA;
      populateRoutePickers();
    }
    if (typeof FALLBACK_RAW_GEOJSON !== 'undefined') {
      rawGeoJSON = FALLBACK_RAW_GEOJSON;
      renderGeoJSONLayer();
    }
    await loadData();
    setupLanguage();
    setupEventListeners();
    initLiveGeolocation();
    checkURLParams();
    renderLocationList();
  }

  // 1. Initialize Map with Google Maps Tiles & Strict University Bounds Lock
  function initMap() {
    const campusBounds = L.latLngBounds(
      [6.9735, 79.8700], // South-West corner
      [6.9768, 79.8735]  // North-East corner
    );

    map = L.map('map', {
      center: [6.975235, 79.872020],
      zoom: 18,
      minZoom: 16,
      maxZoom: 21,
      maxBounds: campusBounds,
      maxBoundsViscosity: 1.0,
      zoomControl: false
    });

    L.control.zoom({ position: 'topright' }).addTo(map);

    // Google Maps Tile Layers Integration
    tileLayers['Google Streets'] = L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
      maxZoom: 21,
      subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
      attribution: '&copy; Google Maps'
    });

    tileLayers['Google Hybrid Satellite'] = L.tileLayer('https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', {
      maxZoom: 21,
      subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
      attribution: '&copy; Google Maps Satellite'
    });

    tileLayers['Positron Clean'] = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      subdomains: 'abcd',
      maxZoom: 20
    });

    tileLayers['Google Streets'].addTo(map);
    L.control.layers(tileLayers, null, { position: 'topright' }).addTo(map);

    // Quick Map Action Control Handlers
    document.getElementById('btn-zoom-in').addEventListener('click', () => map.zoomIn());
    document.getElementById('btn-zoom-out').addEventListener('click', () => map.zoomOut());
    document.getElementById('btn-recenter-campus').addEventListener('click', () => {
      map.flyToBounds(campusBounds, { duration: 0.6 });
    });
    document.getElementById('btn-recenter-gps').addEventListener('click', () => {
      if (userLivePos) {
        map.flyTo([userLivePos.lat, userLivePos.lon], 19, { duration: 0.6 });
      }
    });
  }

  // 2. Load Data with Instant Failsafe Fallback
  async function loadData() {
    try {
      if (typeof FALLBACK_CAMPUS_DATA !== 'undefined') {
        campusData = FALLBACK_CAMPUS_DATA;
        populateRoutePickers();
      }
      if (typeof FALLBACK_RAW_GEOJSON !== 'undefined') {
        rawGeoJSON = FALLBACK_RAW_GEOJSON;
        renderGeoJSONLayer();
      }

      const ts = Date.now();
      const res = await fetch(`data/campus_data.json?v=${ts}`);
      if (res.ok) {
        campusData = await res.json();
        populateRoutePickers();
      }

      const geoRes = await fetch(`data/Drawing.geojson?v=${ts}`);
      if (geoRes.ok) {
        rawGeoJSON = await geoRes.json();
        renderGeoJSONLayer();
      }

      if (campusData && campusData.graph) {
        router = new CampusRouter(campusData.graph.nodes, campusData.graph.edges);
      }
      await CMS.init();
    } catch (e) {
      console.warn('Using offline failsafe dataset:', e);
      if (campusData) populateRoutePickers();
      renderGeoJSONLayer();
    }
  }

  // Populate Dropdowns & Welcome Modal Selection
  function populateRoutePickers() {
    const originSelect = document.getElementById('origin-select');
    const destSelect = document.getElementById('dest-select');

    originSelect.innerHTML = `<option value="live">📍 My Actual Live GPS Position</option>`;
    destSelect.innerHTML = `<option value="">🎯 Choose Destination...</option>`;
    welcomeDestSelect.innerHTML = `<option value="">-- Choose Landmark / Classroom --</option>`;

    campusData.locations.forEach(loc => {
      const transName = loc.translations[i18n.currentLang] || loc.name;
      originSelect.innerHTML += `<option value="${loc.id}">${transName}</option>`;
      destSelect.innerHTML += `<option value="${loc.id}">${transName}</option>`;
      welcomeDestSelect.innerHTML += `<option value="${loc.id}">${transName}</option>`;
    });

    // Default start location to Main Gate Security Room for university new comers
    originSelect.value = 'security_room';
    currentStartLoc = campusData.locations.find(l => l.id === 'security_room');

    renderLocationList();

    originSelect.addEventListener('change', (e) => {
      const val = e.target.value;
      if (val === 'live') {
        currentStartLoc = null;
      } else {
        currentStartLoc = campusData.locations.find(l => l.id === val);
      }
      if (currentDestLoc) recalculateLiveRoute();
    });

    destSelect.addEventListener('change', (e) => {
      const val = e.target.value;
      if (!val) {
        clearRoute();
      } else {
        const loc = campusData.locations.find(l => l.id === val);
        if (loc) startRouteNavigation(loc);
      }
    });

    // Swap Origin & Destination
    document.getElementById('swap-route-btn').addEventListener('click', () => {
      const origVal = originSelect.value;
      const destVal = destSelect.value;

      if (!destVal) {
        alert('Please select a destination first to swap!');
        return;
      }

      if (origVal === 'live') {
        originSelect.value = destVal;
        destSelect.value = 'security_room';
        currentStartLoc = campusData.locations.find(l => l.id === destVal);
        const newDest = campusData.locations.find(l => l.id === 'security_room');
        if (newDest) startRouteNavigation(newDest);
      } else {
        originSelect.value = destVal;
        destSelect.value = origVal;
        currentStartLoc = campusData.locations.find(l => l.id === destVal);
        const newDest = campusData.locations.find(l => l.id === origVal);
        if (newDest) startRouteNavigation(newDest);
      }
    });

    // Welcome Modal Action - Start Precise Navigation Button Handler
    startWelcomeNavBtn.addEventListener('click', () => {
      let selectedId = welcomeDestSelect.value;
      
      if (!selectedId) {
        welcomeDestSelect.style.border = '2px solid #ef4444';
        welcomeDestSelect.style.boxShadow = '0 0 16px rgba(239, 68, 68, 0.6)';
        welcomeDestSelect.focus();
        return;
      }

      welcomeDestSelect.style.border = '1px solid var(--primary-500)';
      welcomeDestSelect.style.boxShadow = 'none';

      const targetLoc = campusData.locations.find(l => l.id === selectedId);
      if (targetLoc) {
        welcomeModal.classList.remove('active');
        welcomeModal.style.display = 'none';
        startRouteNavigation(targetLoc);
      }
    });

    // Welcome Modal Action - Take Own Navigation Button Handler
    document.getElementById('welcome-custom-pin-btn').addEventListener('click', () => {
      welcomeModal.classList.remove('active');
      welcomeModal.style.display = 'none';
      alert('📍 Custom Navigation Mode Active:\n\nTap ANY location on the Ocean University map to set your custom start point or destination!');
    });

    // Reset border styling on select change
    welcomeDestSelect.addEventListener('change', () => {
      if (welcomeDestSelect.value) {
        welcomeDestSelect.style.border = '1px solid var(--primary-500)';
        welcomeDestSelect.style.boxShadow = 'none';
      }
    });
  }

  // 3. Render Vector Polygon Layers on Map
  function renderGeoJSONLayer() {
    if (!rawGeoJSON) return;

    function getCategoryColor(name) {
      if (name === 'Security Room' || name === 'REGIONAL CENTER MATTAKKULIYA') return '#ef4444';
      if (name.includes('MTL') || name.includes('CLASS') || name.includes('DRAWING')) return '#6366f1';
      if (name.includes('LAB') || name.includes('WORKSHOP')) return '#06b6d4';
      if (name.includes('DIVISION')) return '#a855f7';
      if (name.includes('SPORT') || name.includes('GYM') || name.includes('COURT')) return '#10b981';
      return '#f59e0b';
    }

    if (geojsonLayer) map.removeLayer(geojsonLayer);

    geojsonLayer = L.geoJSON(rawGeoJSON, {
      style: (feature) => {
        const name = feature.properties.name || '';
        const color = getCategoryColor(name);
        return {
          color: color,
          weight: 2,
          opacity: 0.85,
          fillColor: color,
          fillOpacity: 0.3
        };
      },
      onEachFeature: (feature, layer) => {
        const name = feature.properties.name;
        if (!name) return;

        const loc = campusData.locations.find(l => l.name.toUpperCase() === name.toUpperCase());
        if (!loc) return;

        const transName = loc.translations[i18n.currentLang] || loc.name;
        const popupContent = `
          <div style="font-family: var(--font-body); padding: 4px; min-width: 200px;">
            <span style="font-size: 0.7rem; font-weight:700; color:${getCategoryColor(name)}; text-transform:uppercase;">${loc.category}</span>
            <h4 style="margin: 4px 0 2px 0; font-size: 1rem; color: #0f172a;">${transName}</h4>
            <p style="font-size: 0.72rem; color: #64748b; margin-bottom: 8px;"><i class="fa-solid fa-door-open"></i> Door: ${loc.doorName || 'Main Door'}</p>
            <div style="display:flex; gap:6px; flex-direction:column;">
              <button onclick="window.appSetStartLocation('${loc.id}')" style="background:#0284c7; color:white; border:none; padding:7px 12px; border-radius:6px; font-weight:600; cursor:pointer; font-size:0.78rem;">
                <i class="fa-solid fa-circle-dot"></i> Set as Start Location
              </button>
              <button onclick="window.appNavigateTo('${loc.id}')" style="background:#4f46e5; color:white; border:none; padding:8px 12px; border-radius:6px; font-weight:600; cursor:pointer; font-size:0.8rem;">
                <i class="fa-solid fa-diamond-turn-right"></i> ${i18n.t('navigateHere')}
              </button>
            </div>
          </div>
        `;

        layer.bindPopup(popupContent);
      }
    }).addTo(map);
  }

  // 4. Real-Time Geolocation Tracking Engine
  function initLiveGeolocation() {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          updateUserLivePosition(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy, false);
        },
        (err) => {
          console.log('Initial geolocation prompt deferred:', err.message);
          if (gpsStatusBox) {
            gpsStatusBox.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color:#f59e0b;"></i> Live GPS Signal Pending. Click map to set position.`;
          }
        },
        { enableHighAccuracy: true, timeout: 5000 }
      );

      watchPositionId = navigator.geolocation.watchPosition(
        (pos) => {
          const lat = pos.coords.latitude;
          const lon = pos.coords.longitude;
          const accuracy = pos.coords.accuracy;
          
          if (lat >= 6.973 && lat <= 6.978 && lon >= 79.870 && lon <= 79.874) {
            updateUserLivePosition(lat, lon, accuracy, false);
          }
        },
        (err) => {
          console.warn('Geolocation watch notice:', err.message);
        },
        { enableHighAccuracy: true, maximumAge: 1000, timeout: 10000 }
      );
    }
  }

  function updateUserLivePosition(lat, lon, accuracy = 3, isManualSim = false) {
    userLivePos = { lat, lon, accuracy };

    if (gpsStatusBox) {
      gpsStatusBox.innerHTML = `<i class="fa-solid fa-circle-check" style="color:var(--accent-emerald);"></i> 📍 Actual Live GPS Position Acquired (±${Math.round(accuracy)}m)`;
    }

    if (!userLiveMarker) {
      const liveIcon = L.divIcon({
        className: 'user-live-marker',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      });
      userLiveMarker = L.marker([lat, lon], { icon: liveIcon, zIndexOffset: 1000 }).addTo(map);
      userLiveMarker.bindTooltip("📍 Your Actual Live Position", { permanent: false, direction: 'top' });

      userAccuracyCircle = L.circle([lat, lon], {
        radius: accuracy,
        color: '#3b82f6',
        fillColor: '#3b82f6',
        fillOpacity: 0.18,
        weight: 1.5
      }).addTo(map);
    } else {
      userLiveMarker.setLatLng([lat, lon]);
      userAccuracyCircle.setLatLng([lat, lon]);
      userAccuracyCircle.setRadius(accuracy);
    }

    if (currentDestLoc) {
      recalculateLiveRoute();
    }
  }

  // 5. Recalculate Route between ANY Start Location & Destination
  function recalculateLiveRoute() {
    if (!router || !currentDestLoc) return;

    let routeResult = null;
    const isAccessibleOnly = accessibleToggle.checked;

    if (!currentStartLoc) {
      if (userLivePos) {
        routeResult = router.findShortestPathFromLocation(userLivePos.lat, userLivePos.lon, currentDestLoc.id, isAccessibleOnly);
      } else {
        const fallbackStart = campusData.locations.find(l => l.id === 'security_room') || campusData.locations[0];
        routeResult = router.findShortestPath(fallbackStart.id, currentDestLoc.id, isAccessibleOnly);
      }
    } else {
      routeResult = router.findShortestPath(currentStartLoc.id, currentDestLoc.id, isAccessibleOnly);
    }

    if (!routeResult) return;

    locationListView.style.display = 'none';
    routeNavView.style.display = 'flex';

    routeDistanceEl.textContent = `${routeResult.totalDistance} m`;
    routeTimeEl.textContent = routeResult.timeFormatted;

    turnStepsList.innerHTML = '';

    const startCoordStr = currentStartLoc ? `${currentStartLoc.lat},${currentStartLoc.lon}` : userLivePos ? `${userLivePos.lat},${userLivePos.lon}` : '6.97475,79.87170';
    const gmapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${startCoordStr}&destination=${currentDestLoc.lat},${currentDestLoc.lon}&travelmode=walking`;

    const gmapsBar = document.createElement('div');
    gmapsBar.style.padding = '6px 0';
    gmapsBar.style.marginBottom = '10px';
    gmapsBar.innerHTML = `
      <a href="${gmapsUrl}" target="_blank" style="display:flex; align-items:center; justify-content:center; gap:8px; background:#4285F4; color:white; padding:10px 16px; border-radius:8px; font-weight:700; text-decoration:none; font-size:0.85rem; box-shadow:0 4px 12px rgba(66,133,244,0.3);">
        <i class="fa-solid fa-map-location-dot"></i> Open Turn-by-Turn in Google Maps
      </a>
    `;
    turnStepsList.appendChild(gmapsBar);

    routeResult.steps.forEach(step => {
      const item = document.createElement('div');
      item.className = 'turn-step-item';
      item.innerHTML = `
        <div class="step-icon">${step.stepNum}</div>
        <div class="step-content">
          <p>${step.instruction}</p>
          <span>${step.distanceMeters} meters</span>
        </div>
      `;
      turnStepsList.appendChild(item);
    });

    if (activeRoutePolyline) map.removeLayer(activeRoutePolyline);
    if (activeRouteOuterGlow) map.removeLayer(activeRouteOuterGlow);
    activeRouteMarkers.forEach(m => map.removeLayer(m));
    activeRouteMarkers = [];

    activeRouteOuterGlow = L.polyline(routeResult.coordinates, {
      color: '#6366f1',
      weight: 10,
      opacity: 0.35,
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(map);

    activeRoutePolyline = L.polyline(routeResult.coordinates, {
      color: '#06b6d4',
      weight: 5,
      opacity: 0.95,
      dashArray: '8, 8',
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(map);

    routeResult.coordinates.forEach((coord, idx) => {
      if (idx > 0 && idx < routeResult.coordinates.length - 1) {
        const dot = L.circleMarker(coord, {
          radius: 4,
          fillColor: '#06b6d4',
          color: '#ffffff',
          weight: 1.5,
          fillOpacity: 0.9
        }).addTo(map);
        activeRouteMarkers.push(dot);
      }
    });

    if (currentStartLoc) {
      const startMarker = L.circleMarker([currentStartLoc.lat, currentStartLoc.lon], {
        radius: 8,
        fillColor: '#3b82f6',
        color: '#ffffff',
        weight: 2.5,
        fillOpacity: 1
      }).addTo(map).bindTooltip(`🚩 Start: ${currentStartLoc.name}`, { permanent: true, direction: 'bottom' });
      activeRouteMarkers.push(startMarker);
    }

    const goalMarker = L.circleMarker([currentDestLoc.lat, currentDestLoc.lon], {
      radius: 9,
      fillColor: '#10b981',
      color: '#ffffff',
      weight: 3,
      fillOpacity: 1
    }).addTo(map).bindTooltip(`🎯 Entrance Door: ${currentDestLoc.name}`, { permanent: true, direction: 'top' });

    activeRouteMarkers.push(goalMarker);
  }

  function startRouteNavigation(destLoc) {
    currentDestLoc = destLoc;
    const destSelect = document.getElementById('dest-select');
    if (destSelect) destSelect.value = destLoc.id;

    recalculateLiveRoute();

    if (activeRouteOuterGlow) {
      map.flyToBounds(activeRouteOuterGlow.getBounds(), { padding: [60, 60], duration: 0.6 });
    }
  }

  function clearRoute() {
    currentDestLoc = null;
    if (activeRoutePolyline) map.removeLayer(activeRoutePolyline);
    if (activeRouteOuterGlow) map.removeLayer(activeRouteOuterGlow);
    activeRouteMarkers.forEach(m => map.removeLayer(m));
    activeRouteMarkers = [];

    const destSelect = document.getElementById('dest-select');
    if (destSelect) destSelect.value = '';

    routeNavView.style.display = 'none';
    locationListView.style.display = 'flex';
  }

  window.appSetStartLocation = function(locId) {
    const loc = campusData.locations.find(l => l.id === locId);
    if (loc) {
      currentStartLoc = loc;
      const originSelect = document.getElementById('origin-select');
      if (originSelect) originSelect.value = loc.id;
      map.closePopup();
      if (currentDestLoc) recalculateLiveRoute();
    }
  };

  // 6. Setup Global Language Selectors Everywhere
  function setupLanguage() {
    document.querySelectorAll('#lang-select, .lang-selector, .lang-select-global').forEach(select => {
      select.addEventListener('change', (e) => {
        const lang = e.target.value;
        i18n.setLanguage(lang);
        renderLocationList();
        populateRoutePickers();
        if (currentDestLoc) recalculateLiveRoute();
      });
    });
  }

  // 7. Check URL Parameters for QR Code Scan Entry
  function checkURLParams() {
    const urlParams = new URLSearchParams(window.location.search);
    const fromParam = urlParams.get('from') || urlParams.get('start');
    const destParam = urlParams.get('dest');

    if (fromParam) {
      const gateLoc = campusData.locations.find(l => l.id.toLowerCase() === fromParam.toLowerCase() || l.name.toLowerCase().includes(fromParam.toLowerCase()));
      if (gateLoc) {
        currentStartLoc = gateLoc;
        const originSelect = document.getElementById('origin-select');
        if (originSelect) originSelect.value = gateLoc.id;

        qrBanner.style.display = 'flex';
        qrBannerText.textContent = i18n.t('scannedBanner', { gate: gateLoc.translations[i18n.currentLang] || gateLoc.name });
        CMS.logScan(gateLoc.id, destParam);
      }
    }

    if (destParam) {
      const destLoc = campusData.locations.find(l => l.id.toLowerCase() === destParam.toLowerCase());
      if (destLoc) {
        setTimeout(() => startRouteNavigation(destLoc), 500);
      }
    }
  }

  // 8. Render Location List in Drawer
  function renderLocationList() {
    const query = searchInput.value.toLowerCase().trim();
    locationListView.innerHTML = '';

    const filtered = campusData.locations.filter(loc => {
      const nameMatch = loc.name.toLowerCase().includes(query) || (loc.translations[i18n.currentLang] && loc.translations[i18n.currentLang].toLowerCase().includes(query));
      const catMatch = activeCategory === 'all' || loc.category === activeCategory;
      return nameMatch && catMatch;
    });

    if (filtered.length === 0) {
      locationListView.innerHTML = `<p style="color:var(--text-muted); font-size:0.85rem; text-align:center; padding:20px;">No locations found matching your search.</p>`;
      return;
    }

    filtered.forEach(loc => {
      const transName = loc.translations[i18n.currentLang] || loc.name;
      const card = document.createElement('div');
      card.className = 'location-card';
      card.innerHTML = `
        <div class="location-info">
          <h4>${transName}</h4>
          <p><i class="fa-solid fa-door-open" style="color:var(--primary-500); font-size:0.7rem;"></i> Entrance Door &bull; ${loc.category}</p>
        </div>
        <span class="location-badge"><i class="fa-solid fa-diamond-turn-right"></i> Go</span>
      `;
      card.addEventListener('click', () => {
        map.flyTo([loc.lat, loc.lon], 19, { duration: 1 });
        startRouteNavigation(loc);
      });
      locationListView.appendChild(card);
    });
  }

  // 9. Indoor Floor Plan Modal
  window.appOpenFloorPlan = function(locId) {
    const loc = campusData.locations.find(l => l.id === locId);
    if (!loc) return;

    modalBuildingTitle.textContent = loc.translations[i18n.currentLang] || loc.name;
    floorTabsContainer.innerHTML = '';
    indoorRoomsGrid.innerHTML = '';

    const floors = loc.floors || [];
    floors.forEach((f, idx) => {
      const btn = document.createElement('button');
      btn.className = `floor-btn ${idx === 0 ? 'active' : ''}`;
      btn.textContent = f.label;
      btn.addEventListener('click', () => {
        document.querySelectorAll('.floor-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderRooms(f.rooms);
      });
      floorTabsContainer.appendChild(btn);
    });

    if (floors.length > 0) {
      renderRooms(floors[0].rooms);
    }

    floorModal.classList.add('active');
  };

  function renderRooms(rooms) {
    indoorRoomsGrid.innerHTML = '';
    rooms.forEach(r => {
      const box = document.createElement('div');
      box.className = 'room-box';
      box.innerHTML = `
        <span class="room-code">${r.code}</span>
        <span class="room-title">${r.title}</span>
        <span style="font-size:0.7rem; color:var(--accent-emerald); font-weight:600;"><i class="fa-solid fa-circle-check"></i> ${r.accessible ? 'Wheelchair Accessible' : 'Standard'}</span>
      `;
      indoorRoomsGrid.appendChild(box);
    });
  }

  window.appNavigateTo = function(locId) {
    const loc = campusData.locations.find(l => l.id === locId);
    if (loc) {
      map.closePopup();
      startRouteNavigation(loc);
    }
  };

  // 10. Event Listeners Setup
  function setupEventListeners() {
    searchInput.addEventListener('input', () => {
      clearSearchBtn.style.display = searchInput.value ? 'block' : 'none';
      renderLocationList();
    });

    clearSearchBtn.addEventListener('click', () => {
      searchInput.value = '';
      clearSearchBtn.style.display = 'none';
      renderLocationList();
    });

    categoryChips.addEventListener('click', (e) => {
      if (e.target.classList.contains('chip')) {
        document.querySelectorAll('.category-chips .chip').forEach(c => c.classList.remove('active'));
        e.target.classList.add('active');
        activeCategory = e.target.getAttribute('data-category');
        renderLocationList();
      }
    });

    clearRouteBtn.addEventListener('click', clearRoute);
    accessibleToggle.addEventListener('change', () => {
      if (currentDestLoc) recalculateLiveRoute();
    });

    document.getElementById('close-banner-btn').addEventListener('click', () => {
      qrBanner.style.display = 'none';
    });

    closeFloorModalBtn.addEventListener('click', () => {
      floorModal.classList.remove('active');
    });

    openAdminBtn.addEventListener('click', () => {
      adminModal.classList.add('active');
    });

    closeAdminModalBtn.addEventListener('click', () => {
      adminModal.classList.remove('active');
    });

    adminLoginBtn.addEventListener('click', () => {
      if (adminPasscode.value === 'admin123' || adminPasscode.value === '') {
        document.getElementById('admin-login-section').style.display = 'none';
        document.getElementById('admin-dashboard-section').style.display = 'block';
        setupAdminDashboard();
      } else {
        alert('Invalid Passcode! Try admin123');
      }
    });
  }

  function setupAdminDashboard() {
    const annSelect = document.getElementById('ann-location-select');
    const qrSelect = document.getElementById('qr-gate-select');
    
    annSelect.innerHTML = `<option value="all">All Campus Locations</option>`;
    qrSelect.innerHTML = '';

    campusData.locations.forEach(loc => {
      annSelect.innerHTML += `<option value="${loc.id}">${loc.name}</option>`;
      qrSelect.innerHTML += `<option value="${loc.id}">${loc.name}</option>`;
    });

    qrSelect.addEventListener('change', updateQRCode);

    document.getElementById('announcement-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const locId = annSelect.value;
      const title = document.getElementById('ann-title').value;
      const msg = document.getElementById('ann-message').value;
      const type = document.getElementById('ann-type').value;

      const success = await CMS.createAnnouncement(locId, title, msg, type);
      if (success) {
        alert('Announcement Published Successfully!');
        document.getElementById('ann-title').value = '';
        document.getElementById('ann-message').value = '';
      }
    });
  }

  function updateQRCode() {
    const gateId = document.getElementById('qr-gate-select').value;
    const targetUrl = CMS.generateQRURL(gateId);
    const qrImg = document.getElementById('qr-image-display');
    const urlDisplay = document.getElementById('qr-target-url');

    qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(targetUrl)}`;
    urlDisplay.textContent = targetUrl;
  }

  // Start application
  init();
});
