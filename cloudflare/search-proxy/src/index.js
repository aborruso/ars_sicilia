// Proxy per Cloudflare AI Search: espone la ricerca sulle trascrizioni ARS
// al sito statico su GitHub Pages senza esporre credenziali (binding nativo).

const ALLOWED_ORIGINS = [
  'https://aborruso.github.io',
  'http://localhost:4321',
];

function corsHeaders(origin) {
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
  };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const headers = corsHeaders(origin);

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers });
    }
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers });
    }

    let query;
    try {
      ({ query } = await request.json());
    } catch {
      return new Response(JSON.stringify({ error: 'Invalid JSON' }), { status: 400, headers });
    }
    if (!query || typeof query !== 'string' || query.trim().length < 2 || query.length > 500) {
      return new Response(JSON.stringify({ error: 'Query non valida' }), { status: 400, headers });
    }

    try {
      const q = query.trim();
      // Il reranker (bge-reranker-base) azzera i punteggi delle query italiane
      // di una sola parola: per quelle il match keyword è già autorevole,
      // quindi si usa BM25 puro senza reranking. Per le query multi-parola
      // resta hybrid+reranker; "or" perché una query naturale non deve
      // richiedere che TUTTI i termini compaiano nel documento.
      const singleWord = q.split(/\s+/).length === 1;
      const result = await env.SEARCH.search({
        messages: [{ role: 'user', content: q }],
        ai_search_options: singleWord
          ? {
              reranking: { enabled: false },
              retrieval: { retrieval_type: 'keyword', score_threshold: 0.1, max_num_results: 20 },
            }
          : { retrieval: { keyword_match_mode: 'or' } },
      });
      const rawChunks = result?.chunks || [];
      const chunks = rawChunks.map((c) => ({
        key: c.item?.key || c.filename || c.attributes?.file?.name || '',
        score: c.score ?? null,
        text: c.text || (Array.isArray(c.content) ? c.content.map((p) => p.text).join('\n') : ''),
      }));
      return new Response(JSON.stringify({ chunks }), { headers });
    } catch (err) {
      return new Response(JSON.stringify({ error: `Ricerca non disponibile: ${err.message}` }), {
        status: 502,
        headers,
      });
    }
  },
};
