import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Download, 
  Printer, 
  MapPin, 
  Copy, 
  Check, 
  ExternalLink, 
  FileText, 
  Lock, 
  Clock, 
  Building2, 
  UserCheck, 
  QrCode, 
  X,
  AlertCircle
} from 'lucide-react';
import { EFirRecord } from '@/types/efir';
import { truncateHash } from '@/lib/crypto';

interface EFirAcknowledgmentModalProps {
  fir: EFirRecord;
  isOpen: boolean;
  onClose: () => void;
  onViewOnMap: (fir: EFirRecord) => void;
}

export const EFirAcknowledgmentModal: React.FC<EFirAcknowledgmentModalProps> = ({
  fir,
  isOpen,
  onClose,
  onViewOnMap
}) => {
  const [copiedMaster, setCopiedMaster] = useState(false);
  const [copiedId, setCopiedId] = useState(false);
  const [copiedHashId, setCopiedHashId] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleCopy = (text: string, type: 'id' | 'master' | string) => {
    navigator.clipboard.writeText(text);
    if (type === 'id') {
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2000);
    } else if (type === 'master') {
      setCopiedMaster(true);
      setTimeout(() => setCopiedMaster(false), 2000);
    } else {
      setCopiedHashId(type);
      setTimeout(() => setCopiedHashId(null), 2000);
    }
  };

  const handleDownloadSlip = () => {
    const textContent = `
================================================================================
                    DELHI POLICE • CRIME REPORTING PORTAL
       DIGITAL e-FIR REGISTRATION ACKNOWLEDGMENT & EVIDENCE CUSTODY RECEIPT
            Generated under Sec 173 BNSS, 2023 & Sec 63 BSA, 2023
================================================================================

REGISTRATION IDENTIFIER : ${fir.id}
FILING TIMESTAMP        : ${fir.auditTrail.filedAt}
JURISDICTIONAL STATUS   : PENDING INVESTIGATION (Beat Officer Dispatched)
STATUTORY COMPLIANCE    : ${fir.auditTrail.legalAct}

--- COMPLAINANT PARTICULARS ---
Name                  : ${fir.complainant.name}
Phone                 : ${fir.complainant.phone}
Government ID / UID   : ${fir.complainant.maskedAadhaar}
Current Address       : ${fir.complainant.address}

--- INCIDENT PARTICULARS ---
Date & Time of Offense: ${fir.incident.date} at ${fir.incident.time} IST
Offense Classification: ${fir.incident.offenseTitle}
Statutory Section     : ${fir.incident.bnsSection} (Equivalent: ${fir.incident.ipcSection})
Location Coordinates  : ${fir.location.lat.toFixed(5)}°N, ${fir.location.lon.toFixed(5)}°E
Landmark / Corridors  : ${fir.location.landmark}
Jurisdictional Station: ${fir.location.policeStation} (${fir.location.district} District)
Assigned Beat Officer : ${fir.auditTrail.investigatingOfficer}

--- SUMMARY OF OCCURRENCE ---
${fir.incident.narrative}

--- CRYPTOGRAPHIC EVIDENCE CHAIN OF CUSTODY (SHA-256) ---
${fir.evidenceFiles.length === 0 ? "No digital evidence files attached during initial registration." : fir.evidenceFiles.map((f, i) => `
Evidence File #${i + 1}:
  Filename    : ${f.name}
  MIME Type   : ${f.type}
  Size        : ${f.size} bytes
  Timestamp   : ${f.timestamp}
  SHA-256 Hash: ${f.sha256}
`).join('\n')}

MASTER BUNDLE HASH (SHA-256):
${fir.auditTrail.masterBundleHash}

--------------------------------------------------------------------------------
NOTICE: This is a system-generated electronic document verifying submission
of an e-FIR for cognizable/non-cognizable offenses under BNSS, 2023.
Tampering with or altering digital evidence hashes is punishable by law.
================================================================================
    `.trim();

    const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `DELHI_POLICE_eFIR_${fir.id}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-4xl my-auto bg-[#0d1117] border border-white/[0.15] rounded-3xl shadow-2xl overflow-hidden text-slate-100 animate-in fade-in zoom-in-95 duration-200">
        
        {/* Top Header Banner with Police Emblem */}
        <div className="relative bg-gradient-to-r from-blue-950/80 via-indigo-950/70 to-slate-900 border-b border-white/[0.12] p-5 sm:p-6">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-full bg-white/[0.06] hover:bg-white/[0.15] text-slate-400 hover:text-white transition-all"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-400 via-amber-500 to-yellow-600 flex items-center justify-center shadow-lg shadow-amber-500/20 border border-amber-300/40 shrink-0">
                <span className="text-2xl">🛡️</span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-mono tracking-widest uppercase text-cyan-400 font-bold bg-cyan-950/60 px-2.5 py-0.5 rounded-full border border-cyan-800/40">
                    DELHI POLICE • e-FIR CELL
                  </span>
                  <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-800/40 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    E-SEALED
                  </span>
                </div>
                <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight mt-1">
                  Official Registration Acknowledgment Slip
                </h2>
                <p className="text-xs text-slate-400">
                  Electronic First Information Report under Sec 173 BNSS, 2023 & Sec 63 BSA Digital Admissibility
                </p>
              </div>
            </div>

            {/* Quick Action Buttons */}
            <div className="flex items-center gap-2 self-stretch sm:self-auto">
              <button
                onClick={handleDownloadSlip}
                className="flex-1 sm:flex-none px-3.5 py-2 rounded-xl bg-white/[0.08] hover:bg-white/[0.15] border border-white/[0.12] text-xs font-semibold text-white flex items-center justify-center gap-1.5 transition-all"
              >
                <Download className="w-3.5 h-3.5 text-cyan-400" />
                <span>Save Receipt</span>
              </button>

              <button
                onClick={handlePrint}
                className="px-3 py-2 rounded-xl bg-white/[0.08] hover:bg-white/[0.15] border border-white/[0.12] text-xs font-semibold text-white flex items-center justify-center gap-1.5 transition-all hidden sm:flex"
              >
                <Printer className="w-3.5 h-3.5 text-slate-300" />
                <span>Print</span>
              </button>
            </div>
          </div>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-5 sm:p-7 space-y-6 max-h-[75vh] overflow-y-auto">
          
          {/* Tracking ID & Status Banner */}
          <div className="rounded-2xl p-4 sm:p-5 bg-gradient-to-r from-emerald-950/30 via-slate-900 to-indigo-950/30 border border-emerald-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">Unique Tracking Identifier</span>
              <div className="flex items-center gap-2.5 mt-0.5">
                <span className="font-mono text-xl sm:text-2xl font-black text-emerald-400 tracking-wider">
                  {fir.id}
                </span>
                <button
                  onClick={() => handleCopy(fir.id, 'id')}
                  className="p-1.5 rounded-lg bg-white/[0.06] hover:bg-white/[0.12] text-slate-400 hover:text-white transition-all text-xs flex items-center gap-1"
                  title="Copy Tracking ID"
                >
                  {copiedId ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
              <div className="text-xs text-slate-400 mt-1 flex items-center gap-2">
                <Clock className="w-3 h-3 text-slate-500" />
                <span>Filing Timestamp: <b>{fir.auditTrail.filedAt}</b></span>
              </div>
            </div>

            <div className="flex flex-col md:items-end gap-1.5 border-t md:border-t-0 border-white/[0.08] pt-3 md:pt-0">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping"></span>
                <span className="text-xs font-mono font-bold text-rose-400 uppercase tracking-wide">
                  Pending Investigation
                </span>
              </div>
              <div className="text-[11px] text-slate-400 font-mono">
                Jurisdiction: <span className="text-slate-200">{fir.location.policeStation}</span>
              </div>
              <div className="text-[11px] text-cyan-400 font-mono">
                Assigned IO: <span className="text-slate-300">{fir.auditTrail.investigatingOfficer}</span>
              </div>
            </div>
          </div>

          {/* Complainant & Incident Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            
            {/* Box 1: Complainant Details */}
            <div className="rounded-2xl p-4 bg-black/40 border border-white/[0.08] space-y-2.5">
              <div className="flex items-center gap-2 text-cyan-400 font-bold border-b border-white/[0.06] pb-2">
                <UserCheck className="w-4 h-4" />
                <span>Complainant Details (Sec 173 BNSS)</span>
              </div>
              <div className="space-y-1.5 text-slate-300">
                <div className="flex justify-between">
                  <span className="text-slate-500">Complainant Name:</span>
                  <span className="font-semibold text-white">{fir.complainant.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Contact Number:</span>
                  <span className="font-mono text-slate-200">{fir.complainant.phone}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Masked ID / Aadhaar:</span>
                  <span className="font-mono text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-800/40">
                    {fir.complainant.maskedAadhaar}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Current Address:</span>
                  <span className="text-right max-w-[200px] text-slate-300 truncate" title={fir.complainant.address}>
                    {fir.complainant.address}
                  </span>
                </div>
              </div>
            </div>

            {/* Box 2: Incident Particulars */}
            <div className="rounded-2xl p-4 bg-black/40 border border-white/[0.08] space-y-2.5">
              <div className="flex items-center gap-2 text-amber-400 font-bold border-b border-white/[0.06] pb-2">
                <Building2 className="w-4 h-4" />
                <span>Incident Classification & Jurisdiction</span>
              </div>
              <div className="space-y-1.5 text-slate-300">
                <div className="flex justify-between">
                  <span className="text-slate-500">Offense Type:</span>
                  <span className="font-semibold text-amber-300">{fir.incident.offenseTitle}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Statutory Sanhita:</span>
                  <span className="font-mono text-slate-200">{fir.incident.bnsSection} ({fir.incident.ipcSection})</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Occurrence Time:</span>
                  <span className="font-mono text-slate-200">{fir.incident.date} at {fir.incident.time} IST</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Nearest Station:</span>
                  <span className="font-semibold text-white">{fir.location.policeStation} ({fir.location.distanceKm} km)</span>
                </div>
              </div>
            </div>

          </div>

          {/* Incident Narrative */}
          <div className="rounded-2xl p-4 bg-black/40 border border-white/[0.08] space-y-2">
            <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block font-bold">
              Occurrence Narrative & Chronological Summary
            </span>
            <p className="text-xs text-slate-200 leading-relaxed bg-black/30 p-3 rounded-xl border border-white/[0.04] italic">
              "{fir.incident.narrative}"
            </p>
            <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 font-mono">
              <span>Geo-Coordinates: {fir.location.lat.toFixed(5)}°N, {fir.location.lon.toFixed(5)}°E</span>
              <span>Landmark: {fir.location.landmark}</span>
            </div>
          </div>

          {/* Cryptographic Evidence Vault Section */}
          <div className="rounded-2xl p-4 sm:p-5 bg-gradient-to-b from-indigo-950/20 via-black/40 to-black/60 border border-indigo-500/20 space-y-3">
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-2.5">
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4 text-cyan-400" />
                <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                  Digital Evidence Vault (SHA-256 Chain of Custody)
                </h4>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded-full border border-emerald-800/50">
                {fir.evidenceFiles.length} Evidence Objects Sealed
              </span>
            </div>

            {fir.evidenceFiles.length === 0 ? (
              <p className="text-xs text-slate-400 italic py-2">
                No initial digital files uploaded. Secondary evidence may be submitted to the IO during physical inquiry.
              </p>
            ) : (
              <div className="space-y-2">
                {fir.evidenceFiles.map((file, idx) => (
                  <div
                    key={file.id}
                    className="p-3 rounded-xl bg-black/50 border border-white/[0.06] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-7 h-7 rounded-lg bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center shrink-0">
                        <FileText className="w-3.5 h-3.5 text-cyan-400" />
                      </div>
                      <div className="min-w-0">
                        <div className="font-semibold text-slate-200 truncate">{file.name}</div>
                        <div className="text-[10px] text-slate-400 font-mono">
                          {(file.size / 1024).toFixed(1)} KB • {file.timestamp}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 bg-black/60 px-2.5 py-1.5 rounded-lg border border-white/[0.06] font-mono text-[11px]">
                      <span className="text-slate-500 text-[10px]">SHA-256:</span>
                      <code className="text-cyan-300 font-bold" title={file.sha256}>
                        {file.truncatedSha}
                      </code>
                      <button
                        onClick={() => handleCopy(file.sha256, file.id)}
                        className="text-slate-400 hover:text-white transition-colors"
                        title="Copy full 64-character SHA-256"
                      >
                        {copiedHashId === file.id ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Master Bundle Hash Verification Stamp */}
            <div className="p-3.5 rounded-xl bg-black/70 border border-emerald-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5">
              <div>
                <span className="text-[10px] font-mono uppercase text-emerald-400 font-bold block">
                  Master Evidence Bundle Digest (Section 63 BSA Hash Stamp)
                </span>
                <code className="text-[11px] font-mono text-slate-200 break-all select-all block mt-0.5">
                  {fir.auditTrail.masterBundleHash}
                </code>
              </div>
              <button
                onClick={() => handleCopy(fir.auditTrail.masterBundleHash, 'master')}
                className="px-2.5 py-1.5 rounded-lg bg-emerald-950/60 hover:bg-emerald-900/60 border border-emerald-700/60 text-emerald-300 text-xs font-mono flex items-center gap-1.5 shrink-0 transition-all"
              >
                {copiedMaster ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                <span>{copiedMaster ? 'Copied' : 'Copy Hash'}</span>
              </button>
            </div>
          </div>

          {/* Map Plotting Callout */}
          <div className="p-4 rounded-2xl bg-gradient-to-r from-violet-950/40 via-purple-950/30 to-slate-900 border border-violet-500/30 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-violet-600/20 border border-violet-500/40 flex items-center justify-center shrink-0">
                <MapPin className="w-5 h-5 text-violet-400" />
              </div>
              <div>
                <div className="font-bold text-white flex items-center gap-1.5">
                  <span>Incident Plotted on Live Crime Sentinel Map</span>
                  <span className="w-2 h-2 rounded-full bg-violet-400 animate-ping"></span>
                </div>
                <p className="text-slate-400 text-[11px] mt-0.5">
                  A high-priority real-time "Pending Investigation" pulse beacon has been dispatched to the hotspot analysis tab.
                </p>
              </div>
            </div>

            <button
              onClick={() => {
                onViewOnMap(fir);
                onClose();
              }}
              className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-violet-950/50 transition-all shrink-0"
            >
              <span>View Pulse on Map</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="bg-[#090b10] border-t border-white/[0.08] px-5 sm:px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 text-slate-400 text-[11px]">
            <AlertCircle className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>Official Legal Reporting: If you require statutory summons, visit your local Police Station.</span>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-white/[0.08] hover:bg-white/[0.12] text-white font-semibold transition-all"
            >
              Close
            </button>
            <button
              onClick={() => {
                onViewOnMap(fir);
                onClose();
              }}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-bold transition-all shadow-md"
            >
              Open Live Crime Map
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
