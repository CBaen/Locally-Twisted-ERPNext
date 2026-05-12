"""Serializable product-page contract models.

The rebuilt product frontend should consume this shape instead of scraping a
random mix of ERPNext/Odoo fields in templates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

CommerceLane = Literal["checkout", "quote_first", "hybrid", "needs_review"]
ProductPageType = Literal["simple_product", "complex_custom_product", "needs_review"]
ImageRole = Literal["primary", "gallery", "variant_image", "reference", "ignored_artifact"]
AxisStatus = Literal["required", "optional_addon", "customization", "needs_review"]
SelectorType = Literal["radio", "single_select", "multi_select_drawer", "cards", "needs_design"]


@dataclass(frozen=True)
class GalleryImageContract:
    url: str
    role: ImageRole
    source: str = "odoo"
    label: str = ""


@dataclass(frozen=True)
class ColorOptionContract:
    name: str
    vendor_name: str = ""
    hex_value: str = ""
    swatch_url: str = ""
    status: str = "needs_color_asset_review"


@dataclass(frozen=True)
class ColorGroupContract:
    group: str
    options: tuple[ColorOptionContract, ...]


@dataclass(frozen=True)
class RequiredOptionAxisContract:
    name: str
    display_type: str
    values: tuple[str, ...]
    status: AxisStatus = "required"
    selector_type: SelectorType = "radio"
    note: str = ""
    color_groups: tuple[ColorGroupContract, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AddOnContract:
    key: str
    label: str
    pricing_rule: str
    item_code: str = ""
    unit_price: float | None = None
    quantity_min: int = 1
    quantity_max: int = 1
    requires_value: bool = False
    receipt_label: str = ""
    source_attribute: str = ""
    status: Literal["confirmed", "needs_review"] = "needs_review"
    note: str = ""


@dataclass(frozen=True)
class OptionDependencyMatrixContract:
    axes: tuple[str, ...]
    valid_combinations: tuple[dict[str, str], ...]
    source_variant_rows: int = 0
    valid_combination_count: int = 0
    status: Literal["source_backed", "needs_review"] = "source_backed"
    note: str = ""


@dataclass(frozen=True)
class ProductPageContract:
    slug: str
    source_name: str
    route: str
    title: str
    description_html: str
    category_hint: str = ""
    product_page_type: ProductPageType = "needs_review"
    product_page_type_label: str = "Needs page review"
    commerce_lane: CommerceLane = "needs_review"
    commerce_lane_label: str = "Needs review before customers use it"
    primary_image: str = ""
    gallery: tuple[GalleryImageContract, ...] = field(default_factory=tuple)
    required_axes: tuple[RequiredOptionAxisContract, ...] = field(default_factory=tuple)
    customization_axes: tuple[RequiredOptionAxisContract, ...] = field(default_factory=tuple)
    add_ons: tuple[AddOnContract, ...] = field(default_factory=tuple)
    dependency_matrices: tuple[OptionDependencyMatrixContract, ...] = field(default_factory=tuple)
    source_variant_rows: int = 0
    has_resolver_prices: bool = False
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return asdict(self)
