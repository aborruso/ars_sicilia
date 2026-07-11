#!/usr/bin/env node
// One-off: riclassifica le categorie dei digest storici (pre-vocabolario) con il LLM.
// Per ogni data/digest/*.json passa il TESTO del digest (non la trascrizione) a `llm`
// con lo schema enum derivato da config/digest-schema.json: il modello sceglie le 1–5
// categorie centrali dal vocabolario controllato. Tocca solo l'array `categories`.
// Uso: node scripts/reclassify_digest_categories.mjs [--only-over 5] [--limit N]

import fs from 'fs';
import os from 'os';
import path from 'path';
import { spawnSync } from 'child_process';
import { fileURLToPath } from 'url';

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIGEST_DIR = path.join(REPO_ROOT, 'data', 'digest');
const MODEL = 'gemini-2.5-flash';
const SLEEP_MS = 4000;
const MAX_RETRIES = 3;

const args = process.argv.slice(2);
const getArg = (name) => {
  const i = args.indexOf(name);
  return i !== -1 ? Number(args[i + 1]) : 0;
};
const onlyOver = getArg('--only-over'); // riclassifica solo digest con più di N categorie
const limit = getArg('--limit');

const vocab = JSON.parse(
  fs.readFileSync(path.join(REPO_ROOT, 'data', 'vocabolario_categorie.json'), 'utf8')
);
const validLabels = new Set(vocab.categorie.map((c) => c.label));
const catList = vocab.categorie.map((c) => `- ${c.label}: ${c.descrizione}`).join('\n');

const fullSchema = JSON.parse(
  fs.readFileSync(path.join(REPO_ROOT, 'config', 'digest-schema.json'), 'utf8')
);
const schema = {
  type: 'object',
  properties: { categories: fullSchema.properties.categories },
  required: ['categories'],
};
const schemaPath = path.join(os.tmpdir(), 'ars-classify-schema.json');
fs.writeFileSync(schemaPath, JSON.stringify(schema));

const systemPrompt = `Sei un classificatore. Ti viene dato il digest di una seduta dell'Assemblea Regionale Siciliana. Assegna da 1 a 5 categorie scegliendo SOLO dal vocabolario controllato, etichette esatte, senza ripetizioni. Scegli solo i temi CENTRALI della seduta (quelli su cui si è discusso o votato davvero), non le menzioni di passaggio.

Vocabolario:
${catList}`;

function classify(digestText) {
  const result = spawnSync(
    'llm',
    ['prompt', '--no-log', '-m', MODEL, '--schema', schemaPath, '-s', systemPrompt],
    { input: digestText, encoding: 'utf8', timeout: 120000 }
  );
  if (result.status !== 0) {
    throw new Error(`llm: ${(result.stderr || '').trim()}`);
  }
  const parsed = JSON.parse(result.stdout.trim());
  const cats = [...new Set(parsed.categories)];
  if (!cats.length || cats.length > 5 || cats.some((c) => !validLabels.has(c))) {
    throw new Error(`output non valido: ${JSON.stringify(parsed.categories)}`);
  }
  return cats;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const files = fs.readdirSync(DIGEST_DIR).filter((f) => f.endsWith('.json'));
let done = 0;
let skipped = 0;
let failed = 0;

for (const file of files) {
  const filePath = path.join(DIGEST_DIR, file);
  const digest = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  if (!digest.digest || !Array.isArray(digest.categories)) {
    skipped += 1;
    continue;
  }
  if (onlyOver && digest.categories.length <= onlyOver) {
    skipped += 1;
    continue;
  }

  let cats = null;
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt += 1) {
    try {
      cats = classify(digest.digest);
      break;
    } catch (err) {
      console.error(`${file}: tentativo ${attempt}/${MAX_RETRIES} fallito — ${err.message}`);
      if (attempt < MAX_RETRIES) await sleep(SLEEP_MS * attempt);
    }
  }
  if (!cats) {
    failed += 1;
    continue;
  }

  console.log(`${file}: ${digest.categories.length} -> ${cats.length}  [${cats.join(', ')}]`);
  digest.categories = cats;
  fs.writeFileSync(filePath, JSON.stringify(digest, null, 2) + '\n');
  done += 1;
  if (limit && done >= limit) break;
  await sleep(SLEEP_MS);
}

console.log(`\nRiclassificati: ${done} | Saltati: ${skipped} | Falliti: ${failed}`);
if (failed > 0) process.exitCode = 1;
