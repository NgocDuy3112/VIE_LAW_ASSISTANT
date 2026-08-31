import re


class LegalTextSplitter:
    """Split Vietnamese legal text into chunks suitable for embedding."""

    SENTENCE_DELIMITERS = re.compile(r"(?<=[.!?。])\s+")
    PARAGRAPH_DELIMITERS = re.compile(r"\n\s*\n")
    ARTICLE_PATTERN = re.compile(r"\n\s*(Điều\s+\d+)", re.IGNORECASE)

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100, min_chunk_size: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def split(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Step 1: split by articles (Điều X) if present
        articles = self._split_by_articles(text)

        # Step 2: split each article by paragraphs
        paragraphs = []
        for article in articles:
            paragraphs.extend(self._split_by_paragraphs(article))

        # Step 3: merge small paragraphs and split large ones
        chunks = self._merge_and_split(paragraphs)

        # Step 4: add overlap
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._add_overlap(chunks)

        return chunks

    def _split_by_articles(self, text: str) -> list[str]:
        """Split text at 'Điều X' boundaries."""
        parts = self.ARTICLE_PATTERN.split(text)
        if len(parts) <= 1:
            return [text]

        # parts alternates: [before, "Điều 1", rest1, "Điều 2", rest2, ...]
        articles = []
        i = 0
        while i < len(parts):
            if re.match(r"\s*Điều\s+\d+", parts[i], re.IGNORECASE):
                # merge "Điều X" with its content
                if i + 1 < len(parts):
                    articles.append(parts[i] + parts[i + 1])
                    i += 2
                else:
                    articles.append(parts[i])
                    i += 1
            else:
                if parts[i].strip():
                    articles.append(parts[i])
                i += 1
        return articles

    def _split_by_paragraphs(self, text: str) -> list[str]:
        """Split article text by double newlines."""
        paragraphs = self.PARAGRAPH_DELIMITERS.split(text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _merge_and_split(self, paragraphs: list[str]) -> list[str]:
        """Merge small paragraphs into chunks, split oversized ones by sentences."""
        chunks = []
        current = ""

        for para in paragraphs:
            # If single paragraph is already too large, split by sentences
            if len(para) > self.chunk_size:
                if current:
                    chunks.append(current)
                    current = ""
                chunks.extend(self._split_by_sentences(para))
                continue

            potential = (current + "\n\n" + para).strip() if current else para

            if len(potential) <= self.chunk_size:
                current = potential
            else:
                if current:
                    chunks.append(current)
                current = para

        if current:
            chunks.append(current)

        return chunks

    def _split_by_sentences(self, text: str) -> list[str]:
        """Split long text by sentence boundaries."""
        sentences = self.SENTENCE_DELIMITERS.split(text)
        chunks = []
        current = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # If single sentence exceeds chunk_size, force split by character
            if len(sentence) > self.chunk_size:
                if current:
                    chunks.append(current)
                    current = ""
                chunks.extend(self._force_split(sentence))
                continue

            potential = (current + " " + sentence).strip() if current else sentence

            if len(potential) <= self.chunk_size:
                current = potential
            else:
                if current:
                    chunks.append(current)
                current = sentence

        if current:
            chunks.append(current)

        return chunks

    def _force_split(self, text: str) -> list[str]:
        """Last resort: split by character limit at word boundaries."""
        words = text.split()
        chunks = []
        current = ""

        for word in words:
            potential = (current + " " + word).strip() if current else word
            if len(potential) > self.chunk_size:
                if current:
                    chunks.append(current)
                current = word
            else:
                current = potential

        if current:
            chunks.append(current)

        return chunks

    def _add_overlap(self, chunks: list[str]) -> list[str]:
        """Add overlap between consecutive chunks."""
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = chunks[i - 1]
            overlap_text = prev[-self.chunk_overlap:]
            # Avoid splitting mid-word
            space_idx = overlap_text.find(" ")
            if space_idx > 0:
                overlap_text = overlap_text[space_idx + 1:]
            overlapped.append(overlap_text + " " + chunks[i])
        return overlapped
