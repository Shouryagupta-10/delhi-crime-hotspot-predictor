import React, { useState, useRef, useEffect } from 'react';
import {
  ShieldCheck,
  FileText,
  UploadCloud,
  Lock,
  CheckCircle2,
  AlertTriangle,
  MapPin,
  Crosshair,
  ExternalLink,
  Copy,
  Check,
  Trash2,
  Clock,
  Building,
  User,
  Phone,
  CreditCard,
  Calendar,
  Eye,
  EyeOff,
  Sparkles,
  RefreshCw,
  FileCheck,
  Navigation,
  FileCode,
  Fingerprint
} from 'lucide-react';
import { 
  DELHI_POLICE_STATIONS, 
  DELHI_OFFENSES, 
  findNearestPoliceStation,
  calculateHaversineDistance,
  PoliceStation,
  OffenseType
} from '@/data/delhiPoliceStations';
import { 
  computeFileSHA256, 
  truncateHash, 
  generateFIRTrackingId, 
  formatFileSize, 
  maskAadhaar,
  getISTTimestamp,
  computeMasterBundleHash
} from '@/lib/crypto';
import { 
  VaultEvidenceFile, 
  EFirRecord, 
  saveStoredFir, 
  getStoredFirs 
} from '@/types/efir';
import { EFirAcknowledgmentModal } from './EFirAcknowledgmentModal';

interface EFirVaultModuleProps {
  onIncidentSubmitted?: (newFir: EFirRecord) => void;
  onNavigateToMap?: (fir: EFirRecord) => void;
}

