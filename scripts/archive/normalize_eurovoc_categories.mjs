#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import http from 'http';
import https from 'https';
import { spawnSync } from 'child_process';

const DEFAULT_MODEL = 'gemini-2.5-flash';
const DEFAULT_REVIEW_THRESHOLD = 0.75;
const DEFAULT_DUMP_BASE = 'http://publications.europa.eu/resource/dataset/eurovoc';
const DEFAULT_DUMP_ZIP_TEMPLATE = (version) =>
  `http://publications.europa.eu/resource/distribution/eurovoc/${version}/zip/skos_core/eurovoc_in_skos_core_concepts.zip`;

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!arg.startsWith('--')) {
      args._.push(arg);
      continue;
    }
    const [key, value] = arg.includes('=') ? arg.split('=') : [arg, null];
    const k = key.replace(/^--/, '');
    if (value !== null) {
      args[k] = value;
      continue;
    }
    const next = argv[i + 1];
    if (next && !next.startsWith('--')) {
      args[k] = next;
      i += 1;
    } else {
      args[k] = true;
    }
  }
  return args;
}

function normalizeText(value) {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function tokenize(value) {
  const normalized = normalizeText(value);
  if (!normalized) return [];
  return normalized.split(' ').filter(Boolean);
}

function scoreCandidate(category, label) {
  if (!label) return 0;
  const normCategory = normalizeText(category);
  const normLabel = normalizeText(label);
  if (!normCategory || !normLabel) return 0;
  if (normCategory === normLabel) return 100;
  let score = 0;
  if (normLabel.includes(normCategory)) score += 10;
  const categoryTokens = tokenize(category);
  const labelTokens = tokenize(label);
  const labelSet = new Set(labelTokens);
  let overlap = 0;
  for (const token of categoryTokens) {
    if (labelSet.has(token)) overlap += 1;
  }
  score += overlap * 4;
  const union = new Set([...categoryTokens, ...labelTokens]).size || 1;
  score += (overlap / union) * 5;
  return score;
}

function fetchText(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    client
      .get(url, (res) => {
        if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          resolve(fetchText(res.headers.location));
          return;
        }
        if (res.statusCode !== 200) {
          reject(new Error(`Request failed (${res.statusCode}) for ${url}`));
          return;
        }
        let data = '';
        res.setEncoding('utf8');
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => resolve(data));
      })
      .on('error', reject);
  });
}

function downloadFile(url, destPath) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    client
      .get(url, (res) => {
        if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          resolve(downloadFile(res.headers.location, destPath));
          return;
        }
        if (res.statusCode !== 200) {
          reject(new Error(`Download failed (${res.statusCode}) for ${url}`));
          return;
        }
        const file = fs.createWriteStream(destPath);
        res.pipe(file);
        file.on('finish', () => file.close(resolve));
      })
      .on('error', (err) => {
        fs.unlink(destPath, () => reject(err));
      });
  });
}

async function resolveLatestVersion(baseUrl) {
  const rdf = await fetchText(baseUrl);
  const matches = [...rdf.matchAll(/http:\/\/publications\.europa\.eu\/resource\/dataset\/eurovoc\/(\d{8}-0)/g)];
  if (!matches.length) {
    throw new Error('Impossibile determinare la versione EuroVoc più recente.');
  }
  const versions = [...new Set(matches.map((m) => m[1]))];
  versions.sort();
  return versions[versions.length - 1];
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function extractRdfFromZip(zipPath, rdfPath) {
  const result = spawnSync('unzip', ['-p', zipPath, 'eurovoc_in_skos_core_concepts.rdf'], {
    encoding: 'buffer',
    maxBuffer: 1024 * 1024 * 256,
  });
  if (result.status !== 0) {
    const stderr = result.stderr ? result.stderr.toString('utf8') : '';
    throw new Error(`Errore unzip: ${stderr}`.trim());
  }
  fs.writeFileSync(rdfPath, result.stdout);
}

function loadEurovocConcepts(rdfPath) {
  const concepts = [];
  const file = fs.readFileSync(rdfPath, 'utf8');
  const lines = file.split(/\r?\n/);
  let currentUri = null;
  let labelIt = null;
  let labelEn = null;

  for (const line of lines) {
    const aboutMatch = line.match(/<rdf:Description rdf:about="(http:\/\/eurovoc\.europa\.eu\/\d+)"/);
    if (aboutMatch) {
      currentUri = aboutMatch[1];
      labelIt = null;
      labelEn = null;
      continue;
    }
    if (!currentUri) continue;

    const itMatch = line.match(/<prefLabel[^>]*xml:lang="it">([^<]+)<\/prefLabel>/);
    if (itMatch) {
      labelIt = itMatch[1].trim();
    }
    const enMatch = line.match(/<prefLabel[^>]*xml:lang="en">([^<]+)<\/prefLabel>/);
    if (enMatch) {
      labelEn = enMatch[1].trim();
    }
    if (line.includes('</rdf:Description>')) {
      if (currentUri && labelIt) {
        concepts.push({ uri: currentUri, label_it: labelIt, label_en: labelEn || '' });
      }
      currentUri = null;
      labelIt = null;
      labelEn = null;
    }
  }

  return concepts;
}

function selectCandidates(category, concepts, limit = 25) {
  const scored = concepts
    .map((concept) => {
      const scoreIt = scoreCandidate(category, concept.label_it);
      const scoreEn = scoreCandidate(category, concept.label_en);
      return {
        ...concept,
        score: Math.max(scoreIt, scoreEn),
      };
    })
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);

  if (!scored.length) {
    return concepts.slice(0, limit);
  }
  return scored;
}

