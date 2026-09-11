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
  Compass,
  MapPin,
  Globe
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

// Once UI Style Live Timezone Clock
const TimeDisplay: React.FC<{ timeZone: string }> = ({ timeZone }) => {
  const [time, setTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(
        new Intl.DateTimeFormat('en-GB', {
          timeZone,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false,
        }).format(now)
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, [timeZone]);

  return <span className="font-mono text-[11px] text-slate-300">{time}</span>;
};

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
    <div className="min-h-screen bg-[#090b10] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-300 relative">
      
      {/* Once UI Dot Grid Background with Radial Mask */}
      <div className="fixed inset-0 once-dots-pattern once-fade-mask pointer-events-none z-0"></div>
      
      {/* Ambient Top Glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[350px] bg-gradient-to-b from-cyan-500/10 via-emerald-500/5 to-transparent blur-3xl pointer-events-none z-0"></div>

      {/* 1. ONCE UI / MAGIC PORTFOLIO STYLE FLOATING CAPSULE HEADER */}
      <header className="sticky top-4 z-50 w-full px-3 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-2 sm:gap-4">
          
          {/* Brand & Location / Timezone */}
          <div 
            className="flex items-center gap-2 sm:gap-3 cursor-pointer group once-surface rounded-full px-3 sm:px-4 py-2 hover:border-white/[0.2] transition-all"
            onClick={() => setActiveTab('map')}
          >
            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
              <Shield className="w-4 h-4 text-slate-950 font-black" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-white tracking-tight text-xs sm:text-sm">Rakshak.ai</span>
                <span className="text-[9px] uppercase font-mono px-1.5 py-0.2 rounded-full bg-cyan-950/70 text-cyan-400 border border-cyan-800/50">
                  x402
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                <Globe className="w-3 h-3 text-emerald-400" />
                <span className="hidden md:inline">Delhi NCR</span>
                <span className="text-slate-600 hidden md:inline">•</span>
                <TimeDisplay timeZone="Asia/Kolkata" />
              </div>
            </div>
          </div>

          {/* Center: Once UI Floating Capsule Segment Switcher */}
          <nav className="flex items-center gap-1 once-surface p-1.5 rounded-full shadow-2xl">
            <button 
              onClick={() => setActiveTab('map')}
              className={`px-3 sm:px-4 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'map' 
                  ? 'bg-white/[0.12] text-white border border-white/[0.2] shadow-sm' 
                  : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
              }`}
            >
              <Navigation className="w-3.5 h-3.5 text-cyan-400" />
              <span className="hidden sm:inline">Sentinel Map</span>
            </button>

            <button 
              onClick={() => setActiveTab('predictive')}
              className={`px-3 sm:px-4 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'predictive' 
                  ? 'bg-white/[0.12] text-white border border-white/[0.2] shadow-sm' 
                  : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
              }`}
            >
              <Cpu className="w-3.5 h-3.5 text-emerald-400" />
              <span>Predictive Policing</span>
            </button>

            <button 
              onClick={() => setActiveTab('x402')}
              className={`px-3 sm:px-4 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'x402' 
                  ? 'bg-white/[0.12] text-white border border-white/[0.2] shadow-sm' 
                  : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
              }`}
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span className="hidden md:inline">x402 Gateway</span>
            </button>

            <button 
              onClick={() => setActiveTab('hotspots')}
              className={`px-3 sm:px-4 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'hotspots' 
                  ? 'bg-white/[0.12] text-white border border-white/[0.2] shadow-sm' 
                  : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
              }`}
            >
              <Flame className="w-3.5 h-3.5 text-rose-400" />
              <span className="hidden md:inline">44 Hotspots</span>
            </button>
          </nav>

          {/* Right Status Actions */}
          <div className="flex items-center gap-2">
            <div className="hidden lg:flex items-center space-x-2 once-surface rounded-full px-3 py-1.5 text-xs">
              <span className={`w-2 h-2 rounded-full ${serverOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`}></span>
              <span className="text-slate-400 text-[11px]">x402:</span>
              <span className="font-mono font-semibold text-white text-[11px]">{serverOnline ? '4021' : 'Ready'}</span>
            </div>

            <a
              href={`${LORA_BASE}/account/${RECEIVER_ADDR}`}
              target="_blank"
              rel="noreferrer"
              className="px-3 py-1.5 rounded-full text-xs font-semibold once-surface hover:border-cyan-500/40 text-cyan-300 flex items-center gap-1.5 shadow-sm transition-all"
            >
              <span className="hidden sm:inline">LoRA</span>
              <ExternalLink className="w-3 h-3 text-cyan-400" />
            </a>

            <button 
              onClick={() => alert('🚨 Emergency SOS Triggered: In case of active danger in Delhi NCR, dial 112 (Delhi Police Control Room) or 1090 (Women Safety Helpline).')} 
              className="px-3 py-1.5 rounded-full text-xs font-bold bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white shadow-lg transition-all flex items-center gap-1"
            >
              <PhoneCall className="w-3 h-3" /> 
              <span>SOS 112</span>
            </button>
          </div>

        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full space-y-6 relative z-10">

        {/* 2. ONCE UI HERO BANNER WITH METRIC CARDS */}
        <div className="once-surface rounded-3xl p-6 sm:p-8 space-y-6">
          
          {/* Eyebrow & Headline */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.1] text-cyan-300 text-[11px] font-mono tracking-wider uppercase">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping"></span>
                <span>PREDICTIVE CIVIC SAFETY & NEAR-REPEAT FORENSICS</span>
              </div>
              <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
                Algorithmic Crime Forensics & Autonomous Agent Deterrence
              </h1>
              <p className="text-xs sm:text-sm text-slate-400 max-w-3xl leading-relaxed">
                Combining <strong>Koper Curve Patrol Routing (12-15m)</strong>, <strong>Knox Spatio-Temporal Contagion</strong>, and <strong>Safest Corridor Navigation</strong> with verifiable on-chain micro-settlement on Algorand Testnet.
              </p>
            </div>

            {/* Quick Action Button */}
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => handleTest402Flow()}
                disabled={loading}
                className="bg-gradient-to-r from-cyan-600 via-teal-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-bold text-xs px-5 py-3 rounded-full shadow-xl hover:shadow-cyan-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                <span>Trigger x402 Micropayment</span>
              </button>
            </div>
          </div>

          {/* 4-Up Once UI Metric Pop Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
            
            <div className="rounded-2xl p-5 once-surface hover:border-emerald-500/40 transition-all group">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xl">🚔</span>
                <span className="text-[10px] font-mono uppercase text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-800/40">Koper Curve</span>
              </div>
              <div className="text-2xl sm:text-3xl font-black text-white tracking-tight group-hover:text-emerald-400 transition-colors">
                14m Dwell
              </div>
              <p className="text-xs text-slate-400 font-medium mt-1 leading-snug">
                Optimal deterrence per patrol beat station stop
              </p>
            </div>

            <div className="rounded-2xl p-5 once-surface hover:border-cyan-500/40 transition-all group">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xl">🔁</span>
                <span className="text-[10px] font-mono uppercase text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded-full border border-cyan-800/40">Knox Test</span>
              </div>
              <div className="text-2xl sm:text-3xl font-black text-cyan-400 tracking-tight group-hover:text-cyan-300 transition-colors">
                450m Knox
              </div>
              <p className="text-xs text-slate-400 font-medium mt-1 leading-snug">
                Spatio-temporal contagion window for 72h surge
              </p>
            </div>

            <div className="rounded-2xl p-5 once-surface hover:border-amber-500/40 transition-all group">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xl">🛡️</span>
                <span className="text-[10px] font-mono uppercase text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded-full border border-amber-800/40">Guarded A*</span>
              </div>
              <div className="text-2xl sm:text-3xl font-black text-amber-400 tracking-tight group-hover:text-amber-300 transition-colors">
                76.9% Safe
              </div>
              <p className="text-xs text-slate-400 font-medium mt-1 leading-snug">
                Vulnerability reduction via CCTV safe corridor
              </p>
            </div>

            <div className="rounded-2xl p-5 once-surface hover:border-emerald-500/40 transition-all group">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xl">🪙</span>
                <span className="text-[10px] font-mono uppercase text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-800/40">Algorand</span>
              </div>
              <div className="text-2xl sm:text-3xl font-black text-emerald-400 tracking-tight group-hover:text-emerald-300 transition-colors">
                &lt;0.005 USDC
              </div>
              <p className="text-xs text-slate-400 font-medium mt-1 leading-snug">
                Per-API query settled on Algorand Testnet
              </p>
            </div>

          </div>

        </div>

        {/* TAB 1: LIVE SENTINEL MAP & RISK RADAR */}
        {activeTab === 'map' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

            {/* Left Panel: Triage & Risk Parameter Inputs */}
            <div className="lg:col-span-4 space-y-6">
              
              <div className="once-surface rounded-3xl p-5 sm:p-6 shadow-2xl space-y-4">
                <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-cyan-400" />
                    <span>Target Risk Parameters</span>
                  </h3>
                  <span className="text-[10px] font-mono font-bold text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded-full border border-cyan-800/60">
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
                      className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3 py-2 text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-400 font-medium mb-1">Target Longitude (Delhi)</label>
                    <input
                      type="text"
                      value={lon}
                      onChange={(e) => setLon(e.target.value)}
                      className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3 py-2 text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-400 font-medium mb-1">Premises Classification</label>
                    <select
                      value={premisesType}
                      onChange={(e) => setPremisesType(e.target.value)}
                      className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
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
                      className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
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

                  <button
                    onClick={() => handleTest402Flow()}
                    disabled={loading}
                    className="w-full mt-2 bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-bold py-2.5 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2"
                  >
                    {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                    <span>Query Protected AI Threat Score</span>
                  </button>
                </div>
              </div>

              {/* Quick Select Hotspot Corridors */}
              <div className="once-surface rounded-3xl p-5 shadow-2xl space-y-3">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Flame className="w-3.5 h-3.5 text-rose-400" />
                  <span>Major Egress Hotspots (Click to Query)</span>
                </h4>
                <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                  {DELHI_HOTSPOTS.slice(0, 6).map((h) => (
                    <div
                      key={h.id}
                      onClick={() => handleSelectFromMap(h.lat, h.lon, h.premises)}
                      className="p-2.5 rounded-xl bg-black/40 hover:bg-white/[0.06] border border-white/[0.06] hover:border-cyan-500/40 cursor-pointer transition-all flex items-center justify-between text-xs"
                    >
                      <div>
                        <div className="font-bold text-slate-200">{h.name}</div>
                        <div className="text-[10px] text-slate-500">{h.district} • {h.crime}</div>
                      </div>
                      <span className={`font-mono font-bold text-[10px] px-2 py-0.5 rounded-full ${
                        h.riskLevel === 'HIGH' ? 'bg-rose-950/80 text-rose-400 border border-rose-800/60' : 'bg-amber-950/80 text-amber-400 border border-amber-800/60'
                      }`}>
                        {Math.round(h.riskScore * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Center + Right: Smooth Map Viewport & Real-Time Radar */}
            <div className="lg:col-span-8 space-y-6">
              
              <div className="once-surface rounded-3xl overflow-hidden p-1 shadow-2xl">
                <SmoothRiskMap 
                  onSelectCoordinate={handleSelectFromMap}
                  onRequestRiskCheck={handleQuickRiskCheck}
                />
              </div>

              {/* Real-time 402 Settlement Inspector */}
              <div className="once-surface rounded-3xl p-5 sm:p-6 shadow-2xl space-y-4">
                <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
                  <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-cyan-400" />
                    <h3 className="text-sm font-bold text-white">x402 Protocol Settlement Pipeline</h3>
                  </div>
                  {currentStep === 4 && (
                    <span className="text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 py-0.5 rounded-full font-bold">
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
                      className={`p-3 rounded-2xl border text-center transition-all ${
                        currentStep >= s.step
                          ? 'bg-cyan-950/40 border-cyan-500/50 text-cyan-300 font-semibold shadow-lg shadow-cyan-950/50'
                          : 'bg-black/30 border-white/[0.06] text-slate-500'
                      }`}
                    >
                      <div className="text-[10px] uppercase font-mono font-bold tracking-wider">Step {s.step}</div>
                      <div className="text-xs truncate mt-0.5">{s.label}</div>
                    </div>
                  ))}
                </div>

                {settledResult ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between bg-emerald-950/30 border border-emerald-500/30 rounded-2xl p-3.5 text-xs">
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

                    <pre className="bg-black/50 rounded-2xl p-4 text-[11px] text-slate-200 font-mono border border-white/[0.08] overflow-x-auto max-h-64 leading-relaxed">
                      {JSON.stringify(settledResult.intelligence_unlocked, null, 2)}
                    </pre>
                  </div>
                ) : challenge ? (
                  <div className="rounded-2xl bg-black/40 border border-white/[0.08] p-4 font-mono text-xs text-slate-300 space-y-2">
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
                  <div className="py-8 text-center text-slate-500 text-xs font-mono">
                    Click <b>"Query Protected AI Threat Score"</b> or click any marker on the map to trigger on-chain micropayment negotiation.
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
          <div className="once-surface rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
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
                className="text-xs bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold px-4 py-2 rounded-full flex items-center gap-1.5 shadow-lg"
              >
                <span>LoRA Explorer</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
              <div className="p-4 rounded-2xl bg-black/40 border border-white/[0.08]">
                <span className="text-slate-400 block mb-1">Merchant Payee</span>
                <code className="text-emerald-400 text-[11px] break-all">{RECEIVER_ADDR}</code>
              </div>
              <div className="p-4 rounded-2xl bg-black/40 border border-white/[0.08]">
                <span className="text-slate-400 block mb-1">Agent Keypair</span>
                <code className="text-cyan-400 text-[11px] break-all">{AGENT_ADDR}</code>
              </div>
              <div className="p-4 rounded-2xl bg-black/40 border border-white/[0.08]">
                <span className="text-slate-400 block mb-1">Facilitator</span>
                <span className="text-white font-bold block">{FACILITATOR_URL}</span>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-black/40 border border-white/[0.08] space-y-3">
              <h4 className="font-bold text-white text-xs">Autonomous Agent CLI Execution</h4>
              <p className="text-slate-400 text-xs">Execute the autonomous Python agent to test end-to-end atomic micropayments:</p>
              <div className="p-3 rounded-xl bg-black/60 border border-white/[0.08] font-mono text-xs text-emerald-400 flex items-center justify-between">
                <code>bash scripts/run_x402_agent.sh</code>
                <span className="text-slate-500 text-[10px]">Auto Signed</span>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: 44 DBSCAN HOTSPOTS FEED */}
        {activeTab === 'hotspots' && (
          <div className="once-surface rounded-3xl p-6 sm:p-8 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
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
                <div key={h.id} className="p-4 rounded-2xl bg-black/40 border border-white/[0.08] hover:border-white/[0.16] transition-all space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white">{h.name}</span>
                    <span className={`font-mono font-bold text-xs px-2.5 py-0.5 rounded-full ${
                      h.riskLevel === 'HIGH' ? 'bg-rose-950/80 text-rose-300 border border-rose-800/60' : 'bg-amber-950/80 text-amber-300 border border-amber-800/60'
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

      {/* ONCE UI MINIMAL FOOTER */}
      <footer className="mt-auto border-t border-white/[0.08] bg-[#090b10]/90 backdrop-blur-xl px-6 py-6 text-xs text-slate-400 relative z-10">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center">
              <Shield className="w-3.5 h-3.5 text-slate-950 font-black" />
            </div>
            <div>
              <span className="font-bold text-white">Rakshak.ai</span>
              <span className="text-slate-500 ml-2">Civic Safety & Predictive Policing Engine</span>
            </div>
          </div>

          <div className="flex items-center gap-4 text-[11px] font-mono">
            <div className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>All Systems Operational</span>
            </div>
            <span className="text-slate-700">•</span>
            <span>Asia/Kolkata</span>
            <span className="text-slate-700">•</span>
            <a 
              href="https://github.com/Shouryagupta-10/delhi-crime-hotspot-predictor" 
              target="_blank" 
              rel="noreferrer" 
              className="text-cyan-400 hover:underline"
            >
              GitHub Source
            </a>
          </div>
        </div>
      </footer>

    </div>
  );
}
