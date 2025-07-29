class CharacterTextSplitter:
    def __init__(self, separator: str = "\n\n", chunk_size: int=512, chunk_overlap: int=0):
        self.separator = separator
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        if not text:
            return []
        splits = text.split(self.separator)
        docs = []
        current_doc = ""
        for split in splits:
            if current_doc:
                potential = current_doc + self.separator + split
            else:
                potential = split
            if len(potential) > self.chunk_size:
                if current_doc:
                    docs.append(current_doc)
                if len(split) > self.chunk_size:
                    # If the split itself is too large, break it further
                    docs.extend(self._split_large_chunk(split))
                    current_doc = ""
                else:
                    current_doc = split
            else:
                current_doc = potential
        if current_doc:
            docs.append(current_doc)
        # Add overlap
        if self.chunk_overlap > 0 and len(docs) > 1:
            docs = self._add_overlap(docs)
        return docs

    def _split_large_chunk(self, chunk: str) -> list[str]:
        # Fallback: split by chunk_size, no separator
        return [chunk[i:i+self.chunk_size] for i in range(0, len(chunk), self.chunk_size)]

    def _add_overlap(self, docs: list[str]) -> list[str]:
        overlapped = []
        for i, doc in enumerate(docs):
            if i == 0:
                overlapped.append(doc)
            else:
                prev = overlapped[-1]
                overlap = prev[-self.chunk_overlap:] if len(prev) > self.chunk_overlap else prev
                overlapped.append(overlap + doc)
        return overlapped
