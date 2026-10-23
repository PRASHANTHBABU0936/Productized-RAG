"""
Lightweight observability for the MM-RAG API.

Provides three things:

* **Metrics** - request counters and latency percentiles collected by an
  HTTP middleware, exposed as JSON or Prometheus text.
* **Usage** - per-model LLM call counts and token totals, with an
  estimated USD cost, so spend can be attributed without a vendor
  dashboard.
* **Health** - liveness plus a readiness probe that pings every
  dependency (PostgreSQL, Redis, Qdrant, Ollama).

Counters and usage totals are persisted to a JSON file
(``METRICS_FILE``, default ``data/metrics/observability.json``) so they
survive a process restart. Latency percentiles stay an in-process
rolling window: they describe recent behaviour, not history.

Still intentionally dependency-free: no Prometheus client library, no
external agent. Point a scraper at ``/metrics?format=prometheus``.
"""

from __future__ import annotations

import atexit
import json
import os
import tempfile
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# Metric storage
# --------------------------------------------------

_lock = threading.Lock()

_request_counts: dict[tuple[str, str, int], int] = defaultdict(int)
_latency_samples: dict[str, list[float]] = defaultdict(list)

# Per-model LLM usage: calls, token totals and estimated cost.
_usage_totals: dict[str, dict[str, float]] = defaultdict(
    lambda: {
        "calls": 0.0,
        "input_tokens": 0.0,
        "output_tokens": 0.0,
        "total_tokens": 0.0,
        "estimated_cost_usd": 0.0,
    }
)

_started_at = time.time()

# Bound the memory used by latency samples per endpoint.
MAX_LATENCY_SAMPLES = 2000

# --------------------------------------------------
# Persistence
# --------------------------------------------------

SCHEMA_VERSION = 1

METRICS_FILE = Path(
    os.getenv("METRICS_FILE")
    or (PROJECT_ROOT / "data" / "metrics" / "observability.json")
)

# Persisting on every request would dominate the latency being measured.
PERSIST_INTERVAL_SECONDS = float(
    os.getenv("METRICS_PERSIST_INTERVAL", "5")
)

# USD per 1,000,000 tokens. The default of 0 is correct for the local
# Ollama models this stack runs out of the box; set these to your
# provider's rates to get meaningful numbers for hosted models.
PRICE_INPUT_PER_MTOK = float(
    os.getenv("LLM_PRICE_INPUT_PER_MTOK") or 0.0
)
PRICE_OUTPUT_PER_MTOK = float(
    os.getenv("LLM_PRICE_OUTPUT_PER_MTOK") or 0.0
)

