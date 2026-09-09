#!/bin/bash
# Autonomous x402 Algorand Testnet Agent Runner
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( dirname "$SCRIPT_DIR" )"
SERVER_DIR="$ROOT_DIR/x402-server"

echo "================================================================="
echo "  🚀 Starting Autonomous x402 Agent on Algorand Testnet"
echo "  Facilitator: GoPlausible (https://facilitator.goplausible.xyz)"
echo "  Explorer:    LoRA Algorand Testnet (https://lora.algokit.io/testnet)"
echo "================================================================="

cd "$SERVER_DIR"
npx tsx scripts/agent_x402_runner.ts
