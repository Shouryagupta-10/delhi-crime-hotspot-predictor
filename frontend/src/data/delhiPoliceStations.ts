/**
 * Delhi Police Stations & Offenses Registry
 * Derived from Delhi Police Headquarters jurisdictional boundaries and GNCTD geospatial coordinates.
 */

export interface PoliceStation {
  name: string;
  district: string;
  lat: number;
  lon: number;
  address: string;
  phone: string;
  shoContact?: string;
}

export interface OffenseType {
  id: string;
  title: string;
  bnsSection: string;
  ipcSection: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  description: string;
  suggestedEvidence: string[];
}

export const DELHI_POLICE_STATIONS: PoliceStation[] = [
  // New Delhi
  { name: "Connaught Place Police Station", district: "New Delhi", lat: 28.6315, lon: 77.2167, address: "B-Block, Connaught Place, New Delhi", phone: "011-23747100 / 112" },
  { name: "Parliament Street Police Station", district: "New Delhi", lat: 28.6238, lon: 77.2142, address: "Parliament Street, New Delhi", phone: "011-23361100 / 112" },
  { name: "Chanakyapuri Police Station", district: "New Delhi", lat: 28.5983, lon: 77.1912, address: "Simon Bolivar Marg, Chanakyapuri", phone: "011-24101100 / 112" },
  { name: "Mandir Marg Police Station", district: "New Delhi", lat: 28.6295, lon: 77.2010, address: "Mandir Marg, Gole Market", phone: "011-23362100 / 112" },
  { name: "Tilak Marg Police Station", district: "New Delhi", lat: 28.6190, lon: 77.2380, address: "Tilak Marg, India Gate Environs", phone: "011-23381100 / 112" },
  { name: "Barakhamba Road Police Station", district: "New Delhi", lat: 28.6288, lon: 77.2285, address: "Barakhamba Road, Connaught Place", phone: "011-23412100 / 112" },

  // Central Delhi
  { name: "Karol Bagh Police Station", district: "Central", lat: 28.6517, lon: 77.1906, address: "Gurudwara Road, Karol Bagh", phone: "011-25721100 / 112" },
  { name: "Paharganj Police Station", district: "Central", lat: 28.6432, lon: 77.2140, address: "Main Bazar, Paharganj", phone: "011-23581100 / 112" },
  { name: "Daryaganj Police Station", district: "Central", lat: 28.6480, lon: 77.2410, address: "Ansari Road, Daryaganj", phone: "011-23271100 / 112" },
  { name: "Chandni Chowk Police Station", district: "Central", lat: 28.6562, lon: 77.2300, address: "Town Hall, Chandni Chowk", phone: "011-23261100 / 112" },
  { name: "Rajinder Nagar Police Station", district: "Central", lat: 28.6390, lon: 77.1790, address: "Old Rajinder Nagar", phone: "011-25741100 / 112" },
  { name: "Kamla Market Police Station", district: "Central", lat: 28.6380, lon: 77.2245, address: "Asaf Ali Road, New Delhi Station", phone: "011-23231100 / 112" },

  // North Delhi
  { name: "Kashmere Gate Police Station", district: "North", lat: 28.6675, lon: 77.2285, address: "Lothian Road, Kashmere Gate", phone: "011-23861100 / 112" },
  { name: "Civil Lines Police Station", district: "North", lat: 28.6750, lon: 77.2230, address: "Rajpur Road, Civil Lines", phone: "011-23811100 / 112" },
  { name: "Timarpur Police Station", district: "North", lat: 28.7010, lon: 77.2190, address: "Timarpur, North Delhi", phone: "011-23812100 / 112" },
  { name: "Maurice Nagar Police Station", district: "North", lat: 28.6890, lon: 77.2080, address: "Delhi University North Campus", phone: "011-27661100 / 112" },
  { name: "Kotwali Police Station", district: "North", lat: 28.6580, lon: 77.2325, address: "Chandni Chowk Kotwali", phone: "011-23281100 / 112" },

  // South Delhi
  { name: "Hauz Khas Police Station", district: "South", lat: 28.5430, lon: 77.2060, address: "Aurobindo Marg, Hauz Khas", phone: "011-26861100 / 112" },
  { name: "Saket Police Station", district: "South", lat: 28.5240, lon: 77.2120, address: "Press Enclave Marg, Saket", phone: "011-26511100 / 112" },
  { name: "Malviya Nagar Police Station", district: "South", lat: 28.5360, lon: 77.2090, address: "Corner Market, Malviya Nagar", phone: "011-26681100 / 112" },
  { name: "Mehrauli Police Station", district: "South", lat: 28.5200, lon: 77.1820, address: "Near Qutub Minar, Mehrauli", phone: "011-26641100 / 112" },
  { name: "Greater Kailash Police Station", district: "South", lat: 28.5400, lon: 77.2380, address: "GK 1 Near M-Block Market", phone: "011-29231100 / 112" },

  // South-East Delhi
  { name: "Lajpat Nagar Police Station", district: "South-East", lat: 28.5677, lon: 77.2433, address: "Feroze Gandhi Road, Lajpat Nagar III", phone: "011-29831100 / 112" },
  { name: "Nehru Place / Kalkaji Police Station", district: "South-East", lat: 28.5492, lon: 77.2527, address: "Kalkaji Environs, Nehru Place", phone: "011-26431100 / 112" },
  { name: "Sarita Vihar Police Station", district: "South-East", lat: 28.5300, lon: 77.2910, address: "Mathura Road, Sarita Vihar", phone: "011-26941100 / 112" },
  { name: "Okhla Industrial Area Police Station", district: "South-East", lat: 28.5350, lon: 77.2720, address: "Okhla Phase 3", phone: "011-26841100 / 112" },
  { name: "Amar Colony Police Station", district: "South-East", lat: 28.5610, lon: 77.2460, address: "Amar Colony, Lajpat Nagar IV", phone: "011-26481100 / 112" },

  // South-West Delhi
  { name: "Vasant Kunj (North) Police Station", district: "South-West", lat: 28.5420, lon: 77.1560, address: "Sector D, Pocket 2, Vasant Kunj", phone: "011-26891100 / 112" },
  { name: "Vasant Vihar Police Station", district: "South-West", lat: 28.5580, lon: 77.1620, address: "Basant Lok, Vasant Vihar", phone: "011-26141100 / 112" },
  { name: "Delhi Cantt Police Station", district: "South-West", lat: 28.5898, lon: 77.1325, address: "Sadar Bazar, Delhi Cantt", phone: "011-25691100 / 112" },
  { name: "Safdarjung Enclave Police Station", district: "South-West", lat: 28.5640, lon: 77.1950, address: "Safdarjung Enclave Market", phone: "011-26101100 / 112" },

  // West Delhi
  { name: "Rajouri Garden Police Station", district: "West", lat: 28.6490, lon: 77.1230, address: "Main Ring Road, Rajouri Garden", phone: "011-25441100 / 112" },
  { name: "Punjabi Bagh Police Station", district: "West", lat: 28.6680, lon: 77.1270, address: "Rohtak Road, Punjabi Bagh", phone: "011-25221100 / 112" },
  { name: "Janakpuri Police Station", district: "West", lat: 28.6290, lon: 77.0810, address: "District Centre Environs, Janakpuri", phone: "011-25551100 / 112" },
  { name: "Tilak Nagar Police Station", district: "West", lat: 28.6365, lon: 77.0965, address: "Near Tilak Nagar Metro Station", phone: "011-25981100 / 112" },
  { name: "Patel Nagar Police Station", district: "West", lat: 28.6508, lon: 77.1654, address: "Main Patel Road, West Patel Nagar", phone: "011-25881100 / 112" },

  // North-West Delhi
  { name: "Netaji Subhash Place Police Station", district: "North-West", lat: 28.6925, lon: 77.1520, address: "Pitampura TV Tower Environs, NSP", phone: "011-27151100 / 112" },
  { name: "Model Town Police Station", district: "North-West", lat: 28.7050, lon: 77.1920, address: "Model Town II, Ring Road", phone: "011-27451100 / 112" },
  { name: "Shalimar Bagh Police Station", district: "North-West", lat: 28.7150, lon: 77.1600, address: "Club Road, Shalimar Bagh", phone: "011-27481100 / 112" },

  // Rohini
  { name: "Rohini Sector 18 Police Station", district: "Rohini", lat: 28.7410, lon: 77.1320, address: "Sector 18, Rohini", phone: "011-27891100 / 112" },
  { name: "Prashant Vihar Police Station", district: "Rohini", lat: 28.7110, lon: 77.1350, address: "Prashant Vihar, Outer Ring Road", phone: "011-27561100 / 112" },
  { name: "South Rohini Police Station", district: "Rohini", lat: 28.7040, lon: 77.1140, address: "Sector 3, Rohini", phone: "011-27941100 / 112" },

  // Dwarka
  { name: "Dwarka Sector 10 Police Station", district: "Dwarka", lat: 28.5810, lon: 77.0580, address: "Sector 10 District Court Complex, Dwarka", phone: "011-28081100 / 112" },
  { name: "Dwarka Sector 23 Police Station", district: "Dwarka", lat: 28.5520, lon: 77.0580, address: "Sector 23, Dwarka", phone: "011-28051100 / 112" },
  { name: "Uttam Nagar Police Station", district: "Dwarka", lat: 28.6210, lon: 77.0650, address: "Najafgarh Road, Uttam Nagar", phone: "011-25611100 / 112" },

  // East Delhi & Shahdara
  { name: "Laxmi Nagar Police Station", district: "East", lat: 28.6310, lon: 77.2780, address: "Vikas Marg, Laxmi Nagar", phone: "011-22441100 / 112" },
  { name: "Preet Vihar Police Station", district: "East", lat: 28.6410, lon: 77.2950, address: "Vikas Marg Ext, Preet Vihar", phone: "011-22521100 / 112" },
  { name: "Mayur Vihar Police Station", district: "East", lat: 28.6080, lon: 77.2950, address: "Pocket 1, Mayur Vihar Phase 1", phone: "011-22751100 / 112" },
  { name: "Anand Vihar Police Station", district: "Shahdara", lat: 28.6480, lon: 77.3160, address: "ISBT Terminal Environs, Anand Vihar", phone: "011-22161100 / 112" },
  { name: "Gandhi Nagar Police Station", district: "Shahdara", lat: 28.6610, lon: 77.2680, address: "Main Road, Gandhi Nagar", phone: "011-22081100 / 112" },

  // North-East & Outer
  { name: "Seelampur Police Station", district: "North-East", lat: 28.6690, lon: 77.2670, address: "GT Road, Seelampur Chowk", phone: "011-22811100 / 112" },
  { name: "Paschim Vihar Police Station", district: "Outer", lat: 28.6730, lon: 77.1080, address: "Jwala Heri Market Road, Paschim Vihar", phone: "011-25261100 / 112" },
  { name: "Narela Police Station", district: "Outer-North", lat: 28.8450, lon: 77.0920, address: "Bawana Road, Narela", phone: "011-27281100 / 112" },
  { name: "Bawana Police Station", district: "Outer-North", lat: 28.7980, lon: 77.0340, address: "Bawana Industrial Area", phone: "011-27751100 / 112" }
];

