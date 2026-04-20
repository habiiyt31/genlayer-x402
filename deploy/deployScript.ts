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
 * genlayer-x402 — Batch Deploy Script v0.2.0
 * ============================================
 * Deploys all 4 x402 Intelligent Contracts in sequence.
 *
 * Usage:
 *   genlayer deploy                          # deploy all to current network
 *   genlayer network set testnet-bradbury    # switch network first
 *   genlayer deploy                          # then deploy to testnet
 *
 * Contracts deployed:
 *   1. X402Paywall      — One-time payment access (with withdraw)
 *   2. X402Metered      — Pay-per-call with credits (with withdraw)
 *   3. X402Subscription — Period-based quota access (with withdraw)
 *   4. X402Escrow       — AI-verified escrow + arbiter + timeout safety
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
  const contractAddress: string =
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
  console.log("  genlayer-x402 v0.2.0 — Deploying all 4 contracts");
  console.log("═══════════════════════════════════════════════════");

  // 1. X402Paywall — 1 GEN for permanent access
  const paywallAddress = await deployContract(
    client,
    "X402Paywall",
    "contracts/x402_paywall.py",
    [
      1000000000000000000n, // price_wei: 1 GEN (= 10^18 wei)
      "https://api.github.com/users/octocat", // data_url
    ],
  );

  // 2. X402Metered — 1 GEN per call, up to 1000 credits per user
  const meteredAddress = await deployContract(
    client,
    "X402Metered",
    "contracts/x402_metered.py",
    [
      1000000000000000000n, // price_per_call_wei: 1 GEN (= 10^18 wei)
      "https://api.github.com/users/", // data_url_prefix
      1000n, // max_credits
    ],
  );

  // 3. X402Subscription — 1 GEN per period, 10 calls per period
  const subscriptionAddress = await deployContract(
    client,
    "X402Subscription",
    "contracts/x402_subscription.py",
    [
      1000000000000000000n, // price_per_period_wei: 1 GEN (= 10^18 wei)
      10n, // calls_per_period
      "https://api.github.com/repos/genlayerlabs/genlayer-project-boilerplate", // data_url
    ],
  );

  // 4. X402Escrow — v0.2.0: structured brief (6 args)
  // Brief minimum requirements:
  //   - title: 10+ chars
  //   - description: 80+ chars
  //   - acceptance_criteria: 80+ chars
  //   - deliverable_format: 30+ chars
  //   - TOTAL: 200+ chars combined
  const escrowAddress = await deployContract(
    client,
    "X402Escrow",
    "contracts/x402_escrow.py",
    [
      // brief_title (10+ chars)
      "Bitcoin Price Fetcher Python Script",

      // brief_description (80+ chars)
      "Build a Python script that fetches the current Bitcoin price from the CoinGecko API and prints it in formatted output with timestamp and 24h change percentage.",

      // brief_acceptance_criteria (80+ chars)
      "Script must run without errors on Python 3.10+. Must use the requests library. Must print price in USD format. Must include error handling for API failures. Code must be PEP8 compliant and well-commented.",

      // brief_deliverable_format (30+ chars)
      "Single Python file named btc_price.py, committed to a public GitHub repository",

      // arbiter_addr (use zero address for testing, or a real neutral 3rd party)
      "0x0000000000000000000000000000000000000000",

      // max_claim_attempts (minimum 3)
      3n,
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
  console.log("\nNext steps:");
  console.log("  1. Save these addresses for frontend / testing");
  console.log("  2. Interact via: genlayer call / genlayer write");
  console.log("  3. Withdraw revenue: genlayer write ... --function withdraw_all");
}