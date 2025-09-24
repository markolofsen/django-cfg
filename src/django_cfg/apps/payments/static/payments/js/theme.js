/**
 * Theme Management for Payment Dashboard
 * Handles light/dark mode switching with persistence
 */

class ThemeManager {
    constructor() {
        this.initTheme();
        this.bindEvents();
    }

    initTheme() {
        // Check for saved theme preference or default to system preference
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme) {
            this.setTheme(savedTheme);
        } else if (systemPrefersDark) {
            this.setTheme('dark');
        } else {
            this.setTheme('light');
        }
    }

    setTheme(theme) {
        const html = document.documentElement;
        const toggleBtn = document.getElementById('theme-toggle');
        const icon = toggleBtn?.querySelector('.material-icons');

        if (theme === 'dark') {
            html.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            if (icon) {
                icon.textContent = 'dark_mode';
                icon.classList.add('text-yellow-400');
                icon.classList.remove('text-gray-600');
            }
        } else {
            html.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            if (icon) {
                icon.textContent = 'light_mode';
                icon.classList.add('text-gray-600');
                icon.classList.remove('text-yellow-400');
            }
        }

        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    }

    toggle() {
        const currentTheme = localStorage.getItem('theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    bindEvents() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    getCurrentTheme() {
        return localStorage.getItem('theme') || 'light';
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
