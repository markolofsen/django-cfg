# i18n CLI
# Usage: make <command> [KEY=...] [T=...] [DIR=...]
#
# Works with:
#   - Package locales (default): src/locales
#   - App locales: DIR=path/to/app/i18n/locales

.PHONY: list check translate add sync help

# List all keys or search by pattern
# Usage: make list [KEY=pattern] [DIR=...]
list:
ifdef DIR
ifdef KEY
	@pnpm i18n list "$(KEY)" -d "$(DIR)"
else
	@pnpm i18n list -d "$(DIR)"
endif
else
ifdef KEY
	@pnpm i18n list "$(KEY)"
else
	@pnpm i18n list
endif
endif

# Check for missing keys in locales
# Usage: make check [DIR=...]
check:
ifdef DIR
	@pnpm i18n check -d "$(DIR)"
else
	@pnpm i18n check
endif

# Generate translation JSON template
# Usage: make translate T="English text"
translate:
ifndef T
	@echo "Usage: make translate T=\"English text\""
	@echo "Example: make translate T=\"Next\""
	@echo ""
	@echo "Show all available translations:"
	@echo "  make translate T=--all"
else ifeq ($(T),--all)
	@pnpm i18n translate --all
else
	@pnpm i18n translate "$(T)"
endif

# Add translation key to all locales
# Usage: make add KEY="path.to.key" T='{"en":"English","ru":"Русский"}' [DIR=...]
add:
ifndef KEY
	@echo "Usage: make add KEY=\"path.to.key\" T='{\"en\":\"English\",\"ru\":\"Русский\"}'"
else ifndef T
	@echo "Usage: make add KEY=\"path.to.key\" T='{\"en\":\"English\",\"ru\":\"Русский\"}'"
else ifdef DIR
	@pnpm i18n add "$(KEY)" '$(T)' -d "$(DIR)"
else
	@pnpm i18n add "$(KEY)" '$(T)'
endif

# Sync missing keys from base locale
# Usage: make sync [DIR=...] [DRY=1] [AUTO=1]
sync:
ifdef DIR
ifdef DRY
	@pnpm i18n sync -d "$(DIR)" --dry
else ifdef AUTO
	@pnpm i18n sync -d "$(DIR)" --auto
else
	@pnpm i18n sync -d "$(DIR)"
endif
else
ifdef DRY
	@pnpm i18n sync --dry
else ifdef AUTO
	@pnpm i18n sync --auto
else
	@pnpm i18n sync
endif
endif

# Show help
help:
	@echo "i18n CLI"
	@echo ""
	@echo "Commands:"
	@echo "  make list                      - List all translation keys"
	@echo "  make list KEY=tour             - Search keys containing 'tour'"
	@echo "  make check                     - Find missing keys in locales"
	@echo "  make translate T=\"Next\"        - Generate translation JSON"
	@echo "  make translate T=--all         - Show all common translations"
	@echo "  make add KEY=\"...\" T='{...}'   - Add key to all locales"
	@echo "  make sync                      - Sync missing keys from en"
	@echo "  make sync DRY=1                - Dry run (show changes)"
	@echo "  make sync AUTO=1               - Auto-translate common words"
	@echo ""
	@echo "Options:"
	@echo "  DIR=path    Work with custom locales directory"
	@echo ""
	@echo "Examples:"
	@echo "  # Package locales (default)"
	@echo "  make list KEY=upload"
	@echo "  make check"
	@echo ""
	@echo "  # App locales"
	@echo "  make list DIR=../../apps/studio/i18n/locales"
	@echo "  make check DIR=../../apps/studio/i18n/locales"
	@echo "  make sync DIR=../../apps/studio/i18n/locales AUTO=1"
	@echo ""
	@echo "Or use pnpm directly:"
	@echo "  pnpm i18n list tour"
	@echo "  pnpm i18n check -d path/to/locales"
	@echo "  pnpm i18n sync --auto -d path/to/locales"
