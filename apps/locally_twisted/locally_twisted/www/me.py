from locally_twisted.customer_portal_pages import account_context, redirect_to
from locally_twisted.marketing_review_access import MARKETING_REVIEW_ROUTE, is_marketing_review_user


no_cache = 1
sitemap = 0


def get_context(context):
    if is_marketing_review_user():
        redirect_to(MARKETING_REVIEW_ROUTE)
    return account_context(context, "dashboard")
