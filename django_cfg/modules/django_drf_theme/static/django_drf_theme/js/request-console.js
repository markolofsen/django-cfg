/*
 * requestConsole — typed "try it" panel for the current endpoint.
 * Reads the operation's path/query params + request body from the schema, builds
 * the request, sends it with fetch (+ the stored auth header), and exposes the
 * live response. No page reload.
 *
 * URL model mirrors @djangocfg/ui-tools OpenapiViewer: path-substitution + query
 * string; body = JSON.
 */
document.addEventListener('alpine:init', () => {
  Alpine.data('requestConsole', (schemaUrl, basePath, methods) => ({
    schemaUrl,
    basePath,                 // concrete URL of the current page
    methods,                  // allowed methods from DRF, e.g. ['GET','POST']
    method: methods[0] || 'GET',
    ops: {},                  // { METHOD: { params:[{name,in,required,type}], hasBody } }
    fields: {},               // param values keyed by name
    body: '',
    sending: false,
    res: null,                // { status, statusText, ok, json, text }

    async init() {
      const NS = window.DRFTheme;
      const schema = await NS.fetchSchema(this.schemaUrl);
      if (!schema) return;
      const entry = Object.entries(schema.paths || {})
        .find(([p]) => NS.normalizePath(p) === this.basePath);
      if (!entry) return;
      for (const [m, op] of Object.entries(entry[1])) {
        const M = m.toUpperCase();
        if (!this.methods.includes(M)) continue;
        this.ops[M] = {
          params: (op.parameters || []).map((p) => ({
            name: p.name, in: p.in, required: !!p.required,
            type: (p.schema && p.schema.type) || 'string',
          })),
          hasBody: !!op.requestBody,
          bodyFields: op.requestBody ? NS.bodyFields(schema, op) : [],
        };
      }
    },

    get current() { return this.ops[this.method] || { params: [], hasBody: false, bodyFields: [] }; },
    get bodyFields() { return this.current.bodyFields || []; },

    prefillBody() { this.body = window.DRFTheme.bodyTemplate(this.bodyFields); },
    get pathParams() { return this.current.params.filter((p) => p.in === 'path'); },
    get queryParams() { return this.current.params.filter((p) => p.in === 'query'); },
    get showBody() { return ['POST', 'PUT', 'PATCH'].includes(this.method) && this.current.hasBody; },
    methodClass(m) { return window.DRFTheme.methodClass(m); },

    buildUrl() {
      let path = this.basePath;
      for (const p of this.pathParams) {
        const v = (this.fields[p.name] || '').trim();
        if (v) path = path.replace(`{${p.name}}`, encodeURIComponent(v));
      }
      const qs = new URLSearchParams();
      for (const p of this.queryParams) {
        const v = (this.fields[p.name] || '').trim();
        if (v) qs.append(p.name, v);
      }
      const q = qs.toString();
      return q ? `${path}?${q}` : path;
    },

    async send() {
      this.sending = true;
      this.res = null;
      const headers = { Accept: 'application/json' };
      const pair = window.DRFTheme.authHeaderPair();
      if (pair) headers[pair[0]] = pair[1];

      const opts = { method: this.method, headers };
      if (this.showBody && this.body.trim()) {
        headers['Content-Type'] = 'application/json';
        opts.body = this.body;
      }
      if (!['GET', 'HEAD'].includes(this.method)) {
        const m = document.querySelector('meta[name="csrf-token"]');
        if (m) headers['X-CSRFToken'] = m.content;
      }

      try {
        const r = await fetch(this.buildUrl(), opts);
        const text = await r.text();
        let json = null;
        try { json = JSON.parse(text); } catch (_) {}
        this.res = { status: r.status, statusText: r.statusText, ok: r.ok, json, text };
      } catch (e) {
        this.res = { status: 0, statusText: 'Network error', ok: false, json: null, text: String(e) };
      } finally {
        this.sending = false;
      }
    },

    resClass() {
      if (!this.res) return '';
      const b = Math.floor(this.res.status / 100);
      return { 2: 'text-emerald-500', 3: 'text-blue-500', 4: 'text-amber-500', 5: 'text-red-500' }[b]
        || 'text-muted-foreground';
    },
  }));
});
