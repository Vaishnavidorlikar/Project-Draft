# project-draft

This repository contains multiple sample deployment projects (Docker/Kubernetes, Serverless/Terraform, ML model, Java Gradle app, Mobile Fastlane pipeline). I updated the CI to push Docker images to **Google Cloud Artifact Registry**.

## Docker build & push to Google Artifact Registry
The Docker workflow now builds container images and pushes them to Artifact Registry using the following secrets (set in GitHub repository settings → Secrets → Actions):

- `GCP_SERVICE_ACCOUNT_KEY` — JSON contents of a Google Cloud service account key with permissions to write to Artifact Registry (stored as a secret string).
- `GCP_PROJECT` — Google Cloud project ID where the Artifact Registry repository exists.
- `AR_REPOSITORY` — Artifact Registry repository name (e.g., `sample-repo`).
- `IMAGE_REGION` — Artifact Registry region portion used in the host, e.g., `us-central1` (the workflow uses `${IMAGE_REGION}-docker.pkg.dev`).

Example image name format:
`us-central1-docker.pkg.dev/<GCP_PROJECT>/<AR_REPOSITORY>/containerized-webapp:<GITHUB_SHA>`

## Deploy to Cloud Run
I added a workflow (`.github/workflows/cloud-run-deploy.yml`) that deploys the built images to **Cloud Run**. The workflow authenticates with the `GCP_SERVICE_ACCOUNT_KEY` secret and deploys services named after the image (for example: `containerized-webapp`, `ml-model`, `automated-webapp`).

Required secrets for deployment:
- `GCP_SERVICE_ACCOUNT_KEY` — service account JSON with `roles/run.admin`, `roles/iam.serviceAccountUser`, and `roles/artifactregistry.reader` (or similar) as needed.
- `GCP_PROJECT` — project id.
- `IMAGE_REGION` — region for Cloud Run and Artifact Registry (e.g., `us-central1`).
- `AR_REPOSITORY` — Artifact Registry repo.

Deployment command used by the workflow:
`gcloud run deploy <service> --image <IMAGE> --region <IMAGE_REGION> --platform managed --project <GCP_PROJECT>`

## Terraform (GCP) example
I added a `main-gcp.tf` example in the `Deploying a Serverless Application using GCP Cloud Functions and Terraform/` folder that demonstrates provisioning a storage bucket and a Cloud Function. There is also a `terraform-gcp.yml` workflow that runs `terraform fmt`, `terraform init`, `terraform validate`, and `terraform plan`, and a gated `terraform-gcp-apply.yml` workflow that performs `terraform apply` and is intended to be run manually (it targets the `production` environment which can be protected by branch/reviewer rules).

Additional secrets for Terraform GCP plan and apply:
- `GCP_SERVICE_ACCOUNT_KEY` — used to authenticate Terraform jobs and deployment workflows.
- `GCP_PROJECT` — passed as `TF_VAR_project` for Terraform planning and used as the gcloud project.

## Cloud Functions
- I added a `app_gcp.py` Cloud Function-compatible handler and a `cloud-functions-deploy.yml` workflow that deploys an HTTP-triggered Cloud Function named `hello-function`.
- For Cloud Functions deployment, ensure the service account referenced by `GCP_SERVICE_ACCOUNT_KEY` has `roles/cloudfunctions.developer` and `roles/storage.admin` (or least-privilege equivalents).

## Required GCP IAM roles (suggested)
- Artifact Registry write: `roles/artifactregistry.writer` or `roles/artifactregistry.admin`
- Cloud Run deploy: `roles/run.admin` and `roles/iam.serviceAccountUser`
- Cloud Functions deploy: `roles/cloudfunctions.developer` and `roles/storage.admin`
- Terraform / infra: `roles/editor` or a scoped set of IAM roles for specific resources (recommended to scope down in production)

## Canary / rollout
- The Cloud Run deploy workflow uses a simple canary: it deploys a new revision with no traffic, shifts 10% traffic to it, waits 30s, then promotes it to 100% traffic. Modify the sleep duration or percentages if you want a different rollout policy.

---

## Project overview & how CI ties things together
This repository contains independent example projects. They do not run as a single monolith; CI is set up so each subproject's pipelines run when files in that subproject change. High-level notes:

- **Independent projects**: Each top-level folder (for example, `Containerized Web Application using Docker and Kubernetes`, `Deploying a Serverless Application using GCP Cloud Functions and Terraform`, `Deploying a Machine Learning Model using TensorFlow, Docker, and Kubernetes `, etc.) is self-contained with its own Dockerfile/terraform/k8s manifests and smoke tests.

- **CI triggers & concurrency**: Workflows are configured with `paths` filters so only relevant workflows run on a push/PR. Multiple workflows may run in parallel when a change touches several folders (e.g., `python-ci`, `docker-build`, and `terraform` can run concurrently).

- **Build → Deploy coordination**: To avoid race conditions where a deploy starts before an image is pushed, the Cloud Run and GKE deploy workflows are triggered on successful completion of the Docker build workflow (`workflow_run`) in addition to push/dispatch triggers. This helps ensure deploys use images that were built for the same commit.

## CI flow (ASCII diagram)
Build (docker-build) [push images]  --->  Deploy (cloud-run-deploy / gke-deploy)
If build fails ----------------------------^ (deploy will not run when triggered by workflow_run unless build succeeded)

- **Manual gating**: The Terraform `apply` job is gated by `workflow_dispatch` and targets the `production` environment (recommended to require manual approvals for production changes).

