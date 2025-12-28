import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { loadVideos } from '../lib/data-loader';
import { formatDateShort, truncateText } from '../lib/utils';

export async function GET(context: APIContext) {
  const videos = await loadVideos();

  // Sort by date DESC and take last 20
  videos.sort((a, b) => {
    const dateCompare = b.dataVideo.localeCompare(a.dataVideo);
    return dateCompare !== 0 ? dateCompare : b.oraVideo.localeCompare(a.oraVideo);
  });

  const recentVideos = videos.slice(0, 20);

  return rss({
    title: 'ARS Sicilia - Sedute Assemblea',
    description: 'Ultimi video e trascrizioni delle sedute dell\'Assemblea Regionale Siciliana',
    site: context.site || 'https://aborruso.github.io/ars_sicilia',
    items: recentVideos.map((video) => {
      const videoUrl = `/sedute/${video.seduta.yearMonthDay.year}/${video.seduta.yearMonthDay.month}/${video.seduta.yearMonthDay.day}/${video.seduta.slug}/${video.slug}`;
      const description = video.digest?.digest
        ? truncateText(video.digest.digest.replace(/[#*\n]/g, ' '), 300)
        : `Video della seduta ${video.seduta.numero} del ${formatDateShort(video.dataVideo)} alle ore ${video.oraVideo}`;

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
