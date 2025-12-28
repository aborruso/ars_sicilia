import fs from 'fs';
import path from 'path';
import { parse as csvParse } from 'csv-parse/sync';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DATA_DIR = path.resolve(__dirname, '../data');
const OUTPUT_DIR = path.resolve(__dirname, '../src/data/processed');

console.log('🚀 Starting data processing...');

// 1. Load CSV anagrafica
console.log('📊 Loading anagrafica_video.csv...');
const csvContent = fs.readFileSync(path.join(DATA_DIR, 'anagrafica_video.csv'), 'utf-8');
const videos = csvParse(csvContent, { columns: true, skip_empty_lines: true });
console.log(`   Found ${videos.length} video records`);

// 2. Load JSONL disegni
console.log('📜 Loading disegni_legge.jsonl...');
const jsonlPath = path.join(DATA_DIR, 'disegni_legge.jsonl');
const jsonlContent = fs.readFileSync(jsonlPath, 'utf-8');
const disegni = jsonlContent.trim().split('\n')
  .filter(line => line.trim())
  .map(line => JSON.parse(line));
console.log(`   Found ${disegni.length} disegni records`);

// 3. Load digest JSON files
console.log('💬 Loading digest files...');
const digestDir = path.join(DATA_DIR, 'digest');
const digestMap = new Map();

const digestFiles = fs.readdirSync(digestDir).filter(file => file.endsWith('.json'));
digestFiles.forEach(file => {
  const youtubeId = file.replace('.json', '');
  const filePath = path.join(digestDir, file);
  const content = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

  // Skip empty or invalid digests
  if (content.digest && content.digest.trim().length > 10) {
    digestMap.set(youtubeId, content);
  }
});
console.log(`   Found ${digestMap.size} valid digests (out of ${digestFiles.length} files)`);

// 4. Aggregate sedute
console.log('🔗 Aggregating sedute...');
const seduteMap = new Map();

videos.forEach(video => {
  const sedutaKey = `${video.numero_seduta}-${video.data_seduta}`;

  if (!seduteMap.has(sedutaKey)) {
    seduteMap.set(sedutaKey, {
      numero: parseInt(video.numero_seduta, 10),
      dataSeduta: video.data_seduta,
      urlPagina: video.url_pagina,
      odgUrl: video.odg_url || null,
      resocontoUrl: video.resoconto_url || null,
      resocontoProvvisorioUrl: video.resoconto_provvisorio_url || null,
      resocontoStenograficoUrl: video.resoconto_stenografico_url || null,
      allegatoUrl: video.allegato_url || null,
      videos: [],
      disegniLegge: [],
      categories: new Set(),
    });
  }

  const seduta = seduteMap.get(sedutaKey);

  // Add video
  const videoData = {
    idVideo: parseInt(video.id_video, 10),
    oraVideo: video.ora_video,
    dataVideo: video.data_video,
    youtubeId: video.youtube_id,
    videoPageUrl: video.video_page_url,
    durationMinutes: parseInt(video.duration_minutes, 10) || 0,
    status: video.status || (video.youtube_id ? 'success' : 'pending'),
    digest: digestMap.get(video.youtube_id) || null,
    slug: `video-${video.ora_video.replace(':', '')}`,
  };

  seduta.videos.push(videoData);

  // Aggregate categories from digest
  if (videoData.digest?.categories) {
    videoData.digest.categories.forEach(cat => seduta.categories.add(cat));
  }
});

console.log(`   Aggregated ${seduteMap.size} sedute`);

// 5. Add disegni to sedute (join by odg_url = pdf_url)
console.log('📑 Linking disegni to sedute...');
let disegniLinked = 0;

disegni.forEach(disegno => {
  for (const [key, seduta] of seduteMap) {
    if (seduta.odgUrl === disegno.pdf_url) {
      // Check if not already added (avoid duplicates)
      const exists = seduta.disegniLegge.some(d => d.numero === disegno.numero_disegno);
      if (!exists) {
        seduta.disegniLegge.push({
          titolo: disegno.titolo_disegno,
          numero: disegno.numero_disegno,
          legislatura: disegno.legislatura,
          urlDisegno: disegno.url_disegno,
        });
        disegniLinked++;
      }
    }
  }
});

console.log(`   Linked ${disegniLinked} disegni to sedute`);

// 6. Convert to arrays and add slugs/metadata
console.log('✨ Finalizing data structure...');
const sedute = Array.from(seduteMap.values()).map(seduta => {
  const [year, month, day] = seduta.dataSeduta.split('-');

  return {
    ...seduta,
    categories: Array.from(seduta.categories).sort(),
    slug: `seduta-${seduta.numero}`,
    yearMonthDay: { year, month, day },
    // Sort videos by data_video + ora_video
    videos: seduta.videos.sort((a, b) => {
      const dateCompare = a.dataVideo.localeCompare(b.dataVideo);
      return dateCompare !== 0 ? dateCompare : a.oraVideo.localeCompare(b.oraVideo);
    }),
  };
});

// Sort sedute by dataSeduta DESC
sedute.sort((a, b) => b.dataSeduta.localeCompare(a.dataSeduta));

// 7. Extract all videos with enriched data
const allVideos = sedute.flatMap(seduta =>
  seduta.videos.map(video => ({
    ...video,
    seduta: {
      numero: seduta.numero,
      dataSeduta: seduta.dataSeduta,
      slug: seduta.slug,
      yearMonthDay: seduta.yearMonthDay,
    },
  }))
);

// 8. Extract categories with counts
const categoryCount = new Map();
allVideos.forEach(video => {
  video.digest?.categories?.forEach(cat => {
    categoryCount.set(cat, (categoryCount.get(cat) || 0) + 1);
  });
});

const categories = Array.from(categoryCount.entries())
  .map(([name, count]) => ({
    name,
    count,
    slug: name.toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, ''),
  }))
  .sort((a, b) => b.count - a.count);

// 9. Write output files
console.log('💾 Writing processed data...');
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

fs.writeFileSync(
  path.join(OUTPUT_DIR, 'sedute.json'),
  JSON.stringify(sedute, null, 2)
);

fs.writeFileSync(
  path.join(OUTPUT_DIR, 'videos.json'),
  JSON.stringify(allVideos, null, 2)
);

fs.writeFileSync(
  path.join(OUTPUT_DIR, 'categories.json'),
  JSON.stringify(categories, null, 2)
);

console.log('✅ Data processing completed!');
console.log(`   - ${sedute.length} sedute → src/data/processed/sedute.json`);
console.log(`   - ${allVideos.length} videos → src/data/processed/videos.json`);
console.log(`   - ${categories.length} categories → src/data/processed/categories.json`);
