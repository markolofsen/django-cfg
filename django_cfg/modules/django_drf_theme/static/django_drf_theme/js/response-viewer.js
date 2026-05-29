/*
 * responseViewer — Response section state (Pretty/Raw/Headers/Example tabs).
 * The Example tab shows a synthetic response built from the OpenAPI schema (no DB),
 * so the response shape is visible even when the live result is empty.
 */
document.addEventListener('alpine:init', () => {
  Alpine.data('responseViewer', (schemaUrl, path) => ({
    tab: 'pretty',
    schemaUrl,
    path,
    example: null,

    async init() {
      if (!this.schemaUrl) return;
      const NS = window.DRFTheme;
      const schema = await NS.fetchSchema(this.schemaUrl);
      if (!schema) return;
      const entry = Object.entries(schema.paths || {})
        .find(([p]) => NS.normalizePath(p) === this.path);
      if (!entry) return;
      const get = entry[1].get;
      if (get) this.example = NS.exampleResponse(schema, get);
    },
  }));
});
