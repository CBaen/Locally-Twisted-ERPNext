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

# Clone upstream apps. --depth 1 keeps the image lean. .git dirs are stripped
# afterward — runtime doesn't need them, and stripping shrinks the image.
RUN cd apps \
    && git clone --depth 1 https://github.com/frappe/payments.git payments \
    && git clone --depth 1 https://github.com/frappe/webshop.git webshop \
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

# Compile assets at image-build time. The compiled bundles end up in
# apps/<app>/public/dist/, which is in the image. No more "Node disappears
# on recreate" because Node was only used during the build, not at runtime.
#
# Build each app explicitly. `bench build --production` (no --app) only walks
# apps registered via `bench get-app`. Because we used `pip install -e` instead,
# the apps must be passed by name or their bundles get skipped — that's the bug
# that left webshop's web.bundle.js missing and broke category pages.
RUN bench build \
    --app frappe \
    --app erpnext \
    --app payments \
    --app webshop \
    --app locally_twisted \
    --production

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
    && grep -q 'proxy_set_header Origin \$http_origin;' /templates/nginx/frappe.conf.template
USER frappe

# Inherit volumes, ports, command from the base image. The base already
# declares VOLUME /home/frappe/frappe-bench/sites and /logs and CMD gunicorn.
