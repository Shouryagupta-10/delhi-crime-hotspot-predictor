import type { Context } from 'hono';

export async function handleHotspotsRequest(c: Context) {
  return c.json({
    status: 'success',
    paid: true,
    protocol: 'x402-avm',
    blockchain: 'Algorand Testnet',
    facilitator: 'GoPlausible',
    timestamp: new Date().toISOString(),
    clustering_model: 'DBSCAN with Haversine Metric (eps=600m, min_samples=18)',
    total_clusters: 44,
    hotspots: [
      { cluster_id: 1, district: 'New Delhi', centroid: [28.6328, 77.2195], landmark: 'Rajiv Chowk Metro', dominant_crime: 'Pickpocketing & Snatching', risk_index: 0.78 },
      { cluster_id: 2, district: 'Central', centroid: [28.6517, 77.1906], landmark: 'Karol Bagh Gaffar Market', dominant_crime: 'Snatching & Burglary', risk_index: 0.81 },
      { cluster_id: 3, district: 'North', centroid: [28.6675, 77.2285], landmark: 'Kashmere Gate ISBT', dominant_crime: 'Robbery & Luggage Theft', risk_index: 0.85 },
      { cluster_id: 4, district: 'South-East', centroid: [28.5494, 77.2528], landmark: 'Nehru Place Electronics Hub', dominant_crime: 'Vehicle Theft & Snatching', risk_index: 0.74 },
      { cluster_id: 5, district: 'Shahdara', centroid: [28.6480, 77.3160], landmark: 'Anand Vihar Terminal', dominant_crime: 'Street Robbery', risk_index: 0.88 },
    ],
  });
}
