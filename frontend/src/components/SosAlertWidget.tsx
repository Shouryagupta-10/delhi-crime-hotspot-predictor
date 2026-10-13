import React, { useState, useEffect, useRef } from 'react';
import { 
  Bell, 
  Settings, 
  X, 
  ShieldAlert,
  VolumeX,
  Volume2,
  ExternalLink,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { DELHI_HOTSPOTS } from './SmoothRiskMap';

export interface PrimaryContact {
  name: string;
  email: string;
}

interface SosAlertWidgetProps {
  currentLat?: number;
  currentLon?: number;
  compact?: boolean;
  onAlertDispatched?: (payload: any) => void;
}

// Inline SVG Data URI for shield icon to ensure 100% offline, client-side reliability
const SHIELD_ICON_DATA_URI = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ef4444'%3E%3Cpath d='M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z'/%3E%3C/svg%3E";

export const SosAlertWidget: React.FC<SosAlertWidgetProps> = ({
  currentLat = 28.6328,
  currentLon = 77.2197,
  compact = false,
  onAlertDispatched,
}) => {
  // 1. Primary Contact Setup & localStorage Persistence under 'rakshak_primary_contact'
  const [contact, setContact] = useState<PrimaryContact | null>(() => {
    try {
      const stored = localStorage.getItem('rakshak_primary_contact');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed && parsed.name && parsed.email) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn('Failed to parse primary contact:', e);
    }
    return null;
  });

  const [modalOpen, setModalOpen] = useState(false);
  const [interceptWarning, setInterceptWarning] = useState(false);
  const [nameInput, setNameInput] = useState('');
  const [emailInput, setEmailInput] = useState('');
  const [nameError, setNameError] = useState('');
  const [emailError, setEmailError] = useState('');

  // 2. Notification Permission Status
  const [notifPermission, setNotifPermission] = useState<NotificationPermission>('default');

  // 3. Audio & Alarm State
  const [isAlarmActive, setIsAlarmActive] = useState(false);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const toneIntervalRef = useRef<any>(null);

  // 4. Proximity & HUD State
  const [isWithin100m, setIsWithin100m] = useState(false);
  const [nearestDistance, setNearestDistance] = useState<number>(Infinity);
  const [nearestHotspotName, setNearestHotspotName] = useState<string>('Delhi Hotspot');
  const [isSimulated100m, setIsSimulated100m] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; isError?: boolean } | null>(null);

  // Synchronize contact inputs when modal opens or contact changes
  useEffect(() => {
    if (contact) {
      setNameInput(contact.name);
      setEmailInput(contact.email);
    }
  }, [contact]);

  // Read current notification permission on mount
  useEffect(() => {
    if (typeof window !== 'undefined' && 'Notification' in window) {
      setNotifPermission(Notification.permission);
    }
  }, []);

  // Distance calculation (Haversine)
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

  useEffect(() => {
    if (isSimulated100m) {
      setIsWithin100m(true);
      setNearestDistance(55);
      setNearestHotspotName('Rajiv Chowk Metro / CP Outer Circle (Critical Risk)');
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

  const showToast = (text: string, isError = false) => {
    setToastMessage({ text, isError });
    setTimeout(() => {
      setToastMessage(null);
    }, 4500);
  };

  const validateEmail = (email: string) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
  };

  // Browser Notification Permission Request
  const requestNotificationPermission = async () => {
    if (typeof window === 'undefined' || !('Notification' in window)) {
      showToast('Browser notifications are not supported in this browser.', true);
      return;
    }

    try {
      const perm = await Notification.requestPermission();
      setNotifPermission(perm);
      if (perm === 'granted') {
        showToast('✅ Browser notification permission granted!');
      } else if (perm === 'denied') {
        showToast('⚠️ Notifications are blocked in browser permissions.', true);
      }
    } catch (e) {
      console.warn('Permission request error:', e);
    }
  };

  // Modal Open Handlers
  const handleOpenModal = (intercepted = false) => {
    setInterceptWarning(intercepted);
    setNameError('');
    setEmailError('');
    if (contact) {
      setNameInput(contact.name);
      setEmailInput(contact.email);
    }
    setModalOpen(true);

    // Request notification permission during setup if still default
    if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then((p) => setNotifPermission(p)).catch(() => {});
    }
  };

  // Save / Update Contact Form Submit
  const handleSaveContact = (e: React.FormEvent) => {
    e.preventDefault();
    let valid = true;

    if (!nameInput.trim()) {
      setNameError('Primary contact name is required.');
      valid = false;
    } else {
      setNameError('');
    }

    if (!emailInput.trim() || !validateEmail(emailInput.trim())) {
      setEmailError('Please enter a valid email address.');
      valid = false;
    } else {
      setEmailError('');
    }

    if (!valid) return;

    const updatedContact: PrimaryContact = {
      name: nameInput.trim(),
      email: emailInput.trim(),
    };

    const isUpdate = !!contact;
    setContact(updatedContact);
    try {
      localStorage.setItem('rakshak_primary_contact', JSON.stringify(updatedContact));
    } catch (err) {
      console.error('Failed to save contact to localStorage:', err);
    }

    setModalOpen(false);
    setInterceptWarning(false);
    showToast(isUpdate ? `✅ Contact updated: ${updatedContact.name}` : `✅ Contact saved: ${updatedContact.name}`);

    // Prompt notification permission if still default
    if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then((p) => setNotifPermission(p)).catch(() => {});
    }
  };

  // Web Audio API Continuous Pulsing Emergency Beep (880Hz alternating with 1200Hz)
  const startAlarmSound = () => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;

      if (!audioCtxRef.current) {
        audioCtxRef.current = new AudioCtx();
      }
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      stopAlarmToneOnly();
      setIsAlarmActive(true);

      let isHighTone = false;
      toneIntervalRef.current = setInterval(() => {
        if (!ctx) return;
        try {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();

          // Continuous pulsing emergency beep alternating rapidly between 880Hz and 1200Hz
          const freq = isHighTone ? 1200 : 880;
          isHighTone = !isHighTone;

          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(freq, ctx.currentTime);

          gain.gain.setValueAtTime(0.35, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.16);

          osc.connect(gain);
          gain.connect(ctx.destination);

          osc.start(ctx.currentTime);
          osc.stop(ctx.currentTime + 0.17);
        } catch (err) {
          console.warn('Tone oscillation tick error:', err);
        }
      }, 180);
    } catch (e) {
      console.warn('Web Audio API error:', e);
    }
  };

  const stopAlarmToneOnly = () => {
    if (toneIntervalRef.current) {
      clearInterval(toneIntervalRef.current);
      toneIntervalRef.current = null;
    }
  };

  const stopEmergencyAlarm = () => {
    stopAlarmToneOnly();
    setIsAlarmActive(false);
    showToast('🔇 Emergency alarm silenced.');
  };

  // Native Browser Notification Trigger
  const triggerNativeNotification = (currentContact: PrimaryContact) => {
    if (typeof window === 'undefined' || !('Notification' in window)) return;

    const notifTitle = 'EMERGENCY SOS: Help Needed!';
    const notifOptions: NotificationOptions = {
      body: `Alert for ${currentContact.name} (${currentContact.email}): The user is in an active danger zone! Lat: ${currentLat.toFixed(5)}, Lng: ${currentLon.toFixed(5)}`,
      icon: SHIELD_ICON_DATA_URI,
      requireInteraction: true,
      tag: 'sos-alert',
    };

    if (Notification.permission === 'granted') {
      try {
        new Notification(notifTitle, notifOptions);
      } catch (e) {
        console.warn('Native notification trigger error:', e);
      }
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then((perm) => {
        setNotifPermission(perm);
        if (perm === 'granted') {
          try {
            new Notification(notifTitle, notifOptions);
          } catch (e) {}
        }
      });
    }
  };

  // SOS Button Click Handler
  const handleSosClick = () => {
    // If alarm is already sounding, tapping dismisses it
    if (isAlarmActive) {
      stopEmergencyAlarm();
      return;
    }

    // Intercept Rule: If a user clicks SOS before saving a primary contact, intercept and open modal first
    if (!contact || !contact.name || !contact.email) {
      showToast('⚠️ Configure your Primary Emergency Contact first!', true);
      handleOpenModal(true);
      return;
    }

    // Start Audio Alarm inside onClick event handler to comply with browser autoplay policy
    startAlarmSound();

    // Trigger Native Browser Notification
    triggerNativeNotification(contact);

    if (onAlertDispatched) {
      onAlertDispatched({
        recipient: contact,
        location: {
          latitude: currentLat,
          longitude: currentLon,
          google_maps_link: `https://www.google.com/maps?q=${currentLat.toFixed(5)},${currentLon.toFixed(5)}`,
        },
        timestamp: new Date().toISOString(),
      });
    }

    showToast(`🚨 SOS Triggered for ${contact.name} (${contact.email})!`);
  };

  const googleMapsUrl = `https://www.google.com/maps?q=${currentLat.toFixed(5)},${currentLon.toFixed(5)}`;

  return (
    <div className="relative w-full font-sans">
      {/* 1. Persistent High-Priority In-Dashboard Alert Banner Across Top of Interface */}
      {isAlarmActive && contact && (
        <div className="fixed top-0 left-0 right-0 z-[999999] bg-gradient-to-r from-red-950 via-red-800 to-rose-900 border-b-2 border-red-500 shadow-[0_4px_30px_rgba(239,68,68,0.9)] px-4 py-3 flex flex-col sm:flex-row items-center justify-between gap-3 text-white animate-in slide-in-from-top duration-300">
          <div className="flex items-center gap-3 flex-1 flex-wrap">
            <span className="text-xl animate-bounce">🚨</span>
            <div className="text-xs sm:text-sm font-bold tracking-tight">
              <span>EMERGENCY ALERT: Distress signal triggered for primary contact </span>
              <span className="underline text-red-200">{contact.name}</span>
              <span> ({contact.email}) with current GPS coordinates.</span>
            </div>
            <a
              href={googleMapsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-black/40 hover:bg-black/60 text-yellow-300 font-mono text-xs underline font-semibold border border-yellow-400/40 transition-colors"
            >
              <span>📍 {googleMapsUrl}</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>

          <button
            onClick={stopEmergencyAlarm}
            className="shrink-0 px-4 py-2 bg-white hover:bg-yellow-100 text-red-950 font-black text-xs uppercase tracking-wider rounded-lg shadow-lg flex items-center gap-2 transition-transform hover:scale-105 active:scale-95 cursor-pointer"
          >
            <VolumeX className="w-4 h-4 text-red-700" />
            <span>Dismiss / Silence Alarm</span>
          </button>
        </div>
      )}

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div
          className={`mb-2 p-2.5 rounded-xl text-xs font-semibold border flex items-center justify-between shadow-2xl transition-all ${
            toastMessage.isError
              ? 'bg-red-950/95 border-red-500 text-red-200 shadow-red-950/50'
              : 'bg-emerald-950/95 border-emerald-500 text-emerald-200 shadow-emerald-950/50'
          }`}
        >
          <div className="flex items-center gap-2">
            <span>{toastMessage.isError ? '⚠️' : '🛡️'}</span>
            <span>{toastMessage.text}</span>
          </div>
          <button onClick={() => setToastMessage(null)} className="text-slate-400 hover:text-white p-0.5">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* COMPACT LAYOUT (e.g. Header bar next to shield logo) */}
      {compact ? (
        <div className="inline-flex items-center gap-2">
          {/* Animated Pulsing SOS Emergency Button */}
          <button
            onClick={handleSosClick}
            className={`px-3.5 py-1.5 rounded-full text-xs font-black tracking-wider text-white flex items-center gap-1.5 shadow-xl transition-all cursor-pointer relative ${
              isAlarmActive
                ? 'bg-gradient-to-r from-red-600 via-rose-600 to-red-700 border-2 border-white animate-pulse shadow-[0_0_25px_rgba(239,68,68,0.95)] ring-4 ring-red-500/50'
                : isWithin100m
                ? 'bg-gradient-to-r from-red-700 via-rose-600 to-red-800 animate-pulse border-2 border-red-400 shadow-[0_0_20px_rgba(239,68,68,0.9)]'
                : 'bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 border border-red-400/50 shadow-[0_0_12px_rgba(239,68,68,0.5)]'
            }`}
            title={isAlarmActive ? 'Alarm Sounding - Click to Silence' : 'Trigger SOS Emergency Alert'}
          >
            <span className="text-xs">🚨</span>
            <span>{isAlarmActive ? 'ALARM ACTIVE' : isWithin100m ? 'HIGH RISK (<100m)' : 'SOS EMERGENCY'}</span>
            <Bell className="w-3.5 h-3.5 fill-white" />
          </button>

          {/* Settings Icon Button next to SOS Button */}
          <button
            onClick={() => handleOpenModal(false)}
            className="p-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 text-slate-300 hover:text-cyan-400 border border-slate-700 hover:border-cyan-500 transition-all cursor-pointer shadow-md"
            title={contact ? `Primary Contact: ${contact.name} (${contact.email})` : 'Configure Primary Emergency Contact'}
          >
            <Settings className="w-3.5 h-3.5" />
          </button>
        </div>
      ) : (
        /* FULL SIDEBAR / CARD LAYOUT */
        <div className="w-full space-y-2.5">
          {/* Action Row: Primary Button + Settings Icon */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleSosClick}
              className={`flex-1 py-3 px-4 rounded-xl text-xs sm:text-sm font-black tracking-wider text-white flex items-center justify-center gap-2 shadow-xl transition-all cursor-pointer relative overflow-hidden ${
                isAlarmActive
                  ? 'bg-gradient-to-r from-red-600 via-rose-600 to-red-700 border-2 border-white ring-4 ring-red-500/70 shadow-[0_0_30px_rgba(239,68,68,0.95)] animate-pulse'
                  : isWithin100m
                  ? 'bg-gradient-to-r from-red-700 via-rose-600 to-red-800 border-2 border-red-400 shadow-[0_0_22px_rgba(239,68,68,0.85)] animate-pulse'
                  : 'bg-gradient-to-r from-red-600 via-rose-600 to-red-700 hover:from-red-500 hover:to-rose-500 border border-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.5)]'
              }`}
            >
              <span className="text-sm">🚨</span>
              <span>{isAlarmActive ? 'ALARM ACTIVE - SILENCE' : isWithin100m ? 'HIGH RISK PROXIMITY (<100m)' : 'SOS EMERGENCY'}</span>
              <Bell className="w-4 h-4 fill-white" />
            </button>

            <button
              onClick={() => handleOpenModal(false)}
              className="h-11 w-11 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-cyan-400 border border-slate-700 hover:border-cyan-500 flex items-center justify-center transition-all cursor-pointer shadow-md shrink-0"
              title={contact ? `Primary Contact: ${contact.name} (${contact.email})` : 'Configure Emergency Contact'}
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>

          {/* Visible Dismiss / Silence Alarm Button */}
          {isAlarmActive && (
            <button
              onClick={stopEmergencyAlarm}
              className="w-full py-2.5 px-3 bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-black text-xs uppercase tracking-wider rounded-xl shadow-lg border border-yellow-300 flex items-center justify-center gap-2 cursor-pointer transition-all"
            >
              <VolumeX className="w-4 h-4 text-slate-950" />
              <span>Dismiss / Silence Alarm</span>
            </button>
          )}

          {/* Status Sub-bar: Notification Badge & Contact Details */}
          <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col gap-1.5 text-[11px]">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 font-medium">Notifications:</span>
              <button
                onClick={requestNotificationPermission}
                className={`px-2 py-0.5 rounded-full font-mono text-[10px] font-bold border transition-colors cursor-pointer ${
                  notifPermission === 'granted'
                    ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60'
                    : notifPermission === 'denied'
                    ? 'bg-rose-950/60 text-rose-400 border-rose-800/60'
                    : 'bg-amber-950/60 text-amber-400 border-amber-800/60'
                }`}
              >
                {notifPermission === 'granted'
                  ? '🟢 Granted'
                  : notifPermission === 'denied'
                  ? '🔴 Blocked'
                  : '🟡 Not Allowed (Click)'}
              </button>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-400 font-medium">Primary Contact:</span>
              <button
                onClick={() => handleOpenModal(false)}
                className="text-cyan-400 hover:text-cyan-300 font-semibold truncate max-w-[160px] text-left underline cursor-pointer"
                title={contact ? `${contact.name} (${contact.email})` : 'Not configured'}
              >
                {contact ? `${contact.name}` : '⚠️ Not Configured'}
              </button>
            </div>

            <div className="flex items-center justify-between pt-1 border-t border-slate-800/80">
              <span className="text-slate-400 font-medium">Zone Proximity:</span>
              <span
                className={`font-mono text-[10px] font-bold px-2 py-0.2 rounded-full border ${
                  isWithin100m
                    ? 'bg-rose-950/80 text-rose-400 border-rose-800/60 animate-pulse'
                    : 'bg-emerald-950/80 text-emerald-400 border-emerald-800/60'
                }`}
              >
                {isWithin100m ? `🚨 High Risk (${nearestDistance}m)` : `${nearestDistance}m Safe Buffer`}
              </span>
            </div>
          </div>

          {/* Quick Simulation Buttons */}
          <div className="flex items-center justify-between text-[10px] text-slate-500 px-1">
            <span>Simulate Geofence:</span>
            <div className="flex gap-1.5">
              <button
                onClick={() => setIsSimulated100m(true)}
                className="px-2 py-0.5 rounded bg-slate-800/70 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[9px] cursor-pointer"
              >
                &lt;100m Hotspot
              </button>
              <button
                onClick={() => setIsSimulated100m(false)}
                className="px-2 py-0.5 rounded bg-slate-800/70 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[9px] cursor-pointer"
              >
                Reset Safe
              </button>
            </div>
          </div>
        </div>
      )}

      {/* EMERGENCY CONTACT CONFIGURATION MODAL */}
      {modalOpen && (
        <div className="fixed inset-0 z-[9999999] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-sm p-5 shadow-2xl space-y-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-red-400" />
                <h3 className="text-sm font-bold text-white">Emergency Contact Setup</h3>
              </div>
              <button
                onClick={() => setModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {interceptWarning && (
              <div className="p-2.5 rounded-xl bg-red-950/60 border border-red-500/60 text-red-200 text-xs flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                <span>Please configure your primary emergency contact before triggering the SOS alert.</span>
              </div>
            )}

            <form onSubmit={handleSaveContact} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Primary Contact Name *
                </label>
                <input
                  type="text"
                  value={nameInput}
                  onChange={(e) => setNameInput(e.target.value)}
                  placeholder="e.g. Inspector Sharma / Guardian"
                  className={`w-full px-3 py-2 rounded-xl bg-slate-800/80 border text-white text-xs placeholder:text-slate-500 outline-none transition-colors ${
                    nameError ? 'border-red-500' : 'border-slate-700 focus:border-cyan-500'
                  }`}
                  autoFocus
                />
                {nameError && <p className="text-[10px] text-red-400 mt-1 font-medium">{nameError}</p>}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Primary Contact Email *
                </label>
                <input
                  type="email"
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                  placeholder="e.g. emergency@contact.com"
                  className={`w-full px-3 py-2 rounded-xl bg-slate-800/80 border text-white text-xs placeholder:text-slate-500 outline-none transition-colors ${
                    emailError ? 'border-red-500' : 'border-slate-700 focus:border-cyan-500'
                  }`}
                />
                {emailError && <p className="text-[10px] text-red-400 mt-1 font-medium">{emailError}</p>}
              </div>

              <div className="p-2.5 rounded-xl bg-slate-800/40 border border-slate-800 flex items-center justify-between text-xs">
                <div>
                  <div className="text-white font-medium text-[11px]">Browser Notifications</div>
                  <div className="text-[10px] text-slate-400">Status: {notifPermission}</div>
                </div>
                <button
                  type="button"
                  onClick={requestNotificationPermission}
                  className="px-2.5 py-1 rounded-lg bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-800 text-cyan-300 text-[10px] font-bold transition-colors cursor-pointer"
                >
                  Enable Permissions
                </button>
              </div>

              <div className="flex gap-2 pt-1">
                <button
                  type="submit"
                  className="flex-1 py-2 px-4 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-xs shadow-lg transition-transform active:scale-95 cursor-pointer"
                >
                  {contact ? 'Update Contact' : 'Save Contact'}
                </button>
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors cursor-pointer"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
