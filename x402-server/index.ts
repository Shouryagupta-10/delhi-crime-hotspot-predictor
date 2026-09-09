/**
 * x402 Agentic Solutions Server - Delhi Premises Risk & Hotspots
 * Powered by x402 Protocol on Algorand TestNet with GoPlausible Facilitator
 */

import { config } from 'dotenv';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { serve } from '@hono/node-server';
import { paymentMiddleware } from '@x402/hono';
import { x402ResourceServer, HTTPFacilitatorClient } from '@x402/core/server';
import { ExactAvmScheme } from '@x402/avm/exact/server';
import { ALGORAND_TESTNET_CAIP2 } from '@x402/avm';
import { bazaarResourceServerExtension } from '@x402-avm/extensions';

import { handleRiskAssessmentRequest } from './handlers/risk-assessment';
import { handlePatrolRouteOptimizerRequest } from './handlers/patrol-advisory';
import { handleHotspotsRequest } from './handlers/hotspot-clusters';
import createPaymentConfig, { ALGORAND_TESTNET_NETWORK } from './endpoints.config';

config();

const avmAddress = process.env.AVM_ADDRESS || 'BWKR3HJ3SYZIJ7M73WJF6566YWEGRLJAIGMNZ2RZRY35ZYFBBJ63H24MOQ';
const facilitatorUrl = process.env.FACILITATOR_URL || 'https://facilitator.goplausible.xyz';
const port = parseInt(process.env.PORT || '4021', 10);

const app = new Hono();

// 1. CORS Middleware (Expose x402 headers so browsers and agents can inspect 402 challenge)
app.use(
  '*',
  cors({
    origin: '*',
    allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowHeaders: ['Content-Type', 'Authorization', 'Payment-Signature', 'Payment-Required'],
    exposeHeaders: ['Payment-Required', 'Payment-Response', 'Payment-Signature'],
  })
);

// 2. Setup x402 Resource Server & GoPlausible Facilitator Client
const facilitatorClient = new HTTPFacilitatorClient({ url: facilitatorUrl });
const x402Server = new x402ResourceServer(facilitatorClient);
x402Server.register(ALGORAND_TESTNET_NETWORK, new ExactAvmScheme());
x402Server.register(ALGORAND_TESTNET_CAIP2, new ExactAvmScheme());
try {
  x402Server.registerExtension(bazaarResourceServerExtension);
} catch (e) {
  // Optional discovery extension ignored if not configured
}

// 3. Payment Middleware configured with Algorand Testnet exact scheme
const paymentConfig = createPaymentConfig(avmAddress);
app.use(paymentMiddleware(paymentConfig, x402Server));

// 4. Protected Endpoints (Only accessible after valid on-chain payment or facilitator settlement)
app.get('/api/v1/risk-assessment', handleRiskAssessmentRequest);
app.post('/api/v1/patrol-route-optimizer', handlePatrolRouteOptimizerRequest);
app.get('/api/v1/dbscan-hotspots', handleHotspotsRequest);

app.get('/health', (c) => c.json({ status: 'OK', network: 'Algorand Testnet', timestamp: new Date().toISOString() }));
app.get('/', (c) =>
  c.json({
    service: 'rakshak.ai: Crime Hotspot & Premises Risk x402 Server',
    track: 'Agentic Solutions: Powered by x402',
    network: 'Algorand Testnet',
    chain_caip2: ALGORAND_TESTNET_CAIP2,
    facilitator: facilitatorUrl,
    receiver_address: avmAddress,
    status: 'ONLINE',
    lora_testnet_explorer: 'https://lora.algokit.io/testnet',
    endpoints: Object.keys(paymentConfig),
  })
);

console.log('═'.repeat(65));
console.log('  🔥 AGENTIC SOLUTIONS: POWERED BY x402 (ALGORAND TESTNET)');
console.log('═'.repeat(65));
console.log(`  Receiver:    ${avmAddress}`);
console.log(`  Facilitator: ${facilitatorUrl}`);
console.log(`  Network:     ${ALGORAND_TESTNET_CAIP2}`);
console.log(`  Port:        ${port}`);
console.log(`  LoRA Link:   https://lora.algokit.io/testnet/account/${avmAddress}`);
console.log('═'.repeat(65));

serve({ fetch: app.fetch, port });
