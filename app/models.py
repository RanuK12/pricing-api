"""Modelos Pydantic para la Pricing API."""
from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    ARS = "ARS"
    GBP = "GBP"
    BRL = "BRL"


class Plan(BaseModel):
    """Plan de precios."""
    id: str = Field(..., description="Identificador único del plan")
    name: str = Field(..., description="Nombre del plan (ej: Basic, Pro, Enterprise)")
    description: str = Field("", description="Descripción del plan")
    base_price: Decimal = Field(..., gt=0, description="Precio base mensual")
    currency: Currency = Field(Currency.USD, description="Moneda del precio base")
    features: list[str] = Field(default_factory=list, description="Lista de features incluidas")
    max_users: Optional[int] = Field(None, ge=1, description="Máximo de usuarios (null = ilimitado)")
    is_active: bool = Field(True, description="Si el plan está disponible")


class PriceRequest(BaseModel):
    """Solicitud de cálculo de precio."""
    base_amount: Decimal = Field(..., gt=0, description="Monto base a calcular")
    currency: Currency = Field(Currency.USD, description="Moneda del monto base")
    markup_percent: Optional[Decimal] = Field(None, ge=0, le=1000, description="Markup % a aplicar")
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100, description="Descuento % a aplicar")
    quantity: int = Field(1, ge=1, description="Cantidad de unidades")
    target_currency: Optional[Currency] = Field(None, description="Moneda de salida (opcional)")


class PriceResponse(BaseModel):
    """Resultado del cálculo de precio."""
    base_amount: Decimal
    markup_amount: Decimal = Field(default=Decimal("0"))
    discount_amount: Decimal = Field(default=Decimal("0"))
    subtotal: Decimal
    quantity: int
    total: Decimal
    currency: Currency
    applied_markup: Optional[Decimal] = None
    applied_discount: Optional[Decimal] = None


class HealthResponse(BaseModel):
    """Respuesta de health check."""
    status: str
    plans_count: int
