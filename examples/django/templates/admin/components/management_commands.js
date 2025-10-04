/**
 * Management Commands JavaScript
 * Handles toggle, search, modal, and command execution functionality
 */

// Global functions for category expansion
window.toggleCategory = function(category) {
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
};

// Command execution functions
window.copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(function() {
        const button = event.target.closest('button');
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="material-icons text-xs mr-1">check</span>Copied';
        button.classList.remove('bg-base-100', 'dark:bg-base-700', 'hover:bg-base-200', 'dark:hover:bg-base-600');
        button.classList.add('bg-green-600', 'hover:bg-green-700', 'dark:bg-green-500', 'dark:hover:bg-green-600', 'text-white');

        setTimeout(function() {
            button.innerHTML = originalText;
            button.classList.remove('bg-green-600', 'hover:bg-green-700', 'dark:bg-green-500', 'dark:hover:bg-green-600', 'text-white');
            button.classList.add('bg-base-100', 'dark:bg-base-700', 'hover:bg-base-200', 'dark:hover:bg-base-600');
        }, 2000);
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
    });
};

window.executeCommand = function(commandName) {
    const modal = document.getElementById('commandModal');
    const commandNameEl = document.getElementById('commandName');
    const commandOutput = document.getElementById('commandOutput');
    const commandStatus = document.getElementById('commandStatus');

    if (!modal || !commandNameEl || !commandOutput || !commandStatus) {
        console.error('Command modal elements not found');
        return;
    }

    commandNameEl.textContent = commandName;
    commandOutput.textContent = '';
    commandStatus.innerHTML = '<div class="w-3 h-3 bg-yellow-500 rounded-full mr-2 animate-pulse"></div><span class="text-sm font-medium text-font-default-light dark:text-font-default-dark">Executing...</span>';
    modal.classList.remove('hidden');

    fetch('/cfg/commands/execute/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            command: commandName,
            args: [],
            options: {}
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        function readStream() {
            return reader.read().then(({done, value}) => {
                if (done) return;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            handleCommandData(data);
                        } catch (e) {
                            console.error('Error parsing command data:', e);
                        }
                    }
                });

                return readStream();
            });
        }

        return readStream();
    })
    .catch(error => {
        console.error('Error executing command:', error);
        commandOutput.textContent += `\n❌ Error: ${error.message}`;
        commandStatus.innerHTML = '<div class="w-3 h-3 bg-red-500 rounded-full mr-2"></div><span class="text-sm font-medium text-red-600 dark:text-red-400">Error</span>';
    });
};

window.closeCommandModal = function() {
    const modal = document.getElementById('commandModal');
    if (modal) {
        modal.classList.add('hidden');
    }
};

// Helper functions
function handleCommandData(data) {
    const output = document.getElementById('commandOutput');
    const status = document.getElementById('commandStatus');

    if (!output || !status) return;

    switch (data.type) {
        case 'start':
            output.innerHTML = '';
            addLogLine(output, `🚀 Starting command: ${data.command}`, 'info');
            addLogLine(output, `📝 Arguments: ${data.args.join(' ')}`, 'info');
            addLogLine(output, '', 'spacer');
            status.innerHTML = '<div class="w-3 h-3 bg-yellow-500 rounded-full mr-2 animate-pulse"></div><span class="text-sm font-medium text-font-default-light dark:text-font-default-dark">Executing...</span>';
            break;
        case 'output':
            addLogLine(output, data.line, 'output');
            scrollToBottom(output);
            break;
        case 'complete':
            const success = data.return_code === 0;
            status.innerHTML = success
                ? '<div class="w-3 h-3 bg-green-500 rounded-full mr-2"></div><span class="text-sm font-medium text-green-600 dark:text-green-400">Completed</span>'
                : '<div class="w-3 h-3 bg-red-500 rounded-full mr-2"></div><span class="text-sm font-medium text-red-600 dark:text-red-400">Failed</span>';

            addLogLine(output, '', 'spacer');
            let completionMessage = `${success ? '✅' : '❌'} Command completed with exit code: ${data.return_code}`;
            if (data.execution_time) {
                completionMessage += ` (${data.execution_time}s)`;
            }
            addLogLine(output, completionMessage, success ? 'success' : 'error');
            scrollToBottom(output);
            break;
        case 'error':
            addLogLine(output, `❌ ${data.message}`, 'error');
            status.innerHTML = '<div class="w-3 h-3 bg-red-500 rounded-full mr-2"></div><span class="text-sm font-medium text-red-600 dark:text-red-400">Error</span>';
            scrollToBottom(output);
            break;
    }
}

function addLogLine(container, text, type = 'output') {
    const line = document.createElement('div');
    line.className = 'log-line';

    switch (type) {
        case 'info':
            line.className += ' text-blue-600 dark:text-blue-400';
            break;
        case 'success':
            line.className += ' text-green-600 dark:text-green-400 font-medium';
            break;
        case 'error':
            line.className += ' text-red-600 dark:text-red-400 font-medium';
            break;
        case 'spacer':
            line.style.height = '1em';
            break;
        default:
            line.className += ' text-font-default-light dark:text-font-default-dark';
    }

    line.textContent = text;
    container.appendChild(line);
}

