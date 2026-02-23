/**
 * Estate Map View - Load and display estate data on Mapbox
 */

// Mapbox access token
mapboxgl.accessToken = 'YOUR_MAPBOX_TOKEN_HERE';

(function () {
    'use strict';

    let map;
    let boundary;
    let plots = [];

    // Get estate ID from URL
    function getEstateId() {
        const path = window.location.pathname;
        const match = path.match(/\/map\/([^\/]+)/);
        return match ? match[1] : null;
    }

    // Load session data from API
    async function loadSessionData() {
        const estateId = getEstateId();
        if (!estateId) {
            console.error('No estate ID found in URL');
            return null;
        }

        try {
            const response = await fetch(`/api/session/${estateId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const session = await response.json();
            console.log('[MAP] Loaded session:', session);
            return session;
        } catch (error) {
            console.error('[MAP] Failed to load session:', error);
            alert('Failed to load estate data');
            return null;
        }
    }

    // Check if coordinates are metric (CAD) or geographic (lat/lng)
    function isMetricCoordinates(coords) {
        if (!coords || coords.length === 0) return false;

        // Check ANY coordinate in the array (not just first one)
        // If any coordinate is outside valid lat/lng range, they're metric
        // Valid lat: -90 to 90, lng: -180 to 180
        for (const coord of coords) {
            const x = Array.isArray(coord) ? coord[0] : coord.x;
            const y = Array.isArray(coord) ? coord[1] : coord.y;

            if (Math.abs(x) > 180 || Math.abs(y) > 90) {
                console.log('[MAP] Detected metric coordinates:', x, y);
                return true;
            }
        }

        console.log('[MAP] Coordinates are geographic (lat/lng)');
        return false;
    }

    // Known industrial zones base locations
    const KNOWN_LOCATIONS = {
        'song_than': { lat: 10.896340, lng: 106.755053, name: 'KCN Sóng Thần' },
        'tien_son': { lat: 21.0885, lng: 106.0425, name: 'KCN Tiên Sơn' },
        'vsip': { lat: 21.0285, lng: 105.8542, name: 'VSIP Bắc Ninh' },
        'default': { lat: 21.0285, lng: 105.8542, name: 'Hanoi' }
    };

    // Detect base location from filename or metadata
    function detectBaseLocation(metadata) {
        const filename = (metadata?.filename || '').toLowerCase();

        // Check metadata first
        if (metadata?.base_location) {
            console.log('[MAP] Using metadata base location:', metadata.base_location);
            return {
                lat: metadata.base_location.lat || metadata.base_location[1],
                lng: metadata.base_location.lng || metadata.base_location[0]
            };
        }

        // Auto-detect from filename
        if (filename.includes('song_than') || filename.includes('song than')) {
            console.log('[MAP] Auto-detected: KCN Sóng Thần');
            return KNOWN_LOCATIONS.song_than;
        }
        if (filename.includes('tien_son') || filename.includes('tien son')) {
            console.log('[MAP] Auto-detected: KCN Tiên Sơn');
            return KNOWN_LOCATIONS.tien_son;
        }
        if (filename.includes('vsip')) {
            console.log('[MAP] Auto-detected: VSIP');
            return KNOWN_LOCATIONS.vsip;
        }

        // Check location field
        const location = (metadata?.location || '').toLowerCase();
        if (location.includes('bình dương') || location.includes('binh duong')) {
            console.log('[MAP] Auto-detected from location: Bình Dương');
            return KNOWN_LOCATIONS.song_than;
        }
        if (location.includes('bắc ninh') || location.includes('bac ninh')) {
            console.log('[MAP] Auto-detected from location: Bắc Ninh');
            return KNOWN_LOCATIONS.tien_son;
        }

        console.log('[MAP] Using default location: Hanoi');
        return KNOWN_LOCATIONS.default;
    }

    // Convert metric (CAD) coordinates to geographic (lng/lat)
    function metricToLngLat(metricCoords, baseLocation = null, metadata = null) {
        // Auto-detect base location if not provided
        if (!baseLocation) {
            baseLocation = detectBaseLocation(metadata);
        }

        console.log('[MAP] Converting metric coords with base location:', baseLocation);

        // 1 degree latitude ≈ 111,320 meters
        // 1 degree longitude ≈ 111,320 * cos(latitude) meters
        const METERS_PER_DEGREE_LAT = 111320;
        const METERS_PER_DEGREE_LNG = 111320 * Math.cos(baseLocation.lat * Math.PI / 180);

        return metricCoords.map(coord => {
            const x = Array.isArray(coord) ? coord[0] : coord.x;
            const y = Array.isArray(coord) ? coord[1] : coord.y;

            // Mapbox uses [lng, lat] format
            return [
                baseLocation.lng + (x / METERS_PER_DEGREE_LNG),
                baseLocation.lat + (y / METERS_PER_DEGREE_LAT)
            ];
        });
    }

    // Calculate center from coordinates - returns [lng, lat] for Mapbox
    function calculateCenter(coords, metadata) {
        if (!coords || coords.length === 0) return [105.8542, 21.0285];

        // Check if metric coordinates
        if (isMetricCoordinates(coords)) {
            // Convert to lng/lat first (will auto-detect base location)
            const geoCoords = metricToLngLat(coords, null, metadata);
            let sumLng = 0, sumLat = 0;
            geoCoords.forEach(coord => {
                sumLng += coord[0];
                sumLat += coord[1];
            });
            return [sumLng / geoCoords.length, sumLat / geoCoords.length];
        }

        // Already geographic coordinates
        let sumLng = 0, sumLat = 0;
        coords.forEach(coord => {
            sumLng += coord[0] || coord.x || 0;
            sumLat += coord[1] || coord.y || 0;
        });

        return [sumLng / coords.length, sumLat / coords.length];
    }

    // Convert coordinates to Mapbox format [lng, lat]
    function convertCoords(coords, metadata) {
        if (!coords || !Array.isArray(coords)) {
            console.log('[MAP] Invalid coords:', coords);
            return [];
        }

        // Check if these are metric coordinates
        if (isMetricCoordinates(coords)) {
            console.log('[MAP] Converting from metric to lng/lat...');
            const geoCoords = metricToLngLat(coords, null, metadata);
            console.log('[MAP] Converted', geoCoords.length, 'metric points to geographic');
            return geoCoords;
        }

        // Already geographic coordinates - ensure [lng, lat] format
        const converted = coords.map(coord => {
            if (Array.isArray(coord)) {
                // Assume [lng, lat] or [x, y]
                return [coord[0], coord[1]];
            } else if (coord.x !== undefined && coord.y !== undefined) {
                return [coord.x, coord.y];
            }
            return null;
        }).filter(c => c !== null);

        console.log('[MAP] Converted coords:', converted.length, 'points');
        return converted;
    }

    // Initialize Mapbox Map
    function initializeMap(session) {
        if (!session) {
            console.error('[MAP] No session data');
            return;
        }

        // Priority: Use uploaded GeoJSON boundary if available
        let coords = [];
        const metadata = session.metadata || {};

        // PRIORITY 1: Check if user uploaded GeoJSON with geographic coordinates
        if (metadata.geojson && metadata.geojson.features) {
            const boundaryFeature = metadata.geojson.features.find(f => f.properties?.type === 'boundary' || f.id === 'boundary');
            if (boundaryFeature && boundaryFeature.geometry.coordinates) {
                console.log('[MAP] Using GeoJSON boundary from metadata (REAL COORDINATES)');
                coords = boundaryFeature.geometry.coordinates[0];
            }
        }

        // PRIORITY 2: Use session boundary (from DXF upload)
        if (coords.length === 0 && session.boundary && session.boundary.coordinates && session.boundary.coordinates.length > 0) {
            console.log('[MAP] Using boundary from session (may be metric)');
            coords = session.boundary.coordinates[0];
        }

        // PRIORITY 3: Fallback to boundary_coords
        if (coords.length === 0 && session.boundary_coords) {
            console.log('[MAP] Using boundary_coords');
            coords = session.boundary_coords;
        }

        if (coords.length === 0) {
            console.log('[MAP] No boundary coordinates available');
        }

        const center = metadata.centroid
            ? [metadata.centroid[0], metadata.centroid[1]]
            : calculateCenter(coords, metadata);

        console.log('[MAP] Session:', session);
        console.log('[MAP] Center:', center);
        console.log('[MAP] Coordinates count:', coords.length);

        // Create Mapbox map
        map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/dark-v11',
            center: center,
            zoom: 14,
            pitch: 0,
            bearing: 0
        });

        // Add navigation control
        map.addControl(new mapboxgl.NavigationControl(), 'top-right');

        // Add scale control
        map.addControl(new mapboxgl.ScaleControl({
            maxWidth: 100,
            unit: 'metric'
        }), 'bottom-left');

        // Wait for map to load
        map.on('load', () => {
            // Expose map globally for subdivision rendering
            window.map = map;

            // Trigger custom event for subdivision UI
            window.dispatchEvent(new CustomEvent('mapReady', { detail: { map } }));

            console.log('[MAP] Map loaded and ready');

            // Draw boundary polygon (HIDDEN - only for bounds calculation)
            if (coords && coords.length > 0) {
                const mapboxCoords = convertCoords(coords, metadata);

                // Add source
                map.addSource('boundary', {
                    'type': 'geojson',
                    'data': {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Polygon',
                            'coordinates': [mapboxCoords]
                        }
                    }
                });

                // Add fill layer (HIDDEN - set opacity to 0)
                map.addLayer({
                    'id': 'boundary-fill',
                    'type': 'fill',
                    'source': 'boundary',
                    'paint': {
                        'fill-color': '#36e27b',
                        'fill-opacity': 0  // HIDDEN: Changed from 0.15 to 0
                    }
                });

                // Add outline layer (HIDDEN - set opacity to 0)
                map.addLayer({
                    'id': 'boundary-outline',
                    'type': 'line',
                    'source': 'boundary',
                    'paint': {
                        'line-color': '#36e27b',
                        'line-width': 3,
                        'line-opacity': 0  // HIDDEN: Added to hide outline
                    }
                });

                // Fit bounds to boundary
                const bounds = mapboxCoords.reduce((bounds, coord) => {
                    return bounds.extend(coord);
                }, new mapboxgl.LngLatBounds(mapboxCoords[0], mapboxCoords[0]));

                map.fitBounds(bounds, { padding: 50 });
            }
        });

        // Update estate info
        if (session.metadata) {
            const titleElement = document.querySelector('.estate-title');
            if (titleElement) {
                titleElement.textContent = session.metadata.filename || session.metadata.dxf_source || 'Industrial Estate';
            }
        }

        setupControls();
    }

    // Setup map controls
    function setupControls() {
        // Zoom controls
        const zoomIn = document.getElementById('zoom-in');
        const zoomOut = document.getElementById('zoom-out');

        if (zoomIn) {
            zoomIn.addEventListener('click', () => {
                map.setZoom(map.getZoom() + 1);
            });
        }

        if (zoomOut) {
            zoomOut.addEventListener('click', () => {
                map.setZoom(map.getZoom() - 1);
            });
        }

        // Back button
        const backButton = document.querySelector('[onclick*="history.back"]');
        if (!backButton) {
            const backBtn = document.querySelector('.estate-title')?.closest('div');
            if (backBtn) {
                backBtn.style.cursor = 'pointer';
                backBtn.addEventListener('click', () => history.back());
            }
        }
    }

    // Main initialization
    async function init() {
        console.log('[MAP] Initializing Mapbox view...');

        // Check Mapbox GL first
        if (typeof mapboxgl === 'undefined') {
            console.log('[MAP] Waiting for Mapbox GL JS...');
            const titleElement = document.querySelector('.estate-title');
            if (titleElement) titleElement.textContent = 'Loading Maps...';
            setTimeout(init, 200);
            return;
        }

        console.log('[MAP] Mapbox ready, loading session...');
        const titleElement = document.querySelector('.estate-title');
        if (titleElement) titleElement.textContent = 'Loading Data...';

        const session = await loadSessionData();
        if (!session) {
            console.error('[MAP] No session data available');
            if (titleElement) titleElement.textContent = 'Error: No Data';
            alert('Failed to load estate data. Please try again.');
            return;
        }

        if (titleElement) titleElement.textContent = 'Rendering Map...';
        initializeMap(session);
    }

    // Render subdivision results on map
    function renderSubdivisionResults(result) {
        if (!map) {
            console.error('[SUBDIVISION] Map not initialized yet');
            return;
        }

        console.log('[SUBDIVISION] Rendering results:', result);

        // Remove existing subdivision layers if any
        const layersToRemove = [
            'subdivision-lots', 'subdivision-lots-outline',
            'subdivision-roads',
            'subdivision-parks', 'subdivision-parks-outline',
            'subdivision-water', 'subdivision-water-outline',
            'subdivision-parking', 'subdivision-parking-outline'
        ];
        layersToRemove.forEach(layer => {
            if (map.getLayer(layer)) map.removeLayer(layer);
        });

        const sourcesToRemove = [
            'subdivision-lots-source', 'subdivision-roads-source',
            'subdivision-parks-source', 'subdivision-water-source',
            'subdivision-parking-source'
        ];
        sourcesToRemove.forEach(source => {
            if (map.getSource(source)) map.removeSource(source);
        });

        // Extract all features from all stages
        const allLots = [];
        const allRoads = [];
        const allParks = [];
        const allWater = [];
        const allParking = [];

        if (result.stages) {
            result.stages.forEach(stage => {
                if (stage.geometry && stage.geometry.features) {
                    stage.geometry.features.forEach(feature => {
                        if (feature.properties.type === 'lot') {
                            allLots.push(feature);
                        } else if (feature.properties.type === 'road') {
                            allRoads.push(feature);
                        } else if (feature.properties.type === 'park') {
                            allParks.push(feature);
                        } else if (feature.properties.type === 'water') {
                            allWater.push(feature);
                        } else if (feature.properties.type === 'parking') {
                            allParking.push(feature);
                        }
                    });
                }
            });
        }

        console.log(`[SUBDIVISION] Rendering ${allLots.length} lots, ${allRoads.length} roads, ${allParks.length} parks, ${allWater.length} water, ${allParking.length} parking`);

        // Render parks (green buffers) FIRST - so they appear under lots
        if (allParks.length > 0) {
            map.addSource('subdivision-parks-source', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: allParks
                }
            });

            map.addLayer({
                id: 'subdivision-parks',
                type: 'fill',
                source: 'subdivision-parks-source',
                paint: {
                    'fill-color': '#2ecc71',  // Green color for parks/buffers
                    'fill-opacity': 0.6
                }
            });

            map.addLayer({
                id: 'subdivision-parks-outline',
                type: 'line',
                source: 'subdivision-parks-source',
                paint: {
                    'line-color': '#27ae60',
                    'line-width': 1
                }
            });
        }

        // Render water features
        if (allWater.length > 0) {
            map.addSource('subdivision-water-source', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: allWater
                }
            });

            map.addLayer({
                id: 'subdivision-water',
                type: 'fill',
                source: 'subdivision-water-source',
                paint: {
                    'fill-color': '#3498db',  // Blue color for water
                    'fill-opacity': 0.7
                }
            });

            map.addLayer({
                id: 'subdivision-water-outline',
                type: 'line',
                source: 'subdivision-water-source',
                paint: {
                    'line-color': '#2980b9',
                    'line-width': 1
                }
            });
        }

        // Render parking areas
        if (allParking.length > 0) {
            map.addSource('subdivision-parking-source', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: allParking
                }
            });

            map.addLayer({
                id: 'subdivision-parking',
                type: 'fill',
                source: 'subdivision-parking-source',
                paint: {
                    'fill-color': '#95a5a6',  // Gray color for parking
                    'fill-opacity': 0.4
                }
            });

            map.addLayer({
                id: 'subdivision-parking-outline',
                type: 'line',
                source: 'subdivision-parking-source',
                paint: {
                    'line-color': '#7f8c8d',
                    'line-width': 1,
                    'line-dasharray': [2, 2]  // Dotted line for parking
                }
            });
        }

        // Render lots
        if (allLots.length > 0) {
            map.addSource('subdivision-lots-source', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: allLots
                }
            });

            // Fill layer with zone-based colors
            map.addLayer({
                id: 'subdivision-lots',
                type: 'fill',
                source: 'subdivision-lots-source',
                paint: {
                    'fill-color': [
                        'match',
                        ['get', 'zone'],
                        'FACTORY', '#FF6B6B',      // Red for factories (large)
                        'WAREHOUSE', '#FFB84D',    // Orange for warehouses (medium)
                        'RESIDENTIAL', '#4ECDC4',  // Teal for residential (small)
                        'SERVICE', '#95E1D3',      // Light green for service
                        // Fallback to old lot_type classification
                        [
                            'match',
                            ['get', 'lot_type'],
                            'Commercial', '#FFB84D',
                            'XLNT', '#36e27b',
                            'Service', '#FF6B6B',
                            '#36e27b'  // default
                        ]
                    ],
                    'fill-opacity': 0.5
                }
            });

            // Outline layer
            map.addLayer({
                id: 'subdivision-lots-outline',
                type: 'line',
                source: 'subdivision-lots-source',
                paint: {
                    'line-color': '#ffffff',
                    'line-width': 1.5
                }
            });

            // Fit map to show all lots
            const bounds = new mapboxgl.LngLatBounds();
            allLots.forEach(feature => {
                if (feature.geometry.coordinates && feature.geometry.coordinates[0]) {
                    feature.geometry.coordinates[0].forEach(coord => {
                        bounds.extend(coord);
                    });
                }
            });
            map.fitBounds(bounds, { padding: 80 });
        }

        // Render roads
        if (allRoads.length > 0) {
            map.addSource('subdivision-roads-source', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: allRoads
                }
            });

            map.addLayer({
                id: 'subdivision-roads',
                type: 'line',
                source: 'subdivision-roads-source',
                paint: {
                    'line-color': '#666666',
                    'line-width': 3
                }
            });
        }

        console.log('[SUBDIVISION] Render complete');
    }

    // Listen for subdivision completion event from modal
    window.addEventListener('subdivisionComplete', (event) => {
        console.log('[SUBDIVISION] Received subdivisionComplete event');
        renderSubdivisionResults(event.detail);
    });

    // Start when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose global for external access
    window.estateMap = { map, init, renderSubdivisionResults };

})();
