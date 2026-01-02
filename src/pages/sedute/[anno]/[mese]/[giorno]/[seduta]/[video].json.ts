import type { APIRoute } from 'astro';
import { loadSedute } from '../../../../../../lib/data-loader';

export async function getStaticPaths() {
  const sedute = await loadSedute();
  const paths = [];

  sedute.forEach((seduta) => {
    seduta.videos.forEach((video) => {
      paths.push({
        params: {
          anno: seduta.yearMonthDay.year,
          mese: seduta.yearMonthDay.month,
          giorno: seduta.yearMonthDay.day,
          seduta: seduta.slug,
          video: video.slug,
        },
        props: { seduta, video },
      });
    });
  });

  return paths;
}

export const GET: APIRoute = async ({ props }) => {
  const { seduta, video } = props;

  const dateStr = new Date(video.dataVideo).toLocaleDateString('it-IT', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const resources = {
    seduta: {
      numero: seduta.numero,
      data: seduta.dataSeduta,
    },
    video: {
      ora: video.oraVideo,
      data: video.dataVideo,
      durataMinuti: video.durationMinutes,
      youtubeId: video.youtubeId,
    },
    risorse: {
      trascrizione: video.youtubeId
        ? `https://raw.githubusercontent.com/aborruso/ars_sicilia/main/data/trascrizioni/${video.youtubeId}.it.txt`
        : null,
      ordinedelgiorno: seduta.odgUrl || null,
      video: `https://www.youtube.com/watch?v=${video.youtubeId}`,
    },
  };

  return new Response(JSON.stringify(resources, null, 2), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
    },
  });
};
