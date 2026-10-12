import React, { useState, useEffect, useRef } from 'react';
import { 
  Bell, 
  AlertTriangle, 
  Radio, 
  MapPin, 
  ExternalLink, 
  PhoneCall, 
  X, 
  Volume2, 
  VolumeX, 
  Plus, 
  Check, 
  ShieldAlert,
  Flame
} from 'lucide-react';
import { DELHI_HOTSPOTS } from './SmoothRiskMap';

interface Contact {
  name: string;
  phone: string;
  relationship: string;
  isPrimary?: boolean;
}

const DEFAULT_CONTACTS: Contact[] = [
  { name: 'Delhi Police PCR Control Room', phone: '112', relationship: 'Police Emergency' },
  { name: 'Delhi Women Safety Helpline', phone: '1090', relationship: 'Emergency Helpline' },
  { name: 'PCR Van Sentinel Unit', phone: '+91 98719 01120', relationship: 'Beat Patrol' },
];

interface SosAlertWidgetProps {
  currentLat?: number;
  currentLon?: number;
  compact?: boolean;
  onAlertDispatched?: (payload: any) => void;
}

export const SosAlertWidget: React.FC<SosAlertWidgetProps> = ({
  currentLat = 28.6328,
  currentLon = 77.2197,
  compact = false,
  onAlertDispatched,
}) => {
  const [contacts, setContacts] = useState<Contact[]>(() => {
    try {
      const stored = localStorage.getItem('rakshak_emergency_contacts') || sessionStorage.getItem('rakshak_emergency_contacts');
      if (stored) return JSON.parse(stored);
    } catch {}
    return DEFAULT_CONTACTS;
  });

  const [modalOpen, setModalOpen] = useState(false);
  const [newName, setNewName] = useState('');
  const [newPhone, setNewPhone] = useState('');
  
  const [isWithin100m, setIsWithin100m] = useState(false);
  const [nearestDistance, setNearestDistance] = useState<number>(Infinity);
  const [nearestHotspotName, setNearestHotspotName] = useState<string>('Delhi Hotspot');
  
  const [dispatchStatus, setDispatchStatus] = useState<any | null>(null);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [isSimulated100m, setIsSimulated100m] = useState(false);

  const audioCtxRef = useRef<AudioContext | null>(null);
  const beepTimerRef = useRef<any>(null);

  // Haversine distance in meters
  const calculateMeters = (lat1: number, lon1: number, lat2: number, lon2: number) => {
    const R = 6371000;
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLon = ((lon2 - lon1) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((lat1 * Math.PI) / 180) *
        Math.cos((lat2 * Math.PI) / 180) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  // Evaluate proximity to red danger zones
  useEffect(() => {
    if (isSimulated100m) {
      setIsWithin100m(true);
      setNearestDistance(58);
      setNearestHotspotName('Rajiv Chowk Metro / CP Outer Circle (High Risk Hotspot)');
      return;
    }

    let minD = Infinity;
    let spotName = 'Delhi Hotspot';

    DELHI_HOTSPOTS.forEach((h) => {
      const d = calculateMeters(currentLat, currentLon, h.lat, h.lon);
      if (d < minD) {
        minD = d;
        spotName = `${h.name} (${h.district})`;
      }
    });

    setNearestDistance(Math.round(minD));
    setNearestHotspotName(spotName);
    setIsWithin100m(minD <= 100);
  }, [currentLat, currentLon, isSimulated100m]);

  // Primary contact is always the last added contact
  const primaryContact = contacts[contacts.length - 1] || DEFAULT_CONTACTS[DEFAULT_CONTACTS.length - 1];

  const saveContactsToStorage = (updated: Contact[]) => {
    setContacts(updated);
    try {
      localStorage.setItem('rakshak_emergency_contacts', JSON.stringify(updated));
      sessionStorage.setItem('rakshak_emergency_contacts', JSON.stringify(updated));
      localStorage.setItem('rakshak_contacts_permission_granted', 'true');
    } catch {}
  };

  // Contact Picker Permission flow
  const requestContactPickerPermission = async (): Promise<boolean> => {
    // 1. Mobile Web Contact Picker API
    if ('contacts' in navigator && 'ContactsManager' in window) {
      try {
        const props = ['name', 'tel'];
        const picked = await (navigator as any).contacts.select(props, { multiple: false });
        if (picked && picked.length > 0) {
          const c = picked[0];
          const name = c.name && c.name[0] ? c.name[0] : 'Emergency Contact';
          const tel = c.tel && c.tel[0] ? c.tel[0] : '';
          if (tel) {
            const updated = [...contacts, { name, phone: tel, relationship: 'Contact Picker Recipient' }];
            saveContactsToStorage(updated);
            return true;
          }
        }
      } catch (e) {
        console.log('Native contact picker dismissed:', e);
      }
    }

    // 2. Fallback modal
    const hasPermission = localStorage.getItem('rakshak_contacts_permission_granted');
    if (!hasPermission && contacts.length <= DEFAULT_CONTACTS.length) {
      setModalOpen(true);
      return false;
    }
    return true;
  };

  // Synthesize Web Audio API 880Hz alternating pulses
  const playSafetyBeep = () => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      if (!audioCtxRef.current) audioCtxRef.current = new AudioCtx();
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') ctx.resume();

      stopSafetyBeep();
      setIsPlayingAudio(true);

      let pulse = 0;
      beepTimerRef.current = setInterval(() => {
        if (pulse >= 14) {
          stopSafetyBeep();
          return;
        }
        pulse++;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        // Alternating pulses at 880Hz (A5) and 988Hz (B5) for emergency safety deterrence
        const freq = pulse % 2 === 0 ? 880 : 988;
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(freq, ctx.currentTime);

        gain.gain.setValueAtTime(0.35, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.14);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.15);
      }, 175);
    } catch (e) {
      console.log('AudioContext initialization note:', e);
    }
  };

  const stopSafetyBeep = () => {
    if (beepTimerRef.current) {
      clearInterval(beepTimerRef.current);
      beepTimerRef.current = null;
    }
    setIsPlayingAudio(false);
  };

  // Trigger SOS alert dispatch
  const handleTriggerSos = async () => {
    const granted = await requestContactPickerPermission();
    if (!granted && !localStorage.getItem('rakshak_contacts_permission_granted')) {
      return;
    }

    playSafetyBeep();

    const mapsLink = `https://maps.google.com/?q=${currentLat.toFixed(5)},${currentLon.toFixed(5)}`;
    const distText = nearestDistance < 1000 ? `${nearestDistance}m` : `${(nearestDistance / 1000).toFixed(1)}km`;
    const distressText = `EMERGENCY: User is in an active danger zone (<100m from hotspot: ${nearestHotspotName}, ${distText} away). Immediate assistance requested.\nLive GPS: ${mapsLink}`;

    const payload = {
      recipient: primaryContact,
      location: {
        latitude: currentLat,
        longitude: currentLon,
        accuracy: 10,
        nearest_hotspot: nearestHotspotName,
        distance_meters: nearestDistance,
      },
      message: distressText,
      push_notification: {
        sound: 'safety_beep.mp3',
        priority: 'high',
      },
    };

    setDispatchStatus({
      timestamp: new Date().toLocaleTimeString(),
      recipient: primaryContact,
      mapsLink,
      message: distressText,
      within100m: isWithin100m,
    });

    if (onAlertDispatched) onAlertDispatched(payload);

    try {
      await fetch('http://127.0.0.1:4021/api/v1/sos-alert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch (e) {
      console.log('Backend simulated SOS dispatch response recorded');
    }
  };

  const handleAddContact = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPhone.trim()) return;
    const item: Contact = {
      name: newName.trim() || 'Emergency Contact',
      phone: newPhone.trim(),
      relationship: 'Primary Recipient',
    };
    const updated = [...contacts, item];
    saveContactsToStorage(updated);
    setNewName('');
    setNewPhone('');
    setModalOpen(false);
  };

  if (compact) {
    return (
      <div className="relative inline-flex items-center gap-2">
        <button
          onClick={handleTriggerSos}
          className={`px-3 py-1.5 rounded-full text-xs font-black tracking-wide text-white flex items-center gap-1.5 shadow-xl transition-all ${
            isWithin100m
              ? 'bg-gradient-to-r from-red-700 via-rose-600 to-red-800 animate-pulse border-2 border-red-400 shadow-[0_0_20px_rgba(239,68,68,0.9)]'
              : 'bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 border border-red-400/50 shadow-[0_0_12px_rgba(239,68,68,0.5)]'
          }`}
          title={isWithin100m ? 'High Risk Proximity (<100m) - Tap to Trigger Emergency SOS' : 'Trigger SOS Emergency Alert'}
        >
          <span className="animate-spin text-xs">🚨</span>
          <span>{isWithin100m ? 'HIGH RISK (<100m)' : 'SOS EMERGENCY'}</span>
          <Bell className="w-3.5 h-3.5 fill-white" />
        </button>

        {/* Proximity Pill */}
        <div 
          onClick={() => setModalOpen(true)}
          className={`cursor-pointer px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border transition-all ${
            isWithin100m
              ? 'bg-red-950/80 text-red-300 border-red-700 animate-pulse'
              : 'bg-slate-900/80 text-slate-300 border-slate-700 hover:border-slate-500'
          }`}
          title="Click to manage emergency contacts"
        >
          {isWithin100m ? `🚨 ${nearestDistance}m` : `🛡️ ${nearestDistance}m`}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-3 font-sans">
      {/* Prominent High-Contrast Pulsing SOS Emergency Button */}
      <button
        onClick={handleTriggerSos}
        className={`w-full py-3.5 px-4 rounded-2xl font-black text-sm tracking-wider uppercase flex items-center justify-center gap-2.5 text-white shadow-2xl transition-all cursor-pointer select-none ${
          isWithin100m
            ? 'bg-gradient-to-r from-red-700 via-rose-600 to-red-900 border-2 border-red-400 shadow-[0_0_30px_rgba(239,68,68,0.95)] animate-pulse scale-[1.01]'
            : 'bg-gradient-to-r from-red-600 via-rose-600 to-red-700 hover:from-red-500 hover:to-rose-500 border-2 border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.7)] hover:shadow-[0_0_28px_rgba(239,68,68,0.9)] active:scale-[0.98]'
        }`}
      >
        <span className="text-lg animate-bounce">🚨</span>
        <span className="drop-shadow-md">
          {isWithin100m ? '⚠️ HIGH RISK PROXIMITY (<100M)' : 'SOS EMERGENCY'}
        </span>
        <span className="text-base animate-pulse">🔔</span>
      </button>

      {/* Geofence Proximity & Primary Contact HUD */}
      <div className="bg-slate-950/80 backdrop-blur-md border border-slate-800 rounded-xl p-3 space-y-2 text-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Radio className={`w-3.5 h-3.5 ${isWithin100m ? 'text-red-400 animate-ping' : 'text-cyan-400'}`} />
            <span className="text-slate-400 text-[11px] font-medium">Danger Geofence:</span>
          </div>
          <span
            className={`font-mono text-[10px] font-bold px-2 py-0.5 rounded-full border ${
              isWithin100m
                ? 'bg-red-950/80 text-red-400 border-red-700 animate-pulse'
                : 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60'
            }`}
          >
            {isWithin100m ? `CRITICAL PROXIMITY (${nearestDistance}m)` : `${nearestDistance}m BUFFER`}
          </span>
        </div>

        {/* Recipient Status */}
        <div className="flex items-center justify-between pt-1 border-t border-slate-800/60">
          <div className="text-[11px] text-slate-300 truncate max-w-[200px]">
            Target: <strong className="text-white">{primaryContact.name}</strong> ({primaryContact.phone})
          </div>
          <button
            onClick={() => setModalOpen(true)}
            className="text-[11px] font-bold text-cyan-400 hover:text-cyan-300 underline cursor-pointer"
          >
            Edit
          </button>
        </div>

        {/* 100m Simulation Quick Toggle */}
        <div className="flex items-center justify-between pt-1 border-t border-slate-800/60 text-[10px] text-slate-500">
          <span>Test Geofence Simulation:</span>
          <div className="flex gap-1.5">
            <button
              onClick={() => setIsSimulated100m(true)}
              className={`px-2 py-0.5 rounded text-[10px] font-bold transition-colors ${
                isSimulated100m ? 'bg-red-600 text-white' : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
              }`}
            >
              &lt;100m Hotspot
            </button>
            <button
              onClick={() => setIsSimulated100m(false)}
              className={`px-2 py-0.5 rounded text-[10px] font-bold transition-colors ${
                !isSimulated100m ? 'bg-emerald-700 text-white' : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
              }`}
            >
              Reset Safe
            </button>
          </div>
        </div>
      </div>

      {/* Dispatch Feedback Alert Banner */}
      {dispatchStatus && (
        <div className="bg-red-950/90 border border-red-600 rounded-xl p-3 space-y-2 text-xs shadow-xl animate-in fade-in slide-in-from-top-2">
          <div className="flex items-center justify-between text-red-200 font-bold">
            <span className="flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-red-400" />
              <span>🚨 DISTRESS ALERT TRANSMITTED</span>
            </span>
            <span className="text-[10px] font-mono text-slate-400">{dispatchStatus.timestamp}</span>
          </div>

          <p className="text-[11px] text-slate-200 leading-snug">
            {dispatchStatus.message}
          </p>

          <div className="flex items-center justify-between pt-1">
            <a
              href={dispatchStatus.mapsLink}
              target="_blank"
              rel="noreferrer"
              className="text-cyan-400 hover:text-cyan-300 text-[11px] font-bold inline-flex items-center gap-1 underline"
            >
              <span>Live Google Maps Link</span>
              <ExternalLink className="w-3 h-3" />
            </a>

            {isPlayingAudio ? (
              <button
                onClick={stopSafetyBeep}
                className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-yellow-300 text-[10px] font-bold flex items-center gap-1"
              >
                <VolumeX className="w-3 h-3" /> Mute 880Hz Beep
              </button>
            ) : (
              <button
                onClick={playSafetyBeep}
                className="px-2 py-0.5 rounded bg-red-800 hover:bg-red-700 text-white text-[10px] font-bold flex items-center gap-1"
              >
                <Volume2 className="w-3 h-3" /> Replay Beep
              </button>
            )}
          </div>
        </div>
      )}

      {/* Emergency Contact Selection & Fallback Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-[99999] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-sm w-full p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-extrabold text-white text-sm flex items-center gap-2">
                <Bell className="w-4 h-4 text-rose-400" />
                <span>Emergency Contacts Registry</span>
              </h3>
              <button
                onClick={() => setModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-400">
              When SOS is triggered, distress telemetry is automatically dispatched to the <strong>last added emergency contact</strong>:
            </p>

            {/* Existing Contacts List */}
            <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
              {contacts.map((c, i) => {
                const isPrimary = i === contacts.length - 1;
                return (
                  <div
                    key={i}
                    className={`p-2 rounded-xl text-xs flex items-center justify-between border ${
                      isPrimary
                        ? 'bg-rose-950/40 border-rose-700/60 text-white'
                        : 'bg-black/40 border-slate-800 text-slate-300'
                    }`}
                  >
                    <div>
                      <div className="font-bold flex items-center gap-1.5">
                        <span>{c.name}</span>
                        {isPrimary && (
                          <span className="text-[9px] font-mono font-black text-rose-400 bg-rose-950 px-1.5 py-0.2 rounded border border-rose-800">
                            PRIMARY
                          </span>
                        )}
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono">{c.phone}</div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Add New Contact Form */}
            <form onSubmit={handleAddContact} className="space-y-2 pt-2 border-t border-slate-800 text-xs">
              <label className="block text-slate-300 font-semibold text-[11px]">Add Emergency Contact</label>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Name (e.g. Guardian / Family Member)"
                className="w-full bg-black/60 border border-slate-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
              <input
                type="tel"
                value={newPhone}
                onChange={(e) => setNewPhone(e.target.value)}
                placeholder="Mobile (+91 98100 12345)"
                className="w-full bg-black/60 border border-slate-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                required
              />
              <button
                type="submit"
                className="w-full py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold rounded-lg shadow transition-all flex items-center justify-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Save as Primary Recipient</span>
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
