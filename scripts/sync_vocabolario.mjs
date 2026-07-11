#!/usr/bin/env node
// Propaga data/vocabolario_categorie.json (unica fonte di verità) verso:
//   - config/digest-schema.json  → enum delle categorie ammesse
//   - config/digest.yaml         → elenco categorie nel prompt (tra i marker)
// Da rilanciare (e committare l'output) ogni volta che il vocabolario cambia.

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const VOCAB_PATH = path.join(REPO_ROOT, 'data', 'vocabolario_categorie.json');
const SCHEMA_PATH = path.join(REPO_ROOT, 'config', 'digest-schema.json');
const PROMPT_PATH = path.join(REPO_ROOT, 'config', 'digest.yaml');

const vocab = JSON.parse(fs.readFileSync(VOCAB_PATH, 'utf8'));
const labels = vocab.categorie.map((c) => c.label);

if (new Set(labels).size !== labels.length) {
  console.error('Errore: label duplicate nel vocabolario.');
  process.exit(1);
}

// 1. Schema: enum chiuso
const schema = JSON.parse(fs.readFileSync(SCHEMA_PATH, 'utf8'));
schema.properties.categories = {
  type: 'array',
  items: { type: 'string', enum: labels },
  minItems: 1,
  maxItems: 5,
  uniqueItems: true,
  description:
    'From 1 to 5 categories characterizing the session, chosen EXCLUSIVELY from the controlled vocabulary (exact labels). Do not invent new categories.',
};
fs.writeFileSync(SCHEMA_PATH, JSON.stringify(schema, null, 2) + '\n');
console.log(`Schema aggiornato: enum con ${labels.length} categorie.`);

// 2. Prompt: elenco tra i marker (indentazione del blocco "prompt: |")
const BEGIN = '[INIZIO ELENCO CATEGORIE]';
const END = '[FINE ELENCO CATEGORIE]';
const promptText = fs.readFileSync(PROMPT_PATH, 'utf8');
const beginIdx = promptText.indexOf(BEGIN);
const endIdx = promptText.indexOf(END);
if (beginIdx === -1 || endIdx === -1 || endIdx < beginIdx) {
  console.error(`Errore: marker ${BEGIN} / ${END} non trovati in config/digest.yaml.`);
  process.exit(1);
}
const lineStart = promptText.lastIndexOf('\n', beginIdx) + 1;
const indent = promptText.slice(lineStart, beginIdx);
const list = vocab.categorie
  .map((c) => `${indent}- ${c.label}: ${c.descrizione}`)
  .join('\n');
const updated =
  promptText.slice(0, beginIdx + BEGIN.length) +
  '\n' +
  list +
  '\n' +
  indent +
  promptText.slice(endIdx);
fs.writeFileSync(PROMPT_PATH, updated);
console.log('Prompt aggiornato: elenco categorie rigenerato tra i marker.');
