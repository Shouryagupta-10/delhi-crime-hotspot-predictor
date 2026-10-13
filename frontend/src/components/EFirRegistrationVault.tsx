import React, { useState, useRef } from 'react';
import {
  ShieldCheck,
  FileText,
  UploadCloud,
  Lock,
  CheckCircle2,
  AlertTriangle,
  MapPin,
  ExternalLink,
  Copy,
  Check,
  Trash2,
  Clock,
  Building2,
  User,
  Phone,
  Calendar,
  X,
  Crosshair,
  Download,
  Film,
  Image as ImageIcon
} from 'lucide-react';

interface EvidenceFileItem {
  id: string;
  file: File;
  name: string;
  size: number;
  type: string;
  sha256: string;
  truncatedSha: string;
  previewUrl?: string;
  timestamp: string;
}

const DELHI_POLICE_STATIONS = [
  { name: 'Connaught Place Police Station', district: 'New Delhi', lat: 28.6315, lon: 77.2167 },
  { name: 'Parliament Street Police Station', district: 'New Delhi', lat: 28.6238, lon: 77.2142 },
  { name: 'Kashmere Gate Police Station', district: 'North', lat: 28.6675, lon: 77.2285 },
  { name: 'Karol Bagh Police Station', district: 'Central', lat: 28.6517, lon: 77.1906 },
  { name: 'Paharganj Police Station', district: 'Central', lat: 28.6432, lon: 77.2140 },
  { name: 'Daryaganj Police Station', district: 'Central', lat: 28.6480, lon: 77.2410 },
  { name: 'Hauz Khas Police Station', district: 'South', lat: 28.5430, lon: 77.2060 },
  { name: 'Saket Police Station', district: 'South', lat: 28.5240, lon: 77.2120 },
  { name: 'Lajpat Nagar Police Station', district: 'South-East', lat: 28.5677, lon: 77.2433 },
  { name: 'Vasant Vihar Police Station', district: 'South-West', lat: 28.5580, lon: 77.1620 },
  { name: 'Rajouri Garden Police Station', district: 'West', lat: 28.6490, lon: 77.1230 },
  { name: 'Netaji Subhash Place Police Station', district: 'North-West', lat: 28.6925, lon: 77.1520 },
  { name: 'Dwarka Sector 10 Police Station', district: 'Dwarka', lat: 28.5810, lon: 77.0580 },
  { name: 'Laxmi Nagar Police Station', district: 'East', lat: 28.6310, lon: 77.2780 }
];

const INCIDENT_TYPES = [
  { id: 'vehicle_theft', title: 'Vehicle Theft', bns: 'Sec 303(2) BNS / IPC 379' },
  { id: 'mobile_snatching', title: 'Mobile / Chain Snatching', bns: 'Sec 304 BNS / IPC 392' },
  { id: 'assault', title: 'Physical Assault & Voluntary Hurt', bns: 'Sec 115 BNS / IPC 323' },
  { id: 'harassment', title: 'Women Harassment & Stalking', bns: 'Sec 74, 78 BNS / IPC 354' },
  { id: 'cyber_fraud', title: 'Cyber Financial Fraud & Phishing', bns: 'Sec 318(4) BNS / IT Act 66D' },
  { id: 'burglary', title: 'House Burglary & Trespass', bns: 'Sec 331(4) BNS / IPC 457' },
  { id: 'extortion', title: 'Extortion & Criminal Threat', bns: 'Sec 308 BNS / IPC 384' }
];

/**
 * Computes SHA-256 hash using native Web Crypto API (window.crypto.subtle.digest)
 */
