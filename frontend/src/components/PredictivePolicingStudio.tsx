import React, { useState } from 'react';
import { 
  Navigation, 
  Clock, 
  RotateCw, 
  Crosshair, 
  MapPin, 
  CheckCircle2, 
  AlertOctagon, 
  Cpu, 
  Coins, 
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Shield,
  Zap,
  Radio,
  Flame,
  FileText,
  Lock,
  Unlock,
  AlertTriangle
} from 'lucide-react';
import { DELHI_HOTSPOTS, DELHI_SAFE_ZONES } from './SmoothRiskMap';

export const PredictivePolicingStudio: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'patrol' | 'knox' | 'safe_corridor' | 'choke' | 'b2b'>('patrol');

  // 1. Patrol Beat State
  const [selectedPatrolUnits, setSelectedPatrolUnits] = useState<number>(4);
  const [selectedShift, setSelectedShift] = useState<'Night' | 'Evening' | 'Day'>('Night');
  const [activeDwellStop, setActiveDwellStop] = useState<number>(1);

  // 2. Knox Near-Repeat State
  const [knoxIncident, setKnoxIncident] = useState(DELHI_HOTSPOTS[0]);
  const [hoursAgo, setHoursAgo] = useState<number>(6);

  // 3. Safe Corridor State
  const [origin, setOrigin] = useState('Connaught Place Outer Circle');
  const [destination, setDestination] = useState('Civil Lines Residential Enclave');

  // 4. Tactical Choke Point State
  const [elapsedMinutes, setElapsedMinutes] = useState<number>(7);
  const [getawayVehicle, setGetawayVehicle] = useState<'Motorcycle' | 'Sedan' | 'Pedestrian'>('Motorcycle');

  // 5. B2B Fleet State
  const [deliveryPartner, setDeliveryPartner] = useState<'Zepto' | 'Blinkit' | 'Uber' | 'Autonomous Drone'>('Zepto');
  const [b2bSettled, setB2bSettled] = useState<boolean>(false);
  const [b2bLoading, setB2bLoading] = useState<boolean>(false);

  // Sample Patrol Itinerary with Koper Dwell Times
  const patrolRoute = [
    { order: 1, name: 'Rajiv Chowk Metro Inner Circle', dwell: 14, task: 'Static deterrence picket + vehicle frisking', risk: 0.84, dist: '0.8 km' },
    { order: 2, name: 'Paharganj Station Approach Corridor', dwell: 12, task: 'Anti-snatching motorcycle Cheetah patrol', risk: 0.76, dist: '1.4 km' },
    { order: 3, name: 'Chandni Chowk Main Bazaar', dwell: 15, task: 'Commercial market foot patrol + CCTV check', risk: 0.79, dist: '2.1 km' },
    { order: 4, name: 'Kashmere Gate Interstate Terminal', dwell: 15, task: 'Interstate luggage surveillance + dark spot lighting', risk: 0.88, dist: '1.9 km' },
  ];

  const handleSimulateB2bApi = () => {
    setB2bLoading(true);
    setB2bSettled(false);
    setTimeout(() => {
      setB2bLoading(false);
      setB2bSettled(true);
    }, 900);
  };

  return (
    <div className="space-y-6">
      
      {/* Top Banner Navigation Ribbon */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-black text-white tracking-tight">Predictive Policing Intelligence Suite</h3>
              <p className="text-[11px] text-slate-400">Criminological spatial modeling, patrol optimization & tactical interception</p>
            </div>
          </div>

          {/* Sub-Tabs Pills */}
          <div className="flex flex-wrap items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => setActiveSubTab('patrol')}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 ${
                activeSubTab === 'patrol' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              <span>🚔 Patrol Dispatcher</span>
            </button>
            <button
              onClick={() => setActiveSubTab('knox')}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 ${
                activeSubTab === 'knox' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              <span>🔁 Near-Repeat (Knox)</span>
            </button>
            <button
              onClick={() => setActiveSubTab('safe_corridor')}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 ${
                activeSubTab === 'safe_corridor' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              <span>🛡️ Safe Corridor Navigator</span>
            </button>
            <button
              onClick={() => setActiveSubTab('choke')}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 ${
                activeSubTab === 'choke' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              <span>🛑 Choke-Point Pickets</span>
            </button>
            <button
              onClick={() => setActiveSubTab('b2b')}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 ${
                activeSubTab === 'b2b' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              <span>⚡ B2B Fleet x402</span>
            </button>
          </div>
        </div>
      </div>

      {/* MODULE 1: PATROL BEAT OPTIMIZER & KOPER CURVE DWELL TIME */}
      {activeSubTab === 'patrol' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Controls */}
          <div className="lg:col-span-4 space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4 text-xs">
              <h4 className="font-bold text-white text-sm flex items-center gap-2">
                <span>🚔 Patrol Configuration</span>
              </h4>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Patrol Shift Window</label>
                <select 
                  value={selectedShift}
                  onChange={(e: any) => setSelectedShift(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="Night">Night Shift (22:00 - 06:00)</option>
                  <option value="Evening">Evening Rush (17:00 - 22:00)</option>
                  <option value="Day">Day Patrol (08:00 - 17:00)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Active PCR Units Deployed</label>
                <input 
                  type="number" 
                  min={1} 
                  max={12} 
                  value={selectedPatrolUnits}
                  onChange={(e) => setSelectedPatrolUnits(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 font-mono focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="p-3 bg-amber-950/30 border border-amber-500/30 rounded-xl space-y-1">
                <span className="text-amber-400 font-bold flex items-center gap-1.5 text-xs">
                  <AlertTriangle className="w-3.5 h-3.5" /> Shift Handover Advisory
                </span>
                <p className="text-slate-300 text-[11px] leading-relaxed">
                  Criminals exploit the 20:00–20:45 changeover window. Stagger PCR rotation to ensure Centroid #1 remains under active watch during changeover.
                </p>
              </div>

              <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                <span className="text-cyan-400 font-bold block text-[11px]">Koper Principle Scientific Basis:</span>
                <p className="text-slate-400 text-[11px] leading-relaxed">
                  Research demonstrates that <strong>12 to 15 minutes</strong> of stationary presence maximizes residual deterrence for up to 2 hours without wasting police manpower.
                </p>
              </div>
            </div>
          </div>

          {/* Right Itinerary View */}
          <div className="lg:col-span-8 space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <h4 className="font-bold text-white text-sm">Optimized Multi-Stop Patrol Loop (Unit #04)</h4>
                  <p className="text-[11px] text-slate-400">Calculated via Traveling Salesperson Problem (TSP) with Great-Circle Haversine Routing</p>
                </div>
                <div className="text-right">
                  <span className="text-xs font-mono font-bold text-emerald-400">Total Route: 6.2 km</span>
                  <span className="text-[10px] text-slate-400 block">Est. Duration: 1h 22m</span>
                </div>
              </div>

              <div className="space-y-3">
                {patrolRoute.map((stop) => (
                  <div 
                    key={stop.order}
                    onClick={() => setActiveDwellStop(stop.order)}
                    className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                      activeDwellStop === stop.order 
                        ? 'bg-emerald-950/40 border-emerald-500/50 shadow-md' 
                        : 'bg-slate-950 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-7 h-7 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-mono font-bold flex items-center justify-center text-xs shrink-0 mt-0.5">
                        {stop.order}
                      </div>
                      <div>
                        <div className="font-bold text-slate-200 text-xs sm:text-sm">{stop.name}</div>
                        <div className="text-[11px] text-slate-400 mt-0.5">{stop.task}</div>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                            Leg Distance: {stop.dist}
                          </span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950/80 text-rose-400 border border-rose-800/60">
                            Risk: {Math.round(stop.risk * 100)}%
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0 sm:border-l sm:border-slate-800 sm:pl-4">
                      <div className="text-right">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block">Koper Dwell Time</span>
                        <span className="text-sm font-mono font-black text-amber-400">{stop.dwell} Minutes</span>
                      </div>
                      <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                        <Clock className="w-4 h-4" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      )}

      {/* MODULE 2: KNOX NEAR-REPEAT CRIME FORECASTER */}
      {activeSubTab === 'knox' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4 text-xs">
              <h4 className="font-bold text-white text-sm">Knox Spatio-Temporal Contagion Engine</h4>
              <p className="text-slate-400 text-[11px]">
                When an offense occurs, adjacent premises within 400m face a temporary surge in vulnerability as offenders exploit familiarity.
              </p>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Anchor Incident Centroid</label>
                <select
                  value={knoxIncident.id}
                  onChange={(e) => {
                    const found = DELHI_HOTSPOTS.find(h => h.id === e.target.value);
                    if (found) setKnoxIncident(found);
                  }}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  {DELHI_HOTSPOTS.map((h) => (
                    <option key={h.id} value={h.id}>{h.name} ({h.crime})</option>
                  ))}
                </select>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-slate-400 font-medium">Time Elapsed Since FIR</label>
                  <span className="font-mono font-bold text-amber-400">{hoursAgo} Hours Ago</span>
                </div>
                <input
                  type="range"
                  min={1}
                  max={72}
                  value={hoursAgo}
                  onChange={(e) => setHoursAgo(Number(e.target.value))}
                  className="w-full accent-emerald-500"
                />
                <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                  <span>1h (Peak Ripple)</span>
                  <span>36h (Mid Window)</span>
                  <span>72h (Decay Limit)</span>
                </div>
              </div>

              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Contagion Status:</span>
                  <span className="font-bold font-mono text-rose-400">
                    {hoursAgo <= 24 ? '🚨 CRITICAL RIPPLE (2.8x Risk)' : '⚠️ MODERATE RIPPLE (1.6x Risk)'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Contagion Radius:</span>
                  <span className="font-bold font-mono text-white">450 Meters</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Offender Return Probability:</span>
                  <span className="font-bold font-mono text-amber-400">
                    {Math.max(15, Math.round(78 - (hoursAgo / 72) * 60))}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-7 space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4 text-xs">
              <h4 className="font-bold text-white text-sm flex items-center justify-between">
                <span>Adjacent Premises at Immediate Risk</span>
                <span className="text-[10px] bg-rose-950 text-rose-300 border border-rose-800 px-2 py-0.5 rounded font-mono">
                  48-Hour High Alert
                </span>
              </h4>

              <div className="space-y-3">
                {[
                  { name: 'Metro Exit Gate #3 Parking Lot', dist: '110m', mult: '3.1x', crime: 'Vehicle Theft', action: 'Install mobile CCTV van' },
                  { name: 'Inner Circle ATM Booth Cluster', dist: '240m', mult: '2.8x', crime: 'Mugging / Snatching', action: 'Direct bank guard to inspect lighting' },
                  { name: 'Palika Underground Walkway', dist: '380m', mult: '2.1x', crime: 'Pickpocketing', action: 'Deploy plainclothes beat constable' },
                ].map((item, idx) => (
                  <div key={idx} className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between gap-3">
                    <div>
                      <div className="font-bold text-slate-200">{item.name}</div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        Distance: <span className="font-mono text-cyan-400">{item.dist}</span> &bull; Likely: <span className="text-slate-300">{item.crime}</span>
                      </div>
                      <div className="text-[10px] text-emerald-400 mt-1">
                        Directive: {item.action}
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="text-[10px] text-slate-400 block uppercase">Surge</span>
                      <span className="font-mono font-black text-sm text-rose-400">{item.mult}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      )}

      {/* MODULE 3: SAFEST CORRIDOR ROUTE PLANNER */}
      {activeSubTab === 'safe_corridor' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4 text-xs">
              <h4 className="font-bold text-white text-sm">Safest Corridor vs. Shortest Path</h4>
              <p className="text-slate-400 text-[11px]">
                Statistically contrasts direct routing through dark crime alleys against protected corridors guarded by 24/7 pickets.
              </p>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Origin Landmark</label>
                <input
                  type="text"
                  value={origin}
                  onChange={(e) => setOrigin(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Destination Landmark</label>
                <input
                  type="text"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="p-3 bg-emerald-950/30 border border-emerald-500/30 rounded-xl space-y-1">
                <span className="text-emerald-400 font-bold flex items-center gap-1.5 text-xs">
                  <CheckCircle2 className="w-3.5 h-3.5" /> 76.9% Crime Vulnerability Reduction
                </span>
                <p className="text-slate-300 text-[11px]">
                  Safest route diverts through Chanakyapuri and India Gate Central Reserve perimeter with 100% street illumination.
                </p>
              </div>
            </div>
          </div>

          <div className="lg:col-span-7 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              
              {/* Direct Path */}
              <div className="bg-slate-900 border border-rose-500/30 rounded-2xl p-5 space-y-3 text-xs">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <span className="font-bold text-rose-400">Shortest Direct Path</span>
                  <span className="text-[10px] bg-rose-950 text-rose-300 border border-rose-800 px-2 py-0.5 rounded font-mono">
                    High Vulnerability
                  </span>
                </div>
                <div>
                  <div className="text-2xl font-black text-white font-mono">4.8 km</div>
                  <div className="text-slate-400 text-[11px]">Est. Travel Time: 12 mins</div>
                </div>
                <div className="p-2.5 rounded-lg bg-rose-950/20 border border-rose-800/40 text-rose-300 text-[11px] leading-relaxed">
                  ⚠️ Traverses 2 unmonitored railway underpasses and Rajiv Chowk snatching perimeter after 21:00 hrs.
                </div>
                <div className="text-[11px] text-slate-400">
                  Threat Exposure: <b className="text-rose-400">78% Risk Index</b>
                </div>
              </div>

              {/* Safest Corridor */}
              <div className="bg-slate-900 border border-emerald-500/40 rounded-2xl p-5 space-y-3 text-xs shadow-lg shadow-emerald-500/5">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <span className="font-bold text-emerald-400">🛡️ Safest Protected Corridor</span>
                  <span className="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded font-mono">
                    Recommended
                  </span>
                </div>
                <div>
                  <div className="text-2xl font-black text-emerald-400 font-mono">5.4 km</div>
                  <div className="text-slate-400 text-[11px]">Est. Travel Time: 14 mins (+2 mins)</div>
                </div>
                <div className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-800/40 text-emerald-300 text-[11px] leading-relaxed">
                  ✅ 100% illuminated arterial road guarded by 2 static police pickets and active PCR patrol.
                </div>
                <div className="text-[11px] text-slate-400">
                  Threat Exposure: <b className="text-emerald-400">18% Risk Index (Safe)</b>
                </div>
              </div>

            </div>
          </div>

        </div>
      )}

      {/* MODULE 4: TACTICAL CHOKE-POINT BARRICADE PLACER */}
      {activeSubTab === 'choke' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4 text-xs">
              <h4 className="font-bold text-white text-sm">Emergency Choke-Point Picket Placer</h4>
              <p className="text-slate-400 text-[11px]">
                Upon receiving an active 112 snatching/theft alert, computes the fleeing offender escape radius and recommends static barricades.
              </p>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Getaway Transport Mode</label>
                <select
                  value={getawayVehicle}
                  onChange={(e: any) => setGetawayVehicle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="Motorcycle">Motorcycle / Scooty (38 km/h urban velocity)</option>
                  <option value="Sedan">Sedan / Car (32 km/h traffic restricted)</option>
                  <option value="Pedestrian">On Foot / Alleyway Dash (9 km/h)</option>
                </select>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-slate-400 font-medium">Minutes Elapsed Since Incident</label>
                  <span className="font-mono font-bold text-rose-400">{elapsedMinutes} Minutes</span>
                </div>
                <input
                  type="range"
                  min={2}
                  max={20}
                  value={elapsedMinutes}
                  onChange={(e) => setElapsedMinutes(Number(e.target.value))}
                  className="w-full accent-rose-500"
                />
              </div>

              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 font-mono">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Current Escape Radius:</span>
                  <span className="text-white font-bold">{((38 * (elapsedMinutes / 60))).toFixed(2)} km</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Target Search Perimeter:</span>
                  <span className="text-cyan-400 font-bold">{Math.round((38 * (elapsedMinutes / 60)) * 1000)} meters</span>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-7 space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4 text-xs">
              <h4 className="font-bold text-white text-sm flex items-center justify-between">
                <span>Recommended Police Barricades & Choke Points</span>
                <span className="text-[10px] bg-rose-600 text-white px-2 py-0.5 rounded font-bold">
                  Flash 112 Net
                </span>
              </h4>

              <div className="space-y-3">
                {[
                  { name: 'Dhaula Kuan Flyover Junction', dist: '1.8 km', eta: '3 mins', priority: 'PRIMARY CHOKE POINT', capacity: 'Arterial Funnel' },
                  { name: 'ITO Bridge & Ring Road Exit', dist: '2.4 km', eta: '5 mins', priority: 'SECONDARY CHOKE POINT', capacity: 'River Crossing' },
                  { name: 'Kashmere Gate ISBT Underpass', dist: '3.1 km', eta: '6 mins', priority: 'TERTIARY EXIT', capacity: 'North Highway Exit' },
                ].map((cp, idx) => (
                  <div key={idx} className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between gap-3">
                    <div>
                      <div className="font-bold text-slate-200">{cp.name}</div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        Distance from Origin: <span className="font-mono text-cyan-400">{cp.dist}</span> &bull; {cp.capacity}
                      </div>
                      <span className="text-[10px] uppercase font-bold text-emerald-400 block mt-1">
                        Picket Dispatch ETA: {cp.eta}
                      </span>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="text-[10px] font-bold px-2.5 py-1 rounded bg-rose-950/80 text-rose-300 border border-rose-800">
                        {cp.priority}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      )}

      {/* MODULE 5: B2B COMMERCIAL FLEET & DRONE RISK API */}
      {activeSubTab === 'b2b' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4 text-xs">
              <h4 className="font-bold text-white text-sm">B2B Delivery Fleet & Drone Guard Risk API</h4>
              <p className="text-slate-400 text-[11px]">
                Autonomous commercial delivery fleets (Zepto, Blinkit, Uber) query Rakshak.ai per delivery stop via x402 micropayments on Algorand.
              </p>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Select Enterprise Client</label>
                <select
                  value={deliveryPartner}
                  onChange={(e: any) => setDeliveryPartner(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="Zepto">Zepto 10-Min Delivery Fleet</option>
                  <option value="Blinkit">Blinkit Dark Store Network</option>
                  <option value="Uber">Uber Night Ride Safety Guard</option>
                  <option value="Autonomous Drone">Autonomous Security Drone Sentinel</option>
                </select>
              </div>

              <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                <div className="flex justify-between text-slate-400">
                  <span>Micro-Fee per Check:</span>
                  <span className="font-mono font-bold text-emerald-400">0.0020 USDC (#10458941)</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Settlement Network:</span>
                  <span className="font-semibold text-white">Algorand Testnet</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Facilitator:</span>
                  <span className="font-semibold text-cyan-400">GoPlausible Sponsored</span>
                </div>
              </div>

              <button
                onClick={handleSimulateB2bApi}
                disabled={b2bLoading}
                className="w-full bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-bold py-3 px-4 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {b2bLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span>Settling x402 Micropayment on Algorand...</span>
                  </>
                ) : (
                  <>
                    <Coins className="w-4 h-4" />
                    <span>Run B2B Fleet Stop Risk Query</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="lg:col-span-7 space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4 text-xs">
              <h4 className="font-bold text-white text-sm flex items-center justify-between">
                <span>Enterprise API Payload (Protected Response)</span>
                {b2bSettled && (
                  <span className="text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2.5 py-0.5 rounded-full font-bold">
                    x402 Verified
                  </span>
                )}
              </h4>

              {b2bSettled ? (
                <div className="space-y-3">
                  <div className="p-3 bg-emerald-950/30 border border-emerald-500/30 rounded-xl text-emerald-300 text-xs">
                    ✅ Stop Location: <b>Seelampur Commercial Hub (28.6644°N, 77.2711°E)</b>
                  </div>
                  <pre className="bg-slate-950 rounded-xl p-4 text-[11px] text-slate-200 font-mono border border-slate-800 overflow-x-auto leading-relaxed">
{JSON.stringify({
  client: deliveryPartner,
  status: "AUTHORIZED_VIA_X402",
  txId: "ALG_ZEPTO_X402_" + Math.random().toString(36).substring(2, 10).toUpperCase(),
  stop_safety_assessment: {
    threat_index: "ELEVATED (88%)",
    category_risk: "Armed Snatching & Vehicle Tampering",
    curfew_window: "21:30 - 04:00",
    rider_safety_directive: "Mandate pair delivery; Avoid rear unlit alleys; Enable live GPS telemetry"
  }
}, null, 2)}
                  </pre>
                </div>
              ) : (
                <div className="py-12 text-center text-slate-500 text-xs flex flex-col items-center justify-center space-y-2">
                  <Lock className="w-6 h-6 text-slate-600" />
                  <p>Click "Run B2B Fleet Stop Risk Query" to observe live enterprise x402 micro-settlement.</p>
                </div>
              )}
            </div>
          </div>

        </div>
      )}

    </div>
  );
};
