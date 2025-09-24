/**
 * Theme Toggle Functionality
 * Handles dark/light mode switching
 */

class ThemeManager {
    constructor() {
        this.init();
    }

    init() {
        // Get saved theme or default to light
        this.currentTheme = localStorage.getItem('theme') || 'light';
        
        // Apply theme on load
        this.applyTheme(this.currentTheme);
        
        // Setup toggle button
        this.setupToggle();
    }

    applyTheme(theme) {
        const html = document.documentElement;
        const toggleButton = document.getElementById('theme-toggle');
        const icon = toggleButton?.querySelector('.material-icons');
        
        console.log('Applying theme:', theme);
        console.log('Toggle button found:', !!toggleButton);
        console.log('Icon found:', !!icon);
        
        if (theme === 'dark') {
            html.classList.add('dark');
            if (icon) {
                icon.textContent = 'dark_mode';
            }
        } else {
            html.classList.remove('dark');
            if (icon) {
                icon.textContent = 'light_mode';
            }
        }
        
        // Save to localStorage
        localStorage.setItem('theme', theme);
        this.currentTheme = theme;
        
        console.log('Theme applied. Current classes:', html.classList.toString());
    }

    toggle() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    setupToggle() {
        const toggleButton = document.getElementById('theme-toggle');
        if (toggleButton) {
            toggleButton.addEventListener('click', () => this.toggle());
            console.log('Theme toggle button found and event listener added');
        } else {
            console.warn('Theme toggle button not found');
            // Try to find it after a short delay
            setTimeout(() => {
                const delayedButton = document.getElementById('theme-toggle');
                if (delayedButton) {
                    delayedButton.addEventListener('click', () => this.toggle());
                    console.log('Theme toggle button found after delay');
                }
            }, 100);
        }
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});
