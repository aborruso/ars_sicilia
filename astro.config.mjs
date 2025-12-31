import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';
import remarkDefaultLayout from './src/lib/remark-default-layout.mjs';

export default defineConfig({
  site: 'https://aborruso.github.io',
  base: '/ars_sicilia',
  integrations: [tailwind(), sitemap(), mdx()],
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
