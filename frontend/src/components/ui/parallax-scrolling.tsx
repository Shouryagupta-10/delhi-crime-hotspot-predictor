// src/components/ui/parallax-scrolling.tsx
'use client';

import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from '@studio-freight/lenis';

export interface ParallaxProps {
  title?: string;
  subtitle?: string;
}

export function ParallaxComponent({ title = 'Parallax', subtitle }: ParallaxProps) {
  const parallaxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);

    const triggerElement = parallaxRef.current?.querySelector('[data-parallax-layers]');

    let tl: gsap.core.Timeline | null = null;
    if (triggerElement) {
      tl = gsap.timeline({
        scrollTrigger: {
          trigger: triggerElement,
          start: '0% 0%',
          end: '100% 0%',
          scrub: 0
        }
      });

      const layers = [
        { layer: '1', yPercent: 70 },
        { layer: '2', yPercent: 55 },
        { layer: '3', yPercent: 40 },
        { layer: '4', yPercent: 10 }
      ];

      layers.forEach((layerObj, idx) => {
        tl?.to(
          triggerElement.querySelectorAll(`[data-parallax-layer="${layerObj.layer}"]`),
          {
            yPercent: layerObj.yPercent,
            ease: 'none'
          },
          idx === 0 ? undefined : '<'
        );
      });
    }

    const lenis = new Lenis();
    lenis.on('scroll', ScrollTrigger.update);
    const tickerCallback = (time: number) => { lenis.raf(time * 1000); };
    gsap.ticker.add(tickerCallback);
    gsap.ticker.lagSmoothing(0);

    return () => {
      ScrollTrigger.getAll().forEach(st => st.kill());
      if (triggerElement) gsap.killTweensOf(triggerElement);
      gsap.ticker.remove(tickerCallback);
      lenis.destroy();
    };
  }, []);

  return (
    <div className="parallax" ref={parallaxRef}>
      <style>{`
        .parallax {
          position: relative;
          width: 100%;
          overflow: hidden;
          background: #080c14;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .parallax__header {
          position: relative;
          height: 90vh;
          min-height: 540px;
          width: 100%;
          overflow: hidden;
        }
        .parallax__visuals {
          position: absolute;
          inset: 0;
          width: 100%;
          height: 100%;
        }
        .parallax__black-line-overflow {
          position: absolute;
          top: -2px;
          left: 0;
          right: 0;
          height: 4px;
          background: #080c14;
          z-index: 10;
        }
        .parallax__layers {
          position: relative;
          width: 100%;
          height: 100%;
        }
        .parallax__layer-img {
          position: absolute;
          bottom: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 100%;
          height: 100%;
          object-fit: cover;
          pointer-events: none;
        }
        .parallax__layer-title {
          position: absolute;
          top: 38%;
          left: 50%;
          transform: translate(-50%, -50%);
          text-align: center;
          z-index: 3;
          width: 100%;
          padding: 0 20px;
        }
        .parallax__title {
          font-size: clamp(2.5rem, 8vw, 6.5rem);
          font-weight: 900;
          letter-spacing: -0.04em;
          color: #ffffff;
          text-transform: uppercase;
          margin: 0;
          text-shadow: 0 10px 40px rgba(0,0,0,0.85);
          background: linear-gradient(180deg, #ffffff 0%, #94a3b8 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .parallax__subtitle {
          font-size: clamp(0.9rem, 2vw, 1.25rem);
          color: #38bdf8;
          font-weight: 600;
          margin-top: 10px;
          letter-spacing: 0.1em;
          text-transform: uppercase;
        }
        .parallax__fade {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          height: 220px;
          background: linear-gradient(to top, #080c14 0%, transparent 100%);
          z-index: 5;
          pointer-events: none;
        }
        .parallax__content {
          position: relative;
          z-index: 6;
          padding: 40px 20px;
          display: flex;
          justify-content: center;
          align-items: center;
          background: #080c14;
        }
        .osmo-icon-svg {
          width: 60px;
          height: 60px;
          color: #38bdf8;
        }
      `}</style>
      <section className="parallax__header">
        <div className="parallax__visuals">
          <div className="parallax__black-line-overflow"></div>
          <div data-parallax-layers className="parallax__layers">
            <img 
              src="https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1600&auto=format&fit=crop&q=80" 
              loading="eager" 
              width="1600" 
              data-parallax-layer="1" 
              alt="Background Horizon" 
              className="parallax__layer-img" 
              style={{ filter: 'brightness(0.5) contrast(1.2)' }}
            />
            <img 
              src="https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=1600&auto=format&fit=crop&q=80" 
              loading="eager" 
              width="1600" 
              data-parallax-layer="2" 
              alt="Midground City" 
              className="parallax__layer-img" 
              style={{ opacity: 0.85, mixBlendMode: 'screen', filter: 'brightness(0.6)' }}
            />
            <div data-parallax-layer="3" className="parallax__layer-title">
              <h2 className="parallax__title">{title}</h2>
              {subtitle && <p className="parallax__subtitle">{subtitle}</p>}
            </div>
            <img 
              src="https://images.unsplash.com/photo-1587474260584-136574528ed5?w=1600&auto=format&fit=crop&q=80" 
              loading="eager" 
              width="1600" 
              data-parallax-layer="4" 
              alt="Foreground Silhouettes" 
              className="parallax__layer-img" 
              style={{ opacity: 0.75, mixBlendMode: 'lighten' }}
            />
          </div>
          <div className="parallax__fade"></div>
        </div>
      </section>
      <section className="parallax__content">
        <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 160 160" fill="none" className="osmo-icon-svg">
          <path d="M94.8284 53.8578C92.3086 56.3776 88 54.593 88 51.0294V0H72V59.9999C72 66.6273 66.6274 71.9999 60 71.9999H0V87.9999H51.0294C54.5931 87.9999 56.3777 92.3085 53.8579 94.8283L18.3431 130.343L29.6569 141.657L65.1717 106.142C67.684 103.63 71.9745 105.396 72 108.939V160L88.0001 160L88 99.9999C88 93.3725 93.3726 87.9999 100 87.9999H160V71.9999H108.939C105.407 71.9745 103.64 67.7091 106.12 65.1938L106.142 65.1716L141.657 29.6568L130.343 18.3432L94.8284 53.8578Z" fill="currentColor"></path>
        </svg>
      </section>
    </div>
  );
}

export default ParallaxComponent;
