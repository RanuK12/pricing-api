"""Lógica de cálculo de precios."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from .models import PriceRequest, PriceResponse


def calculate_price(req: PriceRequest) -> PriceResponse:
    """Calcula el precio final aplicando markup, descuento y cantidad."""
    base = req.base_amount

    # Markup
    markup_amount = Decimal("0")
    if req.markup_percent:
        markup_amount = (base * req.markup_percent / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    # Discount sobre base + markup
    subtotal_before_discount = base + markup_amount
    discount_amount = Decimal("0")
    if req.discount_percent:
        discount_amount = (
            subtotal_before_discount * req.discount_percent / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    subtotal = subtotal_before_discount - discount_amount
    total = (subtotal * Decimal(str(req.quantity))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return PriceResponse(
        base_amount=base,
        markup_amount=markup_amount,
        discount_amount=discount_amount,
        subtotal=subtotal,
        quantity=req.quantity,
        total=total,
        currency=req.target_currency or req.currency,
        applied_markup=req.markup_percent,
        applied_discount=req.discount_percent,
    )
