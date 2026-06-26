"""Tests para la Pricing API."""
from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Plan, PriceRequest
from app.pricing import calculate_price

client = TestClient(app)


# ── Helpers ────────────────────────────────────────────────────────
def _clean():
    """Limpia los planes in-memory."""
    from app.main import _plans
    _plans.clear()


# ── Health ─────────────────────────────────────────────────────────
class TestHealth:
    def test_health_ok(self):
        _clean()
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["plans_count"] == 0

    def test_health_with_plans(self):
        _clean()
        client.post("/plans", json={"id": "x", "name": "X", "base_price": 10})
        resp = client.get("/health")
        assert resp.json()["plans_count"] == 1


# ── Plans CRUD ─────────────────────────────────────────────────────
class TestPlans:
    def setup_method(self):
        _clean()

    def test_create_plan(self):
        resp = client.post("/plans", json={
            "id": "pro", "name": "Pro", "base_price": 99, "currency": "USD"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == "pro"
        assert data["base_price"] == "99"
        assert data["currency"] == "USD"

    def test_create_free_plan(self):
        """base_price=0 debe ser aceptado."""
        resp = client.post("/plans", json={
            "id": "free", "name": "Free", "base_price": 0
        })
        assert resp.status_code == 201
        assert resp.json()["base_price"] == "0"

    def test_create_duplicate(self):
        client.post("/plans", json={"id": "a", "name": "A", "base_price": 10})
        resp = client.post("/plans", json={"id": "a", "name": "A", "base_price": 10})
        assert resp.status_code == 409

    def test_list_plans(self):
        client.post("/plans", json={"id": "a", "name": "A", "base_price": 10})
        client.post("/plans", json={"id": "b", "name": "B", "base_price": 20})
        resp = client.get("/plans")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_plan(self):
        client.post("/plans", json={"id": "x", "name": "X", "base_price": 15})
        resp = client.get("/plans/x")
        assert resp.status_code == 200
        assert resp.json()["name"] == "X"

    def test_get_plan_not_found(self):
        resp = client.get("/plans/nonexistent")
        assert resp.status_code == 404

    def test_update_plan(self):
        client.post("/plans", json={"id": "x", "name": "X", "base_price": 10})
        resp = client.put("/plans/x", json={
            "id": "x", "name": "X Updated", "base_price": 20
        })
        assert resp.status_code == 200
        assert resp.json()["base_price"] == "20"

    def test_update_not_found(self):
        resp = client.put("/plans/nope", json={
            "id": "nope", "name": "N", "base_price": 5
        })
        assert resp.status_code == 404

    def test_delete_plan(self):
        client.post("/plans", json={"id": "x", "name": "X", "base_price": 10})
        resp = client.delete("/plans/x")
        assert resp.status_code == 204
        assert client.get("/plans/x").status_code == 404

    def test_delete_not_found(self):
        resp = client.delete("/plans/nonexistent")
        assert resp.status_code == 404


# ── Calculate ──────────────────────────────────────────────────────
class TestCalculate:
    def test_basic_calculation(self):
        resp = client.post("/calculate", json={
            "base_amount": 100, "quantity": 1
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == "100.00"
        assert data["currency"] == "USD"

    def test_with_discount(self):
        resp = client.post("/calculate", json={
            "base_amount": 100, "discount_percent": 20, "quantity": 1
        })
        assert resp.json()["total"] == "80.00"

    def test_with_markup(self):
        resp = client.post("/calculate", json={
            "base_amount": 100, "markup_percent": 50, "quantity": 1
        })
        assert resp.json()["total"] == "150.00"

    def test_with_markup_and_discount(self):
        """Markup se aplica primero, descuento después."""
        resp = client.post("/calculate", json={
            "base_amount": 100, "markup_percent": 10, "discount_percent": 10, "quantity": 1
        })
        # base=100, markup=10 → 110, discount 10% → 99
        assert resp.json()["total"] == "99.00"

    def test_with_quantity(self):
        resp = client.post("/calculate", json={
            "base_amount": 50, "quantity": 3
        })
        assert resp.json()["total"] == "150.00"

    def test_free_plan(self):
        """base_amount=0 debe dar total=0."""
        resp = client.post("/calculate", json={
            "base_amount": 0, "quantity": 1
        })
        assert resp.json()["total"] == "0.00"

    def test_quantity_annual_discount(self):
        """Pro $99/mes x12 con 15% descuento anual."""
        resp = client.post("/calculate", json={
            "base_amount": 99, "discount_percent": 15, "quantity": 12
        })
        assert resp.json()["total"] == "1009.80"

    def test_reseller_markup(self):
        """Starter $29 +30% markup."""
        resp = client.post("/calculate", json={
            "base_amount": 29, "markup_percent": 30, "quantity": 1
        })
        assert resp.json()["total"] == "37.70"


# ── Unit: pricing logic ────────────────────────────────────────────
class TestPricingLogic:
    def test_calculate_price_markup_discount(self):
        req = PriceRequest(
            base_amount=Decimal("200"),
            markup_percent=Decimal("15"),
            discount_percent=Decimal("10"),
            quantity=2,
        )
        result = calculate_price(req)
        # base=200, markup=30 → 230, discount 10% → 207, x2 = 414
        assert result.total == Decimal("414.00")
        assert result.markup_amount == Decimal("30.00")
        assert result.discount_amount == Decimal("23.00")

    def test_edge_large_discount(self):
        """100% discount = free."""
        req = PriceRequest(
            base_amount=Decimal("100"),
            discount_percent=Decimal("100"),
            quantity=1,
        )
        assert calculate_price(req).total == Decimal("0.00")

    def test_edge_large_markup(self):
        """1000% markup."""
        req = PriceRequest(
            base_amount=Decimal("10"),
            markup_percent=Decimal("1000"),
            quantity=1,
        )
        assert calculate_price(req).total == Decimal("110.00")
