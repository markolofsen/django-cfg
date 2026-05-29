/*
 * endpointNav — left sidepanel navigation. Lazily fetches the current group's
 * drf-spectacular schema, expands it into operations (path × method) with human
 * labels, grouped by resource. No server-side OpenAPI parsing.
 */
document.addEventListener('alpine:init', () => {
  Alpine.data('endpointNav', (schemaUrl) => ({
    schemaUrl,
    loading: true,
    error: false,
    query: '',
    ops: [],                 // [{ method, path, href, parametrized, name, group }]
    here: window.location.pathname,

    async init() {
      const NS = window.DRFTheme;
      const schema = await NS.fetchSchema(this.schemaUrl);
      if (!schema) { this.loading = false; this.error = true; return; }
      const order = NS.METHOD_ORDER;
      const out = [];
      for (const [path, methods] of Object.entries(schema.paths || {})) {
        for (const [method, op] of Object.entries(methods)) {
          if (!(method in order)) continue;
          out.push({
            method: method.toUpperCase(),
            path,
            href: NS.normalizePath(path),
            parametrized: /\{[^}]+\}/.test(path),
            name: this.label(op, method, path),
            group: this.groupOf(path),
          });
        }
      }
      out.sort((a, b) => a.path.localeCompare(b.path)
        || order[a.method.toLowerCase()] - order[b.method.toLowerCase()]);
      this.ops = out;
      this.loading = false;
    },

    // Human label: summary → humanized operationId → derived verb + noun.
    label(op, method, path) {
      if (op.summary) return op.summary;
      if (op.operationId) {
        return op.operationId
          .replace(/_/g, ' ')
          .replace(/([a-z])([A-Z])/g, '$1 $2')
          .replace(/\b\w/g, (c) => c.toUpperCase());
      }
      const seg = path.replace(/\/$/, '').split('/').filter(Boolean).pop() || path;
      const noun = seg.replace(/\{[^}]+\}/g, 'item');
      const verb = { GET: path.includes('{') ? 'Retrieve' : 'List', POST: 'Create',
                     PUT: 'Replace', PATCH: 'Update', DELETE: 'Delete' }[method.toUpperCase()];
      return `${verb} ${noun}`;
    },

    // Resource group: the path tail after prefix + group segment.
    groupOf(path) {
      const segs = path.split('/').filter(Boolean).filter((s) => !s.startsWith('{'));
      const tail = segs.slice(2);
      return tail.length ? tail.join(' / ') : (segs[segs.length - 1] || 'API');
    },

    get filtered() {
      const q = this.query.trim().toLowerCase();
      if (!q) return this.ops;
      return this.ops.filter((o) =>
        o.name.toLowerCase().includes(q) || o.path.toLowerCase().includes(q) || o.method.toLowerCase().includes(q));
    },

    get groups() {
      const map = new Map();
      for (const op of this.filtered) {
        if (!map.has(op.group)) map.set(op.group, []);
        map.get(op.group).push(op);
      }
      return [...map.entries()].map(([name, ops]) => ({ name, ops }));
    },

    // Only the GET on the concrete (non-parametrized) path matching the URL is open.
    isActive(op) {
      return op.method === 'GET' && !op.parametrized && this.here === op.href;
    },

    methodClass(m) { return window.DRFTheme.methodClass(m); },
  }));
});
