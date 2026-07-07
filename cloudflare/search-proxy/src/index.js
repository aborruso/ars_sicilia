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

      let usedOptions = options;
      let result = await env.SEARCH.search({
        messages: [{ role: 'user', content: effective }],
        ai_search_options: usedOptions,
      });

      // Fallback per le multi-parola azzerate dal reranker: keyword puro in
      // modalità "and" (tutte le parole nello stesso chunk) — preciso e onesto.
      if (!singleWord && !(result?.chunks || []).length) {
        usedOptions = {
          reranking: { enabled: false },
          retrieval: {
            retrieval_type: 'keyword',
            keyword_match_mode: 'and',
            score_threshold: 0.1,
            max_num_results: 20,
          },
        };
        result = await env.SEARCH.search({
          messages: [{ role: 'user', content: effective }],
          ai_search_options: usedOptions,
        });
      }

      const rawChunks = result?.chunks || [];
      const chunks = rawChunks.map((c) => ({
        key: c.item?.key || c.filename || c.attributes?.file?.name || '',
        score: c.score ?? null,
        text: c.text || (Array.isArray(c.content) ? c.content.map((p) => p.text).join('\n') : ''),
      }));

      // Modalità opt-in "Risposta AI": genera SOLO se la ricerca ha trovato
      // passaggi (guardrail deterministico contro risposte enciclopediche),
      // con le stesse opzioni di retrieval che hanno prodotto i risultati.
      let answer = null;
      if (ai && chunks.length) {
        const aiResult = await env.SEARCH.chatCompletions({
          messages: [
            {
              role: 'system',
              content:
                "I passaggi forniti sono trascrizioni di sedute dell'Assemblea Regionale Siciliana. " +
                'Rispondi in italiano, in modo conciso, basandoti ESCLUSIVAMENTE su quei passaggi. ' +
                'Se i passaggi non contengono informazioni pertinenti, rispondi SOLO con: ' +
                '"Le trascrizioni disponibili non contengono informazioni su questo tema." ' +
                'NON usare MAI conoscenze generali esterne ai passaggi, nemmeno per spiegare i concetti. ' +
                'Per citare una fonte scrivi SOLO il segnaposto [fonte: NOMEFILE] (mai la parola "documento" ' +
                "né il nome file nudo), e se disponibile indica il minuto (es. 'al minuto 00:37:39').",
            },
            { role: 'user', content: q },
          ],
          model: '@cf/meta/llama-3.3-70b-instruct-fp8-fast',
          ai_search_options: usedOptions,
        }).catch(() => null);
        answer = aiResult?.choices?.[0]?.message?.content || null;
      }
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
