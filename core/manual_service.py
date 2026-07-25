from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from core.database import (
    update_manual_processing_status,
)
from core.document_processor import (
    DocumentProcessingError,
    process_pdf_manual,
)
from core.rag_engine import (
    VectorStoreError,
    create_vector_store,
    get_appliance_vector_path,
)


BASE_DIR = Path(__file__).resolve().parent.parent
MANUALS_DIR = BASE_DIR / "data" / "manuals"


class ManualServiceError(Exception):
    """Raised when a manual operation cannot be completed."""


def save_uploaded_manual(
    uploaded_file,
) -> tuple[str, str]:
    """Save an uploaded PDF and return its original name and path."""

    if uploaded_file is None:
        raise ManualServiceError(
            "No manual was provided."
        )

    original_filename = Path(
        uploaded_file.name
    ).name

    if Path(original_filename).suffix.lower() != ".pdf":
        raise ManualServiceError(
            "Only PDF manuals are supported."
        )

    MANUALS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    unique_filename = (
        f"{uuid.uuid4().hex}.pdf"
    )

    saved_path = (
        MANUALS_DIR / unique_filename
    )

    try:
        with saved_path.open("wb") as file:
            file.write(
                uploaded_file.getbuffer()
            )

    except OSError as error:
        raise ManualServiceError(
            f"The manual could not be saved: {error}"
        ) from error

    return (
        original_filename,
        str(saved_path),
    )


def prepare_manual_for_ai(
    appliance_id: int,
    manual_path: str,
) -> int:
    """
    Extract the manual, create embeddings, and save its FAISS index.

    Returns the number of generated chunks.
    """

    try:
        chunks = process_pdf_manual(
            manual_path
        )

        create_vector_store(
            appliance_id=appliance_id,
            documents=chunks,
        )

        update_manual_processing_status(
            appliance_id=appliance_id,
            processed=True,
            chunk_count=len(chunks),
        )

        return len(chunks)

    except (
        DocumentProcessingError,
        VectorStoreError,
    ) as error:
        update_manual_processing_status(
            appliance_id=appliance_id,
            processed=False,
            chunk_count=0,
        )

        raise ManualServiceError(
            str(error)
        ) from error

    except Exception as error:
        update_manual_processing_status(
            appliance_id=appliance_id,
            processed=False,
            chunk_count=0,
        )

        raise ManualServiceError(
            f"The manual could not be prepared: {error}"
        ) from error


def delete_manual_file(
    manual_path: str | None,
) -> None:
    """Delete a saved manual file safely."""

    if not manual_path:
        return

    path = Path(manual_path)

    if path.exists() and path.is_file():
        try:
            path.unlink()

        except OSError:
            pass


def delete_vector_store(
    appliance_id: int,
) -> None:
    """Delete one appliance's FAISS data safely."""

    try:
        vector_path = (
            get_appliance_vector_path(
                appliance_id
            )
        )

        if vector_path.exists():
            shutil.rmtree(
                vector_path,
                ignore_errors=True,
            )

    except Exception:
        pass


def delete_appliance_files(
    appliance: dict,
) -> None:
    """Delete an appliance's manual and AI search data."""

    delete_manual_file(
        appliance.get("manual_path")
    )

    delete_vector_store(
        int(appliance["id"])
    )