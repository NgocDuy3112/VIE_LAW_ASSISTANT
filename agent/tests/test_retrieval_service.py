"""Unit tests for modules.documents.services.retrieval_service.RetrievalService.

Document repository, cache repository and embedding service are mocked.
"""

from unittest.mock import AsyncMock

import numpy as np
import pytest

from modules.documents.schemas.retrieve import RetrieveRequest
from modules.documents.services.retrieval_service import RetrievalService

QUERY_VECTOR = np.array([0.1] * 8, dtype=np.float32)


def es_hit(hit_id: str, content: str) -> dict:
    return {"_id": hit_id, "_source": {"id": hit_id, "content": content, "source": f"{hit_id}.pdf"}}


@pytest.fixture
def document_repo():
    return AsyncMock()


@pytest.fixture
def cache_repo():
    repo = AsyncMock()
    repo.search.return_value = []  # cache miss by default
    return repo


@pytest.fixture
def embedding_service():
    service = AsyncMock()
    service.embed.return_value = QUERY_VECTOR
    return service


@pytest.fixture
def service(document_repo, cache_repo, embedding_service):
    return RetrievalService(
        document_repo=document_repo,
        cache_repo=cache_repo,
        embedding_service=embedding_service,
    )


class TestRetrieve:
    async def test_cache_hit_skips_search(self, service, cache_repo, document_repo, embedding_service):
        cache_repo.search.return_value = [
            {"payload": {"id": "doc-1", "content": "Luật đất đai", "source": "land.pdf"}},
        ]

        response = await service.retrieve(RetrieveRequest(query="đất đai", top_k=3))

        assert response.status == "success"
        assert len(response.results) == 1
        assert response.results[0].id == "doc-1"
        embedding_service.embed.assert_awaited_once_with("đất đai")
        document_repo.search_lexical.assert_not_awaited()
        document_repo.search_semantic.assert_not_awaited()

    async def test_cache_miss_fuses_lexical_and_semantic(self, service, document_repo, cache_repo):
        document_repo.search_lexical.return_value = [es_hit("a", "Điều 1"), es_hit("b", "Điều 2")]
        document_repo.search_semantic.return_value = [es_hit("b", "Điều 2"), es_hit("c", "Điều 3")]

        response = await service.retrieve(RetrieveRequest(query="điều 1", top_k=2))

        assert response.status == "success"
        # "b" appears in both result lists → highest RRF score, top_k=2 limits output
        assert [doc.id for doc in response.results] == ["b", "a"]
        assert len(response.results) == 2

    async def test_results_are_cached(self, service, document_repo, cache_repo):
        document_repo.search_lexical.return_value = [es_hit("a", "Nội dung")]
        document_repo.search_semantic.return_value = []

        await service.retrieve(RetrieveRequest(query="truy vấn", top_k=5))

        cache_repo.set.assert_awaited_once()
        args = cache_repo.set.await_args.args
        assert args[0] == "Nội dung"
        np.testing.assert_array_equal(args[1], QUERY_VECTOR)

    async def test_embedding_failure_returns_error_response(self, service, embedding_service):
        embedding_service.embed.side_effect = RuntimeError("embedding server down")

        response = await service.retrieve(RetrieveRequest(query="anything"))

        assert response.status == "error"
        assert response.results == []
        assert "embedding server down" in response.detail

    async def test_search_failure_returns_error_response(self, service, document_repo):
        document_repo.search_lexical.side_effect = RuntimeError("elasticsearch down")

        response = await service.retrieve(RetrieveRequest(query="anything"))

        assert response.status == "error"
        assert "elasticsearch down" in response.detail

    async def test_top_k_limits_results(self, service, document_repo):
        document_repo.search_lexical.return_value = [es_hit(f"d{i}", f"content {i}") for i in range(10)]
        document_repo.search_semantic.return_value = []

        response = await service.retrieve(RetrieveRequest(query="q", top_k=3))

        assert len(response.results) == 3

    async def test_filter_is_merged_with_keyword_filter(self, service, document_repo):
        document_repo.search_lexical.return_value = []
        document_repo.search_semantic.return_value = []
        user_filter = {"term": {"source": "bo-luat-dan-su"}}

        await service.retrieve(RetrieveRequest(query="hợp đồng", top_k=5, filter=user_filter))

        sent_filter = document_repo.search_lexical.await_args.kwargs["filters"]
        # user filter and keyword filter are combined under bool.must
        assert sent_filter["bool"]["must"][0] == user_filter
        assert "should" in sent_filter["bool"]["must"][1]["bool"]

    async def test_no_keywords_and_no_filter_passes_none(self, service, document_repo):
        document_repo.search_lexical.return_value = []
        document_repo.search_semantic.return_value = []

        await service.retrieve(RetrieveRequest(query="???", top_k=5))

        assert document_repo.search_lexical.await_args.kwargs["filters"] is None
