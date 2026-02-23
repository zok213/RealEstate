"use client";

import React, { useState, useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Upload, MapPin, Layers, Eye, EyeOff } from 'lucide-react';

// Mapbox token (set in environment variables)
mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';

interface DXFFeature {
  id: string;
  type: string;
  geometry: any;
  properties: any;
}

interface ExistingFeatures {
  water_bodies: any[];
  buildings: any[];
  roads: any[];
  vegetation: any[];
  obstacles: any[];
  boundary: any;
  summary: any;
}

interface Reusability {
  keep_as_is: string[];
  reuse_modified: string[];
  demolish: string[];
  constraints: any[];
}

export default function DXFMapboxViewer() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  
  const [fileId, setFileId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [needsGeoreference, setNeedsGeoreference] = useState(false);
  const [geojson, setGeojson] = useState<any>(null);
  const [features, setFeatures] = useState<ExistingFeatures | null>(null);
  const [reusability, setReusability] = useState<Reusability | null>(null);
  
  // Layer visibility
  const [layersVisible, setLayersVisible] = useState({
    boundary: true,
    water: true,
    buildings: true,
    roads: true,
    vegetation: true,
    obstacles: true,
    satellite: true
  });
  
  // Control points for georeferencing
  const [dxfControlPoints, setDxfControlPoints] = useState<[number, number][]>([]);
  const [geoControlPoints, setGeoControlPoints] = useState<[number, number][]>([]);
  const [selectingControlPoint, setSelectingControlPoint] = useState(false);

  // Initialize Mapbox
  useEffect(() => {
    if (!mapContainer.current) return;
    if (map.current) return; // Already initialized

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/satellite-streets-v12', // Satellite with streets
      center: [100.5, 13.75], // Default: Bangkok, Thailand
      zoom: 12,
      pitch: 0,
      bearing: 0
    });

    // Add navigation controls
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    // Add scale
    map.current.addControl(
      new mapboxgl.ScaleControl({ unit: 'metric' }),
      'bottom-left'
    );

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  // Upload DXF file
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/dxf/upload', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      
      setFileId(data.file_id);
      setNeedsGeoreference(data.needs_manual_georeferencing);

      if (!data.needs_manual_georeferencing) {
        // Auto-georeferenced, load features
        await loadFeaturesAndGeoJSON(data.file_id);
      }

    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload DXF file');
    } finally {
      setUploading(false);
    }
  };

  // Load features from backend
  const loadFeaturesAndGeoJSON = async (fid: string) => {
    try {
      // Load detected features
      const featuresResponse = await fetch(`/api/dxf/${fid}/features`);
      const featuresData = await featuresResponse.json();
      setFeatures(featuresData);

      // Load georeferenced GeoJSON
      const geojsonResponse = await fetch(`/api/dxf/${fid}/geojson`);
      const geojsonData = await geojsonResponse.json();
      setGeojson(geojsonData.geojson);

      // Fit map to bounds
      if (geojsonData.bounds && map.current) {
        map.current.fitBounds([
          [geojsonData.bounds.west, geojsonData.bounds.south],
          [geojsonData.bounds.east, geojsonData.bounds.north]
        ], { padding: 50 });
      }

      // Load reusability classification
      const reusabilityResponse = await fetch(
        `/api/dxf/${fid}/classify-reusability`,
        { method: 'POST' }
      );
      const reusabilityData = await reusabilityResponse.json();
      setReusability(reusabilityData);

      // Add layers to map
      addLayersToMap(featuresData, reusabilityData);

    } catch (error) {
      console.error('Failed to load features:', error);
    }
  };

  // Set georeferencing control points
  const handleGeoreference = async () => {
    if (!fileId || dxfControlPoints.length < 3 || geoControlPoints.length < 3) {
      alert('Need at least 3 control points');
      return;
    }

    try {
      const response = await fetch('/api/dxf/georeference', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_id: fileId,
          dxf_points: dxfControlPoints,
          geo_points: geoControlPoints
        })
      });

      if (response.ok) {
        setNeedsGeoreference(false);
        await loadFeaturesAndGeoJSON(fileId);
      }
    } catch (error) {
      console.error('Georeferencing failed:', error);
      alert('Failed to georeference');
    }
  };

  // Add features as map layers
  const addLayersToMap = (featuresData: ExistingFeatures, reusabilityData: Reusability) => {
    if (!map.current) return;

    // Remove existing layers if any
    ['boundary-layer', 'water-layer', 'buildings-layer', 'roads-layer', 'vegetation-layer'].forEach(id => {
      if (map.current!.getLayer(id)) map.current!.removeLayer(id);
      if (map.current!.getSource(id)) map.current!.removeSource(id);
    });

    // Add boundary
    if (featuresData.boundary) {
      map.current.addSource('boundary-layer', {
        type: 'geojson',
        data: {
          type: 'Feature',
          geometry: featuresData.boundary,
          properties: {}
        }
      });

      map.current.addLayer({
        id: 'boundary-layer',
        type: 'line',
        source: 'boundary-layer',
        paint: {
          'line-color': '#ffffff',
          'line-width': 3,
          'line-dasharray': [2, 2]
        }
      });
    }

    // Add water bodies (blue, keep as-is)
    if (featuresData.water_bodies.length > 0) {
      map.current.addSource('water-layer', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: featuresData.water_bodies.map(wb => ({
            type: 'Feature',
            geometry: wb.polygon,
            properties: {
              id: wb.id,
              area: wb.area_m2,
              reusable: reusabilityData.keep_as_is.includes(wb.id)
            }
          }))
        }
      });

      map.current.addLayer({
        id: 'water-layer',
        type: 'fill',
        source: 'water-layer',
        paint: {
          'fill-color': [
            'case',
            ['get', 'reusable'],
            '#3b82f6', // Blue for keep
            '#06b6d4'  // Cyan for reuse
          ],
          'fill-opacity': 0.6
        }
      });

      map.current.addLayer({
        id: 'water-layer-outline',
        type: 'line',
        source: 'water-layer',
        paint: {
          'line-color': '#1e40af',
          'line-width': 2
        }
      });
    }

    // Add buildings (gray/red)
    if (featuresData.buildings.length > 0) {
      map.current.addSource('buildings-layer', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: featuresData.buildings.map(b => ({
            type: 'Feature',
            geometry: b.polygon,
            properties: {
              id: b.id,
              area: b.area_m2,
              demolish: reusabilityData.demolish.includes(b.id),
              reuse: reusabilityData.reuse_modified.includes(b.id)
            }
          }))
        }
      });

      map.current.addLayer({
        id: 'buildings-layer',
        type: 'fill',
        source: 'buildings-layer',
        paint: {
          'fill-color': [
            'case',
            ['get', 'demolish'],
            '#ef4444', // Red for demolish
            ['get', 'reuse'],
            '#f59e0b', // Orange for reuse
            '#64748b'  // Gray for keep
          ],
          'fill-opacity': 0.7
        }
      });

      map.current.addLayer({
        id: 'buildings-layer-outline',
        type: 'line',
        source: 'buildings-layer',
        paint: {
          'line-color': '#1e293b',
          'line-width': 2
        }
      });
    }

    // Add roads (yellow)
    if (featuresData.roads.length > 0) {
      map.current.addSource('roads-layer', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: featuresData.roads.map(r => ({
            type: 'Feature',
            geometry: r.linestring,
            properties: {
              id: r.id,
              length: r.length_m
            }
          }))
        }
      });

      map.current.addLayer({
        id: 'roads-layer',
        type: 'line',
        source: 'roads-layer',
        paint: {
          'line-color': '#fbbf24',
          'line-width': 4,
          'line-opacity': 0.8
        }
      });
    }

    // Add vegetation (green)
    if (featuresData.vegetation.length > 0) {
      map.current.addSource('vegetation-layer', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: featuresData.vegetation.map(v => ({
            type: 'Feature',
            geometry: v.polygon,
            properties: {
              id: v.id,
              significant: v.significant
            }
          }))
        }
      });

      map.current.addLayer({
        id: 'vegetation-layer',
        type: 'fill',
        source: 'vegetation-layer',
        paint: {
          'fill-color': '#10b981',
          'fill-opacity': 0.5
        }
      });

      map.current.addLayer({
        id: 'vegetation-layer-outline',
        type: 'circle',
        source: 'vegetation-layer',
        paint: {
          'circle-radius': 3,
          'circle-color': '#065f46'
        }
      });
    }

    // Add click handlers for feature info
    map.current.on('click', ['water-layer', 'buildings-layer', 'roads-layer'], (e) => {
      if (!e.features || e.features.length === 0) return;
      
      const feature = e.features[0];
      const props = feature.properties;
      
      new mapboxgl.Popup()
        .setLngLat(e.lngLat)
        .setHTML(`
          <strong>${feature.layer.id.replace('-layer', '')}</strong><br/>
          ID: ${props.id || 'N/A'}<br/>
          ${props.area ? `Area: ${(props.area / 1600).toFixed(2)} rai` : ''}
          ${props.length ? `Length: ${props.length.toFixed(0)} m` : ''}
          ${props.reusable !== undefined ? `<br/>Reusable: ${props.reusable ? 'Yes' : 'No'}` : ''}
          ${props.demolish !== undefined ? `<br/>Demolish: ${props.demolish ? 'Yes' : 'No'}` : ''}
        `)
        .addTo(map.current!);
    });

    // Change cursor on hover
    map.current.on('mouseenter', ['water-layer', 'buildings-layer', 'roads-layer'], () => {
      if (map.current) map.current.getCanvas().style.cursor = 'pointer';
    });

    map.current.on('mouseleave', ['water-layer', 'buildings-layer', 'roads-layer'], () => {
      if (map.current) map.current.getCanvas().style.cursor = '';
    });
  };

  // Toggle layer visibility
  const toggleLayer = (layerId: string) => {
    if (!map.current) return;

    const visibility = layersVisible[layerId as keyof typeof layersVisible];
    const newVisibility = !visibility;

    const mapLayerId = `${layerId}-layer`;
    if (map.current.getLayer(mapLayerId)) {
      map.current.setLayoutProperty(
        mapLayerId,
        'visibility',
        newVisibility ? 'visible' : 'none'
      );
    }

    setLayersVisible(prev => ({ ...prev, [layerId]: newVisibility }));
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div className="w-96 bg-background border-r overflow-y-auto">
        <Card className="m-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              DXF Terrain Overlay
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Upload */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Upload DXF/DWG File
              </label>
              <input
                type="file"
                accept=".dxf,.dwg"
                onChange={handleFileUpload}
                disabled={uploading}
                className="block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
              />
              {uploading && <p className="text-sm text-muted-foreground mt-2">Uploading...</p>}
            </div>

            {/* Georeferencing */}
            {needsGeoreference && fileId && (
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <h3 className="font-medium mb-2">Manual Georeferencing Required</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Provide 3+ control points to map DXF coordinates to real-world locations.
                </p>
                <Button onClick={handleGeoreference} disabled={dxfControlPoints.length < 3}>
                  Set {dxfControlPoints.length}/3 Control Points
                </Button>
              </div>
            )}

            {/* Feature Summary */}
            {features && (
              <div className="space-y-3">
                <h3 className="font-medium">Detected Features</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex justify-between">
                    <span>Site Area:</span>
                    <Badge variant="outline">{features.summary.site_area_rai.toFixed(1)} rai</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Water Bodies:</span>
                    <Badge variant="default">{features.water_bodies.length}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Buildings:</span>
                    <Badge variant="default">{features.buildings.length}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Roads:</span>
                    <Badge variant="default">{features.roads.length}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Water Coverage:</span>
                    <Badge variant="outline">{features.summary.water_area_pct.toFixed(1)}%</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Building Coverage:</span>
                    <Badge variant="outline">{features.summary.building_coverage_pct.toFixed(1)}%</Badge>
                  </div>
                </div>
              </div>
            )}

            {/* Reusability */}
            {reusability && (
              <div className="space-y-3">
                <h3 className="font-medium">Reusability Analysis</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                      Keep as-is
                    </span>
                    <Badge variant="default">{reusability.keep_as_is.length}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                      Reuse/Modify
                    </span>
                    <Badge variant="default">{reusability.reuse_modified.length}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-red-500"></div>
                      Demolish
                    </span>
                    <Badge variant="default">{reusability.demolish.length}</Badge>
                  </div>
                </div>
              </div>
            )}

            {/* Layer Controls */}
            {features && (
              <div className="space-y-2">
                <h3 className="font-medium flex items-center gap-2">
                  <Layers className="h-4 w-4" />
                  Layer Visibility
                </h3>
                {Object.entries(layersVisible).map(([layer, visible]) => (
                  <Button
                    key={layer}
                    variant="outline"
                    size="sm"
                    className="w-full justify-between"
                    onClick={() => toggleLayer(layer)}
                  >
                    <span className="capitalize">{layer.replace('_', ' ')}</span>
                    {visible ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                  </Button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Map */}
      <div ref={mapContainer} className="flex-1" />
    </div>
  );
}
