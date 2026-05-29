/*
 * jsonViewer — interactive, collapsible JSON tree rendered into an x-html target.
 * Recursion is done here (not via server-side includes); collapse/expand uses
 * event delegation on the container, so there are no inline onclick strings.
 */
document.addEventListener('alpine:init', () => {
  Alpine.data('jsonViewer', (data) => ({
    data,
    autoExpandDepth: 2, // root + 2 levels open by default; deeper collapsed

    init() {
      this.$el.innerHTML = this.render(this.data, null, true);
      this.$el.addEventListener('click', (e) => {
        const toggle = e.target.closest('[data-json-toggle]');
        if (!toggle) return;
        const node = toggle.closest('.json-node');
        const open = node.dataset.open === 'true';
        node.dataset.open = open ? 'false' : 'true';
        toggle.textContent = open ? '▸' : '▾';
        node.querySelector(':scope > .json-body').style.display = open ? 'none' : 'block';
        node.querySelector(':scope > .json-body-close').style.display = open ? 'none' : 'block';
        const summary = node.querySelector(':scope > .json-line > .json-summary');
        if (summary) summary.style.display = open ? 'inline' : 'none';
      });
    },

    esc(s) {
      return String(s).replace(/[&<>"]/g, (c) =>
        ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    },

    keyHtml(key) {
      if (key === null) return '';
      return `<span class="json-key">"${this.esc(key)}"</span><span class="json-punct">: </span>`;
    },

    render(value, key, isLast, depth = 0) {
      const comma = isLast ? '' : '<span class="json-punct">,</span>';

      if (value === null)
        return `<div>${this.keyHtml(key)}<span class="json-null">null</span>${comma}</div>`;
      const t = typeof value;
      if (t === 'string')
        return `<div>${this.keyHtml(key)}<span class="json-string">"${this.esc(value)}"</span>${comma}</div>`;
      if (t === 'number' || t === 'boolean')
        return `<div>${this.keyHtml(key)}<span class="json-${t === 'number' ? 'number' : 'bool'}">${this.esc(value)}</span>${comma}</div>`;

      const isArr = Array.isArray(value);
      const entries = isArr ? value.map((v, i) => [i, v]) : Object.entries(value);
      const open = isArr ? '[' : '{';
      const close = isArr ? ']' : '}';

      if (entries.length === 0)
        return `<div>${this.keyHtml(key)}<span class="json-punct">${open}${close}</span>${comma}</div>`;

      const startOpen = depth <= this.autoExpandDepth;
      const label = `${entries.length} ${isArr ? 'items' : 'keys'}`;
      const children = entries
        .map(([k, v], i) => this.render(v, isArr ? null : k, i === entries.length - 1, depth + 1))
        .join('');

      return `
        <div class="json-node" data-open="${startOpen}">
          <div class="json-line">
            <button data-json-toggle class="json-toggle select-none mr-1" style="color:var(--muted-foreground)">${startOpen ? '▾' : '▸'}</button>
            ${this.keyHtml(key)}<span class="json-punct">${open}</span><span class="json-summary text-xs ml-1" style="color:var(--muted-foreground);display:${startOpen ? 'none' : 'inline'}">${label}${close}${comma ? ',' : ''}</span>
          </div>
          <div class="json-body ml-4 pl-3" style="border-left:1px solid var(--border);display:${startOpen ? 'block' : 'none'}">${children}</div>
          <div class="json-body-close" style="display:${startOpen ? 'block' : 'none'}"><span class="json-punct">${close}</span>${comma}</div>
        </div>`;
    },
  }));
});
