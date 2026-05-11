from locally_twisted.customer_portal_pages import redirect_to


sitemap = 0


def get_context(context):
    redirect_to("/me")
