# Scripts

Utility scripts for the frontend monorepo. Run from `frontend/`.

## Publisher (`publish/`)

`node scripts/publish/cli.mjs <list|plan|bump|publish|clean>`, behind the root
`Makefile`. Groups and their versioning policy are in `publish.config.mjs`.

```bash
make list                 # local vs npm
make plan BUMP=auto       # what publish would do — writes nothing
make publish BUMP=patch   # bump, stage, build, publish
```

### Two versioning policies

- **`packages/*` — synced.** One version for the whole set; every member moves
  together so a consumer pins one number for the framework.
- **`widgets/*` — independent.** Each has its own version and is **published
  only when its content changed**. The publisher packs the local package and
  the published tarball and compares them file by file, ignoring `version` and
  `@djangocfg/*` ranges (the publisher rewrites both itself). `--all` forces a
  republish.

### How a release runs

1. Decide every target version (`plan` shows this and writes nothing).
2. Skip unchanged widgets.
3. Copy each member to `.tmp/publish/` — never publish from the working tree,
   which keeps `workspace:*` throughout.
4. Rewrite `workspace:*` to `^<version>` — **the version that will be on the
   registry**: the one this run publishes, or for a skipped widget the one
   already there. Naming the bumped local version of a skipped package is what
   made it uninstallable for everything depending on it.
5. Build in the original directory (monorepo deps resolve there), copy `dist/`.
6. `npm publish` from the stage.

Nothing waits on the registry. npm indexes a new version within a minute or
two on its own, nothing downstream reads it during a release, and the wait that
used to sit between steps hid real failures behind minutes of silence.

Run it as `make update [patch|minor|major]` from the django-cfg repo root or from `projects/solution/frontend` (default patch); it is `publish --bump <kind>`. Anywhere else there is no `update` target.

`publish` does not ask "publish? y/N": it prints a 3 second countdown (Ctrl+C cancels), or none with `--yes`. A failed gate or build stops it before anything is published.

### The one-time password

Direct publishing with a token that bypasses 2FA is being retired by npm (account
changes since 31 Jul 2026, publishing targeted for Jan 2027; and in practice a
saved bypass token still got `EOTP` on 6 Nov 2026). So the publisher uses your
login plus an OTP and makes that cheap:

- The code is asked for **right after the build**, with a system sound
  (`afplay` Glass) and a macOS notification, so you can walk away during the
  build and are called back when it is time. Elsewhere it rings the terminal bell.
- One code covers the whole parallel run. Type it at once: it lasts ~30 s.
- If npm rejects it (expired, mistyped), you are called again and **only the
  failed packages** are retried, with no rebuild.
- `--otp <code>` skips the prompt. Empty answer = no code.
- `npm whoami` must work (`npm login`, or a token in `~/.npmrc`): the OTP is
  paired with that login. Revoking old tokens needs an OTP too
  (`npm token revoke <id> --otp=<code>`).
- Long term: Trusted Publishing from CI, which needs neither token nor code.

### Three failures this design exists to prevent

- **An OTP is single-use.** One code sent with every package in a parallel run
  authenticates the first and fails the rest with `EOTP`. Avoid codes: use a
  token that bypasses 2FA (see Credentials). `npm profile` reports 2FA mode
  `auth-only` while npm still answers `EOTP` on publish, so the mode is no guide.
- **npm's exit code is not the verdict.** It prints `+ name@version` and exits
  0 for a publish it rejected with `EOTP`, so `publishOne` checks the output
  too. Trusting the code is how a release reported eleven successes and landed
  eight.
- **`files` is a recursive whitelist.** `.npmignore` is ignored inside a
  whitelisted directory, so `.claude/`, `@dev/` and `@sources/` shipped to npm
  until v2.1.294. The stage deletes every `.*` and `@*` path before packing.

### Layout

| File | Holds |
|---|---|
| `cli.mjs` | commands, the plan, arg parsing |
| `lib/workspace.mjs` | discovers members from `publish.config.mjs` |
| `lib/stage.mjs` | staging, dependency rewriting, build, `npm publish` |
| `lib/content.mjs` | has this package changed since its last release |
| `lib/registry.mjs` | reads npm — versions, whoami, 2FA mode |
| `lib/semver.mjs`, `lib/ui.mjs` | version maths; logging, tables, process running |

## NPM cleanup (`npm-cleanup.js`)

Interactive removal or deprecation of old versions on npm. Discovers the
package list the same way the publisher does. `make cleanup-npm`.

## Use Client Manager

Universal script to manage `'use client'` directives in Next.js App Router projects.

### Usage

```bash
# Scan for files that need 'use client'
node use-client-manager.js scan

# Scan specific directory
node scripts/use-client-manager.js scan packages/ui-core/src/components

# Add 'use client' to all files that need it
node use-client-manager.js add

# Remove 'use client' from all files
node use-client-manager.js remove
```

### What it detects

The script automatically detects files that need `'use client'` based on:

**Third-party libraries:**
- `@radix-ui/*` (UI primitives)
- `vaul` (drawer)
- `recharts` (charts)
- `react-hook-form` (forms)
- `cmdk` (command menu)
- `embla-carousel-react` (carousel)
- `react-day-picker` (calendar)
- `react-resizable-panels` (resizable panels)
- `sonner` (toast notifications)
- `input-otp` (OTP input)
- `framer-motion` (animations)
- `@vidstack` (video player)

**React patterns:**
- React hooks: `useState`, `useEffect`, `useContext`, etc.
- Browser APIs: `window`, `document`, `navigator`, `localStorage`, etc.
- Event handlers: `onClick`, `onChange`, `onSubmit`, etc.

### Examples

```bash
# Check what needs fixing (defaults to packages/)
node scripts/use-client-manager.js scan

# Fix all UI components
node scripts/use-client-manager.js add packages/ui-core/src

# Fix only hooks
node scripts/use-client-manager.js add packages/ui-core/src/hooks

# Remove all directives (for testing)
node scripts/use-client-manager.js remove packages/ui-core/src
```

## Why 'use client'?

Next.js 15 App Router uses a server-first architecture where all components are Server Components by default. Components that use:

- React hooks
- Browser APIs
- Interactive libraries
- Event handlers

Must be explicitly marked as Client Components with the `'use client'` directive.

## Best Practices

1. **Don't add everywhere** - Only add to components that actually need it
2. **Use the scanner** - Let the script detect what needs the directive
3. **Review changes** - Check the scan results before running `add`
4. **Keep Server Components** - Simple presentational components should stay as Server Components for better performance
