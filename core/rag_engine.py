from __future__ import annotations

import shutil
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings


BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_STORE_DIR = BASE_DIR / "data" / "vector_store"

EMBEDDING_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


class VectorStoreError(Exception):
    """Raised when a vector-store operation fails."""


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Load the local Hugging Face embedding model."""

    try:
        return HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={
                "device": "cpu",
            },
            encode_kwargs={
                "normalize_embeddings": True,
            },
        )

    except Exception as error:
        raise VectorStoreError(
            f"The embedding model could not be loaded: {error}"
        ) from error


def get_appliance_vector_path(
    appliance_id: int,
) -> Path:
    """Return the vector database folder for one appliance."""

    if appliance_id <= 0:
        raise ValueError(
            "Appliance ID must be greater than zero."
        )

    return VECTOR_STORE_DIR / f"appliance_{appliance_id}"


def vector_store_exists(appliance_id: int) -> bool:
    """Check whether an appliance vector database exists."""

    vector_path = get_appliance_vector_path(appliance_id)

    return (
        vector_path.exists()
        and (vector_path / "index.faiss").exists()
        and (vector_path / "index.pkl").exists()
    )


def create_vector_store(
    appliance_id: int,
    documents: list[Document],
) -> Path:
    """Create and save a FAISS index for one appliance."""

    if not documents:
        raise VectorStoreError(
            "No document chunks were provided."
        )

    vector_path = get_appliance_vector_path(appliance_id)

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        if vector_path.exists():
            shutil.rmtree(vector_path)

        embeddings = get_embedding_model()

        vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embeddings,
        )

        vector_store.save_local(
            str(vector_path)
        )

    except Exception as error:
        if vector_path.exists():
            shutil.rmtree(
                vector_path,
                ignore_errors=True,
            )

        raise VectorStoreError(
            f"The vector database could not be created: {error}"
        ) from error

    return vector_path


def load_vector_store(
    appliance_id: int,
) -> FAISS:
    """Load one appliance's saved FAISS index."""

    vector_path = get_appliance_vector_path(appliance_id)

    if not vector_store_exists(appliance_id):
        raise VectorStoreError(
            "This appliance does not have a processed manual."
        )

    try:
        embeddings = get_embedding_model()

        return FAISS.load_local(
            folder_path=str(vector_path),
            embeddings=embeddings,
            allow_dangerous_deserialization=True,
        )

    except Exception as error:
        raise VectorStoreError(
            f"The vector database could not be loaded: {error}"
        ) from error


def search_manual(
    appliance_id: int,
    question: str,
    number_of_results: int = 4,
) -> list[Document]:
    """Retrieve relevant chunks from one appliance manual."""

    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError(
            "Question cannot be empty."
        )

    if number_of_results <= 0:
        raise ValueError(
            "Number of results must be greater than zero."
        )

    vector_store = load_vector_store(appliance_id)

    return vector_store.similarity_search(
        query=cleaned_question,
        k=number_of_results,
    )