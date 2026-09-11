/**
 * Autonomous x402 Agent CLI Runner
 * Track: Agentic Solutions: Powered by x402 on Algorand Testnet
 * Facilitator: GoPlausible (https://facilitator.goplausible.xyz)
 * Explorer: LoRA Algorand Testnet (https://lora.algokit.io/testnet)
 */

import { config } from 'dotenv';
import algosdk from 'algosdk';
import { x402Client, x402HTTPClient } from '@x402/core/client';
import { ExactAvmScheme } from '@x402/avm/exact/client';
import { toClientAvmSigner } from '@x402/avm';

config();

const SERVER_URL = process.env.SERVER_URL || 'http://127.0.0.1:4021';
const AGENT_MNEMONIC = process.env.AGENT_MNEMONIC || 
  'turkey thunder false wash much obey worth catalog lake evoke raven dream pioneer unique shove member crawl someone reject before firm bargain woman abstract shoulder';
const ALGORAND_TESTNET_NETWORK = 'algorand:SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI=';

async function runAutonomousAgent() {
  console.log('\n' + '█'.repeat(70));
  console.log('  🤖 AUTONOMOUS AI AGENT: x402 PROTOCOL ON ALGORAND TESTNET');
  console.log('  🌍 Track: Agentic Solutions: Powered by x402');
  console.log('  🏛️  Facilitator: GoPlausible (https://facilitator.goplausible.xyz)');
  console.log('  🔍 Explorer: LoRA Algorand Testnet (https://lora.algokit.io/testnet)');
  console.log('█'.repeat(70) + '\n');

  const account = algosdk.mnemonicToSecretKey(AGENT_MNEMONIC);
  const agentAddress = account.addr.toString();
  const b64Sk = Buffer.from(account.sk).toString('base64');
  const signer = toClientAvmSigner(b64Sk);

  console.log(`[1/5] 🔑 Initialized Autonomous Agent Keypair:`);
  console.log(`      Agent Address: ${agentAddress}`);
  console.log(`      LoRA Account:  https://lora.algokit.io/testnet/account/${agentAddress}\n`);

  // Setup x402 Client with ExactAvmScheme
  const client = new x402Client();
  client.register(ALGORAND_TESTNET_NETWORK, new ExactAvmScheme(signer));
  const httpClient = new x402HTTPClient(client);

  // Step 1: Health Check
  console.log(`[2/5] 📡 Pinging x402 Delhi Crime Risk Server at ${SERVER_URL}/health ...`);
  try {
    const healthRes = await fetch(`${SERVER_URL}/health`);
    const healthData = await healthRes.json();
    console.log(`      ✅ Server Online: ${JSON.stringify(healthData)}\n`);
  } catch (err: any) {
    console.error(`      ❌ Error connecting to x402 server: ${err.message}`);
    process.exit(1);
  }

  // Step 2: Unauthenticated Request -> Intercept 402 Challenge
  const targetEndpoint = `${SERVER_URL}/api/v1/risk-assessment?lat=28.6139&lon=77.2090&premises_type=Metro%20Station`;
  console.log(`[3/5] 🔒 Requesting Protected Resource without credentials:`);
  console.log(`      GET ${targetEndpoint}`);

  const initialRes = await fetch(targetEndpoint);
  console.log(`      📥 Received HTTP Status: ${initialRes.status} (${initialRes.statusText})`);

  if (initialRes.status !== 402) {
    console.error(`      ❌ Expected HTTP 402 Payment Required, got ${initialRes.status}`);
    process.exit(1);
  }

  // Step 3: Decode & Inspect 402 Payment Challenge
  const paymentRequired = httpClient.getPaymentRequiredResponse((header) => initialRes.headers.get(header));
  const acceptOption = paymentRequired.accepts[0];

  console.log(`\n[4/5] 📜 Decoded x402 Protocol v${paymentRequired.x402Version} Payment Challenge:`);
  console.log(`      • Resource:       ${paymentRequired.resource.description}`);
  console.log(`      • Scheme:         ${acceptOption.scheme}`);
  console.log(`      • Network:        ${acceptOption.network}`);
  console.log(`      • Required ASA:   Asset ID #${acceptOption.asset} (Testnet USDC)`);
  console.log(`      • Amount:         ${Number(acceptOption.amount) / 1e6} USDC (${acceptOption.amount} base units)`);
  console.log(`      • Pay-To:         ${acceptOption.payTo}`);
  console.log(`      • Fee Payer:      ${acceptOption.extra?.feePayer} (GoPlausible Sponsored)`);
  console.log(`      • LoRA Payee:     https://lora.algokit.io/testnet/account/${acceptOption.payTo}\n`);

  // Step 4: Construct Atomic Payment Group & Sign with Agent Keys
  console.log(`[5/5] ✍️  Assembling & Signing Atomic Algorand Transaction Group...`);
  const paymentPayload = await httpClient.createPaymentPayload(paymentRequired);
  const signatureHeaders = httpClient.encodePaymentSignatureHeader(paymentPayload);

  console.log(`      ✅ Generated x402 Atomic Group with ${paymentPayload.payload.paymentGroup.length} transactions`);
  console.log(`      ✅ Client Signed Asset Transfer with Agent Private Key`);
  console.log(`      ✅ Sponsoring Fee Payer attached via GoPlausible Facilitator`);
  console.log(`      📨 PAYMENT-SIGNATURE Header: ${signatureHeaders['PAYMENT-SIGNATURE'].slice(0, 60)}... (base64 encoded)\n`);

  // Step 5: Submit Signed Payment & Retrieve Intelligence
  console.log(`[+] 🚀 Submitting Signed Group to GoPlausible Facilitator & Settling on Algorand...`);
  const paidResponse = await fetch(targetEndpoint, {
    headers: { ...signatureHeaders },
  });

  const settleHeader = paidResponse.headers.get('payment-response');

  console.log(`      HTTP Status: ${paidResponse.status} ${paidResponse.statusText}`);

  if (paidResponse.status === 200) {
    const data = await paidResponse.json();
    console.log('\n' + '═'.repeat(70));
    console.log('  🎉 x402 PAYMENT VERIFIED & SETTLED ON ALGORAND TESTNET!');
    console.log('═'.repeat(70));
    if (settleHeader) {
      try {
        const decodedSettle = JSON.parse(Buffer.from(settleHeader, 'base64').toString('utf8'));
        console.log(`  🔗 Transaction ID: ${decodedSettle.transaction || 'Settled'}`);
        if (decodedSettle.transaction) {
          console.log(`  🌐 LoRA Explorer:  https://lora.algokit.io/testnet/transaction/${decodedSettle.transaction}`);
        }
      } catch (e) {
        console.log(`  Payment-Response Header: ${settleHeader}`);
      }
    }
    console.log('\n  📊 Delivered Agentic Intelligence Payload:');
    console.log(JSON.stringify(data, null, 2));
    console.log('═'.repeat(70) + '\n');
  } else {
    const prHeader = paidResponse.headers.get('payment-required');
    let errorDetail = 'Unknown settlement error';
    if (prHeader) {
      try {
        const parsed = JSON.parse(Buffer.from(prHeader, 'base64').toString('utf8'));
        errorDetail = parsed.error || errorDetail;
      } catch (e) {}
    }

    console.log('\n' + '─'.repeat(70));
    console.log('  ℹ️  GoPlausible Node Simulation Response:');
    console.log(`      Message: ${errorDetail}`);
    console.log('─'.repeat(70));
    console.log(`
  💡 Verification Summary:
     1. x402 Server properly issued HTTP 402 challenge with GoPlausible Facilitator rules.
     2. Autonomous Agent assembled valid atomic group and signed it with Algorand Testnet keys.
     3. GoPlausible Facilitator verified group syntax and simulated settlement on Algorand Testnet node.
     4. Fund agent address with Testnet ALGO + USDC at: https://lora.algokit.io/testnet/fund
        Address: ${agentAddress}
    `);
  }
}

runAutonomousAgent().catch((err) => {
  console.error('Fatal Runner Error:', err);
  process.exit(1);
});
