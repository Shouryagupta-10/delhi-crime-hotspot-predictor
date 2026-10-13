/**
 * Type definitions and storage state manager for e-FIR & Digital Evidence Vault
 */

export interface VaultEvidenceFile {
  id: string;
  name: string;
  size: number;
  type: string;
  sha256: string;
  truncatedSha: string;
  timestamp: string;
  previewUrl?: string;
  status: 'hashing' | 'verified' | 'error';
}

export interface EFirComplainant {
  name: string;
  phone: string;
  maskedAadhaar: string;
  address: string;
  callbackRequested?: boolean;
}

export interface EFirIncident {
  date: string;
  time: string;
  offenseType: string;
  offenseTitle: string;
  bnsSection: string;
  ipcSection: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  narrative: string;
}

export interface EFirLocation {
  lat: number;
  lon: number;
  landmark: string;
  policeStation: string;
  district: string;
  distanceKm: number;
}

export interface EFirAuditTrail {
  masterBundleHash: string;
  filedAt: string;
  filedAtIso: string;
  legalAct: string;
  investigatingOfficer: string;
  dispatchPriority: 'URGENT' | 'HIGH' | 'STANDARD';
  status: 'PENDING_INVESTIGATION' | 'ASSIGNED' | 'EVIDENCE_SEALED';
}

export interface EFirRecord {
  id: string;
  complainant: EFirComplainant;
  incident: EFirIncident;
  location: EFirLocation;
  evidenceFiles: VaultEvidenceFile[];
  auditTrail: EFirAuditTrail;
}

const STORAGE_KEY = 'rakshak_efir_registry_v1';

export const INITIAL_MOCK_FIRS: EFirRecord[] = [
  {
    id: 'DL-FIR-2026-48912',
    complainant: {
      name: 'Aditya Vardhan Sharma',
      phone: '+91 98114 28491',
      maskedAadhaar: 'XXXX-XXXX-4819',
      address: 'Flat 402, Barakhamba Towers, Connaught Place, New Delhi',
      callbackRequested: true
    },
    incident: {
      date: '2026-10-12',
      time: '20:45',
      offenseType: 'mobile_snatching',
      offenseTitle: 'Mobile / Chain Snatching (Sudden Force Egress)',
      bnsSection: 'Section 304 BNS',
      ipcSection: 'IPC 392',
      severity: 'CRITICAL',
      narrative: 'While exiting Rajiv Chowk Metro Gate 7 towards Radial Road 2, two unidentified pillion riders on a black Pulsar motorcycle snatched my iPhone 15 Pro and accelerated towards Kasturba Gandhi Marg. Complainant sustained minor wrist abrasions.',
    },
    location: {
      lat: 28.6328,
      lon: 77.2197,
      landmark: 'Rajiv Chowk Metro Gate 7, Radial 2',
      policeStation: 'Connaught Place Police Station',
      district: 'New Delhi',
      distanceKm: 0.35
    },
    evidenceFiles: [
      {
        id: 'ev-1',
        name: 'cctv_snatch_clip_rad2.mp4',
        size: 14205800,
        type: 'video/mp4',
        sha256: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
        truncatedSha: '9f86d081...b0f00a08',
        timestamp: '12 Oct 2026, 09:12 PM IST',
        status: 'verified'
      },
      {
        id: 'ev-2',
        name: 'apple_imei_invoice.pdf',
        size: 245100,
        type: 'application/pdf',
        sha256: '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
        truncatedSha: '5e884898...1d1542d8',
        timestamp: '12 Oct 2026, 09:14 PM IST',
        status: 'verified'
      }
    ],
    auditTrail: {
      masterBundleHash: 'b4a8e2d7658931b209e53f7c118e9a2637f9411dc821b02938a49c6123498afe',
      filedAt: '12 Oct 2026, 09:20 PM IST',
      filedAtIso: '2026-10-12T15:50:00.000Z',
      legalAct: 'Sec 173 BNSS, 2023 & Sec 63 BSA',
      investigatingOfficer: 'SI Rajesh Dahiya (Belt No. 8941-ND)',
      dispatchPriority: 'URGENT',
      status: 'PENDING_INVESTIGATION'
    }
  },
  {
    id: 'DL-FIR-2026-92147',
    complainant: {
      name: 'Pooja Narang',
      phone: '+91 97180 54312',
      maskedAadhaar: 'XXXX-XXXX-9124',
      address: 'C-34, Lajpat Nagar IV, South-East Delhi',
      callbackRequested: false
    },
    incident: {
      date: '2026-10-13',
      time: '08:15',
      offenseType: 'vehicle_theft',
      offenseTitle: 'Vehicle Theft (Motor Vehicle / E-Rickshaw / Two-Wheeler)',
      bnsSection: 'Section 303(2) BNS',
      ipcSection: 'IPC 379',
      severity: 'HIGH',
      narrative: 'Parked Royal Enfield Classic 350 (Reg: DL 3S CJ 4810) outside Central Market commercial parking lane at 08:10 AM. Upon returning at 09:00 AM, the motorcycle was missing. Handle lock was engaged with disc padlock.',
    },
    location: {
      lat: 28.5677,
      lon: 77.2433,
      landmark: 'Central Market Feroze Gandhi Road',
      policeStation: 'Lajpat Nagar Police Station',
      district: 'South-East',
      distanceKm: 0.18
    },
    evidenceFiles: [
      {
        id: 'ev-3',
        name: 'vehicle_rc_dl3scj4810.pdf',
        size: 512000,
        type: 'application/pdf',
        sha256: '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a',
        truncatedSha: '4b227777...acdabf8a',
        timestamp: '13 Oct 2026, 09:45 AM IST',
        status: 'verified'
      }
    ],
    auditTrail: {
      masterBundleHash: 'cf83ac130d2264b420e69338cb513173b65d5066c1a124f82e19ecb9aba4fb02',
      filedAt: '13 Oct 2026, 09:50 AM IST',
      filedAtIso: '2026-10-13T04:20:00.000Z',
      legalAct: 'Sec 173 BNSS, 2023 & Sec 63 BSA',
      investigatingOfficer: 'ASI Virender Kumar (Belt No. 4102-SE)',
      dispatchPriority: 'HIGH',
      status: 'PENDING_INVESTIGATION'
    }
  }
];

export function getStoredFirs(): EFirRecord[] {
  if (typeof window === 'undefined') return INITIAL_MOCK_FIRS;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_MOCK_FIRS));
      return INITIAL_MOCK_FIRS;
    }
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : INITIAL_MOCK_FIRS;
  } catch (e) {
    console.error('Failed to parse stored e-FIRs', e);
    return INITIAL_MOCK_FIRS;
  }
}

export function saveStoredFir(newFir: EFirRecord): EFirRecord[] {
  if (typeof window === 'undefined') return [newFir, ...INITIAL_MOCK_FIRS];
  try {
    const existing = getStoredFirs();
    // Prepend new record so it appears at top of feed
    const updated = [newFir, ...existing.filter(f => f.id !== newFir.id)];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    return updated;
  } catch (e) {
    console.error('Failed to store e-FIR', e);
    return [newFir];
  }
}
