#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
PAYLOAD_DIR = Path(__file__).resolve().parent / "api_payloads"


@dataclass(frozen=True)
class EndpointCheck:
    label: str
    method: str
    path: str
    payload_file: str | None = None


def build_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def load_payload(payload_file: str) -> dict[str, Any]:
    payload_path = PAYLOAD_DIR / payload_file
    with payload_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _request_json(method: str, url: str, payload: dict[str, Any] | None = None, timeout: float = 10.0) -> dict[str, Any]:
    data: bytes | None = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url=url, method=method.upper(), data=data, headers=headers)
    with request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else {}


def summarize_response(path: str, response_json: dict[str, Any]) -> str:
    if path == "/demo":
        result = response_json.get("result", {})
        return (
            f"demo={response_json.get('name')} "
            f"format={response_json.get('format')} "
            f"result_keys={len(result.keys()) if isinstance(result, dict) else 0}"
        )
    if path == "/compare":
        baseline = response_json.get("baseline", {})
        sce = response_json.get("sce", {})
        return (
            f"baseline_provider={baseline.get('provider')} "
            f"sce_plan={sce.get('selected_plan')} "
            f"score_count={len(sce.get('scores', []))}"
        )
    if path == "/decide":
        return (
            f"selected_plan={response_json.get('selected_plan')} "
            f"executed={response_json.get('executed')} "
            f"execution_success={response_json.get('execution_success')}"
        )
    if path == "/memory":
        meta = response_json.get("meta", {})
        return f"episodes={len(response_json.get('episodes', []))} persistence={meta.get('persistence')}"
    if path == "/reliability":
        rel = response_json.get("reliability", {})
        return (
            f"window={rel.get('recent_window_size')} "
            f"avg_reliability={rel.get('average_reliability')} "
            f"success_rate={rel.get('success_rate')}"
        )
    if path == "/graph":
        meta = response_json.get("meta", {})
        return f"nodes={meta.get('node_count')} edges={meta.get('edge_count')}"
    return "ok"


def run_check(base_url: str, check: EndpointCheck) -> tuple[bool, str]:
    url = build_url(base_url, check.path)
    payload = load_payload(check.payload_file) if check.payload_file else None
    response_json = _request_json(check.method, url, payload=payload)
    return True, summarize_response(check.path, response_json)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify live SCE Core FastAPI endpoints.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"API base URL (default: {DEFAULT_BASE_URL})")
    args = parser.parse_args()

    checks = [
        EndpointCheck("POST /demo (resource-stability)", "POST", "/demo", "demo_resource_stability.json"),
        EndpointCheck("POST /demo (epidemic-regime)", "POST", "/demo", "demo_epidemic_regime.json"),
        EndpointCheck("POST /demo (hypothesis)", "POST", "/demo", "demo_hypothesis.json"),
        EndpointCheck("POST /compare", "POST", "/compare", "compare_epidemic_context.json"),
        EndpointCheck("POST /decide", "POST", "/decide", "decide_resource_context.json"),
        EndpointCheck("GET /memory", "GET", "/memory"),
        EndpointCheck("GET /reliability", "GET", "/reliability"),
        EndpointCheck("GET /graph", "GET", "/graph"),
    ]

    print(f"Verifying live SCE API at: {args.base_url}")

    failures = 0
    for check in checks:
        try:
            ok, summary = run_check(args.base_url, check)
            marker = "PASS" if ok else "FAIL"
            print(f"[{marker}] {check.label}: {summary}")
            if not ok:
                failures += 1
        except error.HTTPError as exc:
            failures += 1
            detail = exc.read().decode("utf-8", errors="replace")
            print(f"[FAIL] {check.label}: HTTP {exc.code} {exc.reason} :: {detail[:220]}")
        except error.URLError as exc:
            failures += 1
            print(
                f"[FAIL] {check.label}: unable to reach backend at {args.base_url} ({exc}). "
                "Start it with: uvicorn sce.api:app --reload"
            )
        except FileNotFoundError as exc:
            failures += 1
            print(f"[FAIL] {check.label}: payload file missing ({exc})")
        except json.JSONDecodeError as exc:
            failures += 1
            print(f"[FAIL] {check.label}: response was not valid JSON ({exc})")
        except Exception as exc:  # pragma: no cover - defensive guardrail
            failures += 1
            print(f"[FAIL] {check.label}: unexpected error ({exc.__class__.__name__}: {exc})")

    if failures:
        print(f"\nVerification finished with {failures} failure(s).")
        return 1

    print("\nVerification finished successfully. Live API endpoints responded as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
