// GitHub raw content URLs for data resources
export const GITHUB_RAW_BASE_URL = 'https://raw.githubusercontent.com/aborruso/ars_sicilia/main';

// Build full URLs for transcripts
export const getTranscriptTxtUrl = (youtubeId: string) =>
  `${GITHUB_RAW_BASE_URL}/data/trascrizioni/${youtubeId}.it.txt`;

export const getTranscriptSrtUrl = (youtubeId: string) =>
  `${GITHUB_RAW_BASE_URL}/data/trascrizioni/${youtubeId}.it.srt`;
