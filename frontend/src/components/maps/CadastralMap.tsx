import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { LandParcel } from '../../types';
import {
  Layers as LayersIcon,
  Navigation,
  Crosshair,
  Plus,
  Minus,
  CheckSquare,
  Square,
  X
} from 'lucide-react';

interface CadastralMapProps {
  parcels: LandParcel[];
  selectedParcel: LandParcel | null;
  onSelectParcel: (parcel: LandParcel) => void;
  mapType: 'map' | 'satellite' | 'hybrid' | 'terrain';
  villageCenter?: { lat: number; lng: number };
}

export const CadastralMap: React.FC<CadastralMapProps> = ({
  parcels,
  selectedParcel,
  onSelectParcel,
  mapType,
  villageCenter
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const geojsonLayerRef = useRef<L.GeoJSON | null>(null);
  const parcelMarkersRef = useRef<L.LayerGroup | null>(null);
  const villageOutlineRef = useRef<L.Polyline | null>(null);
  const waterLayerRef = useRef<L.LayerGroup | null>(null);

  const [showLayersModal, setShowLayersModal] = useState(true);
  const [layersState, setLayersState] = useState({
    landParcels: true,
    surveyBoundary: true,
    villageBoundary: true,
    roads: true,
    waterBodies: true,
    oldRecords: false,
    discrepancyAreas: true
  });

  // Center coordinate around Pimpalgaon cadastral center
  const centerLat = 19.1245;
  const centerLng = 74.4315;

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [centerLat, centerLng],
      zoom: 16,
      zoomControl: false,
      attributionControl: false
    });

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!mapInstanceRef.current || !villageCenter || villageCenter.lat === 0 || villageCenter.lng === 0) return;
    mapInstanceRef.current.setView([villageCenter.lat, villageCenter.lng], 14);
  }, [villageCenter]);

  // Update Base Tile Layer according to mapType
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    if (tileLayerRef.current) {
      map.removeLayer(tileLayerRef.current);
    }

    let tileUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
    let maxZoom = 19;

    if (mapType === 'map') {
      tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    } else if (mapType === 'terrain') {
      tileUrl = 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png';
      maxZoom = 17;
    } else if (mapType === 'satellite' || mapType === 'hybrid') {
      tileUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
    }

    tileLayerRef.current = L.tileLayer(tileUrl, { maxZoom }).addTo(map);
  }, [mapType]);

  // Render Village Boundary Contour & River Line (Water Body)
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    // Village boundary purple contour
    const villageRing: [number, number][] = [
      [19.1170, 74.4240],
      [19.1220, 74.4200],
      [19.1280, 74.4230],
      [19.1330, 74.4290],
      [19.1340, 74.4380],
      [19.1290, 74.4440],
      [19.1210, 74.4430],
      [19.1160, 74.4360],
      [19.1170, 74.4240]
    ];

    if (villageOutlineRef.current) {
      map.removeLayer(villageOutlineRef.current);
    }

    if (layersState.villageBoundary) {
      villageOutlineRef.current = L.polyline(villageRing, {
        color: '#a855f7',
        weight: 3.5,
        opacity: 0.95,
        dashArray: undefined
      }).addTo(map);
    }
  }, [layersState.villageBoundary]);

  useEffect(() => {
    if (!mapInstanceRef.current) return;
    const map = mapInstanceRef.current;
    if (waterLayerRef.current) {
      map.removeLayer(waterLayerRef.current);
      waterLayerRef.current = null;
    }
    if (!layersState.waterBodies || !villageCenter || villageCenter.lat === 0 || villageCenter.lng === 0) return;

    const controller = new AbortController();
    const waterLayer = L.layerGroup().addTo(map);
    waterLayerRef.current = waterLayer;
    const query = `[out:json];(way["natural"="water"](around:5000,${villageCenter.lat},${villageCenter.lng});way["waterway"~"dam|reservoir|stream|river"](around:5000,${villageCenter.lat},${villageCenter.lng});node["waterway"="dam"](around:5000,${villageCenter.lat},${villageCenter.lng}););out geom;`;

    fetch(`https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`, { signal: controller.signal })
      .then((response) => response.json())
      .then((data) => {
        if (waterLayerRef.current !== waterLayer) return;
        data.elements?.forEach((element: any) => {
          const tags = element.tags || {};
          const name = tags.name || tags.name_en || (tags.waterway === 'dam' ? 'Bund / बांध' : 'Water body / जलस्रोत');
          if (element.type === 'node' && element.lat && element.lon) {
            L.marker([element.lat, element.lon], {
              icon: L.divIcon({
                className: 'water-label-icon',
                html: `<div style="background:#075985;color:#fff;border:1px solid #bae6fd;border-radius:5px;padding:3px 5px;font-size:10px;font-weight:700;white-space:nowrap">${name}</div>`
              })
            }).addTo(waterLayer).bindPopup(`<strong>${name}</strong><br/>बंधारा / जलस्रोत<br/><small>Source: OpenStreetMap</small>`);
            return;
          }
          const coordinates = element.geometry?.map((point: any) => [point.lat, point.lon]);
          if (!coordinates?.length) return;
          const isArea = coordinates.length > 2 && coordinates[0][0] === coordinates[coordinates.length - 1][0] && coordinates[0][1] === coordinates[coordinates.length - 1][1];
          const shape = isArea
            ? L.polygon(coordinates, { color: '#0369a1', fillColor: '#38bdf8', fillOpacity: 0.45, weight: 2 })
            : L.polyline(coordinates, { color: '#0284c7', weight: 4, opacity: 0.8 });
          shape.addTo(waterLayer).bindPopup(`<strong>${name}</strong><br/>जलस्रोत / Water body<br/><small>Source: OpenStreetMap</small>`);
        });
      })
      .catch(() => {});

    return () => {
      controller.abort();
      if (waterLayerRef.current === waterLayer) {
        map.removeLayer(waterLayer);
        waterLayerRef.current = null;
      }
    };
  }, [layersState.waterBodies, villageCenter]);

  // Render Cadastral Parcels Layer
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    if (geojsonLayerRef.current) {
      map.removeLayer(geojsonLayerRef.current);
    }
    if (parcelMarkersRef.current) {
      map.removeLayer(parcelMarkersRef.current);
      parcelMarkersRef.current = null;
    }

    if (!layersState.landParcels || parcels.length === 0) return;

    const parcelMarkers = L.layerGroup().addTo(map);
    parcelMarkersRef.current = parcelMarkers;

    // Create GeoJSON features from parcels
    const features = parcels.map((p) => {
      let geometry;
      try {
        geometry = p.boundary_geojson ? JSON.parse(p.boundary_geojson) : null;
      } catch (_) {}

      if (!geometry) {
        geometry = {
          type: 'Polygon',
          coordinates: [[
            [p.center_lng - 0.0015, p.center_lat - 0.0012],
            [p.center_lng + 0.0015, p.center_lat - 0.0012],
            [p.center_lng + 0.0012, p.center_lat + 0.0012],
            [p.center_lng - 0.0015, p.center_lat + 0.0012],
            [p.center_lng - 0.0015, p.center_lat - 0.0012]
          ]]
        };
      }

      return {
        type: 'Feature',
        id: p.id,
        properties: p,
        geometry
      };
    });

    const geojsonLayer = L.geoJSON({ type: 'FeatureCollection', features } as any, {
      style: (feature: any) => {
        const p: LandParcel = feature.properties;
        const isSelected = selectedParcel?.id === p.id;
        const isDiscrepancy = p.boundary_status === 'Discrepancy' || p.discrepancy_status?.includes('Discrepancy');
        const isInProgress = p.boundary_status === 'In Progress';

        if (isSelected) {
          return {
            color: '#38bdf8',
            weight: 3,
            dashArray: '5, 5',
            fillColor: '#0284c7',
            fillOpacity: 0.75
          };
        }

        if (isDiscrepancy && layersState.discrepancyAreas) {
          return {
            color: '#ef4444',
            weight: 2.5,
            fillColor: '#dc2626',
            fillOpacity: 0.65
          };
        }

        if (isInProgress) {
          return {
            color: '#f59e0b',
            weight: 1.5,
            fillColor: '#d97706',
            fillOpacity: 0.35
          };
        }

        // Verified parcel (greenish tint as in reference image)
        return {
          color: '#86efac',
          weight: 1.5,
          fillColor: '#15803d',
          fillOpacity: 0.38
        };
      },
      onEachFeature: (feature: any, layer: L.Layer) => {
        const p: LandParcel = feature.properties;

        // Custom div icon for Survey Number label (e.g. 50/1, 48/3)
        const isSelected = selectedParcel?.id === p.id;
        const isDiscrepancy = p.boundary_status === 'Discrepancy';

        const labelHtml = `
          <div class="flex items-center justify-center font-bold text-[11px] leading-none pointer-events-none drop-shadow-md select-none ${
            isSelected
              ? 'text-white bg-sky-600 px-1.5 py-0.5 rounded shadow border border-sky-300 ring-2 ring-sky-400/50 scale-110'
              : isDiscrepancy
              ? 'text-white bg-red-600/90 px-1 py-0.5 rounded'
              : 'text-emerald-100 bg-slate-900/60 px-1 py-0.5 rounded text-[10.5px]'
          }">
            ${p.survey_number || p.gat_number}
          </div>
        `;

        const labelIcon = L.divIcon({
          html: labelHtml,
          className: 'parcel-label-icon',
          iconSize: [40, 20],
          iconAnchor: [20, 10]
        });

        // Add permanent marker text on polygon centroid
        const marker = L.marker([p.center_lat, p.center_lng], {
          icon: labelIcon,
          interactive: false
        });
        marker.addTo(parcelMarkers);

        // Click on polygon selects parcel
        layer.on({
          click: () => onSelectParcel(p),
          mouseover: (e: any) => {
            const l = e.target;
            if (selectedParcel?.id !== p.id) {
              l.setStyle({ fillOpacity: 0.6, weight: 2.5 });
            }
          },
          mouseout: (e: any) => {
            const l = e.target;
            if (selectedParcel?.id !== p.id) {
              geojsonLayer.resetStyle(l);
            }
          }
        });
      }
    }).addTo(map);

    geojsonLayerRef.current = geojsonLayer;
  }, [parcels, selectedParcel, layersState]);

  // Pan to selected parcel when changed
  useEffect(() => {
    if (selectedParcel && mapInstanceRef.current) {
      mapInstanceRef.current.setView([selectedParcel.center_lat, selectedParcel.center_lng], 16.5, {
        animate: true
      });
    }
  }, [selectedParcel]);

  const toggleLayer = (layerKey: keyof typeof layersState) => {
    setLayersState((prev) => ({ ...prev, [layerKey]: !prev[layerKey] }));
  };

  return (
    <div className="relative w-full h-full rounded-xl overflow-hidden shadow-sm border border-slate-200">
      {/* Map Container */}
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* TOP LEFT FLOATING CARD - Layers Panel */}
      {showLayersModal && (
        <div className="absolute top-3 left-3 bg-white/95 backdrop-blur-md rounded-xl p-3 shadow-lg border border-slate-200 z-[1000] w-48 text-slate-800 animate-in fade-in duration-200">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
            <div className="flex items-center gap-1.5 font-bold text-xs text-slate-800">
              <LayersIcon className="w-3.5 h-3.5 text-blue-600" />
              <span>Layers</span>
            </div>
            <button
              onClick={() => setShowLayersModal(false)}
              className="text-slate-400 hover:text-slate-700 p-0.5 rounded"
            >
              <X className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-1.5 text-xs">
            <label
              onClick={() => toggleLayer('landParcels')}
              className="flex items-center gap-2 cursor-pointer hover:bg-slate-50 p-1 rounded transition"
            >
              {layersState.landParcels ? (
                <CheckSquare className="w-3.5 h-3.5 text-emerald-600 fill-emerald-50" />
              ) : (
                <Square className="w-3.5 h-3.5 text-slate-400" />
              )}
              <span className="w-2.5 h-2.5 rounded bg-emerald-500 inline-block"></span>
              <span className="text-[11.5px] font-medium text-slate-700">Land Parcels</span>
            </label>

            <label
              onClick={() => toggleLayer('surveyBoundary')}
              className="flex items-center gap-2 cursor-pointer hover:bg-slate-50 p-1 rounded transition"
            >
              {layersState.surveyBoundary ? (
                <CheckSquare className="w-3.5 h-3.5 text-sky-600 fill-sky-50" />
              ) : (
                <Square className="w-3.5 h-3.5 text-slate-400" />
              )}
              <span className="w-2.5 h-1 border-t-2 border-dashed border-sky-400 inline-block"></span>
              <span className="text-[11.5px] font-medium text-slate-700">Survey Boundary</span>
            </label>

            <label
              onClick={() => toggleLayer('villageBoundary')}
              className="flex items-center gap-2 cursor-pointer hover:bg-slate-50 p-1 rounded transition"
            >
              {layersState.villageBoundary ? (
                <CheckSquare className="w-3.5 h-3.5 text-purple-600 fill-purple-50" />
              ) : (
                <Square className="w-3.5 h-3.5 text-slate-400" />
              )}
              <span className="w-2.5 h-1 border-t-2 border-purple-500 inline-block"></span>
              <span className="text-[11.5px] font-medium text-slate-700">Village Boundary</span>
            </label>

            <label
              onClick={() => toggleLayer('roads')}
              className="flex items-center gap-2 cursor-pointer hover:bg-slate-50 p-1 rounded transition"
            >
              {layersState.roads ? (
                <CheckSquare className="w-3.5 h-3.5 text-slate-600 fill-slate-50" />
              ) : (
                <Square className="w-3.5 h-3.5 text-slate-400" />
              )}
              <span className="w-2.5 h-1 bg-amber-400 inline-block"></span>
              <span className="text-[11.5px] font-medium text-slate-700">Roads</span>
            </label>

            <label
              onClick={() => toggleLayer('waterBodies')}
              className="flex items-center gap-2 cursor-pointer hover:bg-slate-50 p-1 rounded transition"
            >
              {layersState.waterBodies ? (
                <CheckSquare className="w-3.5 h-3.5 text-blue-600 fill-blue-50" />
              ) : (
                <Square className="w-3.5 h-3.5 text-slate-400" />
              )}
              <span className="w-2.5 h-2.5 rounded bg-blue-500 inline-block"></span>
              <span className="text-[11.5px] font-medium text-slate-700">Water Bodies / बंधारे</span>
            </label>

            <label
              onClick={() => toggleLayer('oldRecords')}
              className="flex items-center gap-2 cursor-pointer hover:bg-slate-50 p-1 rounded transition"
            >
              {layersState.oldRecords ? (
                <CheckSquare className="w-3.5 h-3.5 text-amber-600 fill-amber-50" />
              ) : (
                <Square className="w-3.5 h-3.5 text-slate-400" />
              )}
              <span className="w-2.5 h-2.5 rounded bg-amber-400 inline-block"></span>
              <span className="text-[11.5px] font-medium text-slate-700">Old Records</span>
            </label>

            <label
              onClick={() => toggleLayer('discrepancyAreas')}
              className="flex items-center gap-2 cursor-pointer hover:bg-slate-50 p-1 rounded transition"
            >
              {layersState.discrepancyAreas ? (
                <CheckSquare className="w-3.5 h-3.5 text-red-600 fill-red-50" />
              ) : (
                <Square className="w-3.5 h-3.5 text-slate-400" />
              )}
              <span className="w-2.5 h-2.5 rounded bg-red-500 inline-block"></span>
              <span className="text-[11.5px] font-medium text-slate-700">Discrepancy Areas</span>
            </label>
          </div>
        </div>
      )}

      {/* Button to reopen layers panel if closed */}
      {!showLayersModal && (
        <button
          onClick={() => setShowLayersModal(true)}
          className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm p-2 rounded-lg shadow-md border border-slate-200 z-[1000] text-slate-700 hover:bg-white"
          title="Show Layers"
        >
          <LayersIcon className="w-4 h-4 text-blue-600" />
        </button>
      )}

      {/* TOP RIGHT - Compass Needle */}
      <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm p-2 rounded-full shadow-md border border-slate-200 z-[1000] flex flex-col items-center justify-center">
        <span className="text-[9px] font-extrabold text-red-600 leading-none">N</span>
        <Navigation className="w-4 h-4 text-red-600 fill-red-600 -rotate-45" />
      </div>

      {/* BOTTOM LEFT - Zoom Controls & Scale Bar */}
      <div className="absolute bottom-4 left-4 z-[1000] flex flex-col items-start gap-2">
        <div className="bg-white/95 backdrop-blur-sm rounded-lg shadow-md border border-slate-200 overflow-hidden flex flex-col">
          <button
            onClick={() => mapInstanceRef.current?.zoomIn()}
            className="p-2 hover:bg-slate-100 text-slate-700 border-b border-slate-100 transition"
            title="Zoom in"
          >
            <Plus className="w-4 h-4" />
          </button>
          <button
            onClick={() => mapInstanceRef.current?.zoomOut()}
            className="p-2 hover:bg-slate-100 text-slate-700 transition"
            title="Zoom out"
          >
            <Minus className="w-4 h-4" />
          </button>
        </div>

        <div className="bg-white/95 backdrop-blur-sm p-2 rounded-lg shadow-md border border-slate-200 flex items-center gap-2">
          <button
            onClick={() => {
              if (selectedParcel && mapInstanceRef.current) {
                mapInstanceRef.current.setView([selectedParcel.center_lat, selectedParcel.center_lng], 17);
              } else if (mapInstanceRef.current) {
                mapInstanceRef.current.setView([centerLat, centerLng], 16);
              }
            }}
            className="text-slate-700 hover:text-blue-600 transition"
            title="Center Current Location"
          >
            <Crosshair className="w-4 h-4" />
          </button>
          {/* Scale bar indicator */}
          <div className="text-[9px] font-mono text-slate-600 flex items-center gap-1 border-l pl-2 border-slate-200">
            <span>0</span>
            <span className="w-8 border-b-2 border-slate-700 inline-block"></span>
            <span>50</span>
            <span className="w-8 border-b-2 border-slate-700 inline-block"></span>
            <span>100</span>
            <span className="w-12 border-b-2 border-slate-700 inline-block"></span>
            <span>200 m</span>
          </div>
        </div>
      </div>

      {/* BOTTOM RIGHT - Parcel Status Legend Card */}
      <div className="absolute bottom-4 right-4 bg-white/95 backdrop-blur-md rounded-xl p-3 shadow-lg border border-slate-200 z-[1000] text-xs w-44">
        <div className="font-bold text-[11.5px] text-slate-800 mb-2">Parcel Status</div>
        <div className="space-y-1.5 text-[11px]">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded bg-[#22c55e] inline-block border border-green-600"></span>
            <span className="text-slate-700 font-medium">Verified</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded bg-[#eab308] inline-block border border-yellow-600"></span>
            <span className="text-slate-700 font-medium">In Progress</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded bg-[#ef4444] inline-block border border-red-600"></span>
            <span className="text-slate-700 font-medium">Discrepancy</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 border-t-2 border-dashed border-sky-400 inline-block"></span>
            <span className="text-slate-700 font-medium">Survey Boundary</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 border-t-2 border-purple-500 inline-block"></span>
            <span className="text-slate-700 font-medium">Village Boundary</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded bg-sky-400 inline-block border border-sky-700"></span>
            <span className="text-slate-700 font-medium">बंधारे / Water</span>
          </div>
          <p className="text-[9px] text-slate-400 pt-1 border-t border-slate-100">Map source: OpenStreetMap. Verify locally before decisions.</p>
        </div>
      </div>
    </div>
  );
};
