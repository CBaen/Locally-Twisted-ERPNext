import frappe


no_cache = 1
sitemap = 0


def get_context(context):
    port = _preview_port()
    preview_origin = f"http://127.0.0.1:{port}"

    context.title = "Event Playground - Internal Preview"
    context.no_breadcrumbs = 1
    context.event_playground_origin = preview_origin
    context.event_playground_asset = f"{preview_origin}/event-playground.html"
    return context


def _preview_port():
    raw = str(
        frappe.form_dict.get("port")
        or frappe.conf.get("event_playground_preview_port")
        or "4306"
    ).strip()
    try:
        port = int(raw)
    except ValueError:
        return 4306
    if 1024 <= port <= 65535:
        return port
    return 4306
