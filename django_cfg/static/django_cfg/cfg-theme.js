"use strict";
// django-cfg admin: dark is the default theme. Runs before Django's admin/js/theme.js
// (admin/base_site.html, block dark-mode-vars).
// theme.js stores "auto" on the first visit even though nobody chose it, so "auto" alone
// does not mean a choice. Once per browser (flag "cfg-theme-default"), a missing or "auto"
// value becomes "dark". After that every value the stock toggle stores (light, dark or
// auto) is the visitor's and is left alone.
try {
    var store = window.localStorage;
    if (!store.getItem("cfg-theme-default")) {
        var current = store.getItem("theme");
        if (!current || current === "auto") {
            store.setItem("theme", "dark");
        }
        store.setItem("cfg-theme-default", "dark");
    }
} catch (e) {
    // Storage blocked: theme.js sets no data-theme either, and cfg-theme.css draws dark then.
}
