import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Circle,
  Polygon,
  Polyline,
  useMap,
  useMapEvents,
} from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix for default markers in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

// Custom marker icons
export const createCustomIcon = (color = "blue", size: "small" | "medium" | "large" = "medium") => {
  const sizes: Record<string, [number, number]> = {
    small: [20, 32],
    medium: [25, 41],
    large: [30, 50],
  };

  return new L.Icon({
    iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
    shadowUrl:
      "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
    iconSize: sizes[size] || sizes.medium,
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
  });
};

// Map event handler component
const MapEvents = ({ onMapClick, onLocationFound }: { onMapClick?: (latlng: any) => void; onLocationFound?: (latlng: any) => void }) => {
  const map = useMapEvents({
    click: (e) => {
      onMapClick && onMapClick(e.latlng);
    },
    locationfound: (e) => {
      onLocationFound && onLocationFound(e.latlng);
      map.flyTo(e.latlng, map.getZoom());
    },
  });

  return null;
};

// Custom control component
const CustomControls = ({ onLocate, onToggleLayer, layers }: { onLocate: () => void; onToggleLayer: (layer: string) => void; layers: any }) => {
  const map = useMap();

  useEffect(() => {
    const control = (L as any).control({ position: "topright" });

    control.onAdd = () => {
      const div = L.DomUtil.create("div", "custom-controls");
      div.innerHTML = `
        <div style="background: rgba(14, 18, 26, 0.9); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.12); padding: 8px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 6px;">
          <button id="locate-btn" style="padding: 6px 10px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #34d399; border-radius: 8px; font-size: 11px; font-weight: 700; cursor: pointer; display: flex; items-center; gap: 4px;">📍 My GPS</button>
          <button id="satellite-btn" style="padding: 6px 10px; background: rgba(6, 182, 212, 0.15); border: 1px solid rgba(6, 182, 212, 0.4); color: #22d3ee; border-radius: 8px; font-size: 11px; font-weight: 700; cursor: pointer;">🛰️ Satellite</button>
          <button id="traffic-btn" style="padding: 6px 10px; background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); color: #fbbf24; border-radius: 8px; font-size: 11px; font-weight: 700; cursor: pointer;">🚦 Carto Dark</button>
        </div>
      `;

      L.DomEvent.disableClickPropagation(div);

      const locateBtn = div.querySelector("#locate-btn") as HTMLElement;
      const satelliteBtn = div.querySelector("#satellite-btn") as HTMLElement;
      const trafficBtn = div.querySelector("#traffic-btn") as HTMLElement;

      if (locateBtn) locateBtn.onclick = () => onLocate();
      if (satelliteBtn) satelliteBtn.onclick = () => onToggleLayer("satellite");
      if (trafficBtn) trafficBtn.onclick = () => onToggleLayer("traffic");

      return div;
    };

    control.addTo(map);

    return () => {
      control.remove();
    };
  }, [map, onLocate, onToggleLayer]);

  return null;
};

