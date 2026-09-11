# Rakshak.ai — Frontend Web Application

Modern, high-performance civic safety intelligence & predictive policing interface built with **React 18**, **TypeScript**, **Vite**, **Tailwind CSS**, and **Leaflet**.

---

## 🚀 Quick Start

From this directory (`frontend/`):

```bash
# 1. Install dependencies
npm install

# 2. Run local development server
npm run dev
```

The application will launch at `http://localhost:5173`.

---

## 📂 Directory Structure

- `src/App.tsx`: Main application shell with glassmorphic navbar, tab routing, live GPS tracking, and safety metrics.
- `src/components/PredictivePolicingStudio.tsx`: The 5-pillar predictive policing suite:
  - 🚔 Patrol Dispatcher (Koper Curve 14m dwell, TSP loop, shift handover alert).
  - 🔁 Near-Repeat Knox Engine (anchor incident selector, 72h contagion slider).
  - 🛡️ Safest Corridor Navigator (Direct high-risk vs protected safe corridor comparison).
  - 🛑 Emergency Choke-Point Barricades (Getaway velocity perimeters & Delhi egress pickets).
  - ⚡ B2B Fleet & Drone Guard x402 Risk API (Enterprise micropayments).
- `src/components/SmoothRiskMap.tsx`: Smooth Leaflet map with dark theme, animated GPS radar, and DBSCAN hotspot cluster layers.
- `index.html`: Entry point with Plus Jakarta Sans and JetBrains Mono typography.
- `vite.config.ts`: Vite build configuration.
- `vercel.json`: Production deployment rules for Vercel.

---

## 🌐 Production Deployment

- **Live URL**: https://x402-client-delta.vercel.app
- **Deploy Command**: `npx vercel --prod`
