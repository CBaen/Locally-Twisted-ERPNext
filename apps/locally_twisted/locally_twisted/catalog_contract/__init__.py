"""Catalog/product-page contract helpers.

This package is intentionally pure/data-oriented. It should be safe to run
against source artifacts before any ERPNext DB purge or import.
"""

from locally_twisted.catalog_contract.models import (
    AddOnContract,
    ColorGroupContract,
    ColorOptionContract,
    GalleryImageContract,
    OptionDependencyMatrixContract,
    ProductPageContract,
    RequiredOptionAxisContract,
)
from locally_twisted.catalog_contract.addon_review import build_add_on_approval_packet
from locally_twisted.catalog_contract.dependency_rules import available_options_for_selection
from locally_twisted.catalog_contract.media_classification import build_media_classification_packet
from locally_twisted.catalog_contract.price_review import build_price_review_packet
from locally_twisted.catalog_contract.source_builder import build_product_page_contract

__all__ = [
    "AddOnContract",
    "ColorGroupContract",
    "ColorOptionContract",
    "GalleryImageContract",
    "OptionDependencyMatrixContract",
    "ProductPageContract",
    "RequiredOptionAxisContract",
    "build_add_on_approval_packet",
    "available_options_for_selection",
    "build_media_classification_packet",
    "build_price_review_packet",
    "build_product_page_contract",
]
