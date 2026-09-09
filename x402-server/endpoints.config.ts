/**
 * x402 Endpoints Configuration for Delhi Premises Risk & Hotspots
 * Defines pay-per-query pricing on Algorand TestNet via GoPlausible Facilitator
 */

import { USDC_TESTNET_ASA_ID } from '@x402/avm';

export const ALGORAND_TESTNET_NETWORK = 'algorand:SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI=';

export interface EndpointConfig {
  [key: string]: {
    accepts: Array<{
      scheme: 'exact';
      price: string;
      network: string;
      payTo: string;
      extra: { asset: number };
    }>;
    description: string;
    extensions?: Record<string, unknown>;
  };
}

export function createPaymentConfig(avmAddress: string): EndpointConfig {
  return {
    'GET /api/v1/risk-assessment': {
      accepts: [
        {
          scheme: 'exact',
          price: '$0.005',
          network: ALGORAND_TESTNET_NETWORK,
          payTo: avmAddress,
          extra: { asset: Number(USDC_TESTNET_ASA_ID) },
        },
      ],
      description: 'Agentic Delhi Premises Risk Assessment API - Pay $0.005 USDC on Algorand Testnet',
    },

    'POST /api/v1/patrol-route-optimizer': {
      accepts: [
        {
          scheme: 'exact',
          price: '$0.01',
          network: ALGORAND_TESTNET_NETWORK,
          payTo: avmAddress,
          extra: { asset: Number(USDC_TESTNET_ASA_ID) },
        },
      ],
      description: 'Agentic High-Security Patrol Route Planner - Pay $0.01 USDC on Algorand Testnet',
    },

    'GET /api/v1/dbscan-hotspots': {
      accepts: [
        {
          scheme: 'exact',
          price: '$0.002',
          network: ALGORAND_TESTNET_NETWORK,
          payTo: avmAddress,
          extra: { asset: Number(USDC_TESTNET_ASA_ID) },
        },
      ],
      description: 'Full DBSCAN Spatial Crime Corridors Coordinates Feed - Pay $0.002 USDC on Algorand Testnet',
    },
  };
}

export default createPaymentConfig;
