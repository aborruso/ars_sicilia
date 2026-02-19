import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { loadVideos } from '../lib/data-loader';
import { truncateText } from '../lib/utils';

export async function GET(context: APIContext) {
  const videos = await loadVideos();
  const videosWithDigest = videos.filter((video) => {
    const digestText = video.digest?.digest;
    return typeof digestText === 'string' && digestText.trim().length > 0;
  });
  const baseUrl = import.meta.env.BASE_URL;
  const basePath = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
  const siteUrl = context.site
    ? new URL(basePath, context.site).toString().replace(/\/$/, '')
    : `https://aborruso.github.io${baseUrl}`;

  // Sort by date DESC and take last 20 (digest-ready videos only)
  videosWithDigest.sort((a, b) => {
    const dateCompare = b.dataVideo.localeCompare(a.dataVideo);
    return dateCompare !== 0 ? dateCompare : b.oraVideo.localeCompare(a.oraVideo);
  });

  const recentVideos = videosWithDigest.slice(0, 20);

  return rss({
    title: 'ARS Sicilia - Sedute Assemblea',
    description: 'Ultimi video e trascrizioni delle sedute dell\'Assemblea Regionale Siciliana',
    site: siteUrl,
    items: recentVideos.map((video) => {
      const videoPath = `${basePath}sedute/${video.seduta.yearMonthDay.year}/${video.seduta.yearMonthDay.month}/${video.seduta.yearMonthDay.day}/${video.seduta.slug}/${video.slug}/`;
      const videoUrl = context.site ? new URL(videoPath, context.site).toString() : videoPath;
      const digestText = video.digest?.digest ?? '';
      const description = truncateText(digestText.replace(/[#*\n]/g, ' '), 300);

      return {
        title: `Seduta ${video.seduta.numero} - Video ${video.oraVideo}`,
        description,
        pubDate: new Date(`${video.dataVideo}T${video.oraVideo}:00`),
        link: videoUrl,
        categories: video.digest?.categories || [],
      };
    }),
  });
}
