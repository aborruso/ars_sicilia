#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Repo root: ${REPO_ROOT}"

echo "==> 1) git pull"
git -C "${REPO_ROOT}" pull

echo "==> 2) download transcripts"
"${REPO_ROOT}/scripts/download_transcripts.sh"

echo "==> 3) generate digests"
"${REPO_ROOT}/scripts/generate_digests.sh"

echo "Done. Next steps (manual): git add/commit/push."
