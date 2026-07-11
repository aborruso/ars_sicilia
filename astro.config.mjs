import { readFileSync } from 'fs';
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';
import remarkDefaultLayout from './src/lib/remark-default-layout.mjs';

// Redirect dai vecchi slug categoria (pre-vocabolario controllato) ai nuovi.
// Stessa logica di slugify in src/lib/utils.ts.
const slugify = (text) =>
  text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');

const vocabolario = JSON.parse(readFileSync('./data/vocabolario_categorie.json', 'utf8'));
const vocabSlugs = new Set(vocabolario.categorie.map((c) => slugify(c.label)));
const { mapping } = JSON.parse(readFileSync('./data/category_mapping.json', 'utf8'));
const categoryRedirects = {};
for (const [oldName, target] of Object.entries(mapping)) {
  const oldSlug = slugify(oldName);
  if (vocabSlugs.has(oldSlug)) continue; // slug già occupato da una pagina reale
  const first = Array.isArray(target) ? target[0] : target;
  categoryRedirects[`/sedute/categoria/${oldSlug}`] =
    `/ars_sicilia/sedute/categoria/${slugify(first)}`;
}

export default defineConfig({
  site: 'https://aborruso.github.io',
  base: '/ars_sicilia',
  redirects: categoryRedirects,
  integrations: [
    tailwind(),
    sitemap({ filter: (page) => !page.includes('/labs/') }),
    mdx(),
  ],
  markdown: {
    remarkPlugins: [[remarkDefaultLayout, { layout: 'src/layouts/PageLayout.astro' }]],
  },
  output: 'static',
  build: {
    format: 'directory',
  },
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: undefined,
        },
      },
    },
  },
});
