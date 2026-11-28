# Frontend monorepo — npm publishing and package utilities.
#
# One publisher for packages/ (synced versions) and widgets/ (independent
# versions). The logic is scripts/publish/cli.mjs; this file is the short
# spelling. Group policy lives in publish.config.mjs.
#
#   make list                          local vs npm, every publishable member
#   make plan BUMP=auto                what publish would do — touches nothing
#   make publish BUMP=patch            bump, build, publish everything
#   make publish BUMP=auto SKIP=ui-tools,ogimage
#   make publish ONLY=ogimage WIDGETS=patch
#   make publish-dry BUMP=patch        npm publish --dry-run
#   make bump BUMP=minor               versions only
#
# Variables: BUMP PACKAGES WIDGETS ONLY SKIP GROUP OTP TAG  (DRY=1 KEEP=1 NOBUILD=1)

PUBLISH := node scripts/publish/cli.mjs

ARGS :=
ifneq ($(BUMP),)
  ARGS += --bump $(BUMP)
endif
ifneq ($(PACKAGES),)
  ARGS += --packages $(PACKAGES)
endif
ifneq ($(WIDGETS),)
  ARGS += --widgets $(WIDGETS)
endif
ifneq ($(ONLY),)
  ARGS += --only $(ONLY)
endif
ifneq ($(SKIP),)
  ARGS += --skip $(SKIP)
endif
ifneq ($(GROUP),)
  ARGS += --group $(GROUP)
endif
ifneq ($(OTP),)
  ARGS += --otp $(OTP)
endif
ifneq ($(TAG),)
  ARGS += --tag $(TAG)
endif
ifneq ($(DRY),)
  ARGS += --dry-run
endif
ifneq ($(KEEP),)
  ARGS += --keep-tmp
endif
ifneq ($(NOBUILD),)
  ARGS += --no-build
endif
ifneq ($(YES),)
  ARGS += --yes
endif

.DEFAULT_GOAL := help

.PHONY: help
help:
	@$(PUBLISH) --help
	@echo "  make list | plan | bump | publish | publish-dry | clean"
	@echo "  make publish-patch | publish-minor | publish-major   (compat: BUMP=<kind>)"
	@echo "  make check           source gates + npm login status"
	@echo "  make check-source    source gates only (also run inside publish)"
	@echo "  make use-client ACTION=scan|add|remove [DIR=packages/ui-core/src]"
	@echo "  make cleanup-npm     interactive cleanup of old npm versions"
	@echo ""

.PHONY: list plan bump publish publish-dry clean
list:
	@$(PUBLISH) list $(ARGS)
plan:
	@$(PUBLISH) plan $(ARGS)
bump: check-source
	@$(PUBLISH) bump $(ARGS)
publish: check-source
	@$(PUBLISH) publish $(ARGS)
publish-dry: check-source
	@$(PUBLISH) publish --dry-run $(ARGS)
clean:
	@$(PUBLISH) clean

# Compatibility with the old packages/Makefile spelling.
.PHONY: publish-patch publish-minor publish-major
publish-patch: check-source
	@$(PUBLISH) publish --bump patch $(ARGS)
publish-minor: check-source
	@$(PUBLISH) publish --bump minor $(ARGS)
publish-major: check-source
	@$(PUBLISH) publish --bump major $(ARGS)

# `make update [patch|minor|major]`: publish every changed @djangocfg/* package (default: patch).
# Same as publish-<kind>; exists because it is what the owner types.
.PHONY: update patch minor major
update: check-source
	@$(PUBLISH) publish --bump $(or $(filter patch minor major,$(MAKECMDGOALS)),patch) $(ARGS)
patch minor major:
	@:

# Source gates that must hold before anything reaches npm. Fast, no build.
# These run inside the publisher too (scripts/publish/lib/gates.mjs) — a make
# target is not a gate if `node scripts/publish/cli.mjs publish` bypasses it.
.PHONY: check-source
check-source:
	@node scripts/check-node.mjs
	@node scripts/check-tailwind-var-syntax.mjs
	@node scripts/check-widget-direction.mjs

.PHONY: check
check: check-source
	@npm whoami >/dev/null 2>&1 && echo "✓ npm: $$(npm whoami)" || (echo "✗ Not logged in to npm. Run: npm login" && exit 1)

.PHONY: use-client
use-client:
	@if [ -z "$(ACTION)" ]; then echo "Usage: make use-client ACTION=scan|add|remove [DIR=path]"; exit 1; fi
	@node scripts/use-client-manager.js $(ACTION) $(DIR)

.PHONY: cleanup-npm
cleanup-npm: check
	@node scripts/npm-cleanup.js
