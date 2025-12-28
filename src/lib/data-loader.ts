import type { Seduta, VideoWithSeduta, Category } from '../types/seduta';
import seduteData from '../data/processed/sedute.json';
import videosData from '../data/processed/videos.json';
import categoriesData from '../data/processed/categories.json';

export async function loadSedute(): Promise<Seduta[]> {
  return seduteData as Seduta[];
}

export async function loadVideos(): Promise<VideoWithSeduta[]> {
  return videosData as VideoWithSeduta[];
}

export async function loadCategories(): Promise<Category[]> {
  return categoriesData as Category[];
}

export async function getSedutaBySlugAndDate(
  year: string,
  month: string,
  day: string,
  slug: string
): Promise<Seduta | null> {
  const sedute = await loadSedute();
  return (
    sedute.find(
      (s) =>
        s.slug === slug &&
        s.yearMonthDay.year === year &&
        s.yearMonthDay.month === month &&
        s.yearMonthDay.day === day
    ) || null
  );
}

export async function getVideosByCategorySlug(slug: string): Promise<VideoWithSeduta[]> {
  const videos = await loadVideos();
  return videos.filter((v) =>
    v.digest?.categories?.some((cat) =>
      cat.toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '') === slug
    )
  );
}
