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

    let query, ai;
    try {
      ({ query, ai } = await request.json());
    } catch {
      return new Response(JSON.stringify({ error: 'Invalid JSON' }), { status: 400, headers });
    }
    if (!query || typeof query !== 'string' || query.trim().length < 2 || query.length > 500) {
      return new Response(JSON.stringify({ error: 'Query non valida' }), { status: 400, headers });
    }

    try {
      const q = query.trim();
      // Le domande ("dove si parla di…") vengono riscritte in parole chiave
      // da un LLM prima della ricerca: le parole interrogative diluiscono il
      // match e il reranker le penalizza.
      const isQuestion =
        q.includes('?') ||
        /^(chi|che|cosa|com[e']|dove|quando|perch[eé]|quale|quali|quant[oaie])\b/i.test(q);
      let effective = q;
      if (isQuestion) {
        try {
          const rw = await env.AI.run('@cf/meta/llama-3.3-70b-instruct-fp8-fast', {
            messages: [
              {
                role: 'system',
                content:
                  'Estrai dalla domanda il tema di ricerca: 1 o 2 parole AL MASSIMO, prese SOLO tra le ' +
                  'parole della domanda (o la loro forma base). NON aggiungere nomi, luoghi, date o ' +
                  'concetti non presenti nella domanda. Niente parole interrogative né verbi generici. ' +
                  'Rispondi SOLO con le parole scelte.',
              },
              { role: 'user', content: q },
            ],
          });
          const kw = (rw?.response || '').replace(/["'.,;:!?]/g, ' ').trim().split(/\s+/).slice(0, 2).join(' ');
          if (kw.length >= 2) effective = kw;
        } catch {
          // riscrittura fallita: si usa la query originale
        }
      }

      // Il reranker (bge-reranker-base) azzera i punteggi delle query italiane
      // di una sola parola: per quelle il match keyword è già autorevole,
      // quindi si usa BM25 puro senza reranking. Per le query multi-parola
      // resta hybrid+reranker; "or" perché una query naturale non deve
      // richiedere che TUTTI i termini compaiano nel documento.
      const singleWord = effective.split(/\s+/).length === 1;
      const options = singleWord
        ? {
            reranking: { enabled: false },
            retrieval: { retrieval_type: 'keyword', score_threshold: 0.1, max_num_results: 20 },
          }
        : { retrieval: { keyword_match_mode: 'or' } };

      const searchPromise = env.SEARCH.search({
        messages: [{ role: 'user', content: effective }],
        ai_search_options: options,
      });

      // Modalità opt-in "Risposta AI": in parallelo alla ricerca, genera una
      // risposta in prosa basata sui passaggi recuperati (Workers AI).
      const answerPromise = ai
        ? env.SEARCH.chatCompletions({
            messages: [
              {
                role: 'system',
                content:
                  'Rispondi in italiano, in modo conciso, basandoti ESCLUSIVAMENTE sui passaggi di trascrizione forniti. ' +
                  'Se i passaggi non contengono la risposta, dillo chiaramente. Non inventare nulla.',
              },
              { role: 'user', content: q },
            ],
            model: '@cf/meta/llama-3.3-70b-instruct-fp8-fast',
            ai_search_options: options,
          }).catch(() => null)
        : Promise.resolve(null);

      const [result, aiResult] = await Promise.all([searchPromise, answerPromise]);

      const rawChunks = result?.chunks || [];
      const chunks = rawChunks.map((c) => ({
        key: c.item?.key || c.filename || c.attributes?.file?.name || '',
        score: c.score ?? null,
        text: c.text || (Array.isArray(c.content) ? c.content.map((p) => p.text).join('\n') : ''),
      }));
      const answer = aiResult?.choices?.[0]?.message?.content || null;
      return new Response(
        JSON.stringify({
          chunks,
          ...(effective !== q ? { query_used: effective } : {}),
          ...(ai ? { answer } : {}),
        }),
        { headers }
      );
    } catch (err) {
      return new Response(JSON.stringify({ error: `Ricerca non disponibile: ${err.message}` }), {
        status: 502,
        headers,
      });
    }
  },
};
