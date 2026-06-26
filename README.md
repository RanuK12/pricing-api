# Pricing API

Microservicio RESTful de planes de precios y cálculo dinámico. Construido con FastAPI, deployado con Docker.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/plans` | Listar todos los planes |
| GET | `/plans/{id}` | Obtener un plan |
| POST | `/plans` | Crear un plan |
| PUT | `/plans/{id}` | Actualizar un plan |
| DELETE | `/plans/{id}` | Eliminar un plan |
| POST | `/calculate` | Calcular precio con markup/descuento/cantidad |

## Uso rápido

```bash
# Crear un plan
curl -X POST http://localhost:8000/plans \
  -H 'Content-Type: application/json' \
  -d '{"id":"pro","name":"Professional","base_price":99,"currency":"USD"}'

# Calcular precio (Pro x12 con 15% descuento anual)
curl -X POST http://localhost:8000/calculate \
  -H 'Content-Type: application/json' \
  -d '{"base_amount":99,"discount_percent":15,"quantity":12}'
```

## Deploy

```bash
docker compose up -d --build
```

La API queda en `http://localhost:8000`. Docs interactivos en `/docs`.

## Stack

- Python 3.12 + FastAPI
- Pydantic v2 (validación)
- Docker + docker-compose
