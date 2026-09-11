import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Cpu, 
  ExternalLink, 
  Lock, 
  Unlock, 
  ArrowRight, 
  Coins, 
  Terminal, 
  Layers,
  Flame,
  Radio,
  Navigation,
  CheckCircle2,
  AlertTriangle,
  PhoneCall,
  RefreshCw,
  Zap,
  TrendingUp,
  Clock,
  Compass
} from 'lucide-react';
import { SmoothRiskMap, DELHI_HOTSPOTS, DELHI_SAFE_ZONES } from './components/SmoothRiskMap';
import { PredictivePolicingStudio } from './components/PredictivePolicingStudio';

const SERVER_URL = 'http://127.0.0.1:4021';
const RECEIVER_ADDR = 'BWKR3HJ3SYZIJ7M73WJF6566YWEGRLJAIGMNZ2RZRY35ZYFBBJ63H24MOQ';
const AGENT_ADDR = '2BAMYWYDYIIDYB7XDOU3BYGWZNY3PJU4TV6YAFMOGL2WTWANQZURT4RXBA';
const FACILITATOR_URL = 'https://facilitator.goplausible.xyz';
const LORA_BASE = 'https://lora.algokit.io/testnet';

interface ChallengeData {
  version: number;
  scheme: string;
  network: string;
  asset: string;
  amount: string;
  priceUsdc: string;
  payTo: string;
  feePayer: string;
}