// Search component
const SearchControl = ({ onSearch }: { onSearch?: (res: any) => void }) => {
  const [query, setQuery] = useState("");
  const map = useMap();

  const handleSearch = async () => {
    if (!query.trim()) return;

    try {
      // Using Nominatim API for geocoding
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`,
      );
      const results = await response.json();

      if (results.length > 0) {
        const { lat, lon, display_name } = results[0];
        const latLng = [parseFloat(lat), parseFloat(lon)];
        map.flyTo(latLng, 13);
        onSearch && onSearch({ latLng, name: display_name });
      }
    } catch (error) {
      console.error("Search error:", error);
    }
  };

  useEffect(() => {
    const control = (L as any).control({ position: "topleft" });

    control.onAdd = () => {
      const div = L.DomUtil.create("div", "search-control");
      div.innerHTML = `
        <div style="background: rgba(14, 18, 26, 0.9); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.12); padding: 6px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); display: flex; gap: 6px; align-items: center;">
          <input 
            id="search-input" 
            type="text" 
            placeholder="Search Delhi places or corridors..." 
            style="padding: 6px 10px; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; width: 220px; color: white; font-size: 11px; outline: none;"
          />
          <button 
            id="search-btn" 
            style="padding: 6px 12px; border: none; border-radius: 8px; cursor: pointer; background: #0891b2; color: white; font-size: 11px; font-weight: 700;"
          >
            🔍
          </button>
        </div>
      `;

      L.DomEvent.disableClickPropagation(div);

      const input = div.querySelector("#search-input") as HTMLInputElement;
      const button = div.querySelector("#search-btn") as HTMLButtonElement;

      if (input) {
        input.addEventListener("input", (e: any) => setQuery(e.target.value));
        input.addEventListener("keypress", (e) => {
          if (e.key === "Enter") handleSearch();
        });
      }
      if (button) {
        button.addEventListener("click", handleSearch);
      }

      return div;
    };

    control.addTo(map);

    return () => {
      control.remove();
    };
  }, [map]);

  return null;
};

// Main AdvancedMap component
export interface AdvancedMapProps {
  center?: [number, number];
  zoom?: number;
  markers?: Array<{
    id?: string | number;
    position: [number, number];
    color?: string;
    size?: "small" | "medium" | "large";
    icon?: any;
    popup?: {
      title?: string;
      content?: string | React.ReactNode;
      image?: string;
    };
    raw?: any;
  }>;
  polygons?: Array<{
    id?: string | number;
    positions: any;
    style?: any;
    popup?: string | React.ReactNode;
  }>;
  circles?: Array<{
    id?: string | number;
    center: [number, number];
    radius: number;
    style?: any;
    popup?: string | React.ReactNode;
  }>;
  polylines?: Array<{
    id?: string | number;
    positions: any;
    style?: any;
    popup?: string | React.ReactNode;
  }>;
  onMarkerClick?: (marker: any) => void;
  onMapClick?: (latlng: any) => void;
  enableClustering?: boolean;
  enableSearch?: boolean;
  enableControls?: boolean;
  enableDrawing?: boolean;
  mapLayers?: {
    openstreetmap: boolean;
    satellite: boolean;
    traffic: boolean;
  };
  className?: string;
  style?: React.CSSProperties;
}

export const AdvancedMap: React.FC<AdvancedMapProps> = ({
  center = [28.6139, 77.2090], // Delhi NCR center default
  zoom = 12,
  markers = [],
  polygons = [],
  circles = [],
  polylines = [],
  onMarkerClick,
  onMapClick,
  enableClustering = true,
  enableSearch = true,
  enableControls = true,
  enableDrawing = false,
  mapLayers = {
    openstreetmap: true,
    satellite: false,
    traffic: false,
  },
  className = "",
  style = { height: "550px", width: "100%" },
}) => {
  const [currentLayers, setCurrentLayers] = useState(mapLayers);
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [searchResult, setSearchResult] = useState<any>(null);
  const [clickedLocation, setClickedLocation] = useState<any>(null);

  // Handle layer toggling
  const handleToggleLayer = useCallback((layerType: string) => {
    setCurrentLayers((prev: any) => ({
      ...prev,
      [layerType]: !prev[layerType],
    }));
  }, []);

  // Handle geolocation
  const handleLocate = useCallback(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setUserLocation([latitude, longitude]);
        },
        (error) => {
          console.error("Geolocation error:", error);
        },
      );
    }
  }, []);

  // Handle map click
  const handleMapClick = useCallback(
    (latlng: any) => {
      setClickedLocation(latlng);
      onMapClick && onMapClick(latlng);
    },
    [onMapClick],
  );

  // Handle search results
  const handleSearch = useCallback((result: any) => {
    setSearchResult(result);
  }, []);

  return (
    <div className={`advanced-map relative rounded-2xl overflow-hidden ${className}`} style={style}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: "100%", width: "100%", background: "#090b10" }}
        scrollWheelZoom={true}
      >
        {/* Base tile layers */}
        {currentLayers.openstreetmap && (
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />
        )}

        {currentLayers.satellite && (
          <TileLayer
            attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          />
        )}

        {currentLayers.traffic && (
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO Dark</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
        )}

        {/* Map events */}
        <MapEvents
          onMapClick={handleMapClick}
          onLocationFound={setUserLocation}
        />

        {/* Search control */}
        {enableSearch && <SearchControl onSearch={handleSearch} />}

        {/* Custom controls */}
        {enableControls && (
          <CustomControls
            onLocate={handleLocate}
            onToggleLayer={handleToggleLayer}
            layers={currentLayers}
          />
        )}

        {/* Markers with clustering */}
        {enableClustering ? (
          <MarkerClusterGroup chunkedLoading>
            {markers.map((marker, index) => (
              <Marker
                key={marker.id || index}
                position={marker.position}
                icon={
                  marker.icon || createCustomIcon(marker.color as any || "red", marker.size || "medium")
                }
                eventHandlers={{
                  click: () => onMarkerClick && onMarkerClick(marker),
                }}
              >
                {marker.popup && (
                  <Popup>
                    <div className="p-1 min-w-[200px] text-xs">
                      {marker.popup.image && (
                        <img
                          src={marker.popup.image}
                          alt={marker.popup.title || "Location photo"}
                          className="w-full h-24 object-cover rounded-lg mb-2 border border-slate-700"
                        />
                      )}
                      <h3 className="font-bold text-sm text-slate-100 mb-1">{marker.popup.title}</h3>
                      <div className="text-slate-300 leading-snug">{marker.popup.content}</div>
                    </div>
                  </Popup>
                )}
              </Marker>
            ))}
          </MarkerClusterGroup>
        ) : (
          markers.map((marker, index) => (
            <Marker
              key={marker.id || index}
              position={marker.position}
              icon={marker.icon || createCustomIcon(marker.color as any || "red", marker.size || "medium")}
              eventHandlers={{
                click: () => onMarkerClick && onMarkerClick(marker),
              }}
            >
              {marker.popup && (
                <Popup>
                  <div className="p-1 min-w-[200px] text-xs">
                    {marker.popup.image && (
                      <img
                        src={marker.popup.image}
                        alt={marker.popup.title || "Location photo"}
                        className="w-full h-24 object-cover rounded-lg mb-2 border border-slate-700"
                      />
                    )}
                    <h3 className="font-bold text-sm text-slate-100 mb-1">{marker.popup.title}</h3>
                    <div className="text-slate-300 leading-snug">{marker.popup.content}</div>
                  </div>
                </Popup>
              )}
            </Marker>
          ))
        )}

        {/* User location marker */}
        {userLocation && (
          <Marker
            position={userLocation}
            icon={createCustomIcon("green", "large")}
          >
            <Popup>
              <div className="p-1 text-xs">
                <span className="font-bold text-emerald-400 block">📍 Your Verified GPS Position</span>
                <span className="text-slate-300 font-mono text-[10px]">{userLocation[0].toFixed(4)}°N, {userLocation[1].toFixed(4)}°E</span>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Search result marker */}
        {searchResult && (
          <Marker
            position={searchResult.latLng}
            icon={createCustomIcon("yellow", "large")}
          >
            <Popup>
              <div className="p-1 text-xs">
                <span className="font-bold text-amber-300">🔍 Search Match</span>
                <p className="text-slate-300 text-[11px] mt-0.5">{searchResult.name}</p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Clicked location marker */}
        {clickedLocation && (
          <Marker
            position={[clickedLocation.lat, clickedLocation.lng]}
            icon={createCustomIcon("orange", "small")}
          >
            <Popup>
              <div className="font-mono text-xs p-1">
                <span className="text-amber-400 font-bold block mb-1">Target Coordinates:</span>
                Lat: {clickedLocation.lat.toFixed(5)}°N<br />
                Lng: {clickedLocation.lng.toFixed(5)}°E
              </div>
            </Popup>
          </Marker>
        )}

        {/* Polygons */}
        {polygons.map((polygon, index) => (
          <Polygon
            key={polygon.id || index}
            positions={polygon.positions}
            pathOptions={
              polygon.style || { color: "#a855f7", weight: 2, fillOpacity: 0.3 }
            }
          >
            {polygon.popup && <Popup>{polygon.popup}</Popup>}
          </Polygon>
        ))}

        {/* Circles */}
        {circles.map((circle, index) => (
          <Circle
            key={circle.id || index}
            center={circle.center}
            radius={circle.radius}
            pathOptions={
              circle.style || { color: "#06b6d4", weight: 2, fillOpacity: 0.2 }
            }
          >
            {circle.popup && <Popup>{circle.popup}</Popup>}
          </Circle>
        ))}

        {/* Polylines */}
        {polylines.map((polyline, index) => (
          <Polyline
            key={polyline.id || index}
            positions={polyline.positions}
            pathOptions={polyline.style || { color: "#f43f5e", weight: 3 }}
          >
            {polyline.popup && <Popup>{polyline.popup}</Popup>}
          </Polyline>
        ))}
      </MapContainer>
    </div>
  );
};

export default AdvancedMap;
