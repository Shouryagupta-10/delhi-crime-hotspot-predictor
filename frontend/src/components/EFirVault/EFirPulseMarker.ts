/**
 * Custom Leaflet Pulse Marker Icon for Real-Time "Pending Investigation" e-FIR Incidents
 */
import L from 'leaflet';

export function createEFirPulseIcon(isNewlySubmitted = false): L.DivIcon {
  const pulseColor = isNewlySubmitted ? '#ec4899' : '#8b5cf6'; // pink-500 or violet-500
  const glowShadow = isNewlySubmitted 
    ? '0 0 15px rgba(236, 72, 153, 0.9), 0 0 30px rgba(236, 72, 153, 0.4)' 
    : '0 0 15px rgba(139, 92, 246, 0.9), 0 0 30px rgba(139, 92, 246, 0.4)';

  const html = `
    <div style="position: relative; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; cursor: pointer;">
      <!-- Outer expanding pulse ring 1 -->
      <span style="
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 9999px;
        background: ${pulseColor};
        opacity: 0.75;
        animation: efir-ping 1.8s cubic-bezier(0, 0, 0.2, 1) infinite;
      "></span>

      <!-- Secondary outer pulse ring -->
      <span style="
        position: absolute;
        width: 80%;
        height: 80%;
        border-radius: 9999px;
        border: 2px solid ${pulseColor};
        opacity: 0.9;
        animation: efir-pulse 2s ease-in-out infinite;
      "></span>

      <!-- Core solid emblem badge -->
      <div style="
        position: relative;
        z-index: 10;
        width: 26px;
        height: 26px;
        border-radius: 9999px;
        background: #090b10;
        border: 2px solid ${pulseColor};
        box-shadow: ${glowShadow};
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-size: 11px;
        font-weight: 800;
        user-select: none;
      ">
        ⚖️
      </div>

      <!-- Small status pill badge -->
      <span style="
        position: absolute;
        bottom: -7px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 20;
        background: #090b10;
        border: 1px solid ${pulseColor};
        color: #f1f5f9;
        font-family: monospace;
        font-size: 8px;
        font-weight: 800;
        padding: 0px 4px;
        border-radius: 4px;
        white-space: nowrap;
        box-shadow: 0 2px 6px rgba(0,0,0,0.8);
        letter-spacing: 0.5px;
      ">
        e-FIR
      </span>

      <style>
        @keyframes efir-ping {
          0% { transform: scale(0.8); opacity: 0.9; }
          75%, 100% { transform: scale(2.2); opacity: 0; }
        }
        @keyframes efir-pulse {
          0%, 100% { transform: scale(1); opacity: 0.9; }
          50% { transform: scale(1.3); opacity: 0.4; }
        }
      </style>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'efir-live-pulse-marker',
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -20]
  });
}
