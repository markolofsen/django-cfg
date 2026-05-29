/*
 * Shared OpenAPI helpers for the DRF theme (used by endpoint-nav + request-console).
 * No framework — plain functions on a global namespace.
 */
window.DRFTheme = window.DRFTheme || {};

(function (NS) {
  const METHOD_ORDER = { get: 0, post: 1, put: 2, patch: 3, delete: 4 };

  NS.METHOD_ORDER = METHOD_ORDER;

  // Fetch a drf-spectacular schema as JSON (or null on failure).
  NS.fetchSchema = async function (url) {
    if (!url) return null;
    try {
      const res = await fetch(url, { headers: { Accept: 'application/json' } });
      return await res.json();
    } catch (e) {
      return null;
    }
  };

  // Normalize a templated path to its concrete page URL: /x/{id}/ → /x/.
  NS.normalizePath = function (p) {
    return p.replace(/\{[^}]+\}/g, '').replace(/\/{2,}/g, '/');
  };

  // Tailwind colour class per HTTP method.
  NS.methodClass = function (m) {
    return {
      GET: 'text-blue-600 dark:text-blue-400',
      POST: 'text-emerald-600 dark:text-emerald-400',
      PUT: 'text-amber-600 dark:text-amber-400',
      PATCH: 'text-violet-600 dark:text-violet-400',
      DELETE: 'text-red-600 dark:text-red-400',
    }[m] || 'text-muted-foreground';
  };

  // Resolve a request body's object schema into a flat field list.
  // Returns [{ name, type, required, readOnly }] (read-only fields excluded —
  // they can't be sent). `schema` is the full OpenAPI doc (for $ref lookup).
  NS.bodyFields = function (schema, operation) {
    const content = operation.requestBody && operation.requestBody.content;
    const json = content && content['application/json'];
    let s = json && json.schema;
    if (!s) return [];
    if (s.$ref) {
      const name = s.$ref.split('/').pop();
      s = ((schema.components || {}).schemas || {})[name] || {};
    }
    const required = new Set(s.required || []);
    const props = s.properties || {};
    const typeOf = (v) => Array.isArray(v.type) ? v.type.filter((t) => t !== 'null')[0] || 'string' : (v.type || 'string');
    return Object.entries(props)
      .filter(([, v]) => !v.readOnly)
      .map(([name, v]) => ({
        name,
        type: typeOf(v) + (v.format ? ` (${v.format})` : ''),
        required: required.has(name),
        readOnly: !!v.readOnly,
      }));
  };

  // A minimal JSON body template from required fields (empty placeholders).
  NS.bodyTemplate = function (fields) {
    const obj = {};
    for (const f of fields.filter((x) => x.required)) {
      obj[f.name] = f.type.startsWith('integer') || f.type.startsWith('number') ? 0
        : f.type.startsWith('boolean') ? false : '';
    }
    return JSON.stringify(obj, null, 2);
  };

  // Build an example value from a schema node (resolves $ref, arrays, objects,
  // nullable types). Values are mock'd by type/format/field-name — a synthetic
  // "example response" without hitting the DB. `doc` is the full OpenAPI doc.
  const MAX_DEPTH = 6;
  function mockScalar(type, format, name) {
    const n = (name || '').toLowerCase();
    if (type === 'integer') return n.includes('id') ? 1 : 42;
    if (type === 'number') return 12.34;
    if (type === 'boolean') return true;
    // strings — format first, then field-name hints (lightweight, no faker.js)
    if (format === 'date-time') return '2026-01-01T12:00:00Z';
    if (format === 'date') return '2026-01-01';
    if (format === 'email') return 'user@example.com';
    if (format === 'uri' || format === 'url') return 'https://example.com';
    if (format === 'uuid') return '3fa85f64-5717-4562-b3fc-2c963f66afa6';
    if (format === 'decimal') return '123.45';
    if (n.includes('email')) return 'user@example.com';
    if (n === 'symbol' || n.includes('symbol')) return 'BTC';
    if (n.includes('name') || n === 'title') return 'Example';
    if (n.includes('url') || n.includes('link')) return 'https://example.com';
    if (n.includes('description') || n.includes('bio')) return 'Example text.';
    if (n.includes('slug')) return 'example';
    return 'string';
  }
  function normType(s) {
    const t = s.type;
    if (Array.isArray(t)) return t.filter((x) => x !== 'null')[0] || 'string';
    return t || (s.properties ? 'object' : 'string');
  }
  function exampleNode(schema, doc, depth, fieldName) {
    if (!schema || depth > MAX_DEPTH) return null;
    if (schema.$ref) {
      const ref = schema.$ref.split('/').pop();
      schema = ((doc.components || {}).schemas || {})[ref] || {};
    }
    if (schema.enum) return schema.enum[0];
    if ('example' in schema) return schema.example;
    if ('default' in schema) return schema.default;
    const t = normType(schema);
    if (t === 'object') {
      const out = {};
      for (const [k, v] of Object.entries(schema.properties || {})) out[k] = exampleNode(v, doc, depth + 1, k);
      return out;
    }
    if (t === 'array') return [exampleNode(schema.items || {}, doc, depth + 1, fieldName)];
    return mockScalar(t, schema.format, fieldName);
  }
  // Example response for an operation's 200/201 JSON body, or null.
  NS.exampleResponse = function (doc, operation) {
    const responses = operation.responses || {};
    const ok = responses['200'] || responses['201'] || {};
    const schema = ((ok.content || {})['application/json'] || {}).schema;
    if (!schema) return null;
    return exampleNode(schema, doc, 0);
  };

  // Auth header [name, value] from the persisted token, or null.
  NS.authHeaderPair = function () {
    const type = localStorage.getItem('drf_auth_type') || 'bearer';
    const token = localStorage.getItem('drf_auth_token') || '';
    if (!token) return null;
    return type === 'apikey' ? ['X-API-Key', token] : ['Authorization', `Bearer ${token}`];
  };
})(window.DRFTheme);