_last_persist_at = 0.0


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Estimate the USD cost of one LLM call from the configured rates.

    Rates are per 1M tokens (``LLM_PRICE_INPUT_PER_MTOK`` /
    ``LLM_PRICE_OUTPUT_PER_MTOK``) and default to 0.
    """
    return (
        (input_tokens / 1_000_000.0) * PRICE_INPUT_PER_MTOK
        + (output_tokens / 1_000_000.0) * PRICE_OUTPUT_PER_MTOK
    )


def _persist_locked() -> None:
    """
    Write the counter state atomically.

    The caller must already hold ``_lock``. Failures are swallowed: a
    metrics backend must never break a request.
    """
    payload = {
        "version": SCHEMA_VERSION,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "requests": [
            {
                "method": method,
                "path": path,
                "status": status,
                "count": count,
            }
            for (method, path, status), count in _request_counts.items()
        ],
        "usage": {
            name: dict(stats) for name, stats in _usage_totals.items()
        },
    }

    try:
        METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)

        descriptor, temp_path = tempfile.mkstemp(
            dir=str(METRICS_FILE.parent),
            prefix=".observability-",
            suffix=".tmp",
        )

        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)

        os.replace(temp_path, METRICS_FILE)
    except OSError:
        pass


def _maybe_persist_locked() -> None:
    """Persist at most once per ``PERSIST_INTERVAL_SECONDS``."""
    global _last_persist_at

    now = time.time()

    if now - _last_persist_at < PERSIST_INTERVAL_SECONDS:
        return

    _last_persist_at = now
    _persist_locked()


def flush() -> None:
    """Force-write the counters (called on interpreter exit)."""
    global _last_persist_at

    with _lock:
        _last_persist_at = time.time()
        _persist_locked()


def _load_persisted() -> None:
    """
    Restore counters written by a previous process.

    Called once at import time, so the import lock makes it race-free.
    """
    try:
        raw = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return

    for entry in raw.get("requests") or []:
        try:
            key = (
                str(entry["method"]).upper(),
                str(entry["path"]),
                int(entry["status"]),
            )
            count = int(entry["count"])
        except (KeyError, TypeError, ValueError):
            continue

        _request_counts[key] += count

    for name, stats in (raw.get("usage") or {}).items():
        target = _usage_totals[str(name)]

        for field in target:
            try:
                target[field] += float((stats or {}).get(field) or 0.0)
            except (TypeError, ValueError):
                continue


def record_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
) -> None:
    """Record one completed HTTP request."""
    key = (method.upper(), path, int(status_code))

    with _lock:
        _request_counts[key] += 1

        samples = _latency_samples[f"{method.upper()} {path}"]
        samples.append(float(duration_ms))

        if len(samples) > MAX_LATENCY_SAMPLES:
            del samples[: len(samples) - MAX_LATENCY_SAMPLES]

        _maybe_persist_locked()


def record_usage(
    model: str | None,
    usage: dict[str, Any] | None,
) -> dict[str, float] | None:
    """
    Accumulate one LLM call's token usage and estimated cost.

    Returns the recorded delta, or ``None`` when the model reported no
    token counts (some local models do not). Unlike request counters,
    usage is written immediately: calls are low-frequency and losing
    cost data to a restart is worse than a small write.
    """
    if not usage:
        return None

    try:
        input_tokens = int(usage.get("input_tokens") or 0)
        output_tokens = int(usage.get("output_tokens") or 0)
        total_tokens = int(
            usage.get("total_tokens") or (input_tokens + output_tokens)
        )
    except (TypeError, ValueError):
        return None

    if not (input_tokens or output_tokens):
        return None

    delta = {
        "calls": 1.0,
        "input_tokens": float(input_tokens),
        "output_tokens": float(output_tokens),
        "total_tokens": float(total_tokens),
        "estimated_cost_usd": estimate_cost(input_tokens, output_tokens),
    }

    global _last_persist_at

    with _lock:
        target = _usage_totals[str(model or "unknown")]

        for field, value in delta.items():
            target[field] += value

        _last_persist_at = time.time()
        _persist_locked()

    return delta


def _percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0

    index = min(
        len(sorted_values) - 1,
        int(round((pct / 100.0) * (len(sorted_values) - 1))),
    )

    return sorted_values[index]


def snapshot() -> dict[str, Any]:
    """Return an aggregated metrics snapshot."""
    with _lock:
        counts = dict(_request_counts)
        latencies = {
            key: sorted(values)
            for key, values in _latency_samples.items()
        }
        usage = {
            name: dict(stats) for name, stats in _usage_totals.items()
        }

    total_requests = sum(counts.values())
    client_errors = sum(
        count
        for (_, _, status), count in counts.items()
        if 400 <= status < 500
    )
    server_errors = sum(
        count
        for (_, _, status), count in counts.items()
        if status >= 500
    )

    endpoints: dict[str, dict[str, Any]] = {}

    for (method, path, status), count in counts.items():
        entry = endpoints.setdefault(
            f"{method} {path}",
            {
                "requests": 0,
                "status_counts": {},
                "latency_ms_mean": 0.0,
                "latency_ms_p50": 0.0,
                "latency_ms_p95": 0.0,
            },
        )

        entry["requests"] += count
        entry["status_counts"][str(status)] = count

    for key, values in latencies.items():
        entry = endpoints.get(key)

        if entry is None or not values:
            continue

        entry["latency_ms_mean"] = sum(values) / len(values)
        entry["latency_ms_p50"] = _percentile(values, 50)
        entry["latency_ms_p95"] = _percentile(values, 95)

    return {
        "uptime_seconds": round(time.time() - _started_at, 1),
        "total_requests": total_requests,
        "client_errors": client_errors,
        "server_errors": server_errors,
        "error_rate": (
            (client_errors + server_errors) / total_requests
            if total_requests
            else 0.0
        ),
        "endpoints": endpoints,
        "usage": {
            "models": usage,
            "totals": {
                field: sum(
                    stats.get(field, 0.0) for stats in usage.values()
                )
                for field in (
                    "calls",
                    "input_tokens",
                    "output_tokens",
                    "total_tokens",
                    "estimated_cost_usd",
                )
            },
            "price_per_mtok": {
                "input": PRICE_INPUT_PER_MTOK,
                "output": PRICE_OUTPUT_PER_MTOK,
            },
        },
    }


def render_prometheus() -> str:
    """Render the snapshot in the Prometheus text exposition format."""
    data = snapshot()

    lines = [
        "# HELP mmrag_uptime_seconds Seconds since the API process started.",
        "# TYPE mmrag_uptime_seconds gauge",
        f"mmrag_uptime_seconds {data['uptime_seconds']}",
        "# HELP mmrag_requests_total Total HTTP requests handled.",
        "# TYPE mmrag_requests_total counter",
    ]

    for (method, path, status), count in _request_counts.items():
        lines.append(
            f'mmrag_requests_total{{method="{method}",'
            f'path="{path}",status="{status}"}} {count}'
        )

    lines.extend(
        [
            "# HELP mmrag_request_latency_ms Request latency in milliseconds.",
            "# TYPE mmrag_request_latency_ms summary",
        ]
    )

    for endpoint, stats in data["endpoints"].items():
        method, _, path = endpoint.partition(" ")
        label = f'method="{method}",path="{path}"'
        lines.append(
            f"mmrag_request_latency_ms{{{label},quantile=\"0.5\"}} "
            f"{stats['latency_ms_p50']:.3f}"
        )
        lines.append(
            f"mmrag_request_latency_ms{{{label},quantile=\"0.95\"}} "
            f"{stats['latency_ms_p95']:.3f}"
        )

    lines.extend(
        [
            "# HELP mmrag_llm_calls_total LLM calls that reported usage.",
            "# TYPE mmrag_llm_calls_total counter",
            "# HELP mmrag_llm_tokens_total LLM tokens consumed by type.",
            "# TYPE mmrag_llm_tokens_total counter",
            "# HELP mmrag_llm_cost_usd_total Estimated LLM spend in USD.",
            "# TYPE mmrag_llm_cost_usd_total counter",
        ]
    )

    for model, stats in data["usage"]["models"].items():
        label = f'model="{model}"'

        lines.append(
            f"mmrag_llm_calls_total{{{label}}} {stats.get('calls', 0):.0f}"
        )

        for token_type, field in (
            ("input", "input_tokens"),
            ("output", "output_tokens"),
        ):
            lines.append(
                f"mmrag_llm_tokens_total{{{label},type=\"{token_type}\"}} "
                f"{stats.get(field, 0):.0f}"
            )

        lines.append(
            f"mmrag_llm_cost_usd_total{{{label}}} "
            f"{stats.get('estimated_cost_usd', 0.0):.6f}"
        )

    return "\n".join(lines) + "\n"


# --------------------------------------------------
# Health / readiness probes
# --------------------------------------------------

def _probe(name: str, check: Any) -> dict[str, Any]:
    started = time.perf_counter()

    try:
        detail = check()
        latency_ms = (time.perf_counter() - started) * 1000.0
        return {
            "status": "up",
            "latency_ms": round(latency_ms, 1),
            **(detail or {}),
        }

    except Exception as exc:  # noqa: BLE001
        return {
            "status": "down",
            "error": f"{type(exc).__name__}: {exc}",
        }


def check_database() -> dict[str, Any]:
    from sqlalchemy import text

    from backend.database import engine

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {}


def check_redis() -> dict[str, Any]:
    import redis

    client = redis.Redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        socket_connect_timeout=2,
        socket_timeout=2,
    )

    client.ping()

    return {}


def check_qdrant() -> dict[str, Any]:
    import requests

    url = (os.getenv("QDRANT_URL") or "").rstrip("/")

    if not url:
        raise RuntimeError("QDRANT_URL is not configured")

    headers = {}

    if os.getenv("QDRANT_API_KEY"):
        headers["api-key"] = os.getenv("QDRANT_API_KEY")

    response = requests.get(
        f"{url}/collections",
        headers=headers,
        timeout=5,
    )
    response.raise_for_status()

    collections = [
        item.get("name")
        for item in (response.json().get("result") or {}).get(
            "collections",
            [],
        )
    ]

    return {"collections": collections}


def check_ollama() -> dict[str, Any]:
    import requests

    base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434",
    ).rstrip("/")

    response = requests.get(f"{base_url}/api/tags", timeout=5)
    response.raise_for_status()

    models = [
        item.get("name") for item in response.json().get("models", [])
    ]

    return {"models": models}


def readiness() -> dict[str, Any]:
    """Probe every dependency and report an aggregate status."""
    dependencies = {
        "database": _probe("database", check_database),
        "redis": _probe("redis", check_redis),
        "qdrant": _probe("qdrant", check_qdrant),
        "ollama": _probe("ollama", check_ollama),
    }

    # Ollama is only needed to generate answers, not to serve the API.
    required = ("database", "redis", "qdrant")

    ready = all(
        dependencies[name]["status"] == "up" for name in required
    )

    return {
        "status": "ready" if ready else "degraded",
        "dependencies": dependencies,
    }


# Restore counters from the previous process and make sure the current
# ones are written even if the process exits without another request.
_load_persisted()

atexit.register(flush)
