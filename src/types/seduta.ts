export interface Person {
  name: string;
  role: string;
}

export interface Digest {
  digest: string;
  categories: string[];
  people: Person[];
}

export interface DisegnoLegge {
  titolo: string;
  numero: string;
  legislatura: string;
  urlDisegno: string;
}

export interface Video {
  idVideo: number;
  oraVideo: string;
  dataVideo: string;
  youtubeId: string;
  videoPageUrl: string;
  durationMinutes: number;
  status: string;
  digest: Digest | null;
  slug: string;
}

export interface Seduta {
  numero: number;
  dataSeduta: string;
  urlPagina: string;
  odgUrl: string | null;
  resocontoUrl: string | null;
  resocontoProvvisorioUrl: string | null;
  resocontoStenograficoUrl: string | null;
  allegatoUrl: string | null;
  videos: Video[];
  disegniLegge: DisegnoLegge[];
  categories: string[];
  slug: string;
  yearMonthDay: {
    year: string;
    month: string;
    day: string;
  };
}

export interface VideoWithSeduta extends Video {
  seduta: {
    numero: number;
    dataSeduta: string;
    slug: string;
    yearMonthDay: {
      year: string;
      month: string;
      day: string;
    };
  };
}

export interface Category {
  name: string;
  count: number;
  slug: string;
}

export interface DDL {
  numero: string;
  legislatura: string;
  titolo: string;
  urlDisegno: string;
  sedute: DDLSeduta[];
}

export interface DDLSeduta {
  numero: number;
  dataSeduta: string;
  slug: string;
  yearMonthDay: {
    year: string;
    month: string;
    day: string;
  };
}
