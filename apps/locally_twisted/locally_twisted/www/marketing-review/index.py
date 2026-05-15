from locally_twisted.marketing_review_access import apply_marketing_review_context


no_cache = 1
sitemap = 0


def get_context(context):
    return apply_marketing_review_context(context)
