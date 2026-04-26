"""
Patch the LT frontend container's nginx config so socket.io passes the
browser's actual Origin header through to the upstream socketio service,
instead of rewriting it to `http://frontend` (the internal Docker hostname).

Why this is needed:
- frappe_docker's stock nginx config sets `proxy_set_header Origin
  $proxy_x_forwarded_proto://frontend;` for the /socket.io/ location.
- The socketio Node service uses `origin: true` (echoes the request's
  Origin back as Access-Control-Allow-Origin).
- The browser sends Origin=http://localhost:8081, but nginx rewrites it
  to http://frontend before the upstream sees it.
- Upstream replies ACAO=http://frontend → browser CORS check fails →
  socketio_client.js logs "Invalid origin" and the live UI is dead.

Fix: replace the rewrite with `proxy_set_header Origin $http_origin;`
which passes the original browser Origin through unchanged.

This is local-dev only. The frappe_docker upstream nginx config assumes
TLS termination at a load balancer where the rewrite is the right call.
For browser-direct localhost access, pass-through is correct.

This script edits the file IN the container; the change does not survive
container recreation. For a permanent fix, mount a custom frappe.conf via
docker-compose override.

Usage (run inside the container after `docker cp` of this file):
  docker cp patch_nginx_socketio_origin.py <container>:/tmp/
  docker exec <container> python3 /tmp/patch_nginx_socketio_origin.py
  docker exec <container> nginx -s reload
"""
import sys

CONF = "/etc/nginx/conf.d/frappe.conf"
OLD = "proxy_set_header Origin $proxy_x_forwarded_proto://frontend;"
NEW = "proxy_set_header Origin $http_origin;"

text = open(CONF).read()
if NEW in text and OLD not in text:
    print("[skip] already patched")
    sys.exit(0)
if OLD not in text:
    print(f"[ERROR] expected line not found in {CONF}")
    sys.exit(1)

open(CONF, "w").write(text.replace(OLD, NEW))
print(f"[ok] patched {CONF}: Origin pass-through enabled")