function runLlmMatch({ category, candidates, model, schemaPath, timeoutMs }) {
  const prompt = `Seleziona la voce EuroVoc più adatta per la categoria: "${category}".\n\nScegli ESCLUSIVAMENTE tra queste opzioni (URI + label IT/EN):\n${JSON.stringify(candidates, null, 2)}\n\nRispondi con JSON conforme allo schema. Se nessuna voce è adatta, usa stringhe vuote per eurovoc_uri, eurovoc_label_it, eurovoc_label_en e confidence=0.`;

  const result = spawnSync('llm', ['prompt', '--no-log', '-m', model, '--schema', schemaPath], {
    input: prompt,
    encoding: 'utf8',
    timeout: timeoutMs,
  });

  if (result.status !== 0) {
    const stderr = result.stderr ? result.stderr.toString() : '';
    throw new Error(`Errore llm: ${stderr}`.trim());
  }

  const output = result.stdout.trim();
  if (!output) {
    throw new Error('Output vuoto da llm.');
  }

  return JSON.parse(output);
}

async function main() {
  const args = parseArgs(process.argv);
  const cwd = process.cwd();

  const categoriesPath = path.resolve(cwd, args.categories || 'src/data/processed/categories.json');
  const mappingPath = path.resolve(cwd, args.mapping || 'data/eurovoc_mapping.json');
  const dumpDir = path.resolve(cwd, args['dump-dir'] || 'data/eurovoc');
  const model = args.model || DEFAULT_MODEL;
  const reviewThreshold = Number(args['review-threshold'] || DEFAULT_REVIEW_THRESHOLD);
  const timeoutMs = Number(args['timeout-ms'] || 120000);
  const refreshDump = Boolean(args['refresh-dump']);
  const version = args.version || (await resolveLatestVersion(DEFAULT_DUMP_BASE));

  ensureDir(dumpDir);

  const zipPath = path.join(dumpDir, `eurovoc_in_skos_core_concepts_${version}.zip`);
  const rdfPath = path.join(dumpDir, `eurovoc_in_skos_core_concepts_${version}.rdf`);
  const dumpUrl = DEFAULT_DUMP_ZIP_TEMPLATE(version);

  if (refreshDump || !fs.existsSync(zipPath)) {
    console.log(`Scarico EuroVoc ${version}...`);
    await downloadFile(dumpUrl, zipPath);
  }

  if (refreshDump || !fs.existsSync(rdfPath)) {
    console.log('Estraggo RDF dal dump...');
    extractRdfFromZip(zipPath, rdfPath);
  }

  const categoriesRaw = JSON.parse(fs.readFileSync(categoriesPath, 'utf8'));
  const categories = categoriesRaw.map((item) => item.name).filter(Boolean);

  let mappingData = { metadata: {}, mappings: [] };
  if (fs.existsSync(mappingPath)) {
    mappingData = JSON.parse(fs.readFileSync(mappingPath, 'utf8'));
  }

  const existingMap = new Map(
    (mappingData.mappings || []).map((entry) => [entry.category, entry])
  );

  let toProcess = categories.filter((name) => !existingMap.has(name));
  const limit = Number(args.limit || 0);
  if (limit > 0) {
    toProcess = toProcess.slice(0, limit);
  }
  if (!toProcess.length) {
    console.log('Nessuna nuova categoria da mappare.');
    return;
  }

  console.log(`Carico concetti EuroVoc (${version})...`);
  const concepts = loadEurovocConcepts(rdfPath);
  if (!concepts.length) {
    throw new Error('Nessun concetto EuroVoc caricato.');
  }

  const schemaPath = path.resolve(cwd, 'config/eurovoc-match-schema.json');
  if (!fs.existsSync(schemaPath)) {
    throw new Error('Schema mancante: config/eurovoc-match-schema.json');
  }

  const newMappings = [];
  for (const category of toProcess) {
    const candidates = selectCandidates(category, concepts);
    const response = runLlmMatch({ category, candidates, model, schemaPath, timeoutMs });
    const confidence = Number(response.confidence || 0);
    const uri = response.eurovoc_uri || '';
    const labelIt = response.eurovoc_label_it || '';
    const labelEn = response.eurovoc_label_en || '';
    const status = confidence < reviewThreshold ? 'review' : 'accepted';
    newMappings.push({
      category,
      eurovoc_uri: uri || null,
      eurovoc_label_it: labelIt || null,
      eurovoc_label_en: labelEn || null,
      confidence,
      status,
      updated_at: new Date().toISOString(),
    });
    console.log(`- ${category} -> ${labelIt || 'NO_MATCH'} (${confidence})`);
  }

  const updatedMappings = [...(mappingData.mappings || []), ...newMappings];
  const metadata = {
    source: DEFAULT_DUMP_BASE,
    dump_url: dumpUrl,
    dump_version: version,
    dump_path: path.relative(cwd, rdfPath),
    model,
    review_threshold: reviewThreshold,
    updated_at: new Date().toISOString(),
  };

  const output = {
    metadata: { ...(mappingData.metadata || {}), ...metadata },
    mappings: updatedMappings,
  };

  fs.writeFileSync(mappingPath, JSON.stringify(output, null, 2));
  console.log(`Mapping aggiornato: ${path.relative(cwd, mappingPath)}`);
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
