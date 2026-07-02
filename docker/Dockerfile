# Locally Twisted — self-contained ERPNext v15 image
#
# Bakes everything into the image:
#   - frappe + erpnext (from base image frappe/erpnext:v15.105.0)
#   - payments (cloned from upstream at build time)
#   - webshop (cloned from upstream at build time)
#   - locally_twisted (COPYed from local source at build time)
#   - Node 18 + yarn (so bench build works)
#   - Compiled assets (bench build runs at image-build time)
#
# Result: docker compose up --force-recreate produces a fully-working stack
# with NO post-recreate scripts. Apps and assets live in the image, not in
# bind-mounts and not in the container's writable layer.
#
# Build (from project root):
#   docker buildx build -f docker/Dockerfile -t locally-twisted-erpnext:v15 .
#
# Build context = project root (so apps/locally_twisted/ is reachable via COPY).

ARG BASE_IMAGE=frappe/erpnext:v15.105.0
FROM ${BASE_IMAGE}
ARG PAYMENTS_REF=6c3be057f87c041779f34c6fcb319d8bf0eda5b0
ARG WEBSHOP_REF=6c8fd0013dfe297edb6ebcc10e27ba495902dd19

USER root

# Node 18 + yarn — bench build needs them. The upstream production image
# strips Node out, which is why install_webshop.py used to install it at
# runtime in the writable layer (lost on every recreate).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g yarn \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER frappe
WORKDIR /home/frappe/frappe-bench

# Clone upstream apps at pinned commits. These refs were verified from the
# official version-15 branches on 2026-05-21; do not float to branch heads
# during build or the image can silently ship different Webshop/Payments code.
# .git dirs are stripped afterward because runtime doesn't need them.
RUN cd apps \
    && git init payments \
    && git -C payments remote add origin https://github.com/frappe/payments.git \
    && git -C payments fetch --depth 1 origin "${PAYMENTS_REF}" \
    && git -C payments checkout --detach FETCH_HEAD \
    && git init webshop \
    && git -C webshop remote add origin https://github.com/frappe/webshop.git \
    && git -C webshop fetch --depth 1 origin "${WEBSHOP_REF}" \
    && git -C webshop checkout --detach FETCH_HEAD \
    && rm -rf payments/.git webshop/.git

# Add the LT custom app from local source. Build context is project root,
# so apps/locally_twisted/ is reachable from here.
COPY --chown=frappe:frappe apps/locally_twisted /home/frappe/frappe-bench/apps/locally_twisted

# Editable install so the bench tooling sees them as proper Python packages.
# Locked into the image layer — survives recreates because the writable layer
# isn't where this lives anymore.
RUN /home/frappe/frappe-bench/env/bin/pip install --quiet --upgrade --no-cache-dir \
    -e apps/payments \
    -e apps/webshop \
    -e apps/locally_twisted

# Register apps in sites/apps.txt so `bench build --app <name>` finds them.
# pip install registers Python packages; bench reads apps.txt to know which
# apps to walk for asset compilation. Configurator service rewrites this file
# at container startup with the live list — at image-build time we just need
# bench to see the apps now.
RUN printf '%s\n' frappe erpnext payments webshop locally_twisted > sites/apps.txt

# Compile assets at image-build time. The compiled bundles end up in
# apps/<app>/public/dist/, which is in the image. No more "Node disappears
# on recreate" because Node was only used during the build, not at runtime.
#
# Build each app explicitly. `bench build --production` (no --app) only walks
# apps registered via `bench get-app`. Because we used `pip install -e` instead,
# the apps must be passed by name or their bundles get skipped — that's the bug
# that left webshop's web.bundle.js missing and broke category pages.
#
# Split into separate RUN steps to avoid OOM on constrained local Docker hosts.
# (yarn's bundler holds a lot of RAM per app; one app per RUN clears between).
# frappe + erpnext are already compiled in the base image, so don't rebuild
# them. locally_twisted has only plain CSS + plain JS (no SCSS, no bundle
# entry point) so it doesn't need bench build either.
#
# NODE_OPTIONS caps Node's heap so the bundler stays within the build host's
# memory budget. Without this, esbuild can OOM during the production minify
# step on constrained local Docker memory defaults.
ENV NODE_OPTIONS=--max-old-space-size=3072
RUN bench build --app payments --production
RUN bench build --app webshop --production

# Strip any leftover .git dirs (defense-in-depth; clones already stripped above).
RUN find apps -mindepth 1 -path "*/.git" -exec rm -rf {} + 2>/dev/null || true

# Patch the nginx config template so socket.io passes the browser's actual
# Origin header through to the upstream socketio service, rather than rewriting
# it to http://frontend (which fails browser-direct-localhost access). The base
# image's nginx-entrypoint.sh renders this template on container startup, so
# patching the template at image-build time means recreates inherit the patch
# automatically — no more runtime patch script needed.
USER root
RUN sed -i 's|proxy_set_header Origin [^;]*;|proxy_set_header Origin $http_origin;|' \
    /templates/nginx/frappe.conf.template \
    && grep -Fq 'proxy_set_header Origin $http_origin;' /templates/nginx/frappe.conf.template
USER frappe

# Inherit volumes, ports, command from the base image. The base already
# declares VOLUME /home/frappe/frappe-bench/sites and /logs and CMD gunicorn.
