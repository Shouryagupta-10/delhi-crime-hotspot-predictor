/**
 * Cryptographic Utility for Rakshak.ai e-FIR Digital Evidence Vault
 * Uses Web Crypto API for client-side SHA-256 evidence hashing and chain-of-custody sealing.
 * Adheres to Section 63 of Bharatiya Sakshya Adhiniyam, 2023 (BSA) for digital forensics integrity.
 */

/**
 * Computes SHA-256 hash of a File or Blob client-side using native Web Crypto API.
 * Returns full 64-character lowercase hex digest.
 */
export async function computeFileSHA256(file: File | Blob): Promise<string> {
  const arrayBuffer = await file.arrayBuffer();
  return computeBufferSHA256(arrayBuffer);
}

/**
 * Computes SHA-256 from an ArrayBuffer or Uint8Array.
 */
export async function computeBufferSHA256(buffer: ArrayBuffer): Promise<string> {
  if (typeof window !== 'undefined' && window.crypto && window.crypto.subtle) {
    const hashBuffer = await window.crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  // Fallback for non-subtle environments (e.g. legacy/testing)
  return fallbackSha256(new Uint8Array(buffer));
}

/**
 * Computes SHA-256 of any UTF-8 text string.
 */
export async function computeTextSHA256(text: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  return computeBufferSHA256(data.buffer as ArrayBuffer);
}

/**
 * Truncates a SHA-256 hash digest for clean UI display.
 * Example: '9f86d081...0f629e4b'
 */
export function truncateHash(hash: string, startChars = 8, endChars = 8): string {
  if (!hash) return '';
  if (hash.length <= startChars + endChars) return hash;
  return `${hash.slice(0, startChars)}...${hash.slice(-endChars)}`;
}

/**
 * Generates an official Delhi Police standard tracking ID.
 * Format: DL-FIR-2026-[5-digit integer]
 */
export function generateFIRTrackingId(): string {
  const randomSuffix = Math.floor(10000 + Math.random() * 90000);
  return `DL-FIR-2026-${randomSuffix}`;
}

/**
 * Formats byte size into human readable string (KB / MB).
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Masks Aadhaar number to display only last 4 digits (e.g. XXXX-XXXX-4819).
 */
export function maskAadhaar(raw: string): string {
  const cleaned = raw.replace(/\D/g, '');
  if (cleaned.length < 4) return raw;
  const last4 = cleaned.slice(-4);
  return `XXXX-XXXX-${last4}`;
}

/**
 * Formats an IST legal timestamp string.
 */
export function getISTTimestamp(date = new Date()): string {
  return new Intl.DateTimeFormat('en-IN', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  }).format(date);
}

/**
 * Computes the Master Bundle Hash that irreversibly binds all FIR details
 * with the SHA-256 digests of all attached evidence files.
 */
export async function computeMasterBundleHash(payload: {
  trackingId: string;
  complainantName: string;
  offenseType: string;
  incidentTimestamp: string;
  coordinates: [number, number];
  policeStation: string;
  evidenceHashes: string[];
}): Promise<string> {
  const normalizedString = JSON.stringify({
    id: payload.trackingId,
    complainant: payload.complainantName,
    offense: payload.offenseType,
    incidentTime: payload.incidentTimestamp,
    lat: payload.coordinates[0].toFixed(5),
    lon: payload.coordinates[1].toFixed(5),
    station: payload.policeStation,
    evidenceChain: payload.evidenceHashes.slice().sort()
  });

  return computeTextSHA256(normalizedString);
}

// Lightweight fallback SHA-256 implementation
function fallbackSha256(bytes: Uint8Array): string {
  function rightRotate(value: number, amount: number) {
    return (value >>> amount) | (value << (32 - amount));
  }

  const mathPow = Math.pow;
  const maxWord = mathPow(2, 32);
  let result = '';

  const words: number[] = [];
  const asciiBitLength = bytes.length * 8;

  let hash = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
  ];

  const k = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
  ];

  for (let i = 0; i < bytes.length; i++) {
    words[i >> 2] |= bytes[i] << (24 - (i % 4) * 8);
  }
  words[asciiBitLength >> 5] |= 0x80 << (24 - (asciiBitLength % 32));
  words[(((asciiBitLength + 64) >> 9) << 4) + 15] = asciiBitLength;

  const w = new Array(64);
  for (let i = 0; i < words.length; i += 16) {
    const [a0, b0, c0, d0, e0, f0, g0, h0] = hash;
    let [a, b, c, d, e, f, g, h] = [a0, b0, c0, d0, e0, f0, g0, h0];

    for (let j = 0; j < 64; j++) {
      if (j < 16) {
        w[j] = words[j + i] || 0;
      } else {
        const gamma0 = rightRotate(w[j - 15], 7) ^ rightRotate(w[j - 15], 18) ^ (w[j - 15] >>> 3);
        const gamma1 = rightRotate(w[j - 2], 17) ^ rightRotate(w[j - 2], 19) ^ (w[j - 2] >>> 10);
        w[j] = (w[j - 16] + gamma0 + w[j - 7] + gamma1) | 0;
      }

      const s1 = rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25);
      const ch = (e & f) ^ (~e & g);
      const temp1 = (h + s1 + ch + k[j] + w[j]) | 0;
      const s0 = rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22);
      const maj = (a & b) ^ (a & c) ^ (b & c);
      const temp2 = (s0 + maj) | 0;

      h = g;
      g = f;
      f = e;
      e = (d + temp1) | 0;
      d = c;
      c = b;
      b = a;
      a = (temp1 + temp2) | 0;
    }

    hash[0] = (hash[0] + a) | 0;
    hash[1] = (hash[1] + b) | 0;
    hash[2] = (hash[2] + c) | 0;
    hash[3] = (hash[3] + d) | 0;
    hash[4] = (hash[4] + e) | 0;
    hash[5] = (hash[5] + f) | 0;
    hash[6] = (hash[6] + g) | 0;
    hash[7] = (hash[7] + h) | 0;
  }

  for (let i = 0; i < 8; i++) {
    for (let j = 3; j >= 0; j--) {
      const byte = (hash[i] >> (j * 8)) & 255;
      result += byte.toString(16).padStart(2, '0');
    }
  }

  return result;
}