export const DELHI_OFFENSES: OffenseType[] = [
  {
    id: "vehicle_theft",
    title: "Vehicle Theft (Motor Vehicle / E-Rickshaw / Two-Wheeler)",
    bnsSection: "Section 303(2) BNS",
    ipcSection: "IPC 379",
    severity: "HIGH",
    description: "Theft of motorized vehicle, motorcycle, or commercial conveyance from public parking or roadway.",
    suggestedEvidence: ["Vehicle RC Copy", "Insurance Policy PDF", "Parking Slip / CCTV Clip", "GPS Tracker Log"]
  },
  {
    id: "mobile_snatching",
    title: "Mobile / Chain Snatching (Sudden Force Egress)",
    bnsSection: "Section 304 BNS",
    ipcSection: "IPC 392 / 356",
    severity: "CRITICAL",
    description: "Forcible snatching of mobile phone, jewellery, or bag by pedestrian or pillion riders.",
    suggestedEvidence: ["IMEI Purchase Invoice", "Telecom Call Detail Records", "Eyewitness Audio Note", "CCTV Footage"]
  },
  {
    id: "assault_hurt",
    title: "Physical Assault & Voluntarily Causing Hurt",
    bnsSection: "Section 115(2) & 118 BNS",
    ipcSection: "IPC 323 / 324",
    severity: "CRITICAL",
    description: "Infliction of bodily harm or assault with or without weapon in public or private area.",
    suggestedEvidence: ["Hospital Medico-Legal MLC Slip", "Photographs of Injuries", "Witness Testimony", "Scene Photo"]
  },
  {
    id: "harassment_stalking",
    title: "Women Harassment, Stalking & Eve-Teasing",
    bnsSection: "Section 74 & 78 BNS",
    ipcSection: "IPC 354 / 354D",
    severity: "HIGH",
    description: "Unwanted physical proximity, verbal abuse, stalking, or harassment targeting women.",
    suggestedEvidence: ["Chat / Message Screenshots", "Audio / Video Recording", "Vehicle Number Plate Photo"]
  },
  {
    id: "cyber_fraud",
    title: "Cyber Financial Fraud & Aadhaar/UPI Phishing",
    bnsSection: "Section 318(4) BNS & Sec 66D IT Act",
    ipcSection: "IPC 420",
    severity: "HIGH",
    description: "Digital deception, fake QR code siphon, SIM swap, or deceptive online banking extraction.",
    suggestedEvidence: ["Bank Transaction Statement PDF", "UPI UTR Reference Screenshot", "Phishing SMS / WhatsApp Chat"]
  },
  {
    id: "burglary_trespass",
    title: "House-Breaking / Burglary & Trespass",
    bnsSection: "Section 331(4) BNS",
    ipcSection: "IPC 457 / 380",
    severity: "HIGH",
    description: "Lurking house-trespass or broken lock robbery during night or absence of residents.",
    suggestedEvidence: ["Photos of Broken Locks/Entrances", "List of Stolen Valuables", "Society DVR CCTV Stream"]
  },
  {
    id: "extortion_threat",
    title: "Extortion & Criminal Intimidation",
    bnsSection: "Section 308 & 351 BNS",
    ipcSection: "IPC 384 / 506",
    severity: "CRITICAL",
    description: "Demanding money, property, or valuable security under threat of bodily injury or exposure.",
    suggestedEvidence: ["Recorded Audio Threats", "Demand Letter / Screenshot", "Call Log History"]
  }
];

/**
 * Calculates exact Haversine distance in kilometers between two GPS coordinates.
 */
export function calculateHaversineDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // Earth radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return parseFloat((R * c).toFixed(2));
}

/**
 * Finds the nearest Delhi Police Station and District based on latitude/longitude.
 */
export function findNearestPoliceStation(lat: number, lon: number): {
  station: PoliceStation;
  distanceKm: number;
} {
  let nearestStation = DELHI_POLICE_STATIONS[0];
  let minDistance = Infinity;

  for (const station of DELHI_POLICE_STATIONS) {
    const dist = calculateHaversineDistance(lat, lon, station.lat, station.lon);
    if (dist < minDistance) {
      minDistance = dist;
      nearestStation = station;
    }
  }

  return {
    station: nearestStation,
    distanceKm: minDistance,
  };
}
