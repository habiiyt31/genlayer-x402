import { readFileSync } from "fs";
import path from "path";
import {
  TransactionHash,
  TransactionStatus,
  GenLayerClient,
  DecodedDeployData,
  GenLayerChain,
} from "genlayer-js/types";
import { testnetBradbury } from "genlayer-js/chains";

/**
 * genlayer-x402 — Batch Deploy Script
 * =====================================
 * Deploys all 4 x402 Intelligent Contracts in sequence.
 *
 * Usage:
 *   genlayer deploy                          # deploy all to current network
 *   genlayer network set testnet-bradbury    # switch network first
 *   genlayer deploy                          # then deploy to testnet
 *
 * Contracts deployed:
 *   1. X402Paywall      — One-time payment access
 *   2. X402Metered      — Pay-per-call with credits
 *   3. X402Subscription — Period-based quota access
 *   4. X402Escrow       — AI-verified escrow payment
 */

async function deployContract(
  client: GenLayerClient<any>,
  name: string,
  contractPath: string,
  args: any[],
): Promise<string> {
  console.log(`\n📦 Deploying ${name}...`);

  const filePath = path.resolve(process.cwd(), contractPath);
  const contractCode = new Uint8Array(readFileSync(filePath));

  await client.initializeConsensusSmartContract();

  const deployTransaction = await client.deployContract({
    code: contractCode,
    args,
  });

  const receipt = await client.waitForTransactionReceipt({
    hash: deployTransaction as TransactionHash,
    retries: 200,
  });

  if (
    receipt.statusName !== TransactionStatus.ACCEPTED &&
    receipt.statusName !== TransactionStatus.FINALIZED
  ) {
    throw new Error(
      `${name} deployment failed. Receipt: ${JSON.stringify(receipt)}`,
    );
  }

  // Address location differs between testnet and localnet/studionet
  const contractAddress =
    (client.chain as GenLayerChain).id !== testnetBradbury.id
      ? (receipt.data as any)?.contract_address
      : (receipt.txDataDecoded as DecodedDeployData)?.contractAddress;

  console.log(`✅ ${name} deployed`);
  console.log(`   Transaction Hash: ${deployTransaction}`);
  console.log(`   Contract Address: ${contractAddress}`);

  return contractAddress;
}

export default async function main(client: GenLayerClient<any>) {
  console.log("═══════════════════════════════════════════════════");
  console.log("  genlayer-x402 — Deploying all 4 contracts");
  console.log("═══════════════════════════════════════════════════");

  // 1. X402Paywall
  const paywallAddress = await deployContract(
    client,
    "X402Paywall",
    "contracts/x402_paywall.py",
    [
      100n, // price_wei
      "https://api.coinbase.com/v2/prices/BTC-USD/spot", // data_url
    ],
  );

  // 2. X402Metered
  const meteredAddress = await deployContract(
    client,
    "X402Metered",
    "contracts/x402_metered.py",
    [
      10n, // price_per_call_wei
      "https://api.coingecko.com/api/v3/simple/price?ids=", // data_url_prefix
      1000n, // max_credits
    ],
  );

  // 3. X402Subscription
  const subscriptionAddress = await deployContract(
    client,
    "X402Subscription",
    "contracts/x402_subscription.py",
    [
      100n, // price_per_period_wei
      50n, // calls_per_period
      "https://api.github.com/repos/genlayerlabs/genlayer-project-boilerplate", // data_url
    ],
  );

  // 4. X402Escrow
  const escrowAddress = await deployContract(
    client,
    "X402Escrow",
    "contracts/x402_escrow.py",
    [
      "Build a simple static HTML landing page with hero section and a contact form.", // brief
    ],
  );

  // Summary
  console.log("\n═══════════════════════════════════════════════════");
  console.log("  ✅ All 4 contracts deployed successfully!");
  console.log("═══════════════════════════════════════════════════");
  console.log(
    JSON.stringify(
      {
        X402Paywall: paywallAddress,
        X402Metered: meteredAddress,
        X402Subscription: subscriptionAddress,
        X402Escrow: escrowAddress,
      },
      null,
      2,
    ),
  );
}
