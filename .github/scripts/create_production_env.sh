#!/usr/bin/env bash
# Helper script to create and protect a `production` environment via GitHub REST API.
# Usage: export GH_TOKEN=<token> && OWNER=org_or_user REPO=repo ./create_production_env.sh

set -euo pipefail

OWNER="${OWNER:-}"  # e.g. my-org
REPO="${REPO:-}"    # e.g. Project-Draft
ENV="production"
TOKEN="${GH_TOKEN:-}" # needs repo admin permission

if [ -z "$OWNER" ] || [ -z "$REPO" ]; then
  echo "Please set OWNER and REPO environment variables."
  echo "Example: OWNER=Vaishnavidorlikar REPO=Project-Draft GH_TOKEN=... $0"
  exit 1
fi

if [ -z "$TOKEN" ]; then
  echo "Please set GH_TOKEN with repo admin permissions (export GH_TOKEN=...)"
  exit 1
fi

# Create environment (idempotent)
echo "Creating environment: $ENV in $OWNER/$REPO..."
curl -s -S -X PUT \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${OWNER}/${REPO}/environments/${ENV}"

echo -e "\nSet protection rules by adding reviewers (numeric GitHub user IDs) in the PAYLOAD below.\n"

# Example: single user reviewer. Replace 1234567 with actual numeric user id(s).
read -r -d '' PAYLOAD <<'JSON'
{
  "wait_timer": 0,
  "reviewers": [
    { "type": "User", "id": 1234567 }
  ]
}
JSON

echo "Applying protection rules (you may want to edit the script and change reviewer IDs)..."
curl -s -S -X PUT \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -d "$PAYLOAD" \
  "https://api.github.com/repos/${OWNER}/${REPO}/environments/${ENV}/protection"

echo "Done. Verify the environment settings in the GitHub UI under Settings → Environments → $ENV."