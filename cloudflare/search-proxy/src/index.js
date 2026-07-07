// Proxy per Cloudflare AI Search: espone la ricerca sulle trascrizioni ARS
// al sito statico su GitHub Pages senza esporre credenziali (binding nativo).

const ALLOWED_ORIGINS = [
  'https://aborruso.github.io',
  'http://localhost:4321',
];

// Parole funzione italiane: in modalità keyword "or" farebbero matchare
// qualunque documento (es. "di" compare 5000+ volte nel corpus), rendendo
// pertinente qualsiasi query. Rimosse solo per il ramo BM25, non per quello
// vettoriale/reranked (l'embedding le gestisce già correttamente).
const STOPWORDS = new Set([
  'a', 'ai', 'al', 'alla', 'alle', 'allo', 'con', 'che', 'chi', 'ci', 'coi',
  'col', 'da', 'dai', 'dal', 'dalla', 'dalle', 'dallo', 'dei', 'del', 'della',
  'delle', 'dello', 'di', 'e', 'ed', 'gli', 'i', 'il', 'in', 'io', 'la', 'le',
  'lo', 'mi', 'ne', 'nei', 'nel', 'nella', 'nelle', 'nello', 'noi', 'o', 'per',
  'più', 'quale', 'quali', 'quando', 'quanto', 'quello', 'questo', 'se', 'si',
  'sono', 'su', 'sua', 'sue', 'sui', 'sul', 'sulla', 'sulle', 'sullo', 'suo',
  'suoi', 'ti', 'tra', 'tu', 'un', 'una', 'uno', 'voi', 'era', 'stato', 'come',
  'dove', 'perché', "perche'",
]);

