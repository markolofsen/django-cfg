.PHONY: help claude commit

help:
	@echo "Available commands:"
	@echo "  make claude       - Start Claude Code in this directory (skip permissions)"
	@echo "  make commit       - Stage all changes and commit with AI-generated message"

# Start Claude Code with dangerously-skip-permissions flag
claude:
	claude --dangerously-skip-permissions

# Stage all changes and commit with AI-generated message using orc
commit:
	git add . && orc commit
