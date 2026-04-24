# Verify the live API in 5 minutes

This guide helps you verify that SCE Core is a **real running backend**, not just a mock UI.

## 1) What is real vs. mock

- **GitHub Pages / Lovable / static frontend** can render mock or precomputed data for presentation.
- **SCE Core FastAPI backend** (`sce.api:app`) is the real execution engine for:
  - `POST /demo`
  - `POST /compare`
  - `POST /decide`
  - `GET /memory`
  - `GET /reliability`
  - `GET /graph`
  - `GET /ui`
- To get live results, the FastAPI backend must be running.

## 2) Run backend locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[api]
uvicorn sce.api:app --reload
```

Open:
- Swagger UI: <http://127.0.0.1:8000/docs>
- Built-in API UI route: <http://127.0.0.1:8000/ui>

## 3) Verify core endpoints with curl

All example payloads below are stored in [`examples/api_payloads/`](../examples/api_payloads).

### `POST /demo` — resource-stability

```bash
curl -sS -X POST http://127.0.0.1:8000/demo \
  -H "Content-Type: application/json" \
  -d @examples/api_payloads/demo_resource_stability.json
```

### `POST /demo` — epidemic-regime

```bash
curl -sS -X POST http://127.0.0.1:8000/demo \
  -H "Content-Type: application/json" \
  -d @examples/api_payloads/demo_epidemic_regime.json
```

### `POST /demo` — hypothesis

```bash
curl -sS -X POST http://127.0.0.1:8000/demo \
  -H "Content-Type: application/json" \
  -d @examples/api_payloads/demo_hypothesis.json
```

### `POST /compare`

```bash
curl -sS -X POST http://127.0.0.1:8000/compare \
  -H "Content-Type: application/json" \
  -d @examples/api_payloads/compare_epidemic_context.json
```

### `POST /decide` (with `execute=true`)

```bash
curl -sS -X POST http://127.0.0.1:8000/decide \
  -H "Content-Type: application/json" \
  -d @examples/api_payloads/decide_resource_context.json
```

### `GET /memory`

```bash
curl -sS http://127.0.0.1:8000/memory
```

### `GET /reliability`

```bash
curl -sS http://127.0.0.1:8000/reliability
```

### `GET /graph`

```bash
curl -sS http://127.0.0.1:8000/graph
```

## 4) One-command verification script

Run:

```bash
python examples/verify_live_api.py
```

or with custom base URL:

```bash
python examples/verify_live_api.py --base-url http://127.0.0.1:8000
```

The script calls all key endpoints, prints concise pass/fail status, and exits non-zero if any check fails.

## 5) Connect frontend to a live backend

- Local API base URL is usually: `http://127.0.0.1:8000`
- A **published static frontend cannot reach your localhost** (`127.0.0.1` on your laptop is not available to other users/browsers).
- For public demos, expose or deploy backend separately:
  - tunnel tools (e.g. ngrok/cloudflared), or
  - deploy FastAPI backend to a reachable host.
- Configure frontend API base URL via environment variable, e.g. `VITE_SCE_API_BASE_URL` (or the exact equivalent used by your frontend project).

## 6) What “data loading” means today

Current API usage is request-driven:
- Inputs are JSON requests and scenario parameters in endpoint payloads.
- CSV/dataset file upload is **not implemented yet** in current API routes.
- Starter payloads are provided in [`examples/api_payloads/`](../examples/api_payloads).
- A future extension can add dataset adapters/upload routes.

## 7) Optional PostgreSQL durability

- Without `SCE_DATABASE_URL`, `/memory` and `/reliability` reflect process-local runtime memory.
- With `SCE_DATABASE_URL`, episodes can be stored via PostgreSQL-backed repository.
- Durability is currently alpha/hybrid (durable episode store plus process-local runtime behavior).
