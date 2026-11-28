# Canonical Django CFG development runtime

This directory is the Docker runtime for the application already present at
`solution/projects/{django,frontend}` in this Git repository. It does not
contain a second sample application.

Prerequisites: Linux Docker Engine with Compose v2 and Buildx, Git,
Python 3.10+, curl, OpenSSL with Ed25519 support, a non-root authorized
local Docker operator and outbound access to the official release,
package and image registries. Have the required PostgreSQL, Redis and
Nginx images available locally. The shared first-install builder verifies
the official signed stable CMDOP artifact, builds the toolbox and records
the exact immutable image ID in owner-private state. It does not accept a
preexisting arbitrary image tag. Native CMDOP updates remain separate.

The development docs service has a separate 10 GiB memory limit and four
CPUs. Allow sufficient additional host memory for the rest of the stack.

From the customer's Git root, choose a unique project name, an unused
four-port loopback range, a unique machine name and an external private state
directory. Keep that directory outside the customer Git root.

```sh
python3 solution/docker/scripts/canonical_launcher.py init \
  --root "$PWD" --state-dir "$HOME/.local/share/example-cfg" \
  --project example-cfg --base-port 28080 \
  --machine example-cfg-dev
python3 solution/docker/scripts/canonical_launcher.py bootstrap \
  --env-file "$HOME/.local/share/example-cfg/private.env"
python3 solution/docker/scripts/canonical_launcher.py inspect \
  --env-file "$HOME/.local/share/example-cfg/private.env"
python3 solution/docker/scripts/canonical_launcher.py start \
  --env-file "$HOME/.local/share/example-cfg/private.env"
```

The private state directory contains credentials and the verified toolbox
receipt. Do not copy it into Git or another installation. Repeating bootstrap
reuses the verified image ID; a mismatched or missing image referenced by an
existing receipt is refused rather than silently rebuilt. The initial image
receipt is a local build attestation, not a registry signature.

The four local routes are demo, docs, Storybook and API in that order.
Dependency bootstrap uses registry access; ordinary application services are
isolated. Inspect status and use the same launcher and private env to stop.
Stopping retains project data. Do not copy identity or secrets into Git.

Machine startup is explicit and requires separate owner admission. No
unattended enrollment, public tunnel or production deployment is enabled.
The customer Git-root `workflow/` is the integration contract.
