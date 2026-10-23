"""
Offline evaluation harness for the MM-RAG pipeline.

Evaluates a labelled JSONL dataset end-to-end through the same
retrieval + generation path the API/UI use, reporting:

    * Retrieval   - Precision@k, Recall@k, MRR, Hit rate
    * Answer      - groundedness (answer <-> context overlap),
                    expected-keyword hit rate
    * Performance - retrieval / generation / total latency
    * Cost        - token usage (when the model reports it)
    * Reliability - error rate

Dataset format (one JSON object per line):

    {
      "question": "What is the notice period?",
      "expected_keywords": ["30 days"],
      "expected_sources": ["Client_Contracts_Policies_and_Incident_Records.pdf"],
      "k": 6
    }

``tenant_id`` (and optionally ``collection_name``) may be set per line or
supplied globally via ``--tenant-id`` / ``--collection``.

Usage:

    python -m evaluation.harness \
        --dataset evaluation/dataset.sample.jsonl \
        --tenant-id <uuid>

    # JSON report for CI
    python -m evaluation.harness --dataset data.jsonl \
        --tenant-id <uuid> --json-out report.json
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from src.generation import MultimodalRAGGenerator

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------

@dataclass
class EvalCase:
    question: str
    tenant_id: str | None = None
    expected_keywords: list[str] = field(default_factory=list)
    expected_sources: list[str] = field(default_factory=list)
    k: int = 6
    collection_name: str | None = None


def load_dataset(path: Path) -> list[EvalCase]:
    cases: list[EvalCase] = []

    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            raw = raw.strip()

            if not raw or raw.startswith("#"):
                continue

            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc

            cases.append(
                EvalCase(
                    question=str(payload["question"]),
                    tenant_id=payload.get("tenant_id"),
                    expected_keywords=list(
                        payload.get("expected_keywords") or []
                    ),
                    expected_sources=list(
                        payload.get("expected_sources") or []
                    ),
                    k=int(payload.get("k", 6)),
                    collection_name=payload.get("collection_name"),
                )
            )

    if not cases:
        raise ValueError(f"No evaluation cases found in {path}")

    return cases


# ---------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------

def _normalize(name: str) -> str:
    return Path(str(name)).name.strip().lower()


def precision_at_k(
    retrieved_sources: list[str],
    expected_sources: list[str],
) -> float:
    if not retrieved_sources:
        return 0.0

    expected = {_normalize(source) for source in expected_sources}

    if not expected:
        return 0.0

    hits = sum(
        1 for source in retrieved_sources if _normalize(source) in expected
    )

    return hits / len(retrieved_sources)


def recall_at_k(
    retrieved_sources: list[str],
    expected_sources: list[str],
) -> float:
    expected = {_normalize(source) for source in expected_sources}

    if not expected:
        return 0.0

    retrieved = {_normalize(source) for source in retrieved_sources}

    return len(expected & retrieved) / len(expected)


def reciprocal_rank(
    retrieved_sources: list[str],
    expected_sources: list[str],
) -> float:
    expected = {_normalize(source) for source in expected_sources}

    if not expected:
        return 0.0

    for rank, source in enumerate(retrieved_sources, start=1):
        if _normalize(source) in expected:
            return 1.0 / rank

    return 0.0


def keyword_hit_rate(answer: str, keywords: list[str]) -> float:
    if not keywords:
        return 0.0

    lowered = answer.lower()

    hits = sum(
        1 for keyword in keywords if str(keyword).lower() in lowered
    )

    return hits / len(keywords)


_WORD = str.maketrans({char: " " for char in ".,;:!?()[]{}\"'`\n\t"})


def groundedness(answer: str, context: str) -> float:
    """
    Fraction of answer content words that also appear in the retrieved
    context. A high value means the answer is grounded in evidence
    rather than hallucinated. Cheap, model-agnostic heuristic.
    """
    answer_words = {
        word
        for word in answer.lower().translate(_WORD).split()
        if len(word) > 2
    }

    if not answer_words:
        return 0.0

    context_words = set(context.lower().translate(_WORD).split())

    return len(answer_words & context_words) / len(answer_words)


# ---------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------

def evaluate_case(
    generator: MultimodalRAGGenerator,
    case: EvalCase,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "question": case.question,
        "tenant_id": tenant_id,
        "error": None,
    }

    started = time.perf_counter()

    try:
        result = generator.answer_question(
            query=case.question,
            tenant_id=tenant_id,
            k=case.k,
            include_context=True,
        )

        total_ms = (time.perf_counter() - started) * 1000.0

        sources = result.get("sources") or []
        retrieved_sources = [
            str(source.get("filename")) for source in sources
        ]

        answer = str(result.get("answer") or "")

        # Prefer the exact context the model saw; fall back to the
        # retrieved source citations when unavailable.
        context = result.get("context") or "\n".join(
            str(source.get("citation", "")) for source in sources
        )

        usage = result.get("usage") or {}

        # Retrieval metrics are only meaningful when the case declares
        # the sources that should have been found; otherwise leave them
        # unset so they don't drag the aggregate down to zero.
        has_expected = bool(case.expected_sources)

        row.update(
            {
                "retrieval_mode": result.get("retrieval_mode"),
                "retrieval_count": result.get("retrieval_count"),
                "retrieved_sources": retrieved_sources,
                "precision": (
                    precision_at_k(
                        retrieved_sources,
                        case.expected_sources,
                    )
                    if has_expected
                    else None
                ),
                "recall": (
                    recall_at_k(
                        retrieved_sources,
                        case.expected_sources,
                    )
                    if has_expected
                    else None
                ),
                "mrr": (
                    reciprocal_rank(
                        retrieved_sources,
                        case.expected_sources,
                    )
                    if has_expected
                    else None
                ),
                "hit": (
                    float(
                        recall_at_k(
                            retrieved_sources,
                            case.expected_sources,
                        )
                        > 0
                    )
                    if has_expected
                    else None
                ),
                "groundedness": groundedness(answer, context),
                "keyword_hit_rate": keyword_hit_rate(
                    answer,
                    case.expected_keywords,
                ),
                "latency_ms": total_ms,
                "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "answer": answer,
            }
        )

    except Exception as exc:  # noqa: BLE001
        row["latency_ms"] = (time.perf_counter() - started) * 1000.0
        row["error"] = f"{type(exc).__name__}: {exc}"
        row["precision"] = None
        row["recall"] = None
        row["mrr"] = None
        row["hit"] = None
        row["groundedness"] = 0.0
        row["keyword_hit_rate"] = 0.0

    return row


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"cases": 0}

    total = len(rows)

    def mean(key: str) -> float:
        values = [
            float(row[key])
            for row in rows
            if row.get(key) is not None
        ]
        return statistics.fmean(values) if values else 0.0

    errors = sum(1 for row in rows if row.get("error"))

    latencies = [
        float(row["latency_ms"]) for row in rows if row.get("latency_ms")
    ]

    sorted_latencies = sorted(latencies)

    def percentile(pct: float) -> float:
        if not sorted_latencies:
            return 0.0
        index = min(
            len(sorted_latencies) - 1,
            int(round((pct / 100.0) * (len(sorted_latencies) - 1))),
        )
        return sorted_latencies[index]

    token_values = [
        row["total_tokens"]
        for row in rows
        if row.get("total_tokens") is not None
    ]

    return {
        "cases": total,
        "errors": errors,
        "error_rate": errors / total,
        "precision_at_k": mean("precision"),
        "recall_at_k": mean("recall"),
        "mrr": mean("mrr"),
        "hit_rate": mean("hit"),
        "groundedness": mean("groundedness"),
        "keyword_hit_rate": mean("keyword_hit_rate"),
        "latency_ms_mean": statistics.fmean(latencies) if latencies else 0.0,
        "latency_ms_p50": percentile(50),
        "latency_ms_p95": percentile(95),
        "total_tokens_sum": sum(token_values) if token_values else None,
        "total_tokens_mean": (
            statistics.fmean(token_values) if token_values else None
        ),
    }


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the MM-RAG offline evaluation harness."
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Path to a JSONL evaluation dataset.",
    )
    parser.add_argument(
        "--tenant-id",
        default=os.getenv("EVAL_TENANT_ID"),
        help="Default tenant_id for cases that don't specify one.",
    )
    parser.add_argument(
        "--collection",
        default=os.getenv("QDRANT_COLLECTION_NAME"),
        help="Default Qdrant collection.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OLLAMA_CHAT_MODEL"),
        help="Chat model override.",
    )
    parser.add_argument(
        "--json-out",
        default=None,
        help="Write the full report (summary + per-case) as JSON.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only evaluate the first N cases.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    cases = load_dataset(Path(args.dataset))

    if args.limit is not None:
        cases = cases[: args.limit]

    default_tenant = args.tenant_id

    if not default_tenant and not all(case.tenant_id for case in cases):
        raise SystemExit(
            "tenant_id is required: pass --tenant-id or set it per case."
        )

    generator = MultimodalRAGGenerator(
        collection_name=args.collection,
        model_name=args.model,
    )

    rows: list[dict[str, Any]] = []

    for index, case in enumerate(cases, start=1):
        tenant_id = case.tenant_id or default_tenant
        print(f"[{index}/{len(cases)}] {case.question}")

        row = evaluate_case(generator, case, tenant_id=str(tenant_id))
        rows.append(row)

        if row.get("error"):
            print(f"    ERROR: {row['error']}")
        else:
            def _fmt(value: float | None) -> str:
                return "n/a" if value is None else f"{value:.2f}"

            print(
                f"    P={_fmt(row['precision'])} "
                f"R={_fmt(row['recall'])} "
                f"MRR={_fmt(row['mrr'])} "
                f"grounded={_fmt(row['groundedness'])} "
                f"{row['latency_ms']:.0f}ms"
            )

    summary = summarize(rows)

    print("\n==== SUMMARY ====")
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"{key:20s}: {value:.4f}")
        else:
            print(f"{key:20s}: {value}")

    if args.json_out:
        report = {
            "summary": summary,
            "cases": rows,
        }
        Path(args.json_out).write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )
        print(f"\nReport written to {args.json_out}")

    return 0 if summary.get("errors", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