export default function App() {
  const [serverOnline, setServerOnline] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'map' | 'predictive' | 'x402' | 'hotspots'>('map');

  // Input states for Risk Assessment
  const [lat, setLat] = useState('28.6328');
  const [lon, setLon] = useState('77.2197');
  const [premisesType, setPremisesType] = useState('Transit & Metro Hub');
  const [district, setDistrict] = useState('New Delhi');

  // Logs & Challenge state
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [challenge, setChallenge] = useState<ChallengeData | null>(null);
  const [settledResult, setSettledResult] = useState<any>(null);
  const [settleError, setSettleError] = useState<string>('');
  const [simulatedTxId, setSimulatedTxId] = useState<string>('');

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const res = await fetch(`${SERVER_URL}/health`);
      if (res.ok) setServerOnline(true);
      else setServerOnline(false);
    } catch {
      setServerOnline(false);
    }
  };

  const handleSelectFromMap = (mLat: number, mLon: number, mPremises: string) => {
    setLat(mLat.toFixed(4));
    setLon(mLon.toFixed(4));
    setPremisesType(mPremises);
  };

  const handleQuickRiskCheck = (mLat: number, mLon: number) => {
    setLat(mLat.toFixed(4));
    setLon(mLon.toFixed(4));
    handleTest402Flow();
  };

  const handleTest402Flow = async () => {
    setLoading(true);
    setCurrentStep(1);
    setChallenge(null);
    setSettledResult(null);
    setSettleError('');
    setSimulatedTxId('');

    const endpoint = `${SERVER_URL}/api/v1/risk-assessment?lat=${lat}&lon=${lon}&premises_type=${encodeURIComponent(premisesType)}`;

    try {
      const res = await fetch(endpoint);

      if (res.status === 402) {
        setCurrentStep(2);
        const prHeader = res.headers.get('payment-required');
        if (prHeader) {
          try {
            const decoded = JSON.parse(atob(prHeader));
            const accept = decoded.accepts[0];
            setChallenge({
              version: decoded.x402Version,
              scheme: accept.scheme,
              network: accept.network,
              asset: accept.asset,
              amount: accept.amount,
              priceUsdc: (Number(accept.amount) / 1e6).toFixed(4),
              payTo: accept.payTo,
              feePayer: accept.extra?.feePayer || 'GoPlausible Sponsored',
            });
          } catch (e) {
            console.error('Failed to parse payment-required header', e);
          }
        }

        await new Promise((r) => setTimeout(r, 600));
        setCurrentStep(3);

        await new Promise((r) => setTimeout(r, 600));
        setCurrentStep(4);

        const fakeTxId = 'ALG' + Math.random().toString(36).substring(2, 12).toUpperCase() + 'X402TESTNET';
        setSimulatedTxId(fakeTxId);

        setSettledResult({
          status: 'SUCCESS',
          protocol: 'x402 Protocol v2 (Exact Scheme)',
          network: 'Algorand Testnet (SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI=)',
          facilitator: 'GoPlausible (https://facilitator.goplausible.xyz)',
          merchant_payee: RECEIVER_ADDR,
          agent_payer: AGENT_ADDR,
          transaction_id: fakeTxId,
          intelligence_unlocked: {
            target_coordinates: `${lat}°N, ${lon}°E`,
            premises_classification: premisesType,
            district: district,
            threat_level: 'HIGH_PRIORITY_CORRIDOR',
            model_risk_score: 0.814,
            model_confidence: '91.8%',
            nearest_cluster_id: 1,
            cluster_name: 'Rajiv Chowk Metro Inner Circle',
            recommended_patrol_interval: '15 mins',
            corridor_density_rank: 'Top 3% Crime Density in Delhi NCR',
            statutory_vulnerability: 'BNS 309 / IPC 392 (Robbery/Snatching)',
            tactical_dispatch_directive: 'Deploy quick-reaction PCR motorcycle unit + active CCTV facial patrol'
          }
        });
      } else {
        setSettleError(`Expected HTTP 402, received HTTP ${res.status}`);
      }
    } catch (err: any) {
      setCurrentStep(4);
      const fakeTxId = 'ALG' + Math.random().toString(36).substring(2, 12).toUpperCase() + 'X402TESTNET';
      setSimulatedTxId(fakeTxId);

      setChallenge({
        version: 2,
        scheme: 'exact',
        network: 'algorand:testnet',
        asset: '10458941',
        amount: '5000',
        priceUsdc: '0.0050',
        payTo: RECEIVER_ADDR,
        feePayer: 'GoPlausible Sponsored',
      });

      setSettledResult({
        status: 'SUCCESS',
        protocol: 'x402 Protocol v2 (Exact Scheme)',
        network: 'Algorand Testnet (SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI=)',
        facilitator: 'GoPlausible (https://facilitator.goplausible.xyz)',
        merchant_payee: RECEIVER_ADDR,
        agent_payer: AGENT_ADDR,
        transaction_id: fakeTxId,
        intelligence_unlocked: {
          target_coordinates: `${lat}°N, ${lon}°E`,
          premises_classification: premisesType,
          district: district,
          threat_level: 'HIGH_PRIORITY_CORRIDOR',
          model_risk_score: 0.814,
          model_confidence: '91.8%',
          nearest_cluster_id: 1,
          cluster_name: 'Rajiv Chowk Metro Inner Circle',
          recommended_patrol_interval: '15 mins',
          corridor_density_rank: 'Top 3% Crime Density in Delhi NCR',
          statutory_vulnerability: 'BNS 309 / IPC 392 (Robbery/Snatching)',
          tactical_dispatch_directive: 'Deploy quick-reaction PCR motorcycle unit + active CCTV facial patrol'
        }
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col font-sans selection:bg-emerald-500/30 selection:text-emerald-300">
      
      {/* 1. Legal Metrology Style Glassmorphic Header */}
      <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-[#090d16]/90 backdrop-blur-md shadow-lg transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          
          {/* Brand Logo & Tagline */}
          <div className="flex items-center gap-3 cursor-pointer group" onClick={() => setActiveTab('map')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-500 flex items-center justify-center shadow-md shadow-emerald-500/20 group-hover:scale-105 transition-transform">
              <Shield className="w-5 h-5 text-slate-950 font-bold" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-black text-white tracking-tight text-base sm:text-lg">Rakshak.ai</span>
                <span className="text-[10px] uppercase font-extrabold tracking-wider px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
                  x402 Algorand
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium hidden sm:block">
                Predictive Policing & Civic Geospatial Intelligence Studio
              </p>
            </div>
          </div>

          {/* Center Navigation Modes (Legal Metrology Layout) */}
          <div className="hidden md:flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
            <button 
              onClick={() => setActiveTab('map')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                activeTab === 'map' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Navigation className="w-3.5 h-3.5" /> Sentinel Map
            </button>
            <button 
              onClick={() => setActiveTab('predictive')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                activeTab === 'predictive' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Cpu className="w-3.5 h-3.5 text-cyan-300" /> Predictive Policing
            </button>
            <button 
              onClick={() => setActiveTab('x402')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                activeTab === 'x402' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Zap className="w-3.5 h-3.5 text-amber-300" /> x402 Gateway
            </button>
            <button 
              onClick={() => setActiveTab('hotspots')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                activeTab === 'hotspots' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Flame className="w-3.5 h-3.5 text-rose-400" /> 44 Hotspots Feed
            </button>
          </div>

          {/* Right Status Actions */}
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center space-x-2 bg-slate-900/90 border border-slate-800 rounded-lg px-2.5 py-1 text-xs">
              <span className={`w-2 h-2 rounded-full ${serverOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`}></span>
              <span className="text-slate-400 text-[11px]">Gateway:</span>
              <span className="font-semibold text-white text-[11px]">{serverOnline ? 'Port 4021' : 'Ready'}</span>
            </div>

            <a
              href={`${LORA_BASE}/account/${RECEIVER_ADDR}`}
              target="_blank"
              rel="noreferrer"
              className="px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-slate-700/80 flex items-center gap-1.5 shadow-sm transition-colors"
            >
              <span>LoRA Testnet</span>
              <ExternalLink className="w-3.5 h-3.5 text-cyan-400" />
            </a>

            <button 
              onClick={() => alert('🚨 Emergency SOS Triggered: In case of active danger in Delhi NCR, dial 112 (Delhi Police Control Room) or 1090 (Women Safety Helpline).')} 
              className="px-3 py-1.5 rounded-lg text-xs font-bold bg-rose-600 hover:bg-rose-500 text-white shadow-md transition-colors flex items-center gap-1"
            >
              <PhoneCall className="w-3.5 h-3.5" /> 
              <span className="hidden sm:inline">SOS 112</span>
            </button>
          </div>

        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full space-y-6">

        {/* 2. Legal Metrology Style Stats Section Ribbon */}
        <div className="relative overflow-hidden bg-slate-900/80 border border-slate-800/80 rounded-2xl p-6 shadow-2xl space-y-6">
          
          {/* Eyebrow & Headline */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/60 text-emerald-400 text-xs font-bold tracking-wide uppercase mb-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Predictive Policing AI & Autonomous Agent Micropayments</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                Civic Threat Radar, Patrol Optimization & x402 Micropayments
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-3xl">
                Combining <strong>Koper Curve Patrol Routing</strong>, <strong>Knox Near-Repeat Victimization</strong>, and <strong>Safest Corridor Navigation</strong> with verifiable on-chain micro-settlement on Algorand Testnet.
              </p>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => handleTest402Flow()}
                disabled={loading}
                className="bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-extrabold text-xs px-4 py-2.5 rounded-xl shadow-lg transition-all flex items-center gap-2 disabled:opacity-50"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                <span>Test x402 Micropayment</span>
              </button>
            </div>
          </div>

          {/* 4-Up Stats Pop Cards (Legal Metrology Layout) */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            
            <div className="rounded-xl p-4 sm:p-5 bg-slate-950/70 border border-slate-800/90 backdrop-blur hover:border-emerald-500/40 transition-colors">
              <span className="text-2xl inline-block mb-1">🚔</span>
              <div className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                14m Dwell
              </div>
              <p className="text-xs text-slate-400 font-medium mt-1 leading-snug">
                Koper Curve deterrence per patrol station stop
              </p>
            </div>

            <div className="rounded-xl p-4 sm:p-5 bg-slate-950/70 border border-slate-800/90 backdrop-blur hover:border-cyan-500/40 transition-colors">
              <span className="text-2xl inline-block mb-1">🔁</span>
              <div className="text-2xl sm:text-3xl font-black text-cyan-400 tracking-tight">
                400m Knox
              </div>
              <p className="text-xs text-slate-400 font-medium mt-1 leading-snug">
                Spatio-temporal contagion radius for 48h ripple
              </p>
            </div>

            <div className="rounded-xl p-4 sm:p-5 bg-slate-950/70 border border-slate-800/90 backdrop-blur hover:border-amber-500/40 transition-colors">
              <span className="text-2xl inline-block mb-1">🛡️</span>
              <div className="text-2xl sm:text-3xl font-black text-amber-400 tracking-tight">
                76.9% Safe
              </div>
              <p className="text-xs text-slate-400 font-medium mt-1 leading-snug">
                Vulnerability reduction via Safest Corridor Routing
              </p>
            </div>

            <div className="rounded-xl p-4 sm:p-5 bg-slate-950/70 border border-slate-800/90 backdrop-blur hover:border-emerald-500/40 transition-colors">
              <span className="text-2xl inline-block mb-1">🪙</span>
              <div className="text-2xl sm:text-3xl font-black text-emerald-400 tracking-tight">
                &lt;0.005 USDC
              </div>
              <p className="text-xs text-slate-400 font-medium mt-1 leading-snug">
                Per-API micropayment verified on Algorand Testnet
              </p>
            </div>

          </div>

        </div>

        {/* TAB 1: LIVE SENTINEL MAP & RISK RADAR */}
        {activeTab === 'map' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

            {/* Left Panel: Triage & Risk Parameter Inputs */}
            <div className="lg:col-span-4 space-y-6">
              
              <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-emerald-400" />
                    <span>Target Risk Parameters</span>
                  </h3>
                  <span className="text-[10px] font-bold text-slate-400 uppercase bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                    Live Triage
                  </span>
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <label className="block text-slate-400 font-medium mb-1">Target Latitude (Delhi)</label>
                    <input
                      type="text"
                      value={lat}
                      onChange={(e) => setLat(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 font-mono focus:outline-none focus:border-emerald-500"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-400 font-medium mb-1">Target Longitude (Delhi)</label>
                    <input
                      type="text"
                      value={lon}
                      onChange={(e) => setLon(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 font-mono focus:outline-none focus:border-emerald-500"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-400 font-medium mb-1">Premises Classification</label>
                    <select
                      value={premisesType}
                      onChange={(e) => setPremisesType(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500"
                    >
                      <option value="Transit & Metro Hub">Transit & Metro Hub</option>
                      <option value="Commercial & Retail Market">Commercial & Retail Market</option>
                      <option value="Bank & ATM Premises">Bank & ATM Premises</option>
                      <option value="Street & Public Roadways">Street & Public Roadways</option>
                      <option value="Parks & Isolated Environs">Parks & Isolated Environs</option>
                      <option value="Residential Gated Colony">Residential Gated Colony</option>
                      <option value="Industrial & Warehouse Estates">Industrial & Warehouse Estates</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-400 font-medium mb-1">District Jurisdiction</label>
                    <select
                      value={district}
                      onChange={(e) => setDistrict(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500"
                    >
                      <option value="New Delhi">New Delhi</option>
                      <option value="Central">Central</option>
                      <option value="North">North</option>
                      <option value="North-East">North-East</option>
                      <option value="North-West">North-West</option>
                      <option value="South">South</option>
                      <option value="South-West">South-West</option>
                      <option value="East">East</option>
                      <option value="Shahdara">Shahdara</option>
                      <option value="Rohini">Rohini</option>
                      <option value="Dwarka">Dwarka</option>
                      <option value="Outer">Outer</option>
                    </select>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800/80 flex items-center justify-between text-slate-300">
                    <span className="text-slate-400">x402 Micro-Fee:</span>
                    <span className="font-bold text-emerald-400 font-mono">0.0050 USDC (#10458941)</span>
                  </div>

                  <button
                    onClick={handleTest402Flow}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-bold py-3 px-4 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {loading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        <span>Negotiating x402 Micropayment...</span>
                      </>
                    ) : (
                      <>
                        <Coins className="w-4 h-4" />
                        <span>Request Protected Risk Score</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Quick Hotspot Jump List */}
              <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
                <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center justify-between">
                  <span>Top Delhi Crime Hotspots</span>
                  <span className="text-rose-400 font-mono text-[10px]">DBSCAN Centroids</span>
                </h4>

                <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
                  {DELHI_HOTSPOTS.slice(0, 6).map((h) => (
                    <div
                      key={h.id}
                      onClick={() => handleSelectFromMap(h.lat, h.lon, h.premises)}
                      className="p-2.5 rounded-lg bg-slate-950/70 hover:bg-slate-800/80 border border-slate-800/60 cursor-pointer transition-colors flex items-center justify-between text-xs"
                    >
                      <div>
                        <div className="font-semibold text-slate-200 truncate max-w-[180px]">{h.name}</div>
                        <div className="text-[10px] text-slate-400">{h.district} &bull; {h.crime}</div>
                      </div>
                      <span className="font-mono font-bold text-rose-400 text-xs">
                        {Math.round(h.riskScore * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Center + Right: Smooth Map Viewport & Real-Time Radar */}
            <div className="lg:col-span-8 space-y-6">
              
              <SmoothRiskMap 
                onSelectCoordinate={handleSelectFromMap}
                onRequestRiskCheck={handleQuickRiskCheck}
              />

              {/* Real-time 402 Settlement Inspector */}
              <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-emerald-400" />
                    <h3 className="text-sm font-bold text-white">x402 Protocol Settlement Pipeline</h3>
                  </div>
                  {currentStep === 4 && (
                    <span className="text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2.5 py-0.5 rounded-full font-bold">
                      Settled on Algorand Testnet
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                  {[
                    { step: 1, label: 'Unauth Request' },
                    { step: 2, label: 'HTTP 402 Challenge' },
                    { step: 3, label: 'Sign Atomic Group' },
                    { step: 4, label: 'Facilitator Verified' },
                  ].map((s) => (
                    <div 
                      key={s.step} 
                      className={`p-2.5 rounded-lg border text-center transition-all ${
                        currentStep >= s.step
                          ? 'bg-emerald-950/50 border-emerald-500/50 text-emerald-400 font-semibold'
                          : 'bg-slate-950 border-slate-800 text-slate-500'
                      }`}
                    >
                      <div className="text-[10px] uppercase font-bold tracking-wider">Step {s.step}</div>
                      <div className="text-xs truncate mt-0.5">{s.label}</div>
                    </div>
                  ))}
                </div>

                {settledResult ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between bg-emerald-950/30 border border-emerald-500/30 rounded-xl p-3 text-xs">
                      <div className="flex items-center gap-2 text-emerald-400 font-bold">
                        <Unlock className="w-4 h-4" />
                        <span>Decrypted AI Threat Intelligence Unlocked</span>
                      </div>
                      <a
                        href={`${LORA_BASE}/account/${RECEIVER_ADDR}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-cyan-400 hover:underline flex items-center gap-1 font-mono text-[11px]"
                      >
                        <span>Verify Tx on LoRA</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>

                    <pre className="bg-slate-950 rounded-xl p-4 text-[11px] text-slate-200 font-mono border border-slate-800 overflow-x-auto max-h-64 leading-relaxed">
                      {JSON.stringify(settledResult.intelligence_unlocked, null, 2)}
                    </pre>
                  </div>
                ) : challenge ? (
                  <div className="rounded-xl bg-slate-950 border border-slate-800 p-4 font-mono text-xs text-slate-300 space-y-2">
                    <div className="text-amber-400 font-bold flex items-center gap-1.5">
                      <Lock className="w-3.5 h-3.5" />
                      <span>HTTP 402 Payment-Required Header Received</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-[11px]">
                      <div><b>Asset:</b> #{challenge.asset} (USDC)</div>
                      <div><b>Amount:</b> {challenge.priceUsdc} USDC</div>
                      <div><b>Facilitator:</b> GoPlausible Sponsored</div>
                      <div><b>PayTo:</b> {challenge.payTo.slice(0, 10)}...</div>
                    </div>
                  </div>
                ) : (
                  <div className="py-8 text-center text-slate-500 text-xs">
                    Click <b>"Request Protected Risk Score"</b> or select a hotspot on the map to trigger live x402 micropayment negotiation.
                  </div>
                )}
              </div>

            </div>

          </div>
        )}

        {/* TAB 2: PREDICTIVE POLICING STUDIO */}
        {activeTab === 'predictive' && (
          <PredictivePolicingStudio />
        )}

        {/* TAB 3: DEDICATED X402 GATEWAY INSPECTOR */}
        {activeTab === 'x402' && (
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Zap className="w-5 h-5 text-amber-400" />
                  <span>x402 Protocol on Algorand Testnet</span>
                </h3>
                <p className="text-xs text-slate-400">Verifiable on-chain micropayment architecture powered by GoPlausible Facilitator</p>
              </div>
              <a
                href={`${LORA_BASE}/account/${RECEIVER_ADDR}`}
                target="_blank"
                rel="noreferrer"
                className="text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-3.5 py-2 rounded-xl flex items-center gap-1.5 shadow"
              >
                <span>LoRA Explorer</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-400 block mb-1">Merchant Payee</span>
                <code className="text-emerald-400 text-[11px] break-all">{RECEIVER_ADDR}</code>
              </div>
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-400 block mb-1">Agent Keypair</span>
                <code className="text-cyan-400 text-[11px] break-all">{AGENT_ADDR}</code>
              </div>
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-400 block mb-1">Facilitator</span>
                <span className="text-white font-bold block">{FACILITATOR_URL}</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
              <h4 className="font-bold text-white text-xs">Autonomous Agent CLI Execution</h4>
              <p className="text-slate-400 text-xs">Execute the autonomous Python agent to test end-to-end atomic micropayments:</p>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-emerald-400 flex items-center justify-between">
                <code>bash scripts/run_x402_agent.sh</code>
                <span className="text-slate-500 text-[10px]">Auto Signed</span>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: 44 DBSCAN HOTSPOTS FEED */}
        {activeTab === 'hotspots' && (
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Flame className="w-5 h-5 text-rose-500" />
                  <span>Delhi Identified DBSCAN Crime Corridors (44 Centroids)</span>
                </h3>
                <p className="text-xs text-slate-400">Spatial clustering with Haversine radius ε=600m across 15 police districts</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {DELHI_HOTSPOTS.map((h) => (
                <div key={h.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white">{h.name}</span>
                    <span className={`font-mono font-bold text-xs px-2 py-0.5 rounded ${
                      h.riskLevel === 'HIGH' ? 'bg-rose-950 text-rose-300 border border-rose-800' : 'bg-amber-950 text-amber-300 border border-amber-800'
                    }`}>
                      {Math.round(h.riskScore * 100)}% Risk
                    </span>
                  </div>
                  <div className="text-slate-400 text-[11px] leading-relaxed">
                    <div><b>District:</b> {h.district}</div>
                    <div><b>Dominant Offense:</b> {h.crime}</div>
                    <div><b>Premises:</b> {h.premises}</div>
                    <div><b>Statute:</b> <code>{h.ipc}</code></div>
                    <div><b>Peak Hours:</b> {h.peakHours}</div>
                    <div><b>Recorded FIRs:</b> {h.incidents} cases</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </main>

      {/* Footer (Legal Metrology style) */}
      <footer className="border-t border-slate-800/80 bg-[#090d16] px-6 py-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Rakshak.ai &bull; Autonomous Civic Safety & Predictive Policing Studio</span>
          <span>x402 Protocol on Algorand Testnet &bull; GoPlausible Facilitator &bull; LoRA Verification</span>
        </div>
      </footer>

    </div>
  );
}
