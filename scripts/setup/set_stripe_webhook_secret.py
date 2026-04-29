"""Set the Stripe webhook signing secret in site_config.json.

Why site_config.json (not Stripe Settings doctype): per-site values that
should NEVER travel between dev/staging/production environments belong
in site_config.json. The doctype gets backed up + restored across sites;
site_config does not. The Stripe webhook secret for the local dev stack
is different from the one Stripe Cloud will issue for production.

Usage:
    python scripts/setup/set_stripe_webhook_secret.py whsec_<your_secret>

Get the secret from one of:
- Local dev: `stripe listen --forward-to <url>` prints the secret on stdout
- Production: Stripe Dashboard > Developers > Webhooks > [endpoint] >
  Signing secret (shown once when the endpoint is created; can be revealed
  again from the endpoint detail page)

Idempotent: re-run with a new secret to rotate.
"""
import json
import subprocess
import sys


def main():
    if len(sys.argv) < 2:
        print("usage: python scripts/setup/set_stripe_webhook_secret.py whsec_<secret>")
        return 2

    secret = sys.argv[1].strip()
    if not secret.startswith("whsec_"):
        print(f"ERROR: signing secret must start with 'whsec_'; got '{secret[:6]}...'")
        return 2

    container = "locally-twisted-erpnext-v15-backend-1"
    site = "frontend"

    cmd = [
        "docker", "exec", container, "sh", "-c",
        f"cd /home/frappe/frappe-bench && bench --site {site} set-config "
        f"stripe_webhook_signing_secret '{secret}'",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FAIL: bench set-config exited {result.returncode}")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        return 1

    # Verify
    verify = subprocess.run(
        ["docker", "exec", container, "sh", "-c",
         f"cat /home/frappe/frappe-bench/sites/{site}/site_config.json"],
        capture_output=True, text=True,
    )
    config = json.loads(verify.stdout)
    if config.get("stripe_webhook_signing_secret"):
        masked = secret[:8] + "..." + secret[-4:]
        print(f"OK — stripe_webhook_signing_secret set ({masked})")
        print(f"     {len(config)} keys in site_config")
        print()
        print("Next: restart backend so the new config loads:")
        print(f"     docker restart {container}")
        return 0
    print("FAIL: secret was not persisted to site_config.json")
    return 1


if __name__ == "__main__":
    sys.exit(main())
