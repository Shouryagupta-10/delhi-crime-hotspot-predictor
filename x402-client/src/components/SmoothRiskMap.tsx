import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { 
  Navigation, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  LocateFixed, 
  Play, 
  Square, 
  Radio, 
  PhoneCall,
  Flame
} from 'lucide-react';

export interface HotspotPoint {
  id: string;
  name: string;
  district: string;
  lat: number;
  lon: number;
  crime: string;
  premises: string;
  riskScore: number;
  riskLevel: 'HIGH' | 'MEDIUM' | 'LOW';
  incidents: number;
  ipc: string;
  peakHours: string;
}

export interface SafeZonePoint {
  id: string;
  name: string;
  district: string;
  lat: number;
  lon: number;
  description: string;
  riskScore: number;
  patrolFrequency: string;
}

export interface PoliceStation {
  name: string;
  lat: number;
  lon: number;
  phone: string;
  district: string;
}

// Delhi DBSCAN Identified Hotspot Centroids & Key Corridors
export const DELHI_HOTSPOTS: HotspotPoint[] = [
  { id: 'H01', name: 'Rajiv Chowk Metro & Inner Circle', district: 'New Delhi', lat: 28.6328, lon: 77.2197, crime: 'Snatching & Street Robbery', premises: 'Transit Hub', riskScore: 0.84, riskLevel: 'HIGH', incidents: 342, ipc: 'IPC 392/379', peakHours: '18:00 - 22:00' },
  { id: 'H02', name: 'Kashmere Gate ISBT & Metro Terminal', district: 'North', lat: 28.6675, lon: 77.2285, crime: 'Luggage Theft & Robbery', premises: 'Interstate Transit', riskScore: 0.88, riskLevel: 'HIGH', incidents: 419, ipc: 'IPC 380/394', peakHours: '20:00 - 02:00' },
  { id: 'H03', name: 'Seelampur & Jaffrabad Market', district: 'North-East', lat: 28.6644, lon: 77.2711, crime: 'Armed Robbery & Snatching', premises: 'Commercial Market', riskScore: 0.91, riskLevel: 'HIGH', incidents: 488, ipc: 'IPC 392/397', peakHours: '19:00 - 23:30' },
  { id: 'H04', name: 'Anand Vihar Railway & Bus Terminal', district: 'Shahdara', lat: 28.6469, lon: 77.3160, crime: 'Pickpocketing & Burglary', premises: 'Transit Terminal', riskScore: 0.82, riskLevel: 'HIGH', incidents: 375, ipc: 'IPC 379/457', peakHours: '21:00 - 04:00' },
  { id: 'H05', name: 'Jahangirpuri Main Road Corridor', district: 'North-West', lat: 28.7259, lon: 77.1685, crime: 'Motor Vehicle Theft & Snatching', premises: 'Public Roadway', riskScore: 0.86, riskLevel: 'HIGH', incidents: 402, ipc: 'IPC 379/356', peakHours: '22:00 - 05:00' },
  { id: 'H06', name: 'Chandni Chowk & Old Delhi Station', district: 'Central', lat: 28.6562, lon: 77.2301, crime: 'Commercial Burglary & Theft', premises: 'Wholesale Market', riskScore: 0.79, riskLevel: 'HIGH', incidents: 310, ipc: 'IPC 380/457', peakHours: '17:00 - 21:00' },
  { id: 'H07', name: 'Mangolpuri Industrial Phase 1', district: 'Outer', lat: 28.6900, lon: 77.0862, crime: 'Vehicle Theft & Robbery', premises: 'Industrial Estates', riskScore: 0.76, riskLevel: 'HIGH', incidents: 285, ipc: 'IPC 379/392', peakHours: '23:00 - 04:00' },
  { id: 'H08', name: 'Laxmi Nagar Vikas Marg', district: 'East', lat: 28.6319, lon: 77.2777, crime: 'Street Robbery / Mugging', premises: 'Commercial Market', riskScore: 0.74, riskLevel: 'HIGH', incidents: 264, ipc: 'IPC 392/394', peakHours: '20:00 - 23:00' },
  { id: 'H09', name: 'Rohini Sector 18 Metro Market', district: 'Rohini', lat: 28.7402, lon: 77.1306, crime: 'Burglary & Vehicle Theft', premises: 'Commercial & Transit', riskScore: 0.58, riskLevel: 'MEDIUM', incidents: 198, ipc: 'IPC 380/379', peakHours: '19:00 - 22:00' },
  { id: 'H10', name: 'Karol Bagh Market Environs', district: 'Central', lat: 28.6517, lon: 77.1906, crime: 'Snatching & Shoplifting', premises: 'Retail Hub', riskScore: 0.55, riskLevel: 'MEDIUM', incidents: 172, ipc: 'IPC 356/379', peakHours: '16:00 - 20:30' },
  { id: 'H11', name: 'Saket Select Citywalk Corridor', district: 'South', lat: 28.5284, lon: 77.2185, crime: 'Vehicle Theft & Valuables', premises: 'Commercial Mall', riskScore: 0.52, riskLevel: 'MEDIUM', incidents: 165, ipc: 'IPC 379', peakHours: '18:00 - 22:30' },
  { id: 'H12', name: 'Dwarka Sector 21 Metro Interchange', district: 'Dwarka', lat: 28.5515, lon: 77.0581, crime: 'Snatching (Chain/Mobile)', premises: 'Metro Perimeter', riskScore: 0.48, riskLevel: 'MEDIUM', incidents: 142, ipc: 'IPC 379/356', peakHours: '19:00 - 21:30' },
  { id: 'H13', name: 'Netaji Subhash Place Commercial Hub', district: 'North-West', lat: 28.6910, lon: 77.1510, crime: 'Pickpocketing & Auto Theft', premises: 'Office Complex', riskScore: 0.50, riskLevel: 'MEDIUM', incidents: 154, ipc: 'IPC 379', peakHours: '17:30 - 20:30' },
  { id: 'H14', name: 'Lajpat Nagar Central Market', district: 'South-East', lat: 28.5684, lon: 77.2435, crime: 'Shoplifting & Snatching', premises: 'Public Market', riskScore: 0.54, riskLevel: 'MEDIUM', incidents: 181, ipc: 'IPC 379/356', peakHours: '16:00 - 21:00' },
];

// Verified Low-Risk / Safe Havens & Protected Corridors
export const DELHI_SAFE_ZONES: SafeZonePoint[] = [
  { id: 'S01', name: 'Chanakyapuri Diplomatic Enclave', district: 'New Delhi', lat: 28.5983, lon: 77.1912, description: '24/7 CCTV & Armed Police Static Pickets', riskScore: 0.12, patrolFrequency: 'Every 10 mins' },
  { id: 'S02', name: 'Delhi Cantt Defense Corridor', district: 'South-West', lat: 28.5898, lon: 77.1325, description: 'Military Police & Access-Controlled Zone', riskScore: 0.15, patrolFrequency: 'Continuous' },
  { id: 'S03', name: 'Civil Lines VIP & Raj Niwas Enclave', district: 'North', lat: 28.6820, lon: 77.2180, description: 'High-Density Patrol & Secure Perimeter', riskScore: 0.18, patrolFrequency: 'Every 15 mins' },
  { id: 'S04', name: 'India Gate & Kartavya Path', district: 'New Delhi', lat: 28.6129, lon: 77.2295, description: 'Continuous Central Reserve & Drone Watch', riskScore: 0.20, patrolFrequency: 'Continuous' },
  { id: 'S05', name: 'Vasant Vihar Institutional Safe Belt', district: 'South-West', lat: 28.5600, lon: 77.1570, description: 'Private Security + Police Mobile Radar', riskScore: 0.22, patrolFrequency: 'Every 20 mins' }
];

// Nearest Delhi Police Stations
export const POLICE_STATIONS: PoliceStation[] = [
  { name: 'Connaught Place Police Station', lat: 28.6304, lon: 77.2177, phone: '011-23340004 / 112', district: 'New Delhi' },
  { name: 'Kashmere Gate Police Station', lat: 28.6655, lon: 77.2298, phone: '011-23968603 / 112', district: 'North' },
  { name: 'Seelampur Police Station', lat: 28.6680, lon: 77.2680, phone: '011-22562100 / 112', district: 'North-East' },
  { name: 'Parliament Street Police Station', lat: 28.6250, lon: 77.2105, phone: '011-23361100 / 112', district: 'New Delhi' },
  { name: 'Saket Police Station', lat: 28.5200, lon: 77.2150, phone: '011-29561000 / 112', district: 'South' },
];

// Simulated Route Steps for Walk / Commute Movement
const SIMULATION_ROUTE: Array<{ lat: number; lon: number; label: string }> = [
  { lat: 28.5983, lon: 77.1912, label: 'Chanakyapuri Safe Haven (Starting point)' },
  { lat: 28.6139, lon: 77.2090, label: 'Rashtrapati Bhavan Perimeter' },
  { lat: 28.6250, lon: 77.2150, label: 'Parliament Street Junction' },
  { lat: 28.6300, lon: 77.2170, label: 'Entering Connaught Place Outer Ring' },
  { lat: 28.6328, lon: 77.2197, label: 'Rajiv Chowk Metro High-Risk Centroid' },
  { lat: 28.6420, lon: 77.2220, label: 'Minto Road Railway Bridge Corridor' },
  { lat: 28.6500, lon: 77.2260, label: 'Approaching Old Delhi / Chandni Chowk' },
  { lat: 28.6600, lon: 77.2280, label: 'Lothian Road towards Kashmere Gate' },
  { lat: 28.6675, lon: 77.2285, label: 'Kashmere Gate Terminal (Critical Hotspot)' },
];

function calculateDistanceMeters(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371e3;
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lon2 - lon1) * Math.PI) / 180;
  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c);
}

interface SmoothRiskMapProps {
  onSelectCoordinate?: (lat: number, lon: number, premises: string) => void;
  onRequestRiskCheck?: (lat: number, lon: number) => void;
}

export const SmoothRiskMap: React.FC<SmoothRiskMapProps> = ({ 
  onSelectCoordinate, 
  onRequestRiskCheck 
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const userMarkerRef = useRef<L.Marker | null>(null);
  const userAccuracyCircleRef = useRef<L.Circle | null>(null);
  const trailPolylineRef = useRef<L.Polyline | null>(null);
  const simulationTimerRef = useRef<any>(null);

  // Live Tracking States
  const [userLocation, setUserLocation] = useState<{ lat: number; lon: number; accuracy: number; speed: number | null } | null>(null);
  const [trailHistory, setTrailHistory] = useState<[number, number][]>([]);
  const [watchId, setWatchId] = useState<number | null>(null);
  const [gpsError, setGpsError] = useState<string>('');

  // Simulation State
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [simulationIndex, setSimulationIndex] = useState<number>(0);

  // Active Map Filter
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'HIGH' | 'MEDIUM' | 'SAFE'>('ALL');
  const [followUser] = useState<boolean>(true);

  // Computed Proximity Radar
  const [nearestHotspot, setNearestHotspot] = useState<{ hotspot: HotspotPoint; distanceMeters: number } | null>(null);
  const [currentThreatLevel, setCurrentThreatLevel] = useState<'CRITICAL_RISK' | 'MODERATE_CAUTION' | 'SAFE_ZONE'>('SAFE_ZONE');

  // Markers group
  const markersGroupRef = useRef<L.LayerGroup | null>(null);

  // 1. Initialize Smooth Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const initialCenter: [number, number] = [28.6289, 77.2150];

    const map = L.map(mapContainerRef.current, {
      center: initialCenter,
      zoom: 13,
      zoomControl: false,
      attributionControl: false,
      preferCanvas: true
    });

    // High performance CartoDB Voyager Smooth Vector Tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd',
    }).addTo(map);

    L.control.zoom({ position: 'topright' }).addTo(map);

    // Breadcrumbs Trail Polyline
    const trail = L.polyline([], {
      color: '#06B6D4',
      weight: 4,
      opacity: 0.85,
      dashArray: '4, 8',
      lineCap: 'round'
    }).addTo(map);
    trailPolylineRef.current = trail;

    mapInstanceRef.current = map;

    renderLayers(map, 'ALL');
    startContinuousTracking();

    return () => {
      if (simulationTimerRef.current) clearInterval(simulationTimerRef.current);
      if (watchId !== null) navigator.geolocation.clearWatch(watchId);
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  const renderLayers = (map: L.Map, filter: 'ALL' | 'HIGH' | 'MEDIUM' | 'SAFE') => {
    if (markersGroupRef.current) {
      markersGroupRef.current.clearLayers();
    } else {
      markersGroupRef.current = L.layerGroup().addTo(map);
    }

    const group = markersGroupRef.current;

    // Render Hotspots
    DELHI_HOTSPOTS.forEach((h) => {
      if (filter === 'SAFE') return;
      if (filter === 'HIGH' && h.riskLevel !== 'HIGH') return;
      if (filter === 'MEDIUM' && h.riskLevel !== 'MEDIUM') return;

      const isHigh = h.riskLevel === 'HIGH';
      const color = isHigh ? '#EF4444' : '#F59E0B';
      const fillColor = isHigh ? '#F87171' : '#FBBF24';
      const radius = isHigh ? 380 : 250;

      const dangerZone = L.circle([h.lat, h.lon], {
        radius,
        color,
        weight: 1.5,
        fillColor,
        fillOpacity: isHigh ? 0.22 : 0.14,
        dashArray: isHigh ? undefined : '5, 5'
      });

      const iconHtml = `
        <div class="relative flex items-center justify-center cursor-pointer">
          <div class="w-8 h-8 rounded-full ${isHigh ? 'bg-rose-600 ring-4 ring-rose-500/30' : 'bg-amber-500 ring-4 ring-amber-400/30'} flex items-center justify-center text-white shadow-xl">
            ${isHigh ? '🚨' : '⚠️'}
          </div>
          <span class="absolute -bottom-5 whitespace-nowrap px-2 py-0.5 rounded text-[10px] font-bold ${isHigh ? 'bg-rose-950 text-rose-300 border border-rose-800' : 'bg-amber-950 text-amber-300 border border-amber-800'} shadow-md">
            ${h.name.split(' ')[0]} (${Math.round(h.riskScore * 100)}%)
          </span>
        </div>
      `;

      const customIcon = L.divIcon({
        className: 'custom-hotspot-pin',
        html: iconHtml,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      const centroidMarker = L.marker([h.lat, h.lon], { icon: customIcon });

      const popupContent = `
        <div style="font-family: inherit; width: 260px; padding: 4px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: ${color}; background: ${color}20; padding: 2px 8px; border-radius: 9999px;">
              ${h.riskLevel} CRIME CORRIDOR
            </span>
            <span style="font-weight: 800; font-size: 13px; color: ${color};">
              ${(h.riskScore * 100).toFixed(0)}% Risk
            </span>
          </div>
          <h4 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #F8FAFC;">
            ${h.name}
          </h4>
          <div style="font-size: 12px; color: #94A3B8; line-height: 1.5; margin-bottom: 8px;">
            <div><b>District:</b> ${h.district}</div>
            <div><b>Dominant Crime:</b> <span style="color: #F8FAFC;">${h.crime}</span></div>
            <div><b>Premises:</b> ${h.premises}</div>
            <div><b>Statute:</b> <code>${h.ipc}</code></div>
            <div><b>Peak Time:</b> ${h.peakHours}</div>
            <div><b>Historical Incidents:</b> ${h.incidents} cases</div>
          </div>
          <button id="btn-assess-${h.id}" style="
            width: 100%;
            background: linear-gradient(135deg, ${color} 0%, #0F172A 100%);
            color: white;
            border: 1px solid ${color};
            border-radius: 8px;
            padding: 7px 10px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            margin-top: 4px;
          ">
            ⚡ Run Protected x402 Assessment
          </button>
        </div>
      `;

      centroidMarker.bindPopup(popupContent, { maxWidth: 300 });

      centroidMarker.on('popupopen', () => {
        const btn = document.getElementById(`btn-assess-${h.id}`);
        if (btn) {
          btn.onclick = () => {
            if (onSelectCoordinate) onSelectCoordinate(h.lat, h.lon, h.premises);
            if (onRequestRiskCheck) onRequestRiskCheck(h.lat, h.lon);
          };
        }
      });

      dangerZone.addTo(group);
      centroidMarker.addTo(group);
    });

    // Render Safe Havens / Low Risk
    if (filter === 'ALL' || filter === 'SAFE') {
      DELHI_SAFE_ZONES.forEach((s) => {
        const safeZone = L.circle([s.lat, s.lon], {
          radius: 400,
          color: '#10B981',
          weight: 1.5,
          fillColor: '#34D399',
          fillOpacity: 0.16
        });

        const iconHtml = `
          <div class="relative flex items-center justify-center cursor-pointer">
            <div class="w-8 h-8 rounded-full bg-emerald-600 ring-4 ring-emerald-500/30 flex items-center justify-center text-white shadow-xl">
              🛡️
            </div>
            <span class="absolute -bottom-5 whitespace-nowrap px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-800 shadow-md">
              Safe Zone
            </span>
          </div>
        `;

        const customIcon = L.divIcon({
          className: 'custom-safe-pin',
          html: iconHtml,
          iconSize: [32, 32],
          iconAnchor: [16, 16]
        });

        const safeMarker = L.marker([s.lat, s.lon], { icon: customIcon });

        safeMarker.bindPopup(`
          <div style="font-family: inherit; width: 230px; padding: 4px;">
            <span style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #10B981; background: #10B98120; padding: 2px 8px; border-radius: 9999px;">
              VERIFIED SAFE CORRIDOR
            </span>
            <h4 style="margin: 6px 0; font-size: 13px; font-weight: 700; color: #F8FAFC;">${s.name}</h4>
            <div style="font-size: 12px; color: #94A3B8; line-height: 1.4;">
              <div><b>District:</b> ${s.district}</div>
              <div><b>Patrol:</b> ${s.patrolFrequency}</div>
              <div><b>Security:</b> ${s.description}</div>
              <div><b>Threat Index:</b> <span style="color: #10B981; font-weight: 700;">${(s.riskScore * 100).toFixed(0)}% (Minimal)</span></div>
            </div>
          </div>
        `);

        safeZone.addTo(group);
        safeMarker.addTo(group);
      });
    }

    // Render Police Stations
    POLICE_STATIONS.forEach((ps) => {
      const psIcon = L.divIcon({
        className: 'custom-ps-pin',
        html: `
          <div class="w-6 h-6 rounded-md bg-sky-600 ring-2 ring-sky-400/40 flex items-center justify-center text-white text-xs shadow-md">
            🚔
          </div>
        `,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      });

      const psMarker = L.marker([ps.lat, ps.lon], { icon: psIcon });
      psMarker.bindPopup(`
        <div style="font-family: inherit; width: 220px; font-size: 12px; color: #E2E8F0;">
          <b style="color: #38BDF8;">🚔 ${ps.name}</b><br/>
          <span>District: ${ps.district}</span><br/>
          <span>Emergency Helpline: <b style="color: #4ADE80;">${ps.phone}</b></span>
        </div>
      `);
      psMarker.addTo(group);
    });
  };

  useEffect(() => {
    if (mapInstanceRef.current) {
      renderLayers(mapInstanceRef.current, activeFilter);
    }
  }, [activeFilter]);

  // 3. Update User Location Marker & Proximity Engine
  const updateUserPosition = (lat: number, lon: number, accuracy: number, speed: number | null) => {
    setUserLocation({ lat, lon, accuracy, speed });

    setTrailHistory((prev) => {
      const updated: [number, number][] = [...prev, [lat, lon]];
      if (trailPolylineRef.current) {
        trailPolylineRef.current.setLatLngs(updated);
      }
      return updated;
    });

    let closestHotspot: HotspotPoint | null = null;
    let minHotspotDist = Infinity;

    DELHI_HOTSPOTS.forEach((h) => {
      const dist = calculateDistanceMeters(lat, lon, h.lat, h.lon);
      if (dist < minHotspotDist) {
        minHotspotDist = dist;
        closestHotspot = h;
      }
    });

    if (closestHotspot) {
      setNearestHotspot({ hotspot: closestHotspot, distanceMeters: minHotspotDist });
    }

    if (minHotspotDist <= 400 && closestHotspot && (closestHotspot as HotspotPoint).riskLevel === 'HIGH') {
      setCurrentThreatLevel('CRITICAL_RISK');
    } else if (minHotspotDist <= 650) {
      setCurrentThreatLevel('MODERATE_CAUTION');
    } else {
      setCurrentThreatLevel('SAFE_ZONE');
    }

    if (mapInstanceRef.current) {
      const map = mapInstanceRef.current;

      const userRadarIcon = L.divIcon({
        className: 'user-radar-beacon',
        html: `
          <div class="relative flex items-center justify-center">
            <div class="w-7 h-7 rounded-full bg-cyan-500 border-2 border-white shadow-2xl flex items-center justify-center text-slate-950 font-black text-xs z-10 radar-pulse-marker">
              📍
            </div>
            <div class="absolute w-12 h-12 bg-cyan-400/30 rounded-full animate-ping pointer-events-none"></div>
          </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });

      if (!userMarkerRef.current) {
        userMarkerRef.current = L.marker([lat, lon], { icon: userRadarIcon, zIndexOffset: 1000 }).addTo(map);
        userMarkerRef.current.bindTooltip('<b>📍 Live Movement Tracked</b><br/>You are here', { permanent: false });
      } else {
        userMarkerRef.current.setLatLng([lat, lon]);
      }

      if (!userAccuracyCircleRef.current) {
        userAccuracyCircleRef.current = L.circle([lat, lon], {
          radius: Math.max(accuracy, 60),
          color: '#06B6D4',
          weight: 1,
          fillColor: '#22D3EE',
          fillOpacity: 0.12
        }).addTo(map);
      } else {
        userAccuracyCircleRef.current.setLatLng([lat, lon]);
        userAccuracyCircleRef.current.setRadius(Math.max(accuracy, 60));
      }

      if (followUser) {
        map.panTo([lat, lon], { animate: true, duration: 0.8 });
      }
    }
  };

  const startContinuousTracking = () => {
    if (!navigator.geolocation) {
      setGpsError('Geolocation is not supported by your browser.');
      return;
    }

    setGpsError('');

    const id = navigator.geolocation.watchPosition(
      (pos) => {
        const { latitude, longitude, accuracy, speed } = pos.coords;
        updateUserPosition(latitude, longitude, accuracy, speed);
      },
      (err) => {
        let msg = err.message;
        if (err.code === 1) msg = 'Location permission denied. Please allow GPS access in browser.';
        else if (err.code === 2) msg = 'GPS signal unavailable. Defaulting to Delhi central.';
        else if (err.code === 3) msg = 'GPS location timed out.';
        setGpsError(msg);

        // Fallback default position (Rajiv Chowk)
        updateUserPosition(28.6328, 77.2197, 100, 0);
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 1000
      }
    );

    setWatchId(id);
  };

  const stopTracking = () => {
    if (watchId !== null) {
      navigator.geolocation.clearWatch(watchId);
      setWatchId(null);
    }
  };

  const toggleSimulation = () => {
    if (isSimulating) {
      if (simulationTimerRef.current) clearInterval(simulationTimerRef.current);
      setIsSimulating(false);
      return;
    }

    stopTracking();
    setIsSimulating(true);
    setSimulationIndex(0);

    let idx = 0;
    const firstPoint = SIMULATION_ROUTE[0];
    updateUserPosition(firstPoint.lat, firstPoint.lon, 25, 4.2);

    simulationTimerRef.current = setInterval(() => {
      idx = (idx + 1) % SIMULATION_ROUTE.length;
      setSimulationIndex(idx);
      const pt = SIMULATION_ROUTE[idx];
      updateUserPosition(pt.lat, pt.lon, 20 + Math.random() * 15, 3.5 + Math.random() * 2);
    }, 2800);
  };

  const centerOnUser = () => {
    if (userLocation && mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([userLocation.lat, userLocation.lon], 15, { duration: 1.2 });
    }
  };

  return (
    <div className="relative w-full h-[620px] rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 shadow-2xl flex flex-col">
      
      {/* Top Floating Glassmorphic HUD Bar */}
      <div className="absolute top-4 left-4 right-4 z-[500] flex flex-wrap items-center justify-between gap-3 pointer-events-none">
        
        {/* Real-time Threat Badge & Hotspot Proximity */}
        <div className="pointer-events-auto bg-slate-900/90 backdrop-blur-md border border-slate-700/70 rounded-xl p-3 shadow-xl flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className={`w-3.5 h-3.5 rounded-full ${
              currentThreatLevel === 'CRITICAL_RISK' ? 'bg-rose-500 animate-ping' :
              currentThreatLevel === 'MODERATE_CAUTION' ? 'bg-amber-400 animate-pulse' :
              'bg-emerald-400'
            }`}></div>
            <div>
              <div className="text-[10px] uppercase font-black tracking-wider text-slate-400">
                Live Zone Threat
              </div>
              <div className={`text-xs font-bold ${
                currentThreatLevel === 'CRITICAL_RISK' ? 'text-rose-400' :
                currentThreatLevel === 'MODERATE_CAUTION' ? 'text-amber-400' :
                'text-emerald-400'
              }`}>
                {currentThreatLevel === 'CRITICAL_RISK' ? '🚨 HIGH RISK CORRIDOR' :
                 currentThreatLevel === 'MODERATE_CAUTION' ? '⚠️ MODERATE CAUTION' :
                 '🛡️ SAFE HAVEN CORRIDOR'}
              </div>
            </div>
          </div>

          {nearestHotspot && (
            <div className="border-l border-slate-700/80 pl-3 hidden sm:block">
              <div className="text-[10px] text-slate-400 uppercase font-bold">Closest Crime Centroid</div>
              <div className="text-xs font-semibold text-slate-200 truncate max-w-[200px]">
                {nearestHotspot.hotspot.name} <span className="text-rose-400 font-mono">({nearestHotspot.distanceMeters}m)</span>
              </div>
            </div>
          )}
        </div>

        {/* Filter Pill Tabs */}
        <div className="pointer-events-auto bg-slate-900/90 backdrop-blur-md border border-slate-700/70 rounded-xl p-1 shadow-xl flex items-center gap-1">
          <button
            onClick={() => setActiveFilter('ALL')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeFilter === 'ALL' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            All Zones
          </button>
          <button
            onClick={() => setActiveFilter('HIGH')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1 ${
              activeFilter === 'HIGH' ? 'bg-rose-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Flame className="w-3.5 h-3.5" /> High Risk
          </button>
          <button
            onClick={() => setActiveFilter('MEDIUM')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeFilter === 'MEDIUM' ? 'bg-amber-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            Caution
          </button>
          <button
            onClick={() => setActiveFilter('SAFE')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1 ${
              activeFilter === 'SAFE' ? 'bg-emerald-700 text-white shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" /> Safe Havens
          </button>
        </div>

        {/* Action Controls: Live GPS, Center, Simulation */}
        <div className="pointer-events-auto flex items-center gap-2">
          
          {/* Movement Simulation Button */}
          <button
            onClick={toggleSimulation}
            className={`px-3 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-lg transition-all ${
              isSimulating 
                ? 'bg-amber-600 hover:bg-amber-500 text-white animate-pulse' 
                : 'bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700 backdrop-blur'
            }`}
            title="Simulate walking through Delhi to test real-time risk transitions"
          >
            {isSimulating ? (
              <>
                <Square className="w-3.5 h-3.5 text-white" />
                <span>Stop Route Sim ({simulationIndex + 1}/9)</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 text-cyan-400" />
                <span>Simulate Movement</span>
              </>
            )}
          </button>

          {/* Re-center GPS Button */}
          <button
            onClick={centerOnUser}
            className="p-2 bg-slate-900/90 hover:bg-slate-800 text-cyan-400 border border-slate-700/80 rounded-xl shadow-lg backdrop-blur transition-all"
            title="Recenter on My Live Location"
          >
            <LocateFixed className="w-4 h-4" />
          </button>
        </div>

      </div>

      {/* Main Leaflet Map Viewport */}
      <div ref={mapContainerRef} className="w-full h-full z-10" />

      {/* Bottom Floating Movement Status Ribbon */}
      <div className="absolute bottom-4 left-4 right-4 z-[500] pointer-events-none flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        
        {/* Coordinates and Speed HUD */}
        <div className="pointer-events-auto bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-xl px-4 py-2.5 shadow-2xl flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
            <div>
              <span className="text-slate-400 text-[10px] block">GPS COORDINATES</span>
              <span className="font-mono font-bold text-white">
                {userLocation ? `${userLocation.lat.toFixed(4)}°N, ${userLocation.lon.toFixed(4)}°E` : '28.6328°N, 77.2197°E'}
              </span>
            </div>
          </div>

          <div className="border-l border-slate-800 pl-4 hidden md:block">
            <span className="text-slate-400 text-[10px] block">PRECISION RADIUS</span>
            <span className="font-mono text-emerald-400 font-semibold">
              &plusmn;{userLocation ? Math.round(userLocation.accuracy) : 15}m
            </span>
          </div>

          <div className="border-l border-slate-800 pl-4 hidden md:block">
            <span className="text-slate-400 text-[10px] block">TRAIL BREADCRUMBS</span>
            <span className="font-mono text-cyan-300 font-semibold">
              {trailHistory.length} Waypoints Logged
            </span>
          </div>

          <div className="border-l border-slate-800 pl-4 hidden lg:block">
            <span className="text-slate-400 text-[10px] block">POLICE HELPLINE</span>
            <span className="text-slate-200 font-semibold flex items-center gap-1">
              <PhoneCall className="w-3 h-3 text-rose-400" /> Dial 112 / 1090
            </span>
          </div>
        </div>

        {/* Legend */}
        <div className="pointer-events-auto bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-xl px-3 py-2 shadow-2xl flex items-center justify-center gap-3 text-[11px] font-semibold text-slate-300">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-sm shadow-rose-500/50"></span>
            <span>High Risk (&ge;60%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 shadow-sm shadow-amber-400/50"></span>
            <span>Caution (45-60%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50"></span>
            <span>Safe Haven (&lt;45%)</span>
          </div>
        </div>

      </div>

      {gpsError && (
        <div className="absolute top-20 left-4 z-[500] bg-rose-950/90 border border-rose-600 text-rose-200 text-xs px-3 py-2 rounded-lg backdrop-blur">
          ⚠️ {gpsError}
        </div>
      )}

    </div>
  );
};
