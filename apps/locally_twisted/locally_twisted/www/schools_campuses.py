"""Schools and campuses event balloon page."""

from locally_twisted.www.event_type_pages import get_event_type_context

no_cache = 1
sitemap = 1


def get_context(context):
    return get_event_type_context(context, "schools_campuses")
