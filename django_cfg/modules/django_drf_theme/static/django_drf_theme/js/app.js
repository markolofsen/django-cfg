/*
 * drfApp — root Alpine component: theme (light/dark/auto), toasts, auth token,
 * and copyable curl/python/js snippets.
 */
document.addEventListener('alpine:init', () => {
  Alpine.data('drfApp', () => ({
    theme: document.documentElement.dataset.theme || 'auto',
    toasts: [],
    authType: localStorage.getItem('drf_auth_type') || 'bearer', // 'bearer' | 'apikey'
    authToken: localStorage.getItem('drf_auth_token') || '',

    init() {
      this.apply();
      window.matchMedia('(prefers-color-scheme: dark)')
        .addEventListener('change', () => { if (this.theme === 'auto') this.apply(); });
      this.$watch('authType', (v) => localStorage.setItem('drf_auth_type', v));
      this.$watch('authToken', (v) => localStorage.setItem('drf_auth_token', v));
    },

    apply() {
      const dark = this.theme === 'dark' ||
        (this.theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches);
      document.documentElement.classList.toggle('dark', dark);
      const light = document.getElementById('hljs-light');
      const darkSheet = document.getElementById('hljs-dark');
      if (light && darkSheet) { light.disabled = dark; darkSheet.disabled = !dark; }
    },

    setTheme(t) {
      this.theme = t;
      this.apply();
      document.cookie = `theme=${t}; path=/; max-age=31536000; SameSite=Lax`;
    },

    // — Auth —
    get headerPair() { return window.DRFTheme.authHeaderPair(); },
    get reqUrl() { return window.location.href.split('?')[0]; },

    get curlSnippet() {
      const p = this.headerPair;
      return p ? `curl '${this.reqUrl}' \\\n  -H '${p[0]}: ${p[1]}'` : `curl '${this.reqUrl}'`;
    },
    get pythonSnippet() {
      const p = this.headerPair;
      const headers = p ? `, headers={"${p[0]}": "${p[1]}"}` : '';
      return `import requests\nr = requests.get("${this.reqUrl}"${headers})\nprint(r.json())`;
    },
    get jsSnippet() {
      const p = this.headerPair;
      const headers = p ? `, {\n  headers: { "${p[0]}": "${p[1]}" }\n}` : '';
      return `const r = await fetch("${this.reqUrl}"${headers});\nconsole.log(await r.json());`;
    },
    snippet(lang) {
      return lang === 'python' ? this.pythonSnippet : lang === 'js' ? this.jsSnippet : this.curlSnippet;
    },

    // — Toasts —
    copy(text, label = 'Copied') {
      navigator.clipboard.writeText(text)
        .then(() => this.toast(label, 'success'))
        .catch(() => this.toast('Copy failed', 'error'));
    },
    toast(message, type = 'success') {
      const id = Date.now() + Math.random();
      this.toasts.push({ id, message, type });
      setTimeout(() => { this.toasts = this.toasts.filter((t) => t.id !== id); }, 3000);
    },
  }));
});
