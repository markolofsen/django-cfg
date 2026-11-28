# syntax=docker/dockerfile:1.7
ARG MACHINE_IMAGE=docker-cfg-machine:local
FROM ${MACHINE_IMAGE} AS machine
FROM node:22-bookworm-slim AS node
FROM python:3.13-slim-bookworm
ARG LOCAL_UID=1000
ARG LOCAL_GID=1000
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git tini util-linux build-essential libpq-dev rsync ripgrep procps \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid ${LOCAL_GID} developer \
    && useradd --uid ${LOCAL_UID} --gid ${LOCAL_GID} --create-home developer
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && npm install --global pnpm@12.18.0 \
    && python -m venv /opt/venv
# Native CMDOP updater atomically replaces its executable beside the old one.
# Only the development workspace permits writes to its container layer.
RUN install -d -o ${LOCAL_UID} -g ${LOCAL_GID} -m 0755 /opt/cmdop/bin
COPY --from=machine --chown=${LOCAL_UID}:${LOCAL_GID} --chmod=0755 /opt/cmdop/bin/cmdop /opt/cmdop/bin/cmdop
RUN ln -s /opt/cmdop/bin/cmdop /usr/local/bin/cmdop
COPY --chmod=0755 tools.sh /usr/local/bin/docker-cfg-tools
COPY --chmod=0755 entry.sh /usr/local/bin/docker-cfg-entry
RUN mkdir -p /workspace/solution/frontend/node_modules \
    /workspace/solution/frontend/apps/site/node_modules /workspace/solution/frontend/apps/site/.next \
    /workspace/solution/frontend/apps/my/node_modules /workspace/solution/frontend/apps/my/.next \
    /workspace/solution/frontend/apps/storybook/node_modules \
    /workspace/solution/frontend/packages/product/node_modules /workspace/solution/frontend/packages/ui/node_modules \
    /workspace/solution/django/staticfiles /workspace/solution/django/media \
    /workspace/solution/projects/django/staticfiles /workspace/solution/projects/django/media \
    /home/developer/.config/cmdop /home/developer/.cache /var/dev-data \
    && chown -R ${LOCAL_UID}:${LOCAL_GID} /workspace /opt/venv /home/developer /var/dev-data
RUN test -e /usr/bin/python3 || ln -s /usr/local/bin/python3 /usr/bin/python3
ENV PATH=/opt/venv/bin:/usr/local/bin:/usr/bin:/bin \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 NEXT_TELEMETRY_DISABLED=1 \
    STORYBOOK_DISABLE_TELEMETRY=1 CMDOP_GUI_ENABLED=false \
    CMDOP_GUI_AUTOSTART=false CMDOP_NO_METRICS=1
USER developer
# Named volumes inherit these image mountpoint owners on first creation.
RUN test -w /workspace/solution/projects/django/media \
    && test -w /workspace/solution/projects/django/staticfiles
RUN /usr/local/bin/docker-cfg-tools --report
WORKDIR /workspace
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/docker-cfg-entry"]
CMD ["python", "/workspace/scripts/workspace.py"]