function stripStopwords(text) {
  const kept = text.split(/\s+/).filter((w) => !STOPWORDS.has(w.toLowerCase()));
  return kept.length ? kept.join(' ') : text;
}

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
      // Esposto al frontend quando la riscrittura era dovuta ma non è
      // riuscita, così l'utente sa che la ricerca ha usato la domanda così
      // com'è invece di parole chiave estratte (comportamento diverso dal
      // solito, non un bug silenzioso).
      let notice = null;
      if (isQuestion) {
        try {
          const rw = await env.AI.run('@cf/meta/llama-3.3-70b-instruct-fp8-fast', {
            messages: [
              {
                role: 'system',
                content:
                  'Estrai dalla domanda i termini di ricerca: da 1 a 4 parole, prese SOLO tra le parole ' +
                  'della domanda (o la loro forma base). Scegli i termini più specifici e distintivi del ' +
                  'tema (es. da "cosa è successo col voto segreto sul terzo mandato dei sindaci?" estrai ' +
                  '"terzo mandato sindaci"). NON aggiungere nomi, luoghi, date o concetti non presenti ' +
                  'nella domanda. Niente parole interrogative né verbi generici. Rispondi SOLO con le parole scelte.',
              },
              { role: 'user', content: q },
            ],
          });
          const kw = (rw?.response || '').replace(/["'.,;:!?]/g, ' ').trim().split(/\s+/).slice(0, 4).join(' ');
          if (kw.length >= 2) effective = kw;
        } catch (err) {
          const msg = String(err?.message || '');
          notice = /neuron|4006/i.test(msg)
            ? 'La riformulazione automatica delle domande in parole chiave non è disponibile in questo momento (limite giornaliero di utilizzo AI raggiunto, si ripristina a mezzanotte UTC). La ricerca ha usato la domanda così com\'è, con risultati meno mirati del solito.'
            : 'La riformulazione automatica delle domande in parole chiave non è riuscita. La ricerca ha usato la domanda così com\'è.';
        }
      }

      // Il reranker (bge-reranker-base) azzera i punteggi delle query italiane
      // di una sola parola: per quelle il match keyword è già autorevole,
      // quindi si usa BM25 puro senza reranking.
      const singleWord = effective.split(/\s+/).length === 1;
      const keywordOptions = {
        reranking: { enabled: false },
        retrieval: {
          retrieval_type: 'keyword',
          keyword_match_mode: 'or',
          score_threshold: 0.1,
          max_num_results: 20,
        },
      };

      let usedOptions, rawChunks;
      if (singleWord) {
        usedOptions = keywordOptions;
        const result = await env.SEARCH.search({
          messages: [{ role: 'user', content: effective }],
          ai_search_options: usedOptions,
        });
        rawChunks = result?.chunks || [];
      } else {
        // Il reranker si è dimostrato inaffidabile anche su query multi-parola
        // con nomi propri/termini specifici (caso verificato: "Mondello" —
        // il chunk giusto esisteva nel corpus, il reranker l'ha scartato a
        // favore di uno adiacente ma non pertinente). Si affianca sempre una
        // ricerca BM25 pura, deterministica e non soggetta al reranker, e si
        // uniscono i risultati (dedup per chunk id).
        const rerankedOptions = { retrieval: { keyword_match_mode: 'or' } };
        const keywordQuery = stripStopwords(effective);
        const [reranked, keywordOnly] = await Promise.all([
          env.SEARCH.search({
            messages: [{ role: 'user', content: effective }],
            ai_search_options: rerankedOptions,
          }).catch(() => null),
          env.SEARCH.search({
            messages: [{ role: 'user', content: keywordQuery }],
            ai_search_options: keywordOptions,
          }).catch(() => null),
        ]);
        const seen = new Set();
        rawChunks = [];
        for (const c of [...(reranked?.chunks || []), ...(keywordOnly?.chunks || [])]) {
          const dedupKey = c.id || `${c.item?.key}:${(c.text || '').slice(0, 40)}`;
          if (seen.has(dedupKey)) continue;
          seen.add(dedupKey);
          rawChunks.push(c);
        }
        // Per la generazione conta il recall: priorità al ramo keyword.
        usedOptions = keywordOptions;
      }
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
        // Meno passaggi al generatore = risposta più focalizzata.
        const genOptions = {
          ...usedOptions,
          retrieval: { ...(usedOptions.retrieval || {}), max_num_results: 8 },
          // La similarity cache può servire una vecchia risposta ("non ci sono
          // informazioni") a query simili: per la generazione conta la freschezza.
          cache: { enabled: false },
        };
        // Il retrieval interno di chatCompletions usa l'ultimo messaggio user:
        // gli si passa la query riscritta (efficace), mentre la domanda
        // originale a cui rispondere viene data nel messaggio di sistema.
        try {
          const aiResult = await env.SEARCH.chatCompletions({
            messages: [
              {
                role: 'system',
                content:
                  "I passaggi forniti sono trascrizioni di sedute dell'Assemblea Regionale Siciliana. " +
                  `La richiesta dell'utente è: "${q}". Rispondi in italiano a quella richiesta seguendo queste regole, in ordine:\n` +
                  '1. Usa SOLO le informazioni contenute nei passaggi. Mai conoscenza esterna, mai spiegazioni generali.\n' +
                  '2. Se i passaggi contengono informazioni pertinenti: scrivi una sintesi di massimo 150 parole, ' +
                  'citando nel testo SOLO le 2-4 fonti più rilevanti, ciascuna nel formato [fonte: NOMEFILE], ' +
                  "seguita dal minuto se noto (es. 'al minuto 00:37:39'). Non elencare le fonti che non citi.\n" +
                  '3. Se i passaggi NON contengono informazioni pertinenti: scrivi SOLO la frase ' +
                  '"Le trascrizioni disponibili non contengono informazioni su questo tema.", senza citazioni né altro.',
              },
              { role: 'user', content: effective },
            ],
            model: '@cf/meta/llama-3.3-70b-instruct-fp8-fast',
            ai_search_options: genOptions,
          });
          answer = aiResult?.choices?.[0]?.message?.content || null;
        } catch (err) {
          const msg = String(err?.message || '');
          notice = /neuron|4006/i.test(msg)
            ? 'La generazione della risposta AI non è disponibile in questo momento (limite giornaliero di utilizzo AI raggiunto, si ripristina a mezzanotte UTC). Sotto trovi comunque i passaggi della ricerca.'
            : 'La generazione della risposta AI non è riuscita. Sotto trovi comunque i passaggi della ricerca.';
        }
      }
      return new Response(
        JSON.stringify({
          chunks,
          ...(effective !== q ? { query_used: effective } : {}),
          ...(notice ? { notice } : {}),
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
