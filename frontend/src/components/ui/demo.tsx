import React, { useState } from "react";
import { AdvancedMap } from "@/components/ui/interactive-map";

export default function DemoOne() {
  const [markers, setMarkers] = useState([
    {
      id: 1,
      position: [28.6328, 77.2197] as [number, number],
      color: "red",
      size: "medium" as const,
      popup: {
        title: "Rajiv Chowk Metro Inner Circle",
        content: "Dominant Offense: Chain/Phone Snatching (BNS 309). Peak: 17:00-22:00.",
        image:
          "https://images.unsplash.com/photo-1596401057633-54a8fe8ef647?w=600&auto=format&fit=crop&q=80",
      },
    },
    {
      id: 2,
      position: [28.6506, 77.2303] as [number, number],
      color: "red",
      size: "large" as const,
      popup: {
        title: "Chandni Chowk Main Market",
        content: "Commercial Hub • Dense Pedestrian Traffic & Pickpocketing vulnerability.",
        image:
          "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=600&auto=format&fit=crop&q=80",
      },
    },
    {
      id: 3,
      position: [28.5921, 77.1563] as [number, number],
      color: "blue",
      size: "medium" as const,
      popup: {
        title: "Dhaula Kuan Police Picket",
        content: "Guarded 24/7 Checkpoint & Tactical Interception Barrier.",
        image:
          "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600&auto=format&fit=crop&q=80",
      },
    },
  ]);

  const polygons = [
    {
      id: 1,
      positions: [
        [28.634, 77.215],
        [28.638, 77.225],
        [28.628, 77.222],
      ],
      style: { color: "#a855f7", weight: 2, fillOpacity: 0.35 },
      popup: "Connaught Place High Deterrence Zone",
    },
  ];

  const circles = [
    {
      id: 1,
      center: [28.6328, 77.2197] as [number, number],
      radius: 600,
      style: { color: "#f43f5e", fillOpacity: 0.2 },
      popup: "DBSCAN Cluster ε=600m Crime Hotspot Buffer",
    },
    {
      id: 2,
      center: [28.5921, 77.1563] as [number, number],
      radius: 400,
      style: { color: "#10b981", fillOpacity: 0.25 },
      popup: "Guarded Safe Haven Perimeter",
    },
  ];

  const handleMarkerClick = (marker: any) => {
    console.log("Marker clicked:", marker);
  };

  const handleMapClick = (latlng: any) => {
    console.log("Map clicked at:", latlng);
  };

  return (
    <div className="w-full space-y-4">
      <h2 className="text-xl font-bold text-white">Interactive Map Demo</h2>
      <AdvancedMap
        center={[28.6328, 77.2197]}
        zoom={12}
        markers={markers}
        polygons={polygons}
        circles={circles}
        onMarkerClick={handleMarkerClick}
        onMapClick={handleMapClick}
        enableClustering={true}
        enableSearch={true}
        enableControls={true}
        style={{ height: "600px", width: "100%" }}
      />
    </div>
  );
}
