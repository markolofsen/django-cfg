/**
 * Django CFG Commands JavaScript
 *
 * Handles command execution and modal interactions
 */

class CommandExecutor {
    constructor() {
        this.modal = document.getElementById('commandModal');
        this.commandNameEl = document.getElementById('commandName');
        this.commandOutput = document.getElementById('commandOutput');
        this.commandStatus = document.getElementById('commandStatus');
    }

    execute(commandName) {
        if (!this.modal || !this.commandNameEl || !this.commandOutput || !this.commandStatus) {
            console.error('Command modal elements not found');
            return;
        }

        this.commandNameEl.textContent = commandName;
        this.commandOutput.textContent = '';
        this.commandStatus.innerHTML = '<div class="w-3 h-3 bg-yellow-500 rounded-full mr-2 animate-pulse"></div><span class="text-sm font-medium text-gray-700 dark:text-gray-300">Executing...</span>';
        this.modal.classList.remove('hidden');

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

            const readStream = () => {
                return reader.read().then(({done, value}) => {
                    if (done) return;

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

                    return readStream();
                });
            };

            return readStream();
        })
        .catch(error => {
            console.error('Error executing command:', error);
            this.commandOutput.textContent += `\n❌ Error: ${error.message}`;
            this.commandStatus.innerHTML = '<div class="w-3 h-3 bg-red-500 rounded-full mr-2"></div><span class="text-sm font-medium text-red-600 dark:text-red-400">Error</span>';
        });
    }

    handleCommandData(data) {
        switch (data.type) {
            case 'start':
                this.commandOutput.innerHTML = '';
                this.addLogLine(`🚀 Starting command: ${data.command}`, 'info');
                this.addLogLine(`📝 Arguments: ${data.args.join(' ')}`, 'info');
                this.addLogLine('', 'spacer');
                this.commandStatus.innerHTML = '<div class="w-3 h-3 bg-yellow-500 rounded-full mr-2 animate-pulse"></div><span class="text-sm font-medium text-gray-700 dark:text-gray-300">Executing...</span>';
                break;
            case 'output':
                this.addLogLine(data.line, 'output');
                this.scrollToBottom();
                break;
            case 'complete':
                const success = data.return_code === 0;
                this.commandStatus.innerHTML = success
                    ? '<div class="w-3 h-3 bg-green-500 rounded-full mr-2"></div><span class="text-sm font-medium text-green-600 dark:text-green-400">Completed</span>'
                    : '<div class="w-3 h-3 bg-red-500 rounded-full mr-2"></div><span class="text-sm font-medium text-red-600 dark:text-red-400">Failed</span>';

                this.addLogLine('', 'spacer');
                let completionMessage = `${success ? '✅' : '❌'} Command completed with exit code: ${data.return_code}`;
                if (data.execution_time) {
                    completionMessage += ` (${data.execution_time}s)`;
                }
                this.addLogLine(completionMessage, success ? 'success' : 'error');
                this.scrollToBottom();
                break;
            case 'error':
                this.addLogLine(`❌ Error: ${data.error}`, 'error');
                this.commandStatus.innerHTML = '<div class="w-3 h-3 bg-red-500 rounded-full mr-2"></div><span class="text-sm font-medium text-red-600 dark:text-red-400">Error</span>';
                this.scrollToBottom();
                break;
        }
    }

    addLogLine(text, type = 'output') {
        const line = document.createElement('div');
        line.className = 'log-line';

        switch (type) {
            case 'info':
                line.className += ' text-blue-600 dark:text-blue-400 font-medium';
                break;
            case 'success':
                line.className += ' text-green-600 dark:text-green-400 font-medium';
                break;
            case 'error':
                line.className += ' text-red-600 dark:text-red-400 font-medium';
                break;
            case 'spacer':
                line.className += ' h-2';
                break;
            default:
                line.className += ' text-gray-700 dark:text-gray-300';
        }

        if (type === 'spacer') {
            line.innerHTML = '&nbsp;';
        } else {
            line.textContent = text;
        }

        this.commandOutput.appendChild(line);
    }

    scrollToBottom() {
        if (!this.commandOutput) return;

        setTimeout(() => {
            this.commandOutput.scrollTop = this.commandOutput.scrollHeight;
        }, 50);
    }

    close() {
        if (this.modal) {
            this.modal.classList.add('hidden');
        }
    }
}

// Global functions
function executeCommand(commandName) {
    const executor = new CommandExecutor();
    executor.execute(commandName);
}

function closeCommandModal() {
    const executor = new CommandExecutor();
    executor.close();
}

// Export
window.CommandExecutor = CommandExecutor;
window.executeCommand = executeCommand;
window.closeCommandModal = closeCommandModal;
