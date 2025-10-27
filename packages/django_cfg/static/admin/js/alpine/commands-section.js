/**
 * Commands Section Alpine.js Component
 *
 * Manages command execution, modals, search, and category toggling
 */

function commandsSectionComponent(totalCommands) {
    return {
        // State
        totalCommands: totalCommands,
        visibleCommands: totalCommands,
        searchQuery: '',
        expandedCategories: new Set(),

        // Modals
        showConfirmModal: false,
        showOutputModal: false,

        // Current command
        currentCommand: '',
        currentCommandApp: '',
        currentCommandDescription: '',

        // Output
        commandOutput: '',
        commandStatus: 'idle', // idle, running, success, error
        statusText: '',
        statusClass: '',

        init() {
            // Keyboard shortcuts
            document.addEventListener('keydown', (e) => {
                // ESC to close modals
                if (e.key === 'Escape') {
                    this.showConfirmModal = false;
                    this.showOutputModal = false;
                }
            });
        },

        // Search functionality
        search() {
            const query = this.searchQuery.toLowerCase().trim();
            let visibleCount = 0;

            // Get all categories
            const categories = document.querySelectorAll('.category-block');

            categories.forEach(categoryBlock => {
                const commands = categoryBlock.querySelectorAll('.command-item');
                let categoryHasVisibleCommands = false;

                commands.forEach(command => {
                    const commandName = command.querySelector('.command-name')?.textContent.toLowerCase() || '';
                    const commandDesc = command.dataset.description?.toLowerCase() || '';

                    if (!query || commandName.includes(query) || commandDesc.includes(query)) {
                        command.style.display = 'block';
                        categoryHasVisibleCommands = true;
                        visibleCount++;
                    } else {
                        command.style.display = 'none';
                    }
                });

                // Show/hide category
                if (categoryHasVisibleCommands) {
                    categoryBlock.style.display = 'block';

                    // Auto-expand when searching
                    if (query) {
                        const category = categoryBlock.querySelector('.category-toggle')?.dataset.category;
                        if (category) {
                            this.expandedCategories.add(category);
                        }
                    }
                } else {
                    categoryBlock.style.display = 'none';
                }
            });

            this.visibleCommands = visibleCount;
        },

        clearSearch() {
            this.searchQuery = '';
            this.visibleCommands = this.totalCommands;

            // Show all
            document.querySelectorAll('.category-block').forEach(block => {
                block.style.display = 'block';
            });
            document.querySelectorAll('.command-item').forEach(item => {
                item.style.display = 'block';
            });

            // Collapse all
            this.expandedCategories.clear();
        },

        // Category toggle
        toggleCategory(category) {
            if (this.expandedCategories.has(category)) {
                this.expandedCategories.delete(category);
            } else {
                this.expandedCategories.add(category);
            }
        },

        isCategoryExpanded(category) {
            return this.expandedCategories.has(category);
        },

        // Command confirmation
        confirmCommand(commandName, commandApp, commandDesc) {
            this.currentCommand = commandName;
            this.currentCommandApp = commandApp || '';
            this.currentCommandDescription = commandDesc || '';
            this.showConfirmModal = true;
        },

        cancelExecution() {
            this.showConfirmModal = false;
            this.currentCommand = '';
        },

        // Command execution
        async executeCommand() {
            this.showConfirmModal = false;
            this.showOutputModal = true;
            this.commandOutput = '';
            this.commandStatus = 'running';
            this.statusText = 'Executing...';
            this.statusClass = 'bg-yellow-500 animate-pulse';

            const commandName = this.currentCommand;

            try {
                const response = await fetch('/cfg/commands/execute/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        command: commandName,
                        args: [],
                        options: {}
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');

                    lines.forEach(line => {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                this.handleCommandData(data);
                            } catch (e) {
                                console.error('Error parsing SSE data:', e);
                            }
                        }
                    });
                }
            } catch (error) {
                console.error('Error executing command:', error);
                this.addOutput(`\n❌ Error: ${error.message}`, 'error');
                this.commandStatus = 'error';
                this.statusText = 'Error';
                this.statusClass = 'bg-red-500';
            }
        },

        handleCommandData(data) {
            switch (data.type) {
                case 'start':
                    this.addOutput(`🚀 Starting command: ${data.command}\n📝 Arguments: ${data.args.join(' ')}\n\n`, 'info');
                    this.commandStatus = 'running';
                    this.statusText = 'Executing...';
                    this.statusClass = 'bg-yellow-500 animate-pulse';
                    break;

                case 'output':
                    this.addOutput(data.line + '\n', 'output');
                    break;

                case 'complete':
                    const success = data.return_code === 0;
                    this.commandStatus = success ? 'success' : 'error';
                    this.statusText = success ? 'Completed' : 'Failed';
                    this.statusClass = success ? 'bg-green-500' : 'bg-red-500';

                    let message = `${success ? '✅' : '❌'} Command completed with exit code: ${data.return_code}`;
                    if (data.execution_time) {
                        message += ` (${data.execution_time}s)`;
                    }
                    this.addOutput('\n' + message, success ? 'success' : 'error');
                    break;

                case 'error':
                    this.addOutput(`❌ Error: ${data.error}\n`, 'error');
                    this.commandStatus = 'error';
                    this.statusText = 'Error';
                    this.statusClass = 'bg-red-500';
                    break;
            }

            // Auto-scroll
            this.$nextTick(() => {
                const outputEl = this.$refs.commandOutput;
                if (outputEl) {
                    outputEl.scrollTop = outputEl.scrollHeight;
                }
            });
        },

        addOutput(text, type = 'output') {
            this.commandOutput += text;
        },

        closeOutputModal() {
            this.showOutputModal = false;
        },

        copyOutput() {
            navigator.clipboard.writeText(this.commandOutput).then(() => {
                // Could add a toast notification here
                console.log('Output copied to clipboard');
            }).catch(err => {
                console.error('Failed to copy:', err);
            });
        },


        get showClearButton() {
            return this.searchQuery.trim() !== '';
        },

        get showNoResults() {
            return this.visibleCommands === 0 && this.searchQuery.trim() !== '';
        }
    };
}

// Register component
document.addEventListener('alpine:init', () => {
    Alpine.data('commandsSection', commandsSectionComponent);
});
