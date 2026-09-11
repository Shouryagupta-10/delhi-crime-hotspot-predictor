// src/demos/parallax-demo.tsx
import { ParallaxComponent } from '@/components/ui/parallax-scrolling';

export default function ParallaxDemo() {
  return (
    <>
      <ParallaxComponent title="Rakshak.ai" subtitle="Predictive Policing & Civic Geospatial Deterrence" />
      <div className="osmo-credits" style={{ padding: '20px', textAlign: 'center', color: '#64748b', fontSize: '13px' }}>
        <p className="osmo-credits__p">
          Resource by <a target="_blank" rel="noreferrer" href="https://www.osmo.supply/" style={{ color: '#38bdf8' }}>Osmo</a>
        </p>
      </div>
    </>
  );
}
