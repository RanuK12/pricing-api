"""Pricing API — microservicio de planes, precios y cálculos dinámicos."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .models import Plan, PriceRequest, PriceResponse, HealthResponse
from .pricing import calculate_price

app = FastAPI(
    title="Pricing API",
    version="1.0.0",
    description="Microservicio de precios dinámicos con planes y cálculos.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── In-memory store ────────────────────────────────────────────────
_plans: dict[str, Plan] = {}


# ── Endpoints ──────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check."""
    return HealthResponse(status="ok", plans_count=len(_plans))


@app.get("/plans", response_model=list[Plan])
async def list_plans():
    """Listar todos los planes."""
    return list(_plans.values())


@app.get("/plans/{plan_id}", response_model=Plan)
async def get_plan(plan_id: str):
    """Obtener un plan por ID."""
    if plan_id not in _plans:
        raise HTTPException(404, f"Plan '{plan_id}' not found")
    return _plans[plan_id]


@app.post("/plans", response_model=Plan, status_code=201)
async def create_plan(plan: Plan):
    """Crear un nuevo plan."""
    if plan.id in _plans:
        raise HTTPException(409, f"Plan '{plan.id}' already exists")
    _plans[plan.id] = plan
    return plan


@app.put("/plans/{plan_id}", response_model=Plan)
async def update_plan(plan_id: str, plan: Plan):
    """Actualizar un plan existente."""
    if plan_id not in _plans:
        raise HTTPException(404, f"Plan '{plan_id}' not found")
    plan.id = plan_id
    _plans[plan_id] = plan
    return plan


@app.delete("/plans/{plan_id}", status_code=204)
async def delete_plan(plan_id: str):
    """Eliminar un plan."""
    if plan_id not in _plans:
        raise HTTPException(404, f"Plan '{plan_id}' not found")
    del _plans[plan_id]


@app.post("/calculate", response_model=PriceResponse)
async def calculate(body: PriceRequest):
    """Calcular precio final aplicando markup, descuento y moneda."""
    result = calculate_price(body)
    return result
