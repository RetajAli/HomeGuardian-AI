from __future__ import annotations

from pathlib import Path

import fitz
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 900
DEFAULT_CHUNK_OVERLAP = 150


class DocumentProcessingError(Exception):
    """Raised when an appliance manual cannot be processed."""


def extract_pdf_pages(pdf_path: str | Path) -> list[Document]:
    """Extract readable text from a PDF, one Document per page."""

    path = Path(pdf_path)

    if not path.exists():
        raise DocumentProcessingError(
            f"The manual file does not exist: {path}"
        )

    if not path.is_file():
        raise DocumentProcessingError(
            "The provided manual path is not a file."
        )

    if path.suffix.lower() != ".pdf":
        raise DocumentProcessingError(
            "Only PDF manuals are supported."
        )

    pages: list[Document] = []

    try:
        with fitz.open(path) as pdf_document:
            if pdf_document.page_count == 0:
                raise DocumentProcessingError(
                    "The PDF does not contain any pages."
                )

            for page_index, page in enumerate(pdf_document):
                text = page.get_text("text", sort=True).strip()

                if not text:
                    continue

                pages.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": path.name,
                            "file_path": str(path),
                            "page": page_index + 1,
                        },
                    )
                )

    except DocumentProcessingError:
        raise

    except Exception as error:
        raise DocumentProcessingError(
            f"The PDF could not be read: {error}"
        ) from error

    if not pages:
        raise DocumentProcessingError(
            "No readable text was found. The PDF may be scanned "
            "or image-based and may require OCR."
        )

    return pages


def split_documents(
    documents: list[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    """Split PDF pages into overlapping text chunks."""

    if not documents:
        raise DocumentProcessingError(
            "There are no extracted pages to split."
        )

    if chunk_size <= 0:
        raise ValueError(
            "Chunk size must be greater than zero."
        )

    if chunk_overlap < 0:
        raise ValueError(
            "Chunk overlap cannot be negative."
        )

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be smaller than chunk size."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise DocumentProcessingError(
            "The extracted text could not be divided into chunks."
        )

    for chunk_number, chunk in enumerate(chunks, start=1):
        chunk.metadata["chunk"] = chunk_number

    return chunks


def process_pdf_manual(
    pdf_path: str | Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    """Extract and split one appliance manual."""

    pages = extract_pdf_pages(pdf_path)

    return split_documents(
        documents=pages,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )