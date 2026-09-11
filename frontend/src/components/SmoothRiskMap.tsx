import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { 
  ShieldCheck, 
  LocateFixed, 
  Play, 
  Square, 
  Radio, 
  PhoneCall,
  Flame,
  Zap,
  Crosshair
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
  const [isGpsActive, setIsGpsActive] = useState<boolean>(false);
  const [gpsError, setGpsError] = useState<string>('');

  // Simulation State
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [simulationIndex, setSimulationIndex] = useState<number>(0);

  // Active Map Filter
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'HIGH' | 'MEDIUM' | 'SAFE'>('ALL');

  // Computed Proximity Radar & Threat Index
  const [nearestHotspot, setNearestHotspot] = useState<{ hotspot: HotspotPoint; distanceMeters: number } | null>(null);
  const [currentThreatLevel, setCurrentThreatLevel] = useState<'CRITICAL_RISK' | 'MODERATE_CAUTION' | 'SAFE_ZONE'>('SAFE_ZONE');
  const [threatPercentage, setThreatPercentage] = useState<number>(20);

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

    // Invalidate size to guarantee no grey tiles
    setTimeout(() => {
      map.invalidateSize();
    }, 200);

    const handleResize = () => map.invalidateSize();
    window.addEventListener('resize', handleResize);

    // Breadcrumbs Trail Polyline
    const trail = L.polyline([], {
      color: '#06B6D4',
      weight: 4,
      opacity: 0.9,
      dashArray: '4, 8',
      lineCap: 'round'
    }).addTo(map);
    trailPolylineRef.current = trail;

    mapInstanceRef.current = map;

    renderLayers(map, 'ALL');

    // Start with default position
    updateUserPosition(28.6328, 77.2197, 20, 0);

    return () => {
      window.removeEventListener('resize', handleResize);
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

    // Render Hotspots with visible danger zones
    DELHI_HOTSPOTS.forEach((h) => {
      if (filter === 'SAFE') return;
      if (filter === 'HIGH' && h.riskLevel !== 'HIGH') return;
      if (filter === 'MEDIUM' && h.riskLevel !== 'MEDIUM') return;

      const isHigh = h.riskLevel === 'HIGH';
      const color = isHigh ? '#EF4444' : '#F59E0B';
      const fillColor = isHigh ? '#DC2626' : '#D97706';
      const radius = isHigh ? 420 : 280;

      // Visible Danger Zone Perimeter
      const dangerZone = L.circle([h.lat, h.lon], {
        radius,
        color,
        weight: 2,
        fillColor,
        fillOpacity: isHigh ? 0.28 : 0.16,
        dashArray: isHigh ? undefined : '5, 5'
      });

      const iconHtml = `
        <div style="display:flex; flex-direction:column; align-items:center; cursor:pointer;">
          <div style="width:30px; height:30px; border-radius:50%; background:${isHigh ? '#DC2626' : '#D97706'}; box-shadow:0 0 12px ${color}; display:flex; align-items:center; justify-content:center; font-size:14px; color:#fff; border:2px solid #fff;">
            ${isHigh ? '🚨' : '⚠️'}
          </div>
          <div style="font-size:10px; font-weight:800; background:#0F172A; color:${color}; border:1px solid ${color}; padding:2px 6px; border-radius:4px; margin-top:2px; white-space:nowrap; box-shadow:0 2px 4px rgba(0,0,0,0.5);">
            ${h.name.split(' ')[0]} (${Math.round(h.riskScore * 100)}%)
          </div>
        </div>
      `;

      const customIcon = L.divIcon({
        className: 'custom-hotspot-pin',
        html: iconHtml,
        iconSize: [44, 44],
        iconAnchor: [22, 22]
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
            <div><b>Historical Cases:</b> ${h.incidents}</div>
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
            ⚡ Select & Test x402 Micropayment
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
          radius: 460,
          color: '#10B981',
          weight: 2,
          fillColor: '#34D399',
          fillOpacity: 0.22
        });

        const iconHtml = `
          <div style="display:flex; flex-direction:column; align-items:center; cursor:pointer;">
            <div style="width:28px; height:28px; border-radius:50%; background:#059669; box-shadow:0 0 10px #10B981; display:flex; align-items:center; justify-content:center; font-size:13px; color:#fff; border:2px solid #fff;">
              🛡️
            </div>
            <div style="font-size:10px; font-weight:800; background:#064E3B; color:#6EE7B7; border:1px solid #10B981; padding:2px 6px; border-radius:4px; margin-top:2px; white-space:nowrap; box-shadow:0 2px 4px rgba(0,0,0,0.5);">
              Safe Haven (${Math.round(s.riskScore * 100)}%)
            </div>
          </div>
        `;

        const customIcon = L.divIcon({
          className: 'custom-safe-pin',
          html: iconHtml,
          iconSize: [44, 44],
          iconAnchor: [22, 22]
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

  // 3. Update User Location Marker & Continuous Proximity Engine
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

    // Quantitative Threat Index:
    // If distance < 350m: Threat is 80-95%
    // If distance 350-800m: Threat is 50-75%
    // If distance > 800m: Threat is 10-35%
    let calcThreat = 20;
    if (minHotspotDist <= 350 && closestHotspot) {
      setCurrentThreatLevel('CRITICAL_RISK');
      calcThreat = Math.round(closestHotspot.riskScore * 100);
    } else if (minHotspotDist <= 800) {
      setCurrentThreatLevel('MODERATE_CAUTION');
      calcThreat = Math.round(55 + (800 - minHotspotDist) / 450 * 20);
    } else {
      setCurrentThreatLevel('SAFE_ZONE');
      calcThreat = Math.max(12, Math.round(35 - (minHotspotDist - 800) / 2000 * 20));
    }
    setThreatPercentage(calcThreat);

    if (mapInstanceRef.current) {
      const map = mapInstanceRef.current;

      const userRadarIcon = L.divIcon({
        className: 'user-radar-beacon',
        html: `
          <div class="relative flex items-center justify-center">
            <div class="w-8 h-8 rounded-full bg-cyan-500 border-2 border-white shadow-2xl flex items-center justify-center text-slate-950 font-black text-xs z-10 radar-pulse-marker">
              📍
            </div>
            <div class="absolute w-14 h-14 bg-cyan-400/40 rounded-full animate-ping pointer-events-none"></div>
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
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
          weight: 1.5,
          fillColor: '#22D3EE',
          fillOpacity: 0.14
        }).addTo(map);
      } else {
        userAccuracyCircleRef.current.setLatLng([lat, lon]);
        userAccuracyCircleRef.current.setRadius(Math.max(accuracy, 60));
      }

      map.panTo([lat, lon], { animate: true, duration: 0.8 });
    }
  };

  const startContinuousTracking = () => {
    if (!navigator.geolocation) {
      setGpsError('Geolocation is not supported by your browser.');
      return;
    }

    setGpsError('');
    setIsGpsActive(true);

    const id = navigator.geolocation.watchPosition(
      (pos) => {
        const { latitude, longitude, accuracy, speed } = pos.coords;
        updateUserPosition(latitude, longitude, accuracy, speed);
      },
      (err) => {
        let msg = err.message;
        if (err.code === 1) msg = 'Location permission denied. Please click "Allow" in browser address bar.';
        else if (err.code === 2) msg = 'GPS signal unavailable. Defaulting to Central Delhi.';
        else if (err.code === 3) msg = 'GPS request timed out.';
        setGpsError(msg);
        setIsGpsActive(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 1000
      }
    );

    setWatchId(id);
  };

  const toggleSimulation = () => {
    if (isSimulating) {
      if (simulationTimerRef.current) clearInterval(simulationTimerRef.current);
      setIsSimulating(false);
      return;
    }

    if (watchId !== null) {
      navigator.geolocation.clearWatch(watchId);
      setWatchId(null);
      setIsGpsActive(false);
    }

    setIsSimulating(true);
    setSimulationIndex(0);

    let idx = 0;
    const firstPoint = SIMULATION_ROUTE[0];
    updateUserPosition(firstPoint.lat, firstPoint.lon, 20, 4.5);

    simulationTimerRef.current = setInterval(() => {
      idx = (idx + 1) % SIMULATION_ROUTE.length;
      setSimulationIndex(idx);
      const pt = SIMULATION_ROUTE[idx];
      updateUserPosition(pt.lat, pt.lon, 18 + Math.random() * 12, 3.8 + Math.random() * 2);
    }, 2800);
  };

  const centerOnUser = () => {
    if (userLocation && mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([userLocation.lat, userLocation.lon], 15, { duration: 1.2 });
    }
  };

  return (
    <div className="relative w-full h-[640px] rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 shadow-2xl flex flex-col">
      
      {/* Top Floating Glassmorphic HUD Bar */}
      <div className="absolute top-4 left-4 right-4 z-[500] flex flex-wrap items-center justify-between gap-3 pointer-events-none">
        
        {/* Real-time Threat Badge & Hotspot Proximity */}
        <div className="pointer-events-auto bg-slate-900/95 backdrop-blur-md border border-slate-700/80 rounded-xl p-3 shadow-xl flex items-center gap-3">
          <div className="flex items-center gap-2.5">
            <div className={`w-3.5 h-3.5 rounded-full ${
              currentThreatLevel === 'CRITICAL_RISK' ? 'bg-rose-500 animate-ping' :
              currentThreatLevel === 'MODERATE_CAUTION' ? 'bg-amber-400 animate-pulse' :
              'bg-emerald-400'
            }`}></div>
            <div>
              <div className="text-[10px] uppercase font-black tracking-wider text-slate-400">
                Live Movement Radar
              </div>
              <div className={`text-xs font-black ${
                currentThreatLevel === 'CRITICAL_RISK' ? 'text-rose-400' :
                currentThreatLevel === 'MODERATE_CAUTION' ? 'text-amber-400' :
                'text-emerald-400'
              }`}>
                {currentThreatLevel === 'CRITICAL_RISK' ? '🚨 HIGH RISK CORRIDOR' :
                 currentThreatLevel === 'MODERATE_CAUTION' ? '⚠️ MODERATE CAUTION' :
                 '🛡️ SAFE HAVEN CORRIDOR'} ({threatPercentage}%)
              </div>
            </div>
          </div>

          {nearestHotspot && (
            <div className="border-l border-slate-700/80 pl-3 hidden sm:block">
              <div className="text-[10px] text-slate-400 uppercase font-bold">Closest Crime Centroid</div>
              <div className="text-xs font-semibold text-slate-200 truncate max-w-[210px]">
                {nearestHotspot.hotspot.name} <span className="text-rose-400 font-mono">({nearestHotspot.distanceMeters}m)</span>
              </div>
            </div>
          )}
        </div>

        {/* Filter Pill Tabs */}
        <div className="pointer-events-auto bg-slate-900/95 backdrop-blur-md border border-slate-700/80 rounded-xl p-1 shadow-xl flex items-center gap-1">
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
            onClick={() => setActiveFilter('SAFE')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1 ${
              activeFilter === 'SAFE' ? 'bg-emerald-700 text-white shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" /> Safe Havens
          </button>
        </div>

        {/* Action Controls: Live GPS, Simulation, Center */}
        <div className="pointer-events-auto flex items-center gap-2">
          
          {/* GPS Tracking Trigger Button */}
          <button
            onClick={startContinuousTracking}
            className={`px-3 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-lg transition-all ${
              isGpsActive
                ? 'bg-emerald-600 text-white border border-emerald-400 shadow-emerald-500/30'
                : 'bg-slate-800/90 hover:bg-slate-700 text-cyan-300 border border-slate-700 backdrop-blur'
            }`}
            title="Start continuous GPS live tracking of your movement"
          >
            <Crosshair className={`w-3.5 h-3.5 ${isGpsActive ? 'animate-spin' : ''}`} />
            <span>{isGpsActive ? '🛰️ Tracking GPS Movement' : '🛰️ Track My Movement'}</span>
          </button>

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
                <Play className="w-3.5 h-3.5 text-amber-400" />
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

      {/* Main Leaflet Map Viewport - Guaranteed 100% height */}
      <div 
        ref={mapContainerRef} 
        className="w-full flex-1 min-h-[500px] z-10" 
      />

      {/* Bottom Floating Movement Status Ribbon with Dynamic Danger Meter */}
      <div className="absolute bottom-4 left-4 right-4 z-[500] pointer-events-none flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        
        {/* Coordinates and Speed HUD */}
        <div className="pointer-events-auto bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-xl px-4 py-2.5 shadow-2xl flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
            <div>
              <span className="text-slate-400 text-[10px] block">LIVE GPS POSITION</span>
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
              {trailHistory.length} Waypoints
            </span>
          </div>

          <div className="border-l border-slate-800 pl-4 hidden lg:block">
            <span className="text-slate-400 text-[10px] block">POLICE EMERGENCY</span>
            <span className="text-slate-200 font-semibold flex items-center gap-1">
              <PhoneCall className="w-3 h-3 text-rose-400" /> Dial 112 / 1090
            </span>
          </div>
        </div>

        {/* Dynamic Threat Meter Bar */}
        <div className="pointer-events-auto bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-xl px-4 py-2.5 shadow-2xl flex items-center gap-3 text-xs">
          <span className="text-[10px] font-bold text-slate-400 uppercase">Live Threat Level:</span>
          <div className="w-28 bg-slate-800 h-2.5 rounded-full overflow-hidden border border-slate-700">
            <div 
              className={`h-full transition-all duration-500 ${
                threatPercentage >= 60 ? 'bg-rose-500' :
                threatPercentage >= 45 ? 'bg-amber-400' :
                'bg-emerald-400'
              }`}
              style={{ width: `${threatPercentage}%` }}
            />
          </div>
          <span className={`font-mono font-black text-xs ${
            threatPercentage >= 60 ? 'text-rose-400' :
            threatPercentage >= 45 ? 'text-amber-400' :
            'text-emerald-400'
          }`}>
            {threatPercentage}%
          </span>
        </div>

      </div>

      {gpsError && (
        <div className="absolute top-20 left-4 z-[500] bg-rose-950/90 border border-rose-600 text-rose-200 text-xs px-3 py-2 rounded-lg backdrop-blur shadow-lg">
          ⚠️ {gpsError}
        </div>
      )}

    </div>
  );
};