function scrollToBottom(element) {
    element.scrollTop = element.scrollHeight;
}

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

// Search functionality
function searchCommands(query) {
    const searchQuery = query.toLowerCase().trim();
    const categories = document.querySelectorAll('[id^="content-"]');
    const clearButton = document.getElementById('clearSearch');
    const commandsCount = document.getElementById('commandsCount');
    let visibleCommands = 0;

    // Show/hide clear button
    if (searchQuery) {
        clearButton.classList.remove('hidden');
    } else {
        clearButton.classList.add('hidden');
    }

    categories.forEach(category => {
        const categoryName = category.id.replace('content-', '');
        const commands = category.querySelectorAll('.command-item');
        let categoryHasVisibleCommands = false;

        commands.forEach(command => {
            const commandName = command.querySelector('.command-name').textContent.toLowerCase();
            const commandDesc = command.querySelector('.command-description')?.textContent.toLowerCase() || '';

            if (!searchQuery || commandName.includes(searchQuery) || commandDesc.includes(searchQuery)) {
                command.style.display = 'block';
                categoryHasVisibleCommands = true;
                visibleCommands++;
            } else {
                command.style.display = 'none';
            }
        });

        // Show/hide category based on whether it has visible commands
        const categoryHeader = document.querySelector(`button[onclick="toggleCategory('${categoryName}')"]`);
        const categoryContainer = categoryHeader.parentElement;

        if (categoryHasVisibleCommands) {
            categoryContainer.style.display = 'block';

            // Auto-expand categories when searching
            if (searchQuery) {
                category.style.display = 'block';
                const icon = categoryHeader.querySelector('.material-icons');
                if (icon) {
                    icon.textContent = 'expand_less';
                    icon.style.transform = 'rotate(0deg)';
                }
            }
        } else {
            categoryContainer.style.display = 'none';
        }
    });

    // Update commands count
    if (commandsCount) {
        commandsCount.textContent = visibleCommands;
    }

    // Show "no results" message if no commands found
    showNoResultsMessage(visibleCommands === 0 && searchQuery);
}

function clearSearch() {
    const searchInput = document.getElementById('commandSearch');
    const clearButton = document.getElementById('clearSearch');
    const commandsCount = document.getElementById('commandsCount');

    searchInput.value = '';
    clearButton.classList.add('hidden');

    // Show all commands and categories
    const categories = document.querySelectorAll('[id^="content-"]');
    const allCommands = document.querySelectorAll('.command-item');

    categories.forEach(category => {
        const categoryName = category.id.replace('content-', '');
        const categoryHeader = document.querySelector(`button[onclick="toggleCategory('${categoryName}')"]`);
        categoryHeader.parentElement.style.display = 'block';
        // Reset to collapsed state
        category.style.display = 'none';
        const icon = categoryHeader.querySelector('.material-icons');
        if (icon) {
            icon.textContent = 'expand_less';
            icon.style.transform = 'rotate(-90deg)';
        }
    });

    allCommands.forEach(command => {
        command.style.display = 'block';
    });

    // Reset commands count to original total
    if (commandsCount && commandsCount.dataset.originalCount) {
        commandsCount.textContent = commandsCount.dataset.originalCount;
    }

    // Hide no results message
    showNoResultsMessage(false);
}

function showNoResultsMessage(show) {
    let noResultsDiv = document.getElementById('noSearchResults');

    if (show && !noResultsDiv) {
        // Create no results message
        noResultsDiv = document.createElement('div');
        noResultsDiv.id = 'noSearchResults';
        noResultsDiv.className = 'text-center py-12';
        noResultsDiv.innerHTML = `
            <div class="flex flex-col items-center">
                <span class="material-icons text-6xl text-base-400 dark:text-base-500 mb-4">search_off</span>
                <h3 class="text-lg font-medium text-font-important-light dark:text-font-important-dark mb-2">
                    No Commands Found
                </h3>
                <p class="text-font-subtle-light dark:text-font-subtle-dark max-w-md mx-auto">
                    No commands match your search criteria. Try different keywords or clear the search.
                </p>
            </div>
        `;

        // Insert after the commands container
        const commandsContainer = document.querySelector('.space-y-4');
        if (commandsContainer && commandsContainer.parentNode) {
            commandsContainer.parentNode.insertBefore(noResultsDiv, commandsContainer.nextSibling);
        }
    } else if (!show && noResultsDiv) {
        noResultsDiv.remove();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('commandSearch');
    const commandsCount = document.getElementById('commandsCount');

    // Store original count for reset
    if (commandsCount) {
        commandsCount.dataset.originalCount = commandsCount.textContent;
    }

    // Focus search with Ctrl+F or Cmd+F
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'f' && searchInput) {
            e.preventDefault();
            searchInput.focus();
        }

        // Clear search with Escape
        if (e.key === 'Escape' && document.activeElement === searchInput) {
            clearSearch();
            searchInput.blur();
        }

        // Close modal with Escape
        if (e.key === 'Escape') {
            closeCommandModal();
        }
    });

    // Close modal on background click
    const modal = document.getElementById('commandModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeCommandModal();
            }
        });
    }
});

// Export functions for global use
window.searchCommands = searchCommands;
window.clearSearch = clearSearch;
