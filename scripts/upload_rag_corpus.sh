#!/usr/bin/env bash
# Carica il corpus RAG (data/rag_corpus/*.md) nel bucket R2 usato da Cloudflare AI Search.
# Prerequisiti: wrangler autenticato (CLOUDFLARE_API_TOKEN o `wrangler login`).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORPUS_DIR="$REPO_ROOT/data/rag_corpus"
BUCKET="${RAG_BUCKET:-ars-trascrizioni}"

if [ ! -d "$CORPUS_DIR" ]; then
  echo "Corpus non trovato: $CORPUS_DIR — genera prima con scripts/build_rag_corpus.py" >&2
  exit 1
fi

count=0
for f in "$CORPUS_DIR"/*.md; do
  key="$(basename "$f")"
  npx wrangler r2 object put "$BUCKET/$key" --file "$f" --content-type "text/markdown" --remote
  count=$((count + 1))
done

echo "Caricati $count file in r2://$BUCKET"