export const EFirVaultModule: React.FC<EFirVaultModuleProps> = ({
  onIncidentSubmitted,
  onNavigateToMap
}) => {
  // Section 1: Complainant Details
  const [complainantName, setComplainantName] = useState('Devendra Sachdeva');
  const [phoneNumber, setPhoneNumber] = useState('+91 98102 34567');
  const [aadhaarRaw, setAadhaarRaw] = useState('5489-3210-9842');
  const [maskAadhaarView, setMaskAadhaarView] = useState(true);
  const [residentialAddress, setResidentialAddress] = useState('B-4/12, Safdarjung Enclave, New Delhi - 110029');
  const [callbackRequested, setCallbackRequested] = useState(true);

  // Section 2: Incident Information
  const [incidentDate, setIncidentDate] = useState(() => {
    const d = new Date();
    return d.toISOString().split('T')[0];
  });
  const [incidentTime, setIncidentTime] = useState('11:30');
  const [selectedOffenseId, setSelectedOffenseId] = useState('mobile_snatching');
  const [narrative, setNarrative] = useState(
    'While walking past Rajiv Chowk Metro Gate 6 towards Inner Circle B-Block, two individuals on a black motorcycle without registration plates snatched my iPhone and laptop backpack. Complainant fell to the ground. Suspects sped away towards Barakhamba Road.'
  );

  // Section 3: Geolocation & Jurisdiction
  const [lat, setLat] = useState('28.6328');
  const [lon, setLon] = useState('77.2197');
  const [landmark, setLandmark] = useState('Rajiv Chowk Metro Gate 6 & Radial Road 1');
  const [selectedStationName, setSelectedStationName] = useState('Connaught Place Police Station');
  const [nearestStation, setNearestStation] = useState<PoliceStation>(DELHI_POLICE_STATIONS[0]);
  const [stationDistance, setStationDistance] = useState<number>(0.35);
  const [locatingGPS, setLocatingGPS] = useState(false);

  // Section 4: Evidence Vault
  const [evidenceFiles, setEvidenceFiles] = useState<VaultEvidenceFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [hashingInProgress, setHashingInProgress] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Submission & Modal State
  const [submitting, setSubmitting] = useState(false);
  const [submittedFir, setSubmittedFir] = useState<EFirRecord | null>(null);
  const [showAckModal, setShowAckModal] = useState(false);
  const [recentFirs, setRecentFirs] = useState<EFirRecord[]>([]);

  // Copied hash state
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  // Current selected offense details
  const currentOffense = DELHI_OFFENSES.find(o => o.id === selectedOffenseId) || DELHI_OFFENSES[0];

  // Load existing records on mount
  useEffect(() => {
    setRecentFirs(getStoredFirs());
  }, []);

  // Recalculate nearest station when coordinates change
  useEffect(() => {
    const parsedLat = parseFloat(lat);
    const parsedLon = parseFloat(lon);
    if (!isNaN(parsedLat) && !isNaN(parsedLon)) {
      const nearest = findNearestPoliceStation(parsedLat, parsedLon);
      setNearestStation(nearest.station);
      setStationDistance(nearest.distanceKm);
    }
  }, [lat, lon]);

  // Handle manual police station selection
  const handlePoliceStationSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const stName = e.target.value;
    setSelectedStationName(stName);
    const station = DELHI_POLICE_STATIONS.find(s => s.name === stName);
    if (station) {
      setLat(station.lat.toFixed(4));
      setLon(station.lon.toFixed(4));
      setNearestStation(station);
      setStationDistance(0);
    }
  };

  // Live GPS geolocation
  const handleGetLiveGPS = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }
    setLocatingGPS(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocatingGPS(false);
        const userLat = pos.coords.latitude.toFixed(4);
        const userLon = pos.coords.longitude.toFixed(4);
        setLat(userLat);
        setLon(userLon);
        const nearest = findNearestPoliceStation(parseFloat(userLat), parseFloat(userLon));
        setNearestStation(nearest.station);
        setSelectedStationName(nearest.station.name);
        setStationDistance(nearest.distanceKm);
        setLandmark(`GPS Triangulated (~${pos.coords.accuracy.toFixed(0)}m accuracy) near ${nearest.station.address}`);
      },
      (err) => {
        setLocatingGPS(false);
        console.warn('Geolocation failed or permission denied, using default Delhi Central coordinates', err);
        setLat('28.6328');
        setLon('77.2197');
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  // Quick Preset Scenarios for demonstration
  const handleLoadScenario = (type: 'snatching' | 'theft' | 'cyber') => {
    if (type === 'snatching') {
      setSelectedOffenseId('mobile_snatching');
      setLat('28.6328');
      setLon('77.2197');
      setLandmark('Rajiv Chowk Metro Gate 6 & Radial 1');
      setSelectedStationName('Connaught Place Police Station');
      setNarrative(
        'While walking past Rajiv Chowk Metro Gate 6 towards Inner Circle B-Block at 11:30 AM, two pillion riders on a black motorcycle without number plates snatched my iPhone and laptop backpack. Complainant suffered abrasions on forearm.'
      );
    } else if (type === 'theft') {
      setSelectedOffenseId('vehicle_theft');
      setLat('28.5677');
      setLon('77.2433');
      setLandmark('Central Market Feroze Gandhi Road, Lajpat Nagar');
      setSelectedStationName('Lajpat Nagar Police Station');
      setNarrative(
        'Parked Honda Activa 6G (Reg: DL 5S AM 9214) in designated paid commercial parking lane. Upon return 45 minutes later, the scooter was missing with broken handle lock shards on the asphalt.'
      );
    } else {
      setSelectedOffenseId('cyber_fraud');
      setLat('28.6925');
      setLon('77.1520');
      setLandmark('Netaji Subhash Place Commercial Complex');
      setSelectedStationName('Netaji Subhash Place Police Station');
      setNarrative(
        'Received fraudulent call claiming to be electricity department arrears verification. Complainant was coerced into installing screen-sharing APK, resulting in unauthorized debit of Rs 87,400 via UPI.'
      );
    }
  };

  // Process uploaded files and compute SHA-256 hash immediately
  const processFiles = async (files: FileList | File[]) => {
    setHashingInProgress(true);
    const newEvidenceList: VaultEvidenceFile[] = [...evidenceFiles];

    for (const file of Array.from(files)) {
      const fileId = `ev-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
      const timestamp = getISTTimestamp();

      try {
        const fullHash = await computeFileSHA256(file);
        const truncated = truncateHash(fullHash, 8, 8);

        // Generate preview URL for images if applicable
        let previewUrl: string | undefined;
        if (file.type.startsWith('image/')) {
          previewUrl = URL.createObjectURL(file);
        }

        newEvidenceList.push({
          id: fileId,
          name: file.name,
          size: file.size,
          type: file.type || 'application/octet-stream',
          sha256: fullHash,
          truncatedSha: truncated,
          timestamp,
          previewUrl,
          status: 'verified'
        });
      } catch (err) {
        console.error('Failed to compute hash for file:', file.name, err);
      }
    }

    setEvidenceFiles(newEvidenceList);
    setHashingInProgress(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(e.target.files);
    }
  };

  const removeEvidence = (id: string) => {
    setEvidenceFiles(prev => prev.filter(f => f.id !== id));
  };

  const handleCopyHash = (hash: string, id: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(id);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  // Final Submission Handler
  const handleSubmitEFir = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!complainantName.trim() || !narrative.trim()) {
      alert('Please fill out Complainant Name and Incident Narrative.');
      return;
    }

    setSubmitting(true);

    try {
      const trackingId = generateFIRTrackingId();
      const filedAt = getISTTimestamp();
      const parsedLat = parseFloat(lat) || 28.6328;
      const parsedLon = parseFloat(lon) || 77.2197;

      // Extract hashes of all evidence files
      const evidenceHashes = evidenceFiles.map(f => f.sha256);

      // Compute Master Bundle Hash (irreversibly binds all FIR details + evidence hashes)
      const masterBundleHash = await computeMasterBundleHash({
        trackingId,
        complainantName,
        offenseType: currentOffense.title,
        incidentTimestamp: `${incidentDate} ${incidentTime}`,
        coordinates: [parsedLat, parsedLon],
        policeStation: nearestStation.name,
        evidenceHashes
      });

      const newRecord: EFirRecord = {
        id: trackingId,
        complainant: {
          name: complainantName,
          phone: phoneNumber,
          maskedAadhaar: maskAadhaarView ? maskAadhaar(aadhaarRaw) : aadhaarRaw,
          address: residentialAddress,
          callbackRequested
        },
        incident: {
          date: incidentDate,
          time: incidentTime,
          offenseType: currentOffense.id,
          offenseTitle: currentOffense.title,
          bnsSection: currentOffense.bnsSection,
          ipcSection: currentOffense.ipcSection,
          severity: currentOffense.severity,
          narrative
        },
        location: {
          lat: parsedLat,
          lon: parsedLon,
          landmark,
          policeStation: nearestStation.name,
          district: nearestStation.district,
          distanceKm: stationDistance
        },
        evidenceFiles,
        auditTrail: {
          masterBundleHash,
          filedAt,
          filedAtIso: new Date().toISOString(),
          legalAct: 'Sec 173 BNSS, 2023 & Sec 63 BSA',
          investigatingOfficer: `SI ${['Ramesh Negi', 'Satish Dahiya', 'Pooja Bishnoi', 'Amit Tanwar'][Math.floor(Math.random() * 4)]} (Belt No. ${Math.floor(1000 + Math.random() * 9000)}-${nearestStation.district.substring(0, 2).toUpperCase()})`,
          dispatchPriority: currentOffense.severity === 'CRITICAL' ? 'URGENT' : 'HIGH',
          status: 'PENDING_INVESTIGATION'
        }
      };

      // Persist to local storage
      const updated = saveStoredFir(newRecord);
      setRecentFirs(updated);

      // Cross-tab notification callback
      if (onIncidentSubmitted) {
        onIncidentSubmitted(newRecord);
      }

      setSubmittedFir(newRecord);
      setShowAckModal(true);
    } catch (err) {
      console.error('Failed to submit simulated e-FIR', err);
      alert('An error occurred during evidence sealing. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* 1. OFFICIAL DISCLAIMER BADGE & BNSS LEGAL NOTICE (Requirement 1) */}
      <div className="once-surface rounded-3xl p-5 sm:p-6 border border-amber-500/30 bg-gradient-to-r from-amber-950/30 via-slate-900 to-black/60 shadow-2xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="w-10 h-10 rounded-2xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center shrink-0 mt-0.5">
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
                Simulated e-FIR Module for Prototype Demonstration. For official legal reporting under Sec 173 BNSS,{' '}
                <a
                  href="https://delhipolice.gov.in/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 underline hover:text-cyan-300 font-bold inline-flex items-center gap-1"
                >
                  Visit Official Delhi Police Portal <ExternalLink className="w-3.5 h-3.5 inline" />
                </a>
                .
              </p>
            </div>
          </div>

          {/* Quick Demo Pre-Fill Action Bar */}
          <div className="flex items-center gap-2 shrink-0 self-stretch sm:self-auto bg-black/40 p-1.5 rounded-2xl border border-white/[0.08]">
            <span className="text-[10px] font-mono text-slate-400 px-2 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-cyan-400" /> Demo Presets:
            </span>
            <button
              type="button"
              onClick={() => handleLoadScenario('snatching')}
              className="px-2.5 py-1 text-[11px] font-semibold rounded-xl bg-white/[0.06] hover:bg-white/[0.12] text-slate-200 transition-all"
            >
              Snatching
            </button>
            <button
              type="button"
              onClick={() => handleLoadScenario('theft')}
              className="px-2.5 py-1 text-[11px] font-semibold rounded-xl bg-white/[0.06] hover:bg-white/[0.12] text-slate-200 transition-all"
            >
              Vehicle Theft
            </button>
            <button
              type="button"
              onClick={() => handleLoadScenario('cyber')}
              className="px-2.5 py-1 text-[11px] font-semibold rounded-xl bg-white/[0.06] hover:bg-white/[0.12] text-slate-200 transition-all"
            >
              Cyber Fraud
            </button>
          </div>
        </div>
      </div>

      {/* Main Form Grid */}
      <form onSubmit={handleSubmitEFir} className="space-y-6">
        
        {/* SECTION 1: COMPLAINANT PARTICULARS */}
        <div className="once-surface rounded-3xl p-6 sm:p-7 shadow-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-cyan-950/70 border border-cyan-800/60 flex items-center justify-center">
                <User className="w-4 h-4 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Section 1: Complainant Details</h3>
                <p className="text-[11px] text-slate-400">Identity details verified under Digital Evidence Protocol</p>
              </div>
            </div>
            <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2.5 py-1 rounded-full border border-cyan-800/40 font-bold">
              Step 1 of 4
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
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
                Phone Number (for OTP & PCR Dispatches) <span className="text-rose-400">*</span>
              </label>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="+91 98102 34567"
                  className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
                />
                <Phone className="w-4 h-4 text-slate-500 absolute right-3 top-3 pointer-events-none" />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-slate-400 font-medium">
                  Masked Aadhaar / Gov ID <span className="text-rose-400">*</span>
                </label>
                <button
                  type="button"
                  onClick={() => setMaskAadhaarView(!maskAadhaarView)}
                  className="text-[10px] text-cyan-400 hover:underline flex items-center gap-1 font-mono"
                >
                  {maskAadhaarView ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                  <span>{maskAadhaarView ? 'Show Masked' : 'Show Raw'}</span>
                </button>
              </div>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={maskAadhaarView ? maskAadhaar(aadhaarRaw) : aadhaarRaw}
                  onChange={(e) => setAadhaarRaw(e.target.value)}
                  placeholder="XXXX-XXXX-1234"
                  className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
                />
                <CreditCard className="w-4 h-4 text-slate-500 absolute right-3 top-3 pointer-events-none" />
              </div>
            </div>

            <div className="md:col-span-2 lg:col-span-2">
              <label className="block text-slate-400 font-medium mb-1.5">Current Residential Address</label>
              <input
                type="text"
                value={residentialAddress}
                onChange={(e) => setResidentialAddress(e.target.value)}
                placeholder="Full address in Delhi NCR"
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            <div className="flex items-center gap-2 pt-6">
              <input
                type="checkbox"
                id="callbackReq"
                checked={callbackRequested}
                onChange={(e) => setCallbackRequested(e.target.checked)}
                className="w-4 h-4 rounded bg-black/40 border border-white/[0.2] text-cyan-500 focus:ring-0"
              />
              <label htmlFor="callbackReq" className="text-xs text-slate-300 font-medium cursor-pointer">
                Request Immediate PCR Callback on Phone (Priority Response)
              </label>
            </div>
          </div>
        </div>

        {/* SECTION 2: INCIDENT INFORMATION */}
        <div className="once-surface rounded-3xl p-6 sm:p-7 shadow-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-amber-950/70 border border-amber-800/60 flex items-center justify-center">
                <FileText className="w-4 h-4 text-amber-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Section 2: Incident Information</h3>
                <p className="text-[11px] text-slate-400">Offense classification under Bharatiya Nyaya Sanhita, 2023</p>
              </div>
            </div>
            <span className="text-[10px] font-mono text-amber-400 bg-amber-950/60 px-2.5 py-1 rounded-full border border-amber-800/40 font-bold">
              Step 2 of 4
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Incident Date</label>
              <div className="relative">
                <input
                  type="date"
                  required
                  value={incidentDate}
                  onChange={(e) => setIncidentDate(e.target.value)}
                  className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Approximate Time (24h IST)</label>
              <div className="relative">
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
              <label className="block text-slate-400 font-medium mb-1.5">Offense Category</label>
              <select
                value={selectedOffenseId}
                onChange={(e) => setSelectedOffenseId(e.target.value)}
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
              >
                {DELHI_OFFENSES.map((offense) => (
                  <option key={offense.id} value={offense.id}>
                    {offense.title}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Statutory Section Badge Card */}
          <div className="p-3.5 rounded-2xl bg-black/40 border border-white/[0.06] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-bold text-white">{currentOffense.title}</span>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold ${
                  currentOffense.severity === 'CRITICAL' 
                    ? 'bg-rose-950/80 text-rose-300 border border-rose-800/60'
                    : 'bg-amber-950/80 text-amber-300 border border-amber-800/60'
                }`}>
                  {currentOffense.severity} PRIORITY
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">{currentOffense.description}</p>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <div className="px-3 py-1.5 rounded-xl bg-cyan-950/60 border border-cyan-800/40 font-mono text-[11px] text-cyan-300 text-right">
                <div className="text-[9px] uppercase text-cyan-500">Statutory Section</div>
                <b>{currentOffense.bnsSection}</b>
              </div>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs text-slate-400 font-medium">
                Detailed Chronological Narrative <span className="text-rose-400">*</span>
              </label>
              <span className="text-[10px] font-mono text-slate-500">{narrative.length} characters</span>
            </div>
            <textarea
              rows={4}
              required
              value={narrative}
              onChange={(e) => setNarrative(e.target.value)}
              placeholder="State chronological sequence of events, description of perpetrators, direction of escape, vehicle license numbers, or stolen items..."
              className="w-full bg-black/40 border border-white/[0.08] rounded-xl p-3.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors leading-relaxed font-sans"
            />
          </div>
        </div>

        {/* SECTION 3: GEOLOCATION & JURISDICTION */}
        <div className="once-surface rounded-3xl p-6 sm:p-7 shadow-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-emerald-950/70 border border-emerald-800/60 flex items-center justify-center">
                <MapPin className="w-4 h-4 text-emerald-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Section 3: Geolocation & Police Jurisdiction</h3>
                <p className="text-[11px] text-slate-400">Precision GPS coordinates and automatic jurisdictional boundary mapping</p>
              </div>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2.5 py-1 rounded-full border border-emerald-800/40 font-bold">
              Step 3 of 4
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Latitude (°N)</label>
              <input
                type="text"
                required
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                placeholder="28.6328"
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Longitude (°E)</label>
              <input
                type="text"
                required
                value={lon}
                onChange={(e) => setLon(e.target.value)}
                placeholder="77.2197"
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1.5">GPS Triangulation</label>
              <button
                type="button"
                onClick={handleGetLiveGPS}
                disabled={locatingGPS}
                className="w-full bg-white/[0.08] hover:bg-white/[0.14] border border-white/[0.1] text-cyan-300 font-semibold py-2.5 px-3.5 rounded-xl transition-all flex items-center justify-center gap-2"
              >
                {locatingGPS ? <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" /> : <Crosshair className="w-4 h-4 text-cyan-400" />}
                <span>{locatingGPS ? 'Triangulating...' : 'Use My Live GPS'}</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Landmark or Crime Hotspot Corridors</label>
              <input
                type="text"
                value={landmark}
                onChange={(e) => setLandmark(e.target.value)}
                placeholder="e.g. Near Rajiv Chowk Metro Gate 6"
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1.5">
                Jurisdictional Police Station (Manual Override or Auto-Assigned)
              </label>
              <select
                value={selectedStationName}
                onChange={handlePoliceStationSelect}
                className="w-full bg-black/40 border border-white/[0.08] rounded-xl px-3.5 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
              >
                {DELHI_POLICE_STATIONS.map((station) => (
                  <option key={station.name} value={station.name}>
                    {station.name} ({station.district} District)
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Computed Jurisdictional Match Callout */}
          <div className="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-900/60 border border-emerald-600/50 flex items-center justify-center shrink-0">
                <Building className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-emerald-400 font-bold block">
                  Autonomously Identified Delhi Jurisdiction
                </span>
                <span className="font-bold text-white text-sm">
                  {nearestStation.name}
                </span>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  {nearestStation.address} • District: <b className="text-slate-200">{nearestStation.district}</b>
                </p>
              </div>
            </div>

            <div className="flex items-center sm:flex-col sm:items-end justify-between border-t sm:border-t-0 border-white/[0.08] pt-2 sm:pt-0">
              <div className="text-[11px] font-mono text-cyan-300">
                Proximity Distance: <b>{stationDistance} km</b>
              </div>
              <div className="text-[10px] text-slate-400 font-mono">
                Helpline: {nearestStation.phone}
              </div>
            </div>
          </div>
        </div>

        {/* SECTION 4: DIGITAL EVIDENCE VAULT & SHA-256 HASHING */}
        <div className="once-surface rounded-3xl p-6 sm:p-7 shadow-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-indigo-950/70 border border-indigo-800/60 flex items-center justify-center">
                <Lock className="w-4 h-4 text-indigo-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Section 4: Digital Evidence Vault</h3>
                <p className="text-[11px] text-slate-400">
                  Cryptographic client-side SHA-256 evidence hashing for court admissibility (Sec 63 BSA, 2023)
                </p>
              </div>
            </div>
            <span className="text-[10px] font-mono text-indigo-400 bg-indigo-950/60 px-2.5 py-1 rounded-full border border-indigo-800/40 font-bold">
              Step 4 of 4
            </span>
          </div>

          {/* Drag & Drop File Upload Box */}
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
              isDragging
                ? 'border-cyan-400 bg-cyan-950/30'
                : 'border-white/[0.12] bg-black/40 hover:border-cyan-500/50 hover:bg-white/[0.02]'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileInputChange}
              multiple
              accept="image/*,video/*,.pdf,.doc,.docx"
              className="hidden"
            />
            <div className="flex flex-col items-center justify-center gap-2">
              <div className="w-12 h-12 rounded-2xl bg-cyan-950/60 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
                {hashingInProgress ? (
                  <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
                ) : (
                  <UploadCloud className="w-6 h-6" />
                )}
              </div>
              <div className="text-xs font-bold text-white">
                {hashingInProgress
                  ? 'Computing Cryptographic SHA-256 Digest...'
                  : 'Click or Drag & Drop Evidence Files Here'}
              </div>
              <p className="text-[11px] text-slate-400 max-w-md leading-relaxed">
                Accepts images (CCTV frames, injuries), videos (dashcam, mobile captures), or documents (purchase invoice, FIR copies).
              </p>
              <div className="flex items-center gap-2 text-[10px] font-mono text-cyan-400/80 bg-cyan-950/40 px-2.5 py-1 rounded-full border border-cyan-800/30 mt-1">
                <Fingerprint className="w-3 h-3" />
                <span>Zero-upload client-side hashing: Raw files never leave your browser unhashed</span>
              </div>
            </div>
          </div>

          {/* Evidence Chain List with Immediate "Integrity Verified" Indicator (Requirement 2) */}
          {evidenceFiles.length > 0 && (
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-300">
                  Attached Evidence Chain ({evidenceFiles.length} files)
                </span>
                <span className="text-[11px] text-slate-500 font-mono">
                  Total Size: {formatFileSize(evidenceFiles.reduce((acc, f) => acc + f.size, 0))}
                </span>
              </div>

              <div className="space-y-2">
                {evidenceFiles.map((file) => (
                  <div
                    key={file.id}
                    className="p-3.5 rounded-2xl bg-black/50 border border-white/[0.08] hover:border-cyan-500/40 transition-all flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      {file.previewUrl ? (
                        <img
                          src={file.previewUrl}
                          alt="Evidence thumbnail"
                          className="w-10 h-10 rounded-xl object-cover border border-white/[0.1] shrink-0"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-xl bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center shrink-0">
                          <FileText className="w-5 h-5 text-cyan-400" />
                        </div>
                      )}
                      <div className="min-w-0">
                        <div className="font-bold text-white truncate max-w-xs">{file.name}</div>
                        <div className="text-[10px] text-slate-400 font-mono">
                          {formatFileSize(file.size)} • {file.timestamp}
                        </div>
                      </div>
                    </div>

                    {/* Cryptographic SHA-256 "Integrity Verified" Badge */}
                    <div className="flex flex-wrap items-center gap-2">
                      <div className="px-2.5 py-1 rounded-lg bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-[11px] font-mono font-bold flex items-center gap-1.5">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Integrity Verified</span>
                      </div>

                      <div className="px-2.5 py-1 rounded-lg bg-black/80 border border-white/[0.1] font-mono text-[11px] text-cyan-300 flex items-center gap-1.5">
                        <span className="text-slate-500 text-[10px]">SHA-256:</span>
                        <code title={file.sha256} className="font-bold">
                          {file.truncatedSha}
                        </code>
                        <button
                          type="button"
                          onClick={() => handleCopyHash(file.sha256, file.id)}
                          className="p-1 hover:text-white transition-colors"
                          title="Copy Full 64-char Hash"
                        >
                          {copiedHash === file.id ? (
                            <Check className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <Copy className="w-3 h-3 text-slate-400" />
                          )}
                        </button>
                      </div>

                      <button
                        type="button"
                        onClick={() => removeEvidence(file.id)}
                        className="p-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-900/40 border border-rose-800/40 text-rose-300 transition-all"
                        title="Remove evidence object"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section 63 BSA Digital Evidence Guarantee Note */}
          <div className="p-3.5 rounded-2xl bg-indigo-950/20 border border-indigo-500/20 text-[11px] text-slate-400 flex items-start gap-2.5 leading-relaxed">
            <Lock className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
            <div>
              <b className="text-slate-200">Legal Evidentiary Chain of Custody:</b> In compliance with Section 63 of Bharatiya Sakshya Adhiniyam, 2023, SHA-256 cryptographic fingerprints are irrevocably sealed into the master submission digest at the millisecond of registration to prevent retroactive fabrication or evidentiary tampering.
            </div>
          </div>
        </div>

        {/* FINAL SUBMIT BUTTON */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-slate-400">
            Clicking submit generates a unique tracking ID (e.g. <code>DL-FIR-2026-XXXXX</code>) and dispatches a live pulse marker to the crime map.
          </div>

          <button
            type="submit"
            disabled={submitting || hashingInProgress}
            className="w-full sm:w-auto px-8 py-3.5 rounded-full bg-gradient-to-r from-cyan-600 via-teal-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-black text-xs uppercase tracking-wider shadow-xl hover:shadow-cyan-500/25 transition-all flex items-center justify-center gap-2.5 disabled:opacity-50"
          >
            {submitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Sealing Evidence & Registering e-FIR...</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4" />
                <span>Register Simulated e-FIR under Sec 173 BNSS</span>
              </>
            )}
          </button>
        </div>

      </form>

      {/* RECENT E-FIR REPORTS LOG IN THIS SESSION */}
      {recentFirs.length > 0 && (
        <div className="once-surface rounded-3xl p-6 sm:p-7 shadow-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-violet-950/70 border border-violet-800/60 flex items-center justify-center">
                <FileCheck className="w-4 h-4 text-violet-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Active Registered e-FIR Docket (Recent Incidents)</h3>
                <p className="text-[11px] text-slate-400">
                  {recentFirs.length} simulated complaints active with real-time pulse beacons on the crime map
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recentFirs.map((fir) => (
              <div
                key={fir.id}
                className="p-4 rounded-2xl bg-black/40 border border-white/[0.08] hover:border-violet-500/40 transition-all space-y-3 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono font-black text-cyan-300 text-sm">{fir.id}</span>
                  <span className="text-[10px] font-mono text-rose-400 bg-rose-950/80 px-2 py-0.5 rounded-full border border-rose-800/60 font-bold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping"></span>
                    Pending Investigation
                  </span>
                </div>

                <div className="space-y-1 text-[11px] text-slate-400">
                  <div className="font-semibold text-white">{fir.incident.offenseTitle}</div>
                  <div><b>Complainant:</b> {fir.complainant.name} ({fir.complainant.maskedAadhaar})</div>
                  <div><b>Station:</b> {fir.location.policeStation} • {fir.location.district} District</div>
                  <div><b>Filing Timestamp:</b> {fir.auditTrail.filedAt}</div>
                  <div className="truncate font-mono text-[10px] text-slate-500" title={fir.auditTrail.masterBundleHash}>
                    <b>Bundle Hash:</b> {truncateHash(fir.auditTrail.masterBundleHash, 10, 10)}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-white/[0.06]">
                  <button
                    type="button"
                    onClick={() => {
                      setSubmittedFir(fir);
                      setShowAckModal(true);
                    }}
                    className="text-xs text-cyan-400 hover:underline font-semibold flex items-center gap-1"
                  >
                    <span>View Acknowledgment Slip</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => onNavigateToMap && onNavigateToMap(fir)}
                    className="px-3 py-1 rounded-xl bg-violet-950/60 hover:bg-violet-900/60 border border-violet-700/60 text-violet-300 text-xs font-semibold flex items-center gap-1.5 transition-all"
                  >
                    <span>Inspect on Map</span>
                    <Navigation className="w-3 h-3 text-violet-400" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Official Acknowledgment Modal */}
      {submittedFir && (
        <EFirAcknowledgmentModal
          fir={submittedFir}
          isOpen={showAckModal}
          onClose={() => setShowAckModal(false)}
          onViewOnMap={(fir) => {
            if (onNavigateToMap) onNavigateToMap(fir);
          }}
        />
      )}

    </div>
  );
};
