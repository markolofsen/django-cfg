.PHONY: help claude codex commit

help:
	@echo "Available commands:"
	@echo "  make claude       - Start Claude Code in this directory (skip permissions)"
	@echo "  make codex        - Start Codex CLI in this directory (bypass approvals/sandbox)"
	@echo "  make commit       - Stage all changes and commit with AI-generated message"

# Start Claude Code with dangerously-skip-permissions flag
claude:
	claude --dangerously-skip-permissions

# Start Codex CLI with bypassed approvals and sandbox
codex:
	codex --dangerously-bypass-approvals-and-sandbox

# Stage all changes and commit with AI-generated message using orc
commit:
	git add . && orc commit