async function computeSha256(file: File): Promise<string> {
  const arrayBuffer = await file.arrayBuffer();
  const hashBuffer = await window.crypto.subtle.digest('SHA-256', arrayBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}

function truncateString(str: string, start = 8, end = 8): string {
  if (!str || str.length <= start + end) return str;
  return `${str.slice(0, start)}...${str.slice(-end)}`;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
}

export const EFirRegistrationVault: React.FC = () => {
  // Input fields
  const [complainantName, setComplainantName] = useState('Rahul Sharma');
  const [phoneNumber, setPhoneNumber] = useState('+91 98112 34567');
  const [incidentType, setIncidentType] = useState('mobile_snatching');
  const [incidentDate, setIncidentDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [incidentTime, setIncidentTime] = useState('11:30');
  const [narrative, setNarrative] = useState(
    'While exiting Rajiv Chowk Metro Gate 6 towards Radial Road 1, two unknown individuals on a black motorcycle snatched my phone and laptop bag and accelerated towards Barakhamba Road.'
  );
  const [policeStation, setPoliceStation] = useState(DELHI_POLICE_STATIONS[0].name);
  const [lat, setLat] = useState('28.6315');
  const [lon, setLon] = useState('77.2167');

  // Evidence files & hashing
  const [evidenceFiles, setEvidenceFiles] = useState<EvidenceFileItem[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [hashingInProgress, setHashingInProgress] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Submission state
  const [submissionModalOpen, setSubmissionModalOpen] = useState(false);
  const [referenceNumber, setReferenceNumber] = useState('');
  const [bundleHash, setBundleHash] = useState('');
  const [copiedId, setCopiedId] = useState(false);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  // Update coordinates when police station changes
  const handlePoliceStationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const stName = e.target.value;
    setPoliceStation(stName);
    const found = DELHI_POLICE_STATIONS.find((s) => s.name === stName);
    if (found) {
      setLat(found.lat.toFixed(4));
      setLon(found.lon.toFixed(4));
    }
  };

  // Device GPS
  const handleUseGPS = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLat(pos.coords.latitude.toFixed(4));
          setLon(pos.coords.longitude.toFixed(4));
        },
        () => {
          setLat('28.6328');
          setLon('77.2197');
        }
      );
    }
  };

  // Process files with Web Crypto API SHA-256
  const handleFiles = async (files: FileList | File[]) => {
    setHashingInProgress(true);
    const newItems: EvidenceFileItem[] = [];

    for (const file of Array.from(files)) {
      try {
        const fullHash = await computeSha256(file);
        let previewUrl: string | undefined;
        if (file.type.startsWith('image/')) {
          previewUrl = URL.createObjectURL(file);
        }

        const now = new Date().toLocaleTimeString('en-IN', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        });

        newItems.push({
          id: `ev-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
          file,
          name: file.name,
          size: file.size,
          type: file.type || 'application/octet-stream',
          sha256: fullHash,
          truncatedSha: truncateString(fullHash, 10, 10),
          previewUrl,
          timestamp: now
        });
      } catch (err) {
        console.error('Failed to compute SHA-256 for file', file.name, err);
      }
    }

    setEvidenceFiles((prev) => [...prev, ...newItems]);
    setHashingInProgress(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  const removeEvidence = (id: string) => {
    setEvidenceFiles((prev) => prev.filter((item) => item.id !== id));
  };

  const copyToClipboard = (text: string, type: 'id' | string) => {
    navigator.clipboard.writeText(text);
    if (type === 'id') {
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2000);
    } else {
      setCopiedHash(type);
      setTimeout(() => setCopiedHash(null), 2000);
    }
  };

  // Form Submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!complainantName.trim() || !narrative.trim()) {
      alert('Please fill out Complainant Name and Incident Narrative.');
      return;
    }

    // Generate reference number DL-FIR-2026-XXXX
    const randomSuffix = Math.floor(1000 + Math.random() * 9000);
    const refNum = `DL-FIR-2026-${randomSuffix}`;
    setReferenceNumber(refNum);

    // Compute composite audit hash
    const compositePayload = JSON.stringify({
      refNum,
      name: complainantName,
      phone: phoneNumber,
      type: incidentType,
      date: incidentDate,
      time: incidentTime,
      station: policeStation,
      coords: `${lat}, ${lon}`,
      evidenceHashes: evidenceFiles.map((f) => f.sha256)
    });
    const encoder = new TextEncoder();
    const digestBuffer = await window.crypto.subtle.digest('SHA-256', encoder.encode(compositePayload));
    const digestArray = Array.from(new Uint8Array(digestBuffer));
    const digestHex = digestArray.map((b) => b.toString(16).padStart(2, '0')).join('');
    setBundleHash(digestHex);

    setSubmissionModalOpen(true);
  };

  const selectedOffenseObj = INCIDENT_TYPES.find((i) => i.id === incidentType) || INCIDENT_TYPES[0];

  return (
    <div className="space-y-6">
      
      {/* 1. DELHI POLICE DISCLAIMER BANNER (Requirement 2b) */}
      <div className="rounded-3xl p-5 border border-amber-500/30 bg-gradient-to-r from-amber-950/30 via-slate-900 to-black/60 shadow-2xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center shrink-0 mt-0.5">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono uppercase tracking-wider font-bold text-amber-300 bg-amber-950/80 px-2 py-0.5 rounded-full border border-amber-800/60">
                  STATUTORY NOTICE
                </span>
                <span className="text-xs font-semibold text-slate-300">
                  Sec 173 Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023
                </span>
              </div>
              <p className="text-xs text-slate-300 font-medium mt-1 leading-relaxed">
                For official legal filing under Sec 173 BNSS, visit{' '}
                <a
                  href="https://delhipolice.gov.in/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 underline hover:text-cyan-300 font-bold inline-flex items-center gap-1"
                >
                  Delhi Police Official Portal <ExternalLink className="w-3 h-3 inline" />
                </a>
                .
              </p>
            </div>
          </div>

          <span className="text-[10px] font-mono text-slate-400 bg-black/40 px-3 py-1.5 rounded-full border border-white/[0.08] shrink-0 self-start sm:self-auto">
            Simulated Prototype Module
          </span>
        </div>
      </div>

      {/* 2. MAIN E-FIR INPUT FORM (Requirement 2c, 2d, 2e) */}
      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* Section A: Complainant Details */}
        <div className="rounded-3xl p-6 sm:p-7 bg-slate-900/60 backdrop-blur-xl border border-white/[0.08] shadow-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center">
                <User className="w-4 h-4 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Complainant Details</h3>
                <p className="text-[11px] text-slate-400">Section 173 BNSS Complainant Record</p>
              </div>
            </div>
            <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2.5 py-1 rounded-full border border-cyan-800/40 font-bold">
              Verification Required
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">
                Complainant Full Name <span className="text-rose-400">*</span>
              </label>
              <input
                type="text"
                required
                value={complainantName}
                onChange={(e) => setComplainantName(e.target.value)}
                placeholder="e.g. Rahul Sharma"
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1.5">
                Phone Number (for SMS & Emergency Alerts) <span className="text-rose-400">*</span>
              </label>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="+91 98112 34567"
                  className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
                />
                <Phone className="w-4 h-4 text-slate-500 absolute right-3 top-3 pointer-events-none" />
              </div>
            </div>
          </div>
        </div>

        {/* Section B: Incident Information */}
        <div className="rounded-3xl p-6 sm:p-7 bg-slate-900/60 backdrop-blur-xl border border-white/[0.08] shadow-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-amber-950/80 border border-amber-800/60 flex items-center justify-center">
                <FileText className="w-4 h-4 text-amber-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Incident Information</h3>
                <p className="text-[11px] text-slate-400">Classified Offense & Chronological Timeline</p>
              </div>
            </div>
            <span className="text-[10px] font-mono text-amber-400 bg-amber-950/60 px-2.5 py-1 rounded-full border border-amber-800/40 font-bold">
              {selectedOffenseObj.bns}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Incident Type</label>
              <select
                value={incidentType}
                onChange={(e) => setIncidentType(e.target.value)}
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
              >
                {INCIDENT_TYPES.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.title} ({t.bns})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Incident Date</label>
              <input
                type="date"
                required
                value={incidentDate}
                onChange={(e) => setIncidentDate(e.target.value)}
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Incident Time</label>
              <input
                type="time"
                required
                value={incidentTime}
                onChange={(e) => setIncidentTime(e.target.value)}
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1.5">
              Narrative Description <span className="text-rose-400">*</span>
            </label>
            <textarea
              rows={4}
              required
              value={narrative}
              onChange={(e) => setNarrative(e.target.value)}
              placeholder="Provide chronological description of the event, physical features of suspects, vehicle models, or stolen property..."
              className="w-full bg-black/40 border border-white/[0.08] rounded-xl p-3.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors leading-relaxed"
            />
          </div>
        </div>

        {/* Section C: Jurisdiction & Location Coordinates */}
        <div className="rounded-3xl p-6 sm:p-7 bg-slate-900/60 backdrop-blur-xl border border-white/[0.08] shadow-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center">
                <MapPin className="w-4 h-4 text-emerald-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Jurisdiction & Location Coordinates</h3>
                <p className="text-[11px] text-slate-400">Delhi Police Station & Latitude/Longitude</p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleUseGPS}
              className="text-[11px] font-semibold text-cyan-300 hover:text-white bg-white/[0.06] hover:bg-white/[0.12] px-3 py-1.5 rounded-xl border border-white/[0.1] flex items-center gap-1.5 transition-all"
            >
              <Crosshair className="w-3.5 h-3.5 text-cyan-400" />
              <span>Use Current GPS</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Delhi Police Station</label>
              <select
                value={policeStation}
                onChange={handlePoliceStationChange}
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
              >
                {DELHI_POLICE_STATIONS.map((s) => (
                  <option key={s.name} value={s.name}>
                    {s.name} ({s.district} District)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Target Latitude (°N)</label>
              <input
                type="text"
                required
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Target Longitude (°E)</label>
              <input
                type="text"
                required
                value={lon}
                onChange={(e) => setLon(e.target.value)}
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>
          </div>
        </div>

        {/* Section D: Digital Evidence Vault & SHA-256 Hashing (Requirement 2d, 2e) */}
        <div className="rounded-3xl p-6 sm:p-7 bg-slate-900/60 backdrop-blur-xl border border-white/[0.08] shadow-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-indigo-950/80 border border-indigo-800/60 flex items-center justify-center">
                <Lock className="w-4 h-4 text-indigo-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Digital Evidence Vault</h3>
                <p className="text-[11px] text-slate-400">
                  Client-Side SHA-256 Hashing via Web Crypto API (Sec 63 BSA, 2023)
                </p>
              </div>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2.5 py-1 rounded-full border border-emerald-800/40 font-bold">
              Web Crypto Active
            </span>
          </div>

          {/* Drag and Drop Box */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-6 sm:p-8 text-center cursor-pointer transition-all ${
              isDragging
                ? 'border-cyan-400 bg-cyan-950/30'
                : 'border-white/[0.12] bg-black/40 hover:border-cyan-500/50 hover:bg-white/[0.02]'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={onFileChange}
              multiple
              accept="image/*,video/*"
              className="hidden"
            />
            <div className="flex flex-col items-center justify-center gap-2">
              <div className="w-12 h-12 rounded-2xl bg-cyan-950/60 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
                <UploadCloud className="w-6 h-6" />
              </div>
              <div className="text-xs font-bold text-white">
                {hashingInProgress ? 'Computing Web Crypto SHA-256 Hash...' : 'Drag & Drop Images and Videos, or Browse'}
              </div>
              <p className="text-[11px] text-slate-400 max-w-sm">
                Accepts camera photos, CCTV stills, or dashcam videos. Computes cryptographic digest instantly in browser.
              </p>
            </div>
          </div>

          {/* Evidence List with "Tamper-Proof Audit Hash Generated" Badge */}
          {evidenceFiles.length > 0 && (
            <div className="space-y-3 pt-2">
              <div className="text-xs font-bold text-slate-300">
                Processed Evidence Chain ({evidenceFiles.length} files)
              </div>

              <div className="space-y-2">
                {evidenceFiles.map((ev) => (
                  <div
                    key={ev.id}
                    className="p-3.5 rounded-2xl bg-black/50 border border-white/[0.08] flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      {ev.previewUrl ? (
                        <img
                          src={ev.previewUrl}
                          alt="Thumbnail"
                          className="w-10 h-10 rounded-xl object-cover border border-white/[0.1] shrink-0"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-xl bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center shrink-0">
                          {ev.type.startsWith('video') ? (
                            <Film className="w-5 h-5 text-cyan-400" />
                          ) : (
                            <ImageIcon className="w-5 h-5 text-cyan-400" />
                          )}
                        </div>
                      )}
                      <div className="min-w-0">
                        <div className="font-semibold text-white truncate max-w-xs">{ev.name}</div>
                        <div className="text-[10px] text-slate-400 font-mono">
                          {formatBytes(ev.size)} • {ev.timestamp}
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      {/* Tamper-Proof Audit Hash Generated Badge (Requirement 2e) */}
                      <span className="px-2.5 py-1 rounded-lg bg-emerald-950/70 border border-emerald-500/40 text-emerald-300 text-[10px] font-mono font-bold flex items-center gap-1.5 shadow-sm">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Tamper-Proof Audit Hash Generated</span>
                      </span>

                      {/* Display of resulting SHA-256 Hash Digest */}
                      <div className="px-2.5 py-1 rounded-lg bg-black/80 border border-white/[0.1] font-mono text-[11px] text-cyan-300 flex items-center gap-1.5">
                        <span className="text-slate-500 text-[10px]">SHA-256:</span>
                        <code title={ev.sha256} className="font-bold">
                          {ev.truncatedSha}
                        </code>
                        <button
                          type="button"
                          onClick={() => copyToClipboard(ev.sha256, ev.id)}
                          className="p-1 hover:text-white transition-colors"
                          title="Copy Full 64-char Hash"
                        >
                          {copiedHash === ev.id ? (
                            <Check className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <Copy className="w-3 h-3 text-slate-400" />
                          )}
                        </button>
                      </div>

                      <button
                        type="button"
                        onClick={() => removeEvidence(ev.id)}
                        className="p-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-900/40 border border-rose-800/40 text-rose-300 transition-all"
                        title="Remove evidence"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            className="w-full sm:w-auto px-8 py-3.5 rounded-full bg-gradient-to-r from-cyan-600 via-teal-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-black text-xs uppercase tracking-wider shadow-xl hover:shadow-cyan-500/25 transition-all flex items-center justify-center gap-2.5"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Submit e-FIR & Generate Audit Certificate</span>
          </button>
        </div>

      </form>

      {/* 3. MOCK CONFIRMATION MODAL (Requirement 2f) */}
      {submissionModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md">
          <div className="relative w-full max-w-2xl bg-[#0e121a] border border-white/[0.15] rounded-3xl shadow-2xl overflow-hidden text-slate-100 p-6 sm:p-8 space-y-6 animate-in fade-in zoom-in-95 duration-200">
            
            <button
              onClick={() => setSubmissionModalOpen(false)}
              className="absolute top-4 right-4 p-2 rounded-full bg-white/[0.06] hover:bg-white/[0.15] text-slate-400 hover:text-white transition-all"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Header */}
            <div className="flex items-center gap-3.5 border-b border-white/[0.08] pb-4">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/20 text-slate-950 font-black shrink-0">
                <CheckCircle2 className="w-6 h-6 text-slate-950" />
              </div>
              <div>
                <span className="text-[10px] font-mono tracking-widest uppercase text-emerald-400 font-bold bg-emerald-950/60 px-2.5 py-0.5 rounded-full border border-emerald-800/40">
                  CONFIRMATION ISSUED
                </span>
                <h3 className="text-xl font-black text-white mt-1">e-FIR Registration & Evidence Receipt</h3>
                <p className="text-xs text-slate-400">
                  Electronic First Information Report logged under Section 173 BNSS, 2023
                </p>
              </div>
            </div>

            {/* Reference Number Card */}
            <div className="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/30 flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase text-slate-400">Official Reference Number</span>
                <div className="font-mono text-2xl font-black text-emerald-400 tracking-wider mt-0.5">
                  {referenceNumber}
                </div>
              </div>
              <button
                type="button"
                onClick={() => copyToClipboard(referenceNumber, 'id')}
                className="px-3 py-1.5 rounded-xl bg-white/[0.08] hover:bg-white/[0.15] text-xs font-semibold text-white flex items-center gap-1.5 transition-all"
              >
                {copiedId ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedId ? 'Copied' : 'Copy Ref'}</span>
              </button>
            </div>

            {/* Computed Master Hash Digest */}
            <div className="p-4 rounded-2xl bg-black/50 border border-white/[0.08] space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono uppercase text-cyan-400 font-bold">
                  Computed Master SHA-256 Audit Hash Digest
                </span>
                <span className="text-[9px] font-mono text-slate-500">64-char Hexadecimal</span>
              </div>
              <code className="text-[11px] font-mono text-slate-200 break-all select-all block bg-black/60 p-2.5 rounded-xl border border-white/[0.06]">
                {bundleHash}
              </code>
            </div>

            {/* Incident Summary */}
            <div className="grid grid-cols-2 gap-3 text-xs bg-black/40 p-4 rounded-2xl border border-white/[0.06]">
              <div>
                <span className="text-slate-500 block">Complainant:</span>
                <span className="font-semibold text-white">{complainantName}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Contact Phone:</span>
                <span className="font-mono text-slate-300">{phoneNumber}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Jurisdiction:</span>
                <span className="font-semibold text-white">{policeStation}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Incident:</span>
                <span className="text-slate-300">{selectedOffenseObj.title}</span>
              </div>
              <div className="col-span-2 pt-2 border-t border-white/[0.06]">
                <span className="text-slate-500 block">Coordinates & Evidence:</span>
                <span className="text-slate-300 font-mono text-[11px]">
                  {lat}°N, {lon}°E • {evidenceFiles.length} Evidence objects hashed
                </span>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setSubmissionModalOpen(false)}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-bold text-xs transition-all shadow-md"
              >
                Done
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
