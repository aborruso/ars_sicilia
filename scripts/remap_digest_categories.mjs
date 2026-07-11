#!/usr/bin/env node
// One-off: normalizza l'array `categories` di ogni data/digest/*.json applicando
// data/category_mapping.json. Tutti gli altri campi restano invariati.
// Idempotente: le label già a vocabolario passano invariate. Nessuna chiamata LLM.
// Uso: node scripts/remap_digest_categories.mjs [--dry-run]

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIGEST_DIR = path.join(REPO_ROOT, 'data', 'digest');
const dryRun = process.argv.includes('--dry-run');

const vocab = JSON.parse(
  fs.readFileSync(path.join(REPO_ROOT, 'data', 'vocabolario_categorie.json'), 'utf8')
);
const validLabels = new Set(vocab.categorie.map((c) => c.label));

const { mapping } = JSON.parse(
  fs.readFileSync(path.join(REPO_ROOT, 'data', 'category_mapping.json'), 'utf8')
);

function remap(categories) {
  const out = [];
  for (const cat of categories) {
    let targets;
    if (validLabels.has(cat)) {
      targets = [cat];
    } else if (cat in mapping) {
      targets = Array.isArray(mapping[cat]) ? mapping[cat] : [mapping[cat]];
    } else {
      throw new Error(`Categoria senza mapping: "${cat}"`);
    }
    for (const t of targets) {
      if (!validLabels.has(t)) throw new Error(`Target fuori vocabolario: "${t}"`);
      if (!out.includes(t)) out.push(t);
    }
  }
  return out;
}

const files = fs.readdirSync(DIGEST_DIR).filter((f) => f.endsWith('.json'));
let changed = 0;
for (const file of files) {
  const filePath = path.join(DIGEST_DIR, file);
  const digest = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  if (!Array.isArray(digest.categories)) continue;
  const before = JSON.stringify(digest.categories);
  const after = remap(digest.categories);
  if (before === JSON.stringify(after)) continue;
  changed += 1;
  if (dryRun) {
    console.log(`${file}: ${before} -> ${JSON.stringify(after)}`);
  } else {
    digest.categories = after;
    fs.writeFileSync(filePath, JSON.stringify(digest, null, 2) + '\n');
  }
}
console.log(`${dryRun ? '[dry-run] ' : ''}File aggiornati: ${changed}/${files.length}`);
