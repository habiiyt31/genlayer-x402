import os
import sys
import shutil
import genlayer_x402

CONTRACTS = {
    "paywall": "x402_paywall.py",
    "metered": "x402_metered.py",
    "subscription": "x402_subscription.py",
    "escrow": "x402_escrow.py",
}


def copy_file(src, dst):
    shutil.copy(src, dst)
    print(f"✔ {os.path.basename(dst)}")


def main():
    args = sys.argv[1:]

    package_path = genlayer_x402.get_package_path()
    target_dir = os.path.abspath("contracts")
    os.makedirs(target_dir, exist_ok=True)

    # 👉 list command
    if args and args[0] == "list":
        print("Available contracts:")
        for k in CONTRACTS:
            print(f"- {k}")
        return

    # 👉 ambil semua
    if len(args) == 0 or args[0] == "init":
        selected = None if len(args) <= 1 else args[1]
    else:
        selected = args[0]

    if selected:
        selected = selected.lower()
        if selected not in CONTRACTS:
            print(f"❌ Unknown contract: {selected}")
            print(f"Available: {', '.join(CONTRACTS.keys())}")
            return

        file = CONTRACTS[selected]
        src = os.path.join(package_path, file)
        dst = os.path.join(target_dir, file)

        copy_file(src, dst)
        print(f"\n✅ {selected} ready!")
        return

    # 👉 semua contract
    for file in CONTRACTS.values():
        src = os.path.join(package_path, file)
        dst = os.path.join(target_dir, file)
        copy_file(src, dst)

    print("\n🚀 All contracts ready!")