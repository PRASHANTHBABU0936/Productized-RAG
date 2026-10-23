"""Retrieval tests: tenant filtering, RRF fusion, and Cross-Encoder rerank.

These exercise the pure logic only - no Qdrant, no model downloads.
"""

import pytest
from langchain_core.documents import Document

from src.retriever import MultimodalQdrantRetriever


def _doc(text: str, **metadata) -> Document:
    return Document(page_content=text, metadata=metadata)


def _filler(index: int) -> Document:
    return _doc(
        f"chunk {index}",
        document_id="doc-1",
        page_number=index,
        content_type="text",
        chunk_id=f"c{index}",
    )


def _bare_retriever() -> MultimodalQdrantRetriever:
    """Instance without running __init__ (avoids loading models/clients)."""
    return object.__new__(MultimodalQdrantRetriever)


# ---------------------------------------------------------------------
# Tenant / metadata filtering
# ---------------------------------------------------------------------


def test_build_filter_requires_tenant_id():
    retriever = _bare_retriever()
    with pytest.raises(ValueError, match="tenant_id is required"):
        retriever.build_filter(tenant_id="")
    with pytest.raises(ValueError, match="tenant_id is required"):
        retriever.build_filter(tenant_id="   ")


def test_build_filter_always_scopes_to_tenant():
    retriever = _bare_retriever()
    flt = retriever.build_filter(
        tenant_id="tenant-a",
        document_id="doc-1",
        content_types=["table", "image"],
    )

    by_key = {condition.key: condition for condition in flt.must}
    assert "metadata.tenant_id" in by_key
    assert by_key["metadata.tenant_id"].match.value == "tenant-a"
    assert by_key["metadata.document_id"].match.value == "doc-1"
    # content_type is an "any of" condition.
    assert by_key["metadata.content_type"].match.any == ["table", "image"]


def test_build_filter_rejects_unknown_content_type():
    retriever = _bare_retriever()
    with pytest.raises(ValueError, match="Unsupported content_types"):
        retriever.build_filter(tenant_id="t", content_types=["video"])


def test_normalize_content_types():
    assert MultimodalQdrantRetriever._normalize_content_types(None) == []
    assert MultimodalQdrantRetriever._normalize_content_types(
        ["table", " image ", ""]
    ) == ["table", "image"]


# ---------------------------------------------------------------------
# Reciprocal Rank Fusion
# ---------------------------------------------------------------------


def test_rrf_promotes_documents_found_by_both_retrievers():
    both = _doc("shared", document_id="d1", page_number=1,
                content_type="text", chunk_id="c1")
    dense_only = _doc("dense", document_id="d1", page_number=2,
                      content_type="text", chunk_id="c2")
    sparse_only = _doc("sparse", document_id="d1", page_number=3,
                       content_type="text", chunk_id="c3")

    fused = MultimodalQdrantRetriever.reciprocal_rank_fusion(
        [(both, 0.9), (dense_only, 0.8)],
        [(both, 7.0), (sparse_only, 6.0)],
        k=60,
        top_k=10,
    )

    assert fused[0][0].page_content == "shared"
    assert {doc.page_content for doc, _ in fused} == {
        "shared",
        "dense",
        "sparse",
    }
    assert fused[0][1] > fused[1][1]


def test_rrf_score_matches_formula():
    doc = _doc("a", document_id="d1", page_number=1,
               content_type="text", chunk_id="c1")
    fused = MultimodalQdrantRetriever.reciprocal_rank_fusion(
        [(doc, 0.5)], [(doc, 9.9)], k=60, top_k=5
    )
    assert fused[0][1] == pytest.approx(2.0 / 61.0)


def test_rrf_top_k_and_validation():
    dense = [(_filler(i), 1.0) for i in range(10)]
    assert len(
        MultimodalQdrantRetriever.reciprocal_rank_fusion(
            dense, [], k=60, top_k=3
        )
    ) == 3

    with pytest.raises(ValueError):
        MultimodalQdrantRetriever.reciprocal_rank_fusion(dense, [], k=0)
    with pytest.raises(ValueError):
        MultimodalQdrantRetriever.reciprocal_rank_fusion(dense, [], top_k=0)


def test_rrf_empty_inputs():
    assert MultimodalQdrantRetriever.reciprocal_rank_fusion([], []) == []


# ---------------------------------------------------------------------
# Cross-Encoder reranking
# ---------------------------------------------------------------------


class _FakeReranker:
    """Deterministic stand-in for the Cross-Encoder."""

    def __init__(self, scores: dict[str, float]) -> None:
        self._scores = scores

    def predict(self, pairs, show_progress_bar=False):
        return [self._scores[text] for _, text in pairs]


def test_rerank_orders_by_cross_encoder_score():
    retriever = _bare_retriever()
    retriever.reranker = _FakeReranker({"low": 0.1, "high": 0.9, "mid": 0.5})

    ranked = retriever.rerank_documents(
        "query",
        [
            (_doc("low"), 0.9),
            (_doc("high"), 0.5),
            (_doc("mid"), 0.7),
        ],
        top_k=2,
    )

    assert [doc.page_content for doc, _ in ranked] == ["high", "mid"]
    assert ranked[0][1] == pytest.approx(0.9)


def test_rerank_empty_candidates_returns_empty():
    retriever = _bare_retriever()
    retriever.reranker = _FakeReranker({})
    assert retriever.rerank_documents("query", [], top_k=5) == []


def test_rerank_blank_query_raises():
    retriever = _bare_retriever()
    retriever.reranker = _FakeReranker({})
    with pytest.raises(Exception):
        retriever.rerank_documents("   ", [(_doc("a"), 1.0)], top_k=5)