## Secrets & environment variables used by CI
- `GCP_SERVICE_ACCOUNT_KEY` — JSON service account key used by GH Actions to authenticate to GCP.
- `GCP_PROJECT` — GCP project id.
- `IMAGE_REGION` — Artifact Registry / Cloud Run region (e.g., `us-central1`).
- `AR_REPOSITORY` — Artifact Registry repository name.

## How to run locally
- Run all tests: `pytest -q`
- Build a Docker image and push locally (example):
  - `docker build -t us-central1-docker.pkg.dev/<GCP_PROJECT>/<AR_REPOSITORY>/containerized-webapp:local .` inside the `Containerized Web Application using Docker and Kubernetes` folder
  - `gcloud auth configure-docker --quiet` and `docker push <image>`
- Run Terraform plan locally in the serverless folder (requires gcloud auth):
  - `cd "Deploying a Serverless Application using GCP Cloud Functions and Terraform"`
  - `gcloud auth activate-service-account --key-file=$GCP_SERVICE_ACCOUNT_KEY`
  - `terraform init` && `terraform plan -var="project=$GCP_PROJECT"`

## Notes & gotchas
- The CI matrix builds several images in parallel; if you rely on a deploy workflow to pick up newly pushed images, prefer the `workflow_run` trigger or add a small delay / check for image existence to avoid race conditions.
- Some tests will be skipped in CI runners if Google Cloud libraries are not installed locally (tests use `pytest.skip` in that case).

If you'd like, I can add a short ASCII flow showing build → push → deploy and include a sample `workflow_run` snippet in the README. Tell me if you want the diagram and an automated `workflow_run` trigger added to `cloud-run-deploy.yml` (recommended).
## Security notes
- Protect the `production` environment in GitHub to require manual approvals for the Terraform apply workflow.

### How to protect the `production` environment (recommended)
You can protect the `production` environment using the GitHub UI or the `gh` CLI. The `terraform-gcp-apply.yml` workflow already targets the `production` environment, so protecting it will force manual approvals before the job runs.

Option A — GitHub UI (recommended):
1. Go to your repository Settings → Environments → **New environment** and create an environment named `production`.
2. Click **Configure environment protection rules** and set:
   - **Required reviewers** (select individual users or teams who must approve deployments).
   - Optional: **Required reviewers wait timer** (time window before deployments are allowed to proceed).
   - Optional: **Deployment branches** (limit which branches can deploy to production).
3. Save changes. The `terraform-gcp-apply.yml` job will now require approval from one of the required reviewers before running.

Option B — GitHub CLI + API (for automation):
You can use the GitHub REST API to configure an environment protection rule programmatically. Below is a helper script template you can run locally (requires `GH_TOKEN` or `GITHUB_TOKEN` with repo admin privileges). Update the reviewer IDs as needed.

```bash
# .github/scripts/create_production_env.sh
#!/usr/bin/env bash
set -euo pipefail

OWNER="<your-github-org-or-user>"
REPO="<your-repo>"
ENV="production"
TOKEN="${GH_TOKEN:-$GITHUB_TOKEN:-}" # Export GH_TOKEN before running

if [ -z "$TOKEN" ]; then
  echo "Please export GH_TOKEN or GITHUB_TOKEN with repo admin permissions"
  exit 1
fi

# Create environment (idempotent)
curl -s -S -X PUT -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/${OWNER}/${REPO}/environments/${ENV}

# Set protection rules (example payload — replace reviewer ids)
read -r -d '' PAYLOAD <<'JSON'
{
  "wait_timer": 0,
  "reviewers": [
    { "type": "User", "id": 1234567 }
  ]
}
JSON

curl -s -S -X PUT -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github+json" \
  -d "$PAYLOAD" https://api.github.com/repos/${OWNER}/${REPO}/environments/${ENV}/protection

echo "Configured environment ${ENV} in ${OWNER}/${REPO}. Update the script with real IDs and run again if needed."
```

Notes:
- To get numeric user IDs you can query: `curl -H "Authorization: token $TOKEN" https://api.github.com/users/<username>` and read the `id` field.
- Run the script locally with: `GH_TOKEN=<token> ./create_production_env.sh`.

---

If you want, I can (choose one):
- Run the script for you (requires an admin token added as a secret temporarily), or
- Prepare a PR with the script and walk you through running it locally. 

If you prefer, I can also add a Slack notification or required checklist step before the apply runs—tell me which option you prefer.

If you want, I can add an optional step to the workflow to automatically deploy the pushed image to a GKE cluster (requires `KUBE_CONFIG` or GKE credentials).

## GKE deploy (optional)
I added `.github/workflows/gke-deploy.yml` as an optional workflow that:
- Authenticates with GCP using `GCP_SERVICE_ACCOUNT_KEY`.
- Retrieves GKE credentials for a cluster (`GKE_CLUSTER`, `GKE_LOCATION`).
- Finds and applies any `deployment.yaml` files in the repo and waits briefly for rollouts.

Required secrets for GKE deploy (suggested names):
- `GCP_SERVICE_ACCOUNT_KEY` — service account JSON with `roles/container.admin` or sufficient RBAC to deploy to the cluster.
- `GCP_PROJECT` — the GCP project id.
- `GKE_CLUSTER` — GKE cluster name.
- `GKE_LOCATION` — GKE cluster zone or region (e.g., `us-central1` or `us-central1-a`).
- `KUBECONFIG` (optional) — base64 encoded kubeconfig if you prefer that over `get-gke-credentials`.

Notes:
- The workflow is deliberately conservative: it is manually triggered (workflow_dispatch) and will only run on pushes that include `deployment.yaml` files.
- The workflow uses `yq` if available to attempt to determine the deployment name for rollout waiting; it tolerates failures and performs best-effort waiting.
