"""Unit tests for app.core.text_splitter.LegalTextSplitter (pure logic, no I/O)."""

import pytest

from core.text_splitter import LegalTextSplitter


@pytest.fixture
def splitter():
    return LegalTextSplitter(chunk_size=200, chunk_overlap=50, min_chunk_size=20)


class TestBasicSplitting:
    def test_empty_text_returns_empty_list(self, splitter):
        assert splitter.split("") == []

    def test_whitespace_only_returns_empty_list(self, splitter):
        assert splitter.split("   \n\t  ") == []

    def test_short_text_single_chunk(self, splitter):
        text = "Đây là một đoạn văn bản ngắn về pháp luật Việt Nam."

        chunks = splitter.split(text)

        assert len(chunks) == 1
        assert chunks[0] == text.strip()

    def test_returns_list_of_strings(self, splitter):
        text = "Câu thứ nhất. Câu thứ hai. Câu thứ ba."

        chunks = splitter.split(text)

        assert all(isinstance(chunk, str) for chunk in chunks)
        assert len(chunks) >= 1


class TestArticleSplitting:
    def test_splits_at_dieu_boundaries(self, splitter):
        text = (
            "Điều 1. Quy định chung về đất đai.\n\n"
            "Điều 2. Nguyên tắc sử dụng đất.\n\n"
            "Điều 3. Nội dung quản lý nhà nước."
        )

        chunks = splitter.split(text)

        joined = "\n".join(chunks)
        assert "Điều 1" in joined
        assert "Điều 2" in joined
        assert "Điều 3" in joined

    def test_article_header_stays_with_its_content(self, splitter):
        text = "Nội dung mở đầu.\n\nĐiều 5. Thời hiệu khởi kiện vụ án hành chính."

        chunks = splitter.split(text)

        article_chunk = next(c for c in chunks if "Điều 5" in c)
        assert "Thời hiệu khởi kiện" in article_chunk

    def test_case_insensitive_article_pattern(self, splitter):
        text = "điều 10. Căn cứ áp dụng."

        chunks = splitter.split(text)

        assert any("điều 10" in c for c in chunks)


class TestChunkSize:
    def test_chunks_respect_chunk_size_plus_overlap(self, splitter):
        paragraph = ("Câu văn mẫu về pháp luật. " * 40).strip()
        text = f"{paragraph}\n\n{paragraph}"

        chunks = splitter.split(text)

        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= splitter.chunk_size + splitter.chunk_overlap

    def test_long_single_sentence_is_force_split(self, splitter):
        # One very long "sentence" without delimiters
        sentence = " ".join(["từ"] * 300)

        chunks = splitter.split(sentence)

        assert len(chunks) > 1
        # Overlap is appended on top of chunk_size, so allow chunk_size + chunk_overlap
        for chunk in chunks:
            assert len(chunk) <= splitter.chunk_size + splitter.chunk_overlap

    def test_no_content_lost(self, splitter):
        text = "Điều 1. Nội dung thứ nhất về hợp đồng.\n\nĐiều 2. Nội dung thứ hai về bồi thường."

        chunks = splitter.split(text)

        joined = " ".join(chunks)
        assert "Nội dung thứ nhất" in joined
        assert "Nội dung thứ hai" in joined


class TestOverlap:
    def test_consecutive_chunks_share_overlap(self):
        splitter = LegalTextSplitter(chunk_size=100, chunk_overlap=30)
        paragraph = ("Câu văn mẫu về pháp luật đất đai. " * 20).strip()

        chunks = splitter.split(f"{paragraph}\n\n{paragraph}")

        if len(chunks) > 1:
            # Replicate the implementation's overlap logic: strip up to the
            # first space of the tail only when the tail does not start with it
            tail = chunks[0][-30:]
            space_idx = tail.find(" ")
            expected_overlap = tail[space_idx + 1:] if space_idx > 0 else tail
            assert chunks[1].startswith(expected_overlap)

    def test_no_overlap_when_single_chunk(self, splitter):
        text = "Văn bản ngắn."

        assert splitter.split(text) == ["Văn bản ngắn."]

    def test_zero_overlap_disabled(self):
        splitter = LegalTextSplitter(chunk_size=100, chunk_overlap=0)
        paragraph = ("Câu văn mẫu về pháp luật. " * 20).strip()

        chunks = splitter.split(f"{paragraph}\n\n{paragraph}")

        # Without overlap, chunk i must not start with tail of chunk i-1
        for prev, curr in zip(chunks, chunks[1:]):
            assert not curr.startswith(prev[-1])
