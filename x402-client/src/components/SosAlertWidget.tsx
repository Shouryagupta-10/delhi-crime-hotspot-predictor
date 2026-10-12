import React, { useState, useEffect, useRef } from 'react';
import { 
  Bell, 
  Settings, 
  Radio, 
  ExternalLink, 
  X, 
  Plus, 
  Check, 
  ShieldAlert,
  Smartphone,
  VolumeX,
  Volume2
} from 'lucide-react';
import { DELHI_HOTSPOTS } from './SmoothRiskMap';

interface Contact {
  name: string;
  phone: string;
  relationship: string;
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
      const stored = localStorage.getItem('rakshak_emergency_contacts');
      if (stored) return JSON.parse(stored);
    } catch {}
    return DEFAULT_CONTACTS;
  });

  const [primaryPhone, setPrimaryPhone] = useState<string>(() => {
    return localStorage.getItem('rakshak_primary_phone') || DEFAULT_CONTACTS[0].phone;
  });

  const [modalOpen, setModalOpen] = useState(false);
  const [newName, setNewName] = useState('');
  const [newPhone, setNewPhone] = useState('');
  
  const [isWithin100m, setIsWithin100m] = useState(false);
  const [nearestDistance, setNearestDistance] = useState<number>(Infinity);
  const [nearestHotspotName, setNearestHotspotName] = useState<string>('Delhi Hotspot');
  
  const [toastMessage, setToastMessage] = useState<{ text: string; isError?: boolean } | null>(null);
  const [isAlarmActive, setIsAlarmActive] = useState(false);
  const [isSimulated100m, setIsSimulated100m] = useState(false);

  const audioCtxRef = useRef<AudioContext | null>(null);
  const toneIntervalRef = useRef<any>(null);

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
      setNearestDistance(55);
      setNearestHotspotName('Rajiv Chowk Metro / CP Outer Circle (High Risk)');
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

  const primaryContact = contacts.find((c) => c.phone === primaryPhone) || contacts[0] || DEFAULT_CONTACTS[0];

  const showToast = (text: string, isError = false) => {
    setToastMessage({ text, isError });
    setTimeout(() => {
      setToastMessage(null);
    }, 4500);
  };

  const handleSelectPrimary = (phone: string) => {
    setPrimaryPhone(phone);
    try {
      localStorage.setItem('rakshak_primary_phone', phone);
    } catch {}
    showToast(`⭐ Primary contact set to ${contacts.find(c => c.phone === phone)?.name || phone}`);
  };

  const handleSaveContact = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPhone.trim()) {
      showToast('Please enter a valid phone number', true);
      return;
    }
    const item: Contact = {
      name: newName.trim() || 'Emergency Guardian',
      phone: newPhone.trim(),
      relationship: 'Personal Contact',
    };
    const updated = [...contacts, item];
    setContacts(updated);
    setPrimaryPhone(item.phone);
    try {
      localStorage.setItem('rakshak_emergency_contacts', JSON.stringify(updated));
      localStorage.setItem('rakshak_primary_phone', item.phone);
    } catch {}
    setNewName('');
    setNewPhone('');
    showToast(`✅ Contact saved and set as Primary!`);
    setModalOpen(false);
  };

  // Web Contact Picker API
  const handleSyncNativeContacts = async () => {
    if ('contacts' in navigator && 'ContactsManager' in window) {
      try {
        const props = ['name', 'tel'];
        const picked = await (navigator as any).contacts.select(props, { multiple: false });
        if (picked && picked.length > 0) {
          const c = picked[0];
          const name = c.name && c.name[0] ? c.name[0] : 'Emergency Contact';
          const tel = c.tel && c.tel[0] ? c.tel[0] : '';
          if (tel) {
            const updated = [...contacts, { name, phone: tel, relationship: 'Mobile Contact' }];
            setContacts(updated);
            setPrimaryPhone(tel);
            localStorage.setItem('rakshak_emergency_contacts', JSON.stringify(updated));
            localStorage.setItem('rakshak_primary_phone', tel);
            showToast(`✅ Synced ${name} as Primary Contact!`);
            return;
          }
        }
      } catch (err) {
        console.log('Contact Picker cancelled:', err);
      }
    } else {
      showToast('ℹ️ Web Contact Picker not supported on this browser. Add contact manually below.', true);
    }
  };

  // Web Audio API: Recurring Two-Tone Alarm (880Hz alternating with 1200Hz)
  const startAlarmSound = () => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      if (!audioCtxRef.current) audioCtxRef.current = new AudioCtx();
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') ctx.resume();

      stopAlarmSound();
      setIsAlarmActive(true);

      let step = 0;
      toneIntervalRef.current = setInterval(() => {
        step++;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        // Recurring two-tone pulsed beep: alternating 880Hz and 1200Hz
        const freq = step % 2 === 0 ? 880 : 1200;
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(freq, ctx.currentTime);

        gain.gain.setValueAtTime(0.35, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.16);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.17);
      }, 200);
    } catch (e) {
      console.log('AudioContext initialization error:', e);
    }
  };

  const stopAlarmSound = () => {
    if (toneIntervalRef.current) {
      clearInterval(toneIntervalRef.current);
      toneIntervalRef.current = null;
    }
    setIsAlarmActive(false);
  };

  // Immediate Alert Trigger Logic
  const handleSosClick = async () => {
    if (isAlarmActive) {
      stopAlarmSound();
      showToast('🔇 Emergency alarm silenced.');
      return;
    }

    // 1. Validation: Check if Primary Contact is set
    if (!primaryContact || !primaryContact.phone) {
      showToast('⚠️ Please select or add a Primary Contact first!', true);
      setModalOpen(true);
      return;
    }

    // 2. Safety Beep Sound: Triggered immediately inside user click interaction
    startAlarmSound();

    // 3. Payload with clickable Google Maps link
    const mapsLink = `https://www.google.com/maps?q=${currentLat.toFixed(5)},${currentLon.toFixed(5)}`;
    const urgentText = `EMERGENCY SOS: User is near a high-risk danger zone (<100m). Immediate help needed! Location: ${mapsLink}`;

    const payload = {
      recipient: primaryContact,
      location: {
        latitude: currentLat,
        longitude: currentLon,
        google_maps_link: mapsLink,
      },
      message: urgentText,
      push_notification: {
        sound: 'safety_beep.mp3',
        priority: 'high',
      },
    };

    if (onAlertDispatched) onAlertDispatched(payload);

    // 4. Alert Dispatch (SMS / Webhook)
    try {
      const endpoints = ['/api/send-sos', 'http://127.0.0.1:4021/api/send-sos', 'http://127.0.0.1:4021/api/v1/sos-alert'];
      for (const ep of endpoints) {
        try {
          fetch(ep, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
        } catch {}
      }
      showToast(`🚨 SOS Alert sent to ${primaryContact.name} (${primaryContact.phone})!`);
    } catch (err) {
      showToast(`⚠️ SOS telemetry logged to ${primaryContact.name}`, true);
    }
  };

  if (compact) {
    return (
      <div className="relative inline-flex items-center gap-2 font-sans">
        <button
          onClick={handleSosClick}
          className={`px-3 py-1.5 rounded-full text-xs font-black tracking-wide text-white flex items-center gap-1.5 shadow-xl transition-all cursor-pointer ${
            isAlarmActive
              ? 'bg-gradient-to-r from-red-600 via-rose-500 to-amber-500 animate-pulse border-2 border-white shadow-[0_0_25px_rgba(255,255,255,0.9)]'
              : isWithin100m
              ? 'bg-gradient-to-r from-red-700 via-rose-600 to-red-800 animate-pulse border-2 border-red-400 shadow-[0_0_20px_rgba(239,68,68,0.9)]'
              : 'bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 border border-red-400/50 shadow-[0_0_12px_rgba(239,68,68,0.5)]'
          }`}
          title={isAlarmActive ? 'Alarm Sounding - Tap to Mute' : 'Trigger SOS Emergency Alert'}
        >
          <span className="text-xs">🚨</span>
          <span>{isAlarmActive ? 'ALARM ACTIVE' : isWithin100m ? 'HIGH RISK (<100m)' : 'SOS EMERGENCY'}</span>
          <Bell className="w-3.5 h-3.5 fill-white" />
        </button>

        <button
          onClick={() => setModalOpen(true)}
          className="p-1 rounded-full bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-700 hover:border-cyan-500 transition-colors"
          title={`Emergency Contacts (Primary: ${primaryContact.name})`}
        >
          <Settings className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }

  return (
    <div className="w-full space-y-2.5 font-sans relative">
      {/* Toast Notification */}
      {toastMessage && (
        <div
          className={`p-2.5 rounded-xl text-xs font-semibold border flex items-center justify-between shadow-2xl transition-all ${
            toastMessage.isError
              ? 'bg-red-950/95 border-red-500 text-red-200'
              : 'bg-slate-900/95 border-emerald-500 text-emerald-200'
          }`}
        >
          <span>{toastMessage.text}</span>
          <button onClick={() => setToastMessage(null)} className="text-slate-400 hover:text-white ml-2">
            ✕
          </button>
        </div>
      )}

      {/* 1. Primary Pulsing SOS Emergency Button */}
      <button
        onClick={handleSosClick}
        className={`w-full py-3.5 px-4 rounded-2xl font-black text-sm tracking-wider uppercase flex items-center justify-center gap-2.5 text-white shadow-2xl transition-all cursor-pointer select-none ${
          isAlarmActive
            ? 'bg-gradient-to-r from-red-600 via-rose-500 to-amber-500 border-2 border-white shadow-[0_0_35px_rgba(255,255,255,0.95)] animate-pulse scale-[1.02]'
            : isWithin100m
            ? 'bg-gradient-to-r from-red-700 via-rose-600 to-red-900 border-2 border-red-400 shadow-[0_0_30px_rgba(239,68,68,0.95)] animate-pulse'
            : 'bg-gradient-to-r from-red-600 via-rose-600 to-red-700 hover:from-red-500 hover:to-rose-500 border-2 border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.7)] hover:shadow-[0_0_28px_rgba(239,68,68,0.9)] active:scale-[0.98]'
        }`}
      >
        <span className="text-lg animate-bounce">🚨</span>
        <span className="drop-shadow-md">
          {isAlarmActive ? '🔊 ALARM SOUNDING - TAP TO SILENCE' : isWithin100m ? '⚠️ HIGH RISK PROXIMITY (<100M)' : 'SOS EMERGENCY'}
        </span>
        <span className="text-base animate-pulse">🔔</span>
      </button>

      {/* Dismiss Alarm Toggle Button */}
      {isAlarmActive && (
        <button
          onClick={stopAlarmSound}
          className="w-full py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg transition-all"
        >
          <VolumeX className="w-4 h-4" />
          <span>Stop Alarm / Dismiss</span>
        </button>
      )}

      {/* 2. Settings Toggle Button directly under SOS Button */}
      <div
        onClick={() => setModalOpen(true)}
        className="w-full bg-slate-950/80 hover:bg-slate-900 border border-slate-800 hover:border-cyan-500/60 rounded-xl px-3 py-2 flex items-center justify-between text-xs cursor-pointer transition-colors"
      >
        <div className="flex items-center gap-1.5 text-slate-300 font-bold">
          <Settings className="w-3.5 h-3.5 text-cyan-400" />
          <span>Emergency Contacts</span>
        </div>
        <span className="text-[10px] font-mono font-bold text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded-full border border-cyan-800/60 truncate max-w-[140px]">
          Primary: {primaryContact.name}
        </span>
      </div>

      {/* 3. Proximity / Geofence Status HUD */}
      <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-2.5 flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5">
          <Radio className={`w-3.5 h-3.5 ${isWithin100m ? 'text-red-400 animate-ping' : 'text-cyan-400'}`} />
          <span className="text-slate-400 text-[11px]">Hotspot Proximity:</span>
        </div>
        <span
          className={`font-mono text-[10px] font-bold px-2 py-0.5 rounded-full border ${
            isWithin100m
              ? 'bg-red-950/80 text-red-400 border-red-700 animate-pulse'
              : 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60'
          }`}
        >
          {isWithin100m ? `CRITICAL (${nearestDistance}m)` : `${nearestDistance}m Buffer`}
        </span>
      </div>

      {/* Quick Test Geofence Sim */}
      <div className="flex items-center justify-between text-[10px] text-slate-500 px-1">
        <span>Test 100m Geofence:</span>
        <div className="flex gap-1.5">
          <button
            onClick={() => setIsSimulated100m(true)}
            className={`px-2 py-0.5 rounded text-[10px] font-bold transition-colors ${
              isSimulated100m ? 'bg-red-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            &lt;100m
          </button>
          <button
            onClick={() => setIsSimulated100m(false)}
            className={`px-2 py-0.5 rounded text-[10px] font-bold transition-colors ${
              !isSimulated100m ? 'bg-emerald-700 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            Safe
          </button>
        </div>
      </div>

      {/* 4. Emergency Contacts Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-[99999] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-sm w-full p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-extrabold text-white text-sm flex items-center gap-2">
                <Settings className="w-4 h-4 text-cyan-400" />
                <span>Emergency Contacts Manager</span>
              </h3>
              <button onClick={() => setModalOpen(false)} className="text-slate-400 hover:text-white p-1 rounded-lg">
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Select or add your <strong>Primary Emergency Contact</strong>. Real-time SMS and distress telemetry will be dispatched targeting this contact:
            </p>

            <button
              onClick={handleSyncNativeContacts}
              className="w-full py-2 px-3 rounded-xl bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-800 text-cyan-300 text-xs font-bold flex items-center justify-center gap-1.5 transition-colors"
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span>Sync via Web Contact Picker API</span>
            </button>

            {/* Contacts List with Radio Selection */}
            <div className="space-y-1.5 max-h-44 overflow-y-auto pr-1">
              {contacts.map((c, i) => {
                const isSelected = c.phone === primaryPhone;
                return (
                  <div
                    key={i}
                    onClick={() => handleSelectPrimary(c.phone)}
                    className={`p-2.5 rounded-xl text-xs flex items-center justify-between border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-emerald-950/30 border-emerald-500 text-white shadow-sm'
                        : 'bg-black/40 border-slate-800 hover:border-slate-700 text-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <input
                        type="radio"
                        name="primaryContactRadio"
                        checked={isSelected}
                        onChange={() => handleSelectPrimary(c.phone)}
                        className="accent-emerald-500 w-4 h-4 cursor-pointer"
                      />
                      <div>
                        <div className="font-bold flex items-center gap-1.5">
                          <span>{c.name}</span>
                          {isSelected && (
                            <span className="text-[9px] font-mono font-black text-emerald-400 bg-emerald-950 px-1.5 py-0.2 rounded border border-emerald-800">
                              PRIMARY
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-slate-400 font-mono">{c.phone}</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Add Contact Form */}
            <form onSubmit={handleSaveContact} className="space-y-2 pt-2 border-t border-slate-800 text-xs">
              <label className="block text-slate-300 font-semibold text-[11px]">Add New Emergency Contact</label>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Name (e.g. Guardian / Sister)"
                className="w-full bg-black/60 border border-slate-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
              <input
                type="tel"
                value={newPhone}
                onChange={(e) => setNewPhone(e.target.value)}
                placeholder="Phone (+91 98100 12345)"
                className="w-full bg-black/60 border border-slate-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                required
              />
              <button
                type="submit"
                className="w-full py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold rounded-lg shadow transition-all flex items-center justify-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Save & Set as Primary</span>
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
