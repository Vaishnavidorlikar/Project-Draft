# GitHub Workflows & Required Secrets

This repository now includes GitHub Actions workflows to make each subproject runnable and testable via GitHub CI. Below is a summary of the workflows and the secrets you should configure in your repository Settings → Secrets & variables → Actions.

## Workflows created
- `.github/workflows/python-ci.yml` — Runs pytest across Python projects (Containerized web app, Serverless, ML model, Monitoring stack, Automated deployment).
- `.github/workflows/docker-build.yml` — Builds and pushes Docker images to GitHub Container Registry (GHCR). Triggered on pushes in Docker projects.
- `.github/workflows/terraform.yml` — Runs `terraform fmt`, `terraform validate` and `terraform plan` for the serverless Terraform folder. `apply` requires manual dispatch and a GCP service account (`GCP_SERVICE_ACCOUNT_KEY`).
- `.github/workflows/gradle.yml` — Builds the Java project with Gradle.
- `.github/workflows/fastlane.yml` — Runs Fastlane-related commands for the mobile app and runs `pytest -k "not appium" to avoid device-dependent tests by default.

## Recommended secrets
- `GITHUB_TOKEN` — automatically available to workflows. Used to push to GHCR for the same repo.
- `CR_PAT` or personal token (optional) — if you prefer pushing packages to GHCR with a PAT.
- `GCP_SERVICE_ACCOUNT_KEY` and `GCP_PROJECT` — Required for Terraform plan/apply and GCP operations.
- `KUBE_CONFIG` (base64) — If you want deployment workflows to apply to a Kubernetes cluster, add your cluster config (base64-encoded). (Not included by default; add workflows carefully.)

## Notes and limitations
- Appium-based mobile tests require an emulator or device; the Fastlane workflow skips Appium tests by default. Use a self-hosted runner with devices to run those tests.
- Docker workflows push images to `ghcr.io/${{ github.repository_owner }}/...` by default. Ensure package permissions and tokens are configured if you use a different registry.
- Terraform `apply` is gated behind `workflow_dispatch` and requires a GCP service account; it won't auto-apply on PRs.

If you'd like, I can also:
- Add workflow templates to automatically build and deploy to a given k8s cluster (requires `KUBE_CONFIG`).
- Add more granular Docker images per subproject and tagging policies.
- Add caching (pip, gradle) and test matrix expansions.

---
If this looks good, I will: add any missing smoke tests (I added minimal ones), validate Python test runs locally where possible, and then proceed to add Docker deployment steps or k8s apply jobs if you'd like. 🔧