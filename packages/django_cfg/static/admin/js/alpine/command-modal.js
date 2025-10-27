/**
 * Command Modal Alpine.js Component
 *
 * Manages command execution modal with tabs for output and documentation
 * Requires: /static/admin/js/utils.js for getCookie function
 */

function commandModalComponent() {
    return {
        open: false,
        commandName: '',
        activeTab: 'output',
        outputHtml: '',
        docsHtml: '<p class="text-font-subtle-light dark:text-font-subtle-dark">Loading documentation...</p>',
        statusText: 'Executing...',
        statusClass: 'bg-yellow-500 animate-pulse',

        async execute(commandName) {
            this.commandName = commandName;
            this.open = true;
            this.activeTab = 'output';
            this.outputHtml = '';
            this.statusText = 'Executing...';
            this.statusClass = 'bg-yellow-500 animate-pulse';

            // Load documentation
            this.loadDocumentation(commandName);

            // Execute command
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
                                console.error('Error parsing command data:', e);
                            }
                        }
                    });
                }
            } catch (error) {
                console.error('Error executing command:', error);
                this.outputHtml += `\n❌ Error: ${error.message}`;
                this.statusText = 'Error';
                this.statusClass = 'bg-red-500';
            }
        },

        handleCommandData(data) {
            switch (data.type) {
                case 'start':
                    this.outputHtml = `🚀 Starting command: ${data.command}\n📝 Arguments: ${data.args.join(' ')}\n\n`;
                    this.statusText = 'Executing...';
                    this.statusClass = 'bg-yellow-500 animate-pulse';
                    break;
                case 'output':
                    this.outputHtml += data.line + '\n';
                    break;
                case 'complete':
                    const success = data.return_code === 0;
                    this.statusText = success ? 'Completed' : 'Failed';
                    this.statusClass = success ? 'bg-green-500' : 'bg-red-500';
                    let completionMessage = `${success ? '✅' : '❌'} Command completed with exit code: ${data.return_code}`;
                    if (data.execution_time) {
                        completionMessage += ` (${data.execution_time}s)`;
                    }
                    this.outputHtml += '\n' + completionMessage;
                    break;
                case 'error':
                    this.outputHtml += `❌ Error: ${data.error}\n`;
                    this.statusText = 'Error';
                    this.statusClass = 'bg-red-500';
                    break;
            }
        },

        async loadDocumentation(commandName) {
            this.docsHtml = `
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold text-font-important-light dark:text-font-important-dark">${commandName}</h3>
                    <div class="text-sm text-font-subtle-light dark:text-font-subtle-dark">
                        <p class="mb-2">Loading documentation for <code class="bg-base-200 dark:bg-base-700 px-2 py-1 rounded">${commandName}</code>...</p>
                        <p class="mt-4">To view full documentation, run:</p>
                        <pre class="bg-base-200 dark:bg-base-700 p-3 rounded-lg mt-2"><code>python manage.py help ${commandName}</code></pre>
                    </div>
                </div>
            `;

            try {
                const response = await fetch(`/cfg/commands/help/${commandName}/`);
                const data = await response.json();
                if (data.help_text) {
                    this.docsHtml = `
                        <div class="space-y-4">
                            <h3 class="text-lg font-semibold text-font-important-light dark:text-font-important-dark">${commandName}</h3>
                            <pre class="text-sm text-font-default-light dark:text-font-default-dark whitespace-pre-wrap">${data.help_text}</pre>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading documentation:', error);
                this.docsHtml = `
                    <div class="text-red-600 dark:text-red-400">
                        <p>Failed to load documentation.</p>
                        <p class="text-sm mt-2">Try running: <code class="bg-base-200 dark:bg-base-700 px-2 py-1 rounded">python manage.py help ${commandName}</code></p>
                    </div>
                `;
            }
        },

        close() {
            this.open = false;
        }
    };
}

// Register component when Alpine initializes
document.addEventListener('alpine:init', () => {
    Alpine.data('commandModal', commandModalComponent);
});

// Global wrapper for backward compatibility
window.executeCommand = function(commandName) {
    const modalEl = document.querySelector('[x-data="commandModal"]');
    if (modalEl && Alpine) {
        const component = Alpine.$data(modalEl);
        if (component && component.execute) {
            component.execute(commandName);
        }
    }
};
