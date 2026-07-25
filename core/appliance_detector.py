from __future__ import annotations

import re
from pathlib import Path

import fitz


KNOWN_BRANDS = [
    "Carrier",
    "Samsung",
    "LG",
    "Bosch",
    "Whirlpool",
    "Electrolux",
    "Haier",
    "Toshiba",
    "Sharp",
    "Panasonic",
    "Philips",
    "Midea",
    "Daikin",
    "Hitachi",
    "Beko",
    "Ariston",
    "Hoover",
    "Zanussi",
    "Fresh",
    "Unionaire",
    "Hisense",
    "Sony",
    "Siemens",
    "Indesit",
    "General Electric",
    "GE",
]


MODEL_BRAND_HINTS = {
    "42HVM": "Carrier",
    "38HVM": "Carrier",
    "MS11M": "Carrier",
    "MOC-": "Carrier",
    "MOF-": "Carrier",
    "MOG-": "Carrier",
}


MODEL_PATTERNS = [
    r"(?:model|model\s+no\.?|model\s+number)\s*[:#-]?\s*"
    r"([A-Z0-9][A-Z0-9._/-]{4,30})",

    r"\b([A-Z]{1,5}[0-9]{2,}[A-Z0-9._/-]{2,})\b",

    r"\b([0-9]{2}[A-Z]{2,}[0-9]{4,}[A-Z0-9._/-]*)\b",
]


class ApplianceDetectionError(Exception):
    """Raised when the uploaded manual cannot be inspected."""


def extract_preview_text(
    pdf_bytes: bytes,
    max_pages: int = 6,
) -> str:
    """Extract text from the first pages of an uploaded PDF."""

    if not pdf_bytes:
        raise ApplianceDetectionError(
            "The uploaded manual is empty."
        )

    extracted_pages: list[str] = []

    try:
        with fitz.open(
            stream=pdf_bytes,
            filetype="pdf",
        ) as document:
            page_limit = min(
                document.page_count,
                max_pages,
            )

            for page_number in range(page_limit):
                page = document.load_page(page_number)

                text = page.get_text(
                    "text",
                    sort=True,
                ).strip()

                if text:
                    extracted_pages.append(text)

    except Exception as error:
        raise ApplianceDetectionError(
            f"The manual could not be inspected: {error}"
        ) from error

    return "\n".join(extracted_pages)


def detect_brand(
    text: str,
    filename: str,
) -> str | None:
    """Try to find the appliance brand."""

    searchable_text = (
        f"{filename}\n{text}"
    ).lower()

    for brand in KNOWN_BRANDS:
        if brand.lower() in searchable_text:
            return brand

    uppercase_text = text.upper()

    for model_prefix, brand in MODEL_BRAND_HINTS.items():
        if model_prefix.upper() in uppercase_text:
            return brand

    return None


def clean_model_candidate(
    candidate: str,
) -> str | None:
    """Clean and validate a possible model number."""

    cleaned = candidate.strip(
        ".,:;()[]{}"
    )

    blocked_words = {
        "CONDITIONER",
        "INVERTER",
        "SERVICE",
        "MANUAL",
        "WARNING",
        "INSTALLATION",
        "TEMPERATURE",
        "OPERATION",
    }

    if cleaned.upper() in blocked_words:
        return None

    if len(cleaned) < 5:
        return None

    if not any(character.isdigit() for character in cleaned):
        return None

    if not any(character.isalpha() for character in cleaned):
        return None

    return cleaned


def detect_model(
    text: str,
    filename: str,
) -> str | None:
    """Try to find a model number from the manual."""

    searchable_text = (
        f"{Path(filename).stem}\n{text}"
    ).upper()

    for pattern in MODEL_PATTERNS:
        matches = re.findall(
            pattern,
            searchable_text,
            flags=re.IGNORECASE,
        )

        for match in matches:
            candidate = (
                match[0]
                if isinstance(match, tuple)
                else match
            )

            cleaned = clean_model_candidate(
                candidate
            )

            if cleaned:
                return cleaned

    return None


def detect_appliance_information(
    pdf_bytes: bytes,
    filename: str,
) -> dict:
    """
    Detect brand and model from an uploaded appliance manual.

    Detection is best-effort. A missing value is returned as None.
    """

    text = extract_preview_text(pdf_bytes)

    brand = detect_brand(
        text=text,
        filename=filename,
    )

    model = detect_model(
        text=text,
        filename=filename,
    )

    return {
        "brand": brand,
        "model_number": model,
    }