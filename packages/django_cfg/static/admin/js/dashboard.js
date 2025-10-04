/**
 * Django CFG Dashboard JavaScript
 *
 * Handles dashboard tabs, navigation, and interactions
 */

// Tab Management
class DashboardTabs {
    constructor() {
        this.tabs = document.querySelectorAll('#dashboard-tabs button');
        this.contents = document.querySelectorAll('.tab-content');
        this.tabNames = ['overview', 'zones', 'users', 'system', 'stats', 'app-stats', 'commands'];
        this.init();
    }

    init() {
        if (!this.tabs.length || !this.contents.length) return;

        // Add click handlers
        this.tabs.forEach((tab, idx) => {
            tab.onclick = (e) => {
                e.preventDefault();
                this.switchTab(idx, true);
            };
        });

        // Handle browser back/forward
        window.addEventListener('hashchange', () => {
            const tabIndex = this.getTabFromHash();
            this.switchTab(tabIndex, false);
        });

        // Activate initial tab
        const initialTab = this.getTabFromHash();
        this.switchTab(initialTab, false);
    }

    switchTab(idx, updateHash = true) {
        this.tabs.forEach((t, i) => {
            if (i === idx) {
                t.classList.add('active');
            } else {
                t.classList.remove('active');
            }
        });

        this.contents.forEach((content, i) => {
            content.style.display = i === idx ? 'block' : 'none';
            content.classList.toggle('active', i === idx);
        });

        if (updateHash && this.tabNames[idx]) {
            history.replaceState(null, null, '#' + this.tabNames[idx]);
        }
    }

    getTabFromHash() {
        const hash = window.location.hash.substring(1);
        const tabIndex = this.tabNames.indexOf(hash);
        return tabIndex >= 0 ? tabIndex : 0;
    }
}

// Category Toggle
function toggleCategory(category) {
    const content = document.getElementById(`content-${category}`);
    const icon = document.getElementById(`icon-${category}`);

    if (!content || !icon) return;

    if (content.style.display === 'none' || content.style.display === '') {
        content.style.display = 'block';
        icon.style.transform = 'rotate(0deg)';
        icon.textContent = 'expand_more';
    } else {
        content.style.display = 'none';
        icon.style.transform = 'rotate(-90deg)';
        icon.textContent = 'expand_less';
    }
}

// Clipboard Functions
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        const button = event.target.closest('button');
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="material-icons text-xs mr-1">check</span>Copied';
        button.classList.remove('bg-gray-100', 'dark:bg-gray-700', 'hover:bg-gray-200', 'dark:hover:bg-gray-600');
        button.classList.add('bg-green-600', 'hover:bg-green-700', 'dark:bg-green-500', 'dark:hover:bg-green-600', 'text-white');

        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-green-600', 'hover:bg-green-700', 'dark:bg-green-500', 'dark:hover:bg-green-600', 'text-white');
            button.classList.add('bg-gray-100', 'dark:bg-gray-700', 'hover:bg-gray-200', 'dark:hover:bg-gray-600');
        }, 2000);
    }).catch((err) => {
        console.error('Could not copy text: ', err);
    });
}

// Utility Functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    new DashboardTabs();
});

// Export for global access
window.DashboardTabs = DashboardTabs;
window.toggleCategory = toggleCategory;
window.copyToClipboard = copyToClipboard;
window.getCookie = getCookie;
