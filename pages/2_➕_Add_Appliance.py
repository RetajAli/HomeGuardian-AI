from __future__ import annotations

import hashlib
import re
import shutil
import uuid
from html import escape
from pathlib import Path

import fitz
import streamlit as st

from core.database import (
    add_appliance,
    delete_appliance,
    get_all_appliances,
    initialize_database,
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
from core.ui import (
    apply_app_style,
    render_hero,
    render_status_pill,
)


st.set_page_config(
    page_title="Add Appliance | HomeGuardian AI",
    page_icon="➕",
    layout="wide",
)

apply_app_style()


BASE_DIR = Path(__file__).resolve().parent.parent
MANUALS_DIR = BASE_DIR / "data" / "manuals"


CATEGORIES = [
    "Air Conditioner",
    "Refrigerator",
    "Washing Machine",
    "Dishwasher",
    "Microwave",
    "Oven",
    "Television",
    "Water Heater",
    "Fan",
    "Vacuum Cleaner",
    "Other",
]


CATEGORY_ICONS = {
    "Air Conditioner": "❄️",
    "Refrigerator": "🧊",
    "Washing Machine": "🧺",
    "Dishwasher": "🍽️",
    "Microwave": "📡",
    "Oven": "🔥",
    "Television": "📺",
    "Water Heater": "🚿",
    "Fan": "🌀",
    "Vacuum Cleaner": "🧹",
    "Other": "🔌",
}


CATEGORY_PATTERNS = {
    "Air Conditioner": [
        (r"\bair\s*conditioner\b", 15),
        (r"\bair\s*conditioning\b", 14),
        (r"\bsplit[-\s]?type\b", 8),
        (r"\bindoor\s+unit\b", 4),
        (r"\boutdoor\s+unit\b", 4),
        (r"\bcooling\s+mode\b", 3),
        (r"\brefrigerant\b", 2),
    ],
    "Refrigerator": [
        (r"\brefrigerator\b", 15),
        (r"\bfridge\b", 12),
        (r"\bfreezer\b", 7),
        (r"\bice\s*maker\b", 4),
        (r"\bfresh\s*food\s*compartment\b", 4),
    ],
    "Washing Machine": [
        (r"\bwashing\s+machine\b", 15),
        (r"\bclothes\s+washer\b", 13),
        (r"\bwasher\b", 7),
        (r"\bspin\s+cycle\b", 5),
        (r"\bdrum\s+clean\b", 4),
    ],
    "Dishwasher": [
        (r"\bdishwasher\b", 15),
        (r"\bdishwashing\s+machine\b", 12),
        (r"\brinse\s+aid\b", 5),
        (r"\bdish\s+rack\b", 4),
    ],
    "Microwave": [
        (r"\bmicrowave\s+oven\b", 15),
        (r"\bmicrowave\b", 10),
        (r"\bturntable\b", 4),
    ],
    "Oven": [
        (r"\belectric\s+oven\b", 15),
        (r"\bgas\s+oven\b", 15),
        (r"\bconvection\s+oven\b", 13),
        (r"\bwall\s+oven\b", 12),
        (r"\boven\b", 6),
    ],
    "Television": [
        (r"\btelevision\b", 15),
        (r"\bsmart\s+tv\b", 13),
        (r"\bled\s+tv\b", 10),
        (r"\blcd\s+tv\b", 10),
    ],
    "Water Heater": [
        (r"\bwater\s+heater\b", 15),
        (r"\btankless\s+heater\b", 13),
        (r"\belectric\s+geyser\b", 12),
        (r"\bhot\s+water\s+system\b", 8),
    ],
    "Fan": [
        (r"\bceiling\s+fan\b", 15),
        (r"\bpedestal\s+fan\b", 13),
        (r"\bstand\s+fan\b", 12),
        (r"\btable\s+fan\b", 12),
        (r"\belectric\s+fan\b", 9),
    ],
    "Vacuum Cleaner": [
        (r"\bvacuum\s+cleaner\b", 15),
        (r"\brobot\s+vacuum\b", 13),
        (r"\bcordless\s+vacuum\b", 12),
        (r"\bsuction\s+power\b", 4),
    ],
}


KNOWN_BRANDS = [
    "A.O. Smith",
    "Ariston",
    "Beko",
    "Bosch",
    "Carrier",
    "Daikin",
    "Dyson",
    "Electrolux",
    "Frigidaire",
    "GE Appliances",
    "Haier",
    "Hisense",
    "Hitachi",
    "Hoover",
    "Hotpoint",
    "Indesit",
    "Kenmore",
    "LG",
    "Midea",
    "Miele",
    "Panasonic",
    "Philips",
    "Rheem",
    "Samsung",
    "Sharp",
    "Siemens",
    "TCL",
    "Toshiba",
    "Whirlpool",
    "Zanussi",
]


MODEL_PREFIX_BRANDS = {
    "42": "Carrier",
    "38": "Carrier",
    "MS": "Midea",
    "AR": "Samsung",
    "RT": "Samsung",
    "RF": "Samsung",
    "WW": "Samsung",
    "WD": "Samsung",
    "F4": "LG",
    "GC": "LG",
    "GR": "LG",
}


MODEL_STOP_WORDS = {
    "INSTALLATION",
    "INSTRUCTIONS",
    "INSTRUCTION",
    "MANUAL",
    "OPERATION",
    "SERVICE",
    "TROUBLESHOOTING",
    "WARNING",
    "WARRANTY",
}


st.markdown(
    """
    <style>
    .hg-auto-intro {
        padding: 1.25rem 1.35rem;
        margin-bottom: 1.25rem;
        background: var(--hg-surface-soft);
        border: 1px solid var(--hg-border);
        border-radius: 18px;
    }

    .hg-auto-title {
        color: var(--hg-text);
        font-size: 1.05rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .hg-auto-text {
        color: var(--hg-muted);
        margin: 0;
    }

    .hg-result-card {
        margin: 1rem 0;
        padding: 1.35rem;
        background: linear-gradient(
            135deg,
            rgba(22, 140, 255, 0.13),
            rgba(0, 199, 217, 0.06)
        );
        border: 1px solid rgba(36, 181, 240, 0.28);
        border-radius: 20px;
    }

    .hg-result-header {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        margin-bottom: 1.1rem;
    }

    .hg-result-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 58px;
        height: 58px;
        flex: 0 0 auto;
        background: var(--hg-accent-soft);
        border: 1px solid var(--hg-border);
        border-radius: 17px;
        font-size: 1.8rem;
    }

    .hg-result-ready {
        color: var(--hg-success);
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.07em;
        text-transform: uppercase;
    }

    .hg-result-name {
        margin-top: 0.15rem;
        color: var(--hg-text);
        font-size: 1.4rem;
        font-weight: 850;
        letter-spacing: -0.03em;
    }

    .hg-result-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.75rem;
    }

    .hg-result-item {
        padding: 0.9rem;
        background: var(--hg-surface-soft);
        border: 1px solid var(--hg-border);
        border-radius: 14px;
    }

    .hg-result-label {
        color: var(--hg-muted);
        font-size: 0.72rem;
        font-weight: 750;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 0.22rem;
    }

    .hg-result-value {
        color: var(--hg-text);
        font-weight: 750;
        overflow-wrap: anywhere;
    }

    .hg-saved-card {
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        background: var(--hg-surface-soft);
        border: 1px solid var(--hg-border);
        border-radius: 18px;
    }

    .hg-saved-title {
        color: var(--hg-text);
        font-size: 1.08rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }

    .hg-saved-meta {
        color: var(--hg-muted);
        font-size: 0.88rem;
    }

    .hg-saved-badge {
        display: block;
        width: fit-content;
        margin-top: 0.8rem;
        margin-bottom: 1.1rem;
    }

    .hg-saved-actions-space {
        height: 0.35rem;
    }

    @media (max-width: 700px) {
        .hg-result-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def clean_value(value: object) -> str:
    """Return a clean one-line value."""

    return re.sub(r"\s+", " ", str(value or "")).strip()


def file_fingerprint(uploaded_file) -> str:
    """Return a stable key for an uploaded PDF."""

    return hashlib.sha256(
        uploaded_file.getvalue()
    ).hexdigest()[:16]


def extract_manual_text(pdf_bytes: bytes) -> tuple[str, dict[str, str]]:
    """Read the first manual pages used for automatic detection."""

    pages: list[str] = []
    metadata: dict[str, str] = {}

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
            raw_metadata = document.metadata or {}
            metadata = {
                key: clean_value(value)
                for key, value in raw_metadata.items()
                if value
            }

            page_limit = min(document.page_count, 15)

            for page_index in range(page_limit):
                text = document[page_index].get_text(
                    "text",
                    sort=True,
                ).strip()

                if text:
                    pages.append(text)

    except Exception as error:
        raise ValueError(
            "HomeGuardian could not read this PDF. Please upload the official readable manual."
        ) from error

    full_text = "\n".join(pages).strip()

    if not full_text:
        raise ValueError(
            "No readable text was found in this manual. It may be a scanned image PDF."
        )

    return full_text, metadata


def detect_category(text: str) -> tuple[str, int]:
    """Detect appliance type from the manual text."""

    normalized = text.lower()
    scores: dict[str, int] = {}

    for category, patterns in CATEGORY_PATTERNS.items():
        score = 0

        for pattern, weight in patterns:
            matches = re.findall(pattern, normalized, flags=re.IGNORECASE)
            score += min(len(matches), 6) * weight

        scores[category] = score

    category = max(scores, key=scores.get)
    score = scores[category]

    if score < 7:
        return "Other", 0

    return category, min(99, 58 + score * 2)


def is_model_candidate(value: str) -> bool:
    """Return whether text looks like a model number."""

    candidate = value.strip(" .,:;()[]{}")
    upper = candidate.upper()

    if not 5 <= len(candidate) <= 38:
        return False

    if upper in MODEL_STOP_WORDS:
        return False

    if not re.search(r"[A-Z]", upper):
        return False

    if not re.search(r"\d", candidate):
        return False

    if re.fullmatch(r"(?:19|20)\d{2}", candidate):
        return False

    if re.fullmatch(
        r"\d+(?:\.\d+)?(?:V|W|HZ|A|KW|KG|MM|CM)",
        upper,
    ):
        return False

    return True


def detect_model(text: str) -> tuple[str, int]:
    """Detect the most likely appliance model number."""

    search_text = text[:70000]
    candidates: dict[str, int] = {}

    explicit_patterns = [
        r"(?im)\bmodel(?:\s+name|\s+number|\s+no\.?|\s+code)?\s*[:#-]?\s*([A-Z0-9][A-Z0-9._/-]{4,37})",
        r"(?im)\bmodels?\s*[:#-]\s*([A-Z0-9][A-Z0-9._/-]{4,37})",
        r"(?im)\bmodel\s*\n\s*([A-Z0-9][A-Z0-9._/-]{4,37})",
        r"(?im)\bindoor\s+unit(?:\s+model)?\s*[:#-]?\s*([A-Z0-9][A-Z0-9._/-]{4,37})",
    ]

    for pattern_index, pattern in enumerate(explicit_patterns):
        for match in re.finditer(pattern, search_text):
            candidate = match.group(1).strip(" .,:;()[]{}")

            if is_model_candidate(candidate):
                score = 115 - pattern_index * 10
                score += max(0, 18 - match.start() // 1800)
                candidates[candidate] = max(
                    candidates.get(candidate, 0),
                    score,
                )

    generic_pattern = re.compile(
        r"\b(?:[A-Z]{1,8}\d[A-Z0-9]*[-_/][A-Z0-9._/-]{3,30}|[A-Z]{1,6}\d[A-Z0-9]{4,30})\b"
    )

    for match in generic_pattern.finditer(search_text.upper()):
        candidate = match.group(0).strip(" .,:;()[]{}")

        if not is_model_candidate(candidate):
            continue

        nearby = search_text[
            max(0, match.start() - 100):
            min(len(search_text), match.end() + 100)
        ].lower()

        score = 28

        if "model" in nearby:
            score += 55
        if "indoor unit" in nearby:
            score += 18
        if "outdoor unit" in nearby:
            score += 10
        if "serial" in nearby:
            score -= 25
        if "error code" in nearby:
            score -= 25

        score += max(0, 16 - match.start() // 3000)
        candidates[candidate] = max(candidates.get(candidate, 0), score)

    if not candidates:
        return "", 0

    model, score = max(
        candidates.items(),
        key=lambda item: (item[1], len(item[0])),
    )

    return model, min(99, max(55, score))


def detect_brand(
    filename: str,
    metadata: dict[str, str],
    text: str,
    model: str,
) -> tuple[str, int]:
    """Detect brand from trusted parts of the manual."""

    first_lines = [
        clean_value(line)
        for line in text.splitlines()
        if clean_value(line)
    ][:160]

    trusted_text = "\n".join(
        [Path(filename).stem, " ".join(metadata.values()), *first_lines]
    )

    normalized = trusted_text.lower()
    best_brand = ""
    best_score = 0

    for brand in KNOWN_BRANDS:
        pattern = re.compile(
            rf"(?<![a-z0-9]){re.escape(brand.lower())}(?![a-z0-9])"
        )
        matches = list(pattern.finditer(normalized))

        if not matches:
            continue

        first_position = matches[0].start()
        score = 55 + min(len(matches), 4) * 8
        score += max(0, 25 - first_position // 250)

        if score > best_score:
            best_brand = brand
            best_score = score

    if not best_brand and model:
        upper_model = model.upper()

        for prefix, brand in MODEL_PREFIX_BRANDS.items():
            if upper_model.startswith(prefix):
                return brand, 65

    return best_brand, min(99, best_score)


def make_appliance_name(brand: str, category: str, model: str) -> str:
    """Create the appliance name automatically."""

    brand = clean_value(brand)
    category = clean_value(category)
    model = clean_value(model)

    if brand and category != "Other":
        return f"{brand} {category}"

    if category != "Other" and model:
        return f"{category} {model}"

    if category != "Other":
        return category

    if brand and model:
        return f"{brand} {model}"

    return model or "Appliance"


@st.cache_data(show_spinner=False)
def inspect_manual(
    pdf_bytes: bytes,
    filename: str,
) -> dict[str, object]:
    """Detect all appliance information from one PDF."""

    text, metadata = extract_manual_text(pdf_bytes)
    category, category_confidence = detect_category(text)
    model, model_confidence = detect_model(text)
    brand, brand_confidence = detect_brand(
        filename=filename,
        metadata=metadata,
        text=text,
        model=model,
    )

    return {
        "category": category,
        "brand": brand,
        "model": model,
        "name": make_appliance_name(brand, category, model),
        "category_confidence": category_confidence,
        "brand_confidence": brand_confidence,
        "model_confidence": model_confidence,
    }


def save_manual(uploaded_file) -> tuple[str, str]:
    """Save a PDF using a safe unique filename."""

    MANUALS_DIR.mkdir(parents=True, exist_ok=True)

    original_name = Path(uploaded_file.name).name
    saved_path = MANUALS_DIR / f"{uuid.uuid4().hex}.pdf"

    with saved_path.open("wb") as file:
        file.write(uploaded_file.getbuffer())

    return original_name, str(saved_path)


def prepare_manual(appliance_id: int, manual_path: str) -> tuple[bool, str]:
    """Prepare the uploaded manual for the AI assistant."""

    try:
        chunks = process_pdf_manual(manual_path)
        create_vector_store(
            appliance_id=appliance_id,
            documents=chunks,
        )
        update_manual_processing_status(
            appliance_id=appliance_id,
            processed=True,
            chunk_count=len(chunks),
        )
        return True, "Manual ready for AI help."

    except (DocumentProcessingError, VectorStoreError) as error:
        update_manual_processing_status(
            appliance_id=appliance_id,
            processed=False,
            chunk_count=0,
        )
        return False, str(error)

    except Exception as error:
        update_manual_processing_status(
            appliance_id=appliance_id,
            processed=False,
            chunk_count=0,
        )
        return False, str(error)


def delete_appliance_files(appliance: dict) -> None:
    """Delete the appliance manual and vector data."""

    manual_path = appliance.get("manual_path")

    if manual_path:
        path = Path(str(manual_path))
        if path.exists() and path.is_file():
            try:
                path.unlink()
            except OSError:
                pass

    try:
        vector_path = get_appliance_vector_path(int(appliance["id"]))
        if vector_path.exists():
            shutil.rmtree(vector_path, ignore_errors=True)
    except Exception:
        pass


def render_detected_card(
    name: str,
    category: str,
    brand: str,
    model: str,
) -> None:
    """Show the information detected automatically."""

    icon = CATEGORY_ICONS.get(category, "🔌")

    card_html = (
        '<section class="hg-result-card">'
        '<div class="hg-result-header">'
        f'<div class="hg-result-icon">{icon}</div>'
        '<div>'
        '<div class="hg-result-ready">Ready to add</div>'
        f'<div class="hg-result-name">{escape(name)}</div>'
        '</div>'
        '</div>'
        '<div class="hg-result-grid">'
        '<div class="hg-result-item">'
        '<div class="hg-result-label">Type</div>'
        f'<div class="hg-result-value">{escape(category)}</div>'
        '</div>'
        '<div class="hg-result-item">'
        '<div class="hg-result-label">Brand</div>'
        f'<div class="hg-result-value">{escape(brand or "Not found")}</div>'
        '</div>'
        '<div class="hg-result-item">'
        '<div class="hg-result-label">Model</div>'
        f'<div class="hg-result-value">{escape(model or "Not found")}</div>'
        '</div>'
        '</div>'
        '</section>'
    )

    st.markdown(card_html, unsafe_allow_html=True)


def add_detected_appliance(
    uploaded_file,
    category: str,
    brand: str,
    model: str,
) -> None:
    """Save the automatically identified appliance."""

    appliance_id: int | None = None
    manual_path: str | None = None

    name = make_appliance_name(brand, category, model)

    try:
        original_name, manual_path = save_manual(uploaded_file)

        appliance_id = add_appliance(
            appliance_name=name,
            category=category,
            brand=brand or "Unknown",
            model_number=model,
            manual_filename=original_name,
            manual_path=manual_path,
        )

        with st.status(
            "Adding the appliance and preparing its manual...",
            expanded=True,
        ) as status:
            ready, message = prepare_manual(
                appliance_id=appliance_id,
                manual_path=manual_path,
            )

            if ready:
                status.update(
                    label="Appliance added and ready.",
                    state="complete",
                    expanded=False,
                )
            else:
                status.update(
                    label="Appliance added, but the manual needs attention.",
                    state="error",
                    expanded=True,
                )
                st.warning(message)

        st.session_state["preferred_appliance_id"] = appliance_id
        st.session_state["appliance_added_message"] = (
            f"{name} was added successfully."
        )
        st.session_state["manual_upload_version"] = (
            st.session_state.get("manual_upload_version", 0) + 1
        )
        st.rerun()

    except Exception:
        if appliance_id is not None:
            try:
                delete_appliance(appliance_id)
            except Exception:
                pass

        if manual_path:
            path = Path(manual_path)
            if path.exists():
                try:
                    path.unlink()
                except OSError:
                    pass

        st.error(
            "The appliance could not be added. Please upload the manual again."
        )


def render_upload_flow() -> None:
    """Render the one-step automatic setup."""

    st.markdown(
        (
            '<section class="hg-auto-intro">'
            '<div class="hg-auto-title">Just upload the appliance manual</div>'
            '<p class="hg-auto-text">HomeGuardian automatically finds the appliance type, brand and model, then creates the appliance name for you.</p>'
            '</section>'
        ),
        unsafe_allow_html=True,
    )

    upload_version = st.session_state.get("manual_upload_version", 0)

    uploaded_file = st.file_uploader(
        "Upload manual",
        type=["pdf"],
        key=f"manual_upload_{upload_version}",
        help="Upload the official appliance PDF manual.",
    )

    if uploaded_file is None:
        st.info("Upload a PDF manual to add an appliance automatically.")
        return

    try:
        with st.spinner("Reading the manual and identifying the appliance..."):
            detected = inspect_manual(
                uploaded_file.getvalue(),
                uploaded_file.name,
            )

    except ValueError as error:
        st.error(str(error))
        return

    fingerprint = file_fingerprint(uploaded_file)

    detected_category = clean_value(detected.get("category")) or "Other"
    detected_brand = clean_value(detected.get("brand"))
    detected_model = clean_value(detected.get("model"))

    final_category = detected_category
    final_brand = detected_brand
    final_model = detected_model

    detection_complete = (
        final_category != "Other"
        and bool(final_model)
    )

    if not detection_complete:
        st.warning(
            "HomeGuardian could not confidently identify every detail. Only the missing information is shown below."
        )

        with st.container(border=True):
            if final_category == "Other":
                final_category = st.selectbox(
                    "What type of appliance is this?",
                    options=[item for item in CATEGORIES if item != "Other"],
                    key=f"fallback_category_{fingerprint}",
                )

            if not final_model:
                final_model = st.text_input(
                    "Model number",
                    placeholder="Copy it from the manual cover",
                    key=f"fallback_model_{fingerprint}",
                ).strip()

    final_name = make_appliance_name(
        final_brand,
        final_category,
        final_model,
    )

    render_detected_card(
        name=final_name,
        category=final_category,
        brand=final_brand,
        model=final_model,
    )

    with st.expander("Detected something incorrectly?", expanded=False):
        st.caption("Change these only when HomeGuardian detected the wrong information.")

        correction_1, correction_2, correction_3 = st.columns(3)

        with correction_1:
            corrected_category = st.selectbox(
                "Type",
                options=CATEGORIES,
                index=(
                    CATEGORIES.index(final_category)
                    if final_category in CATEGORIES
                    else CATEGORIES.index("Other")
                ),
                key=f"correct_category_{fingerprint}",
            )

        with correction_2:
            corrected_brand = st.text_input(
                "Brand",
                value=final_brand,
                key=f"correct_brand_{fingerprint}",
            ).strip()

        with correction_3:
            corrected_model = st.text_input(
                "Model",
                value=final_model,
                key=f"correct_model_{fingerprint}",
            ).strip()

    final_category = corrected_category
    final_brand = corrected_brand
    final_model = corrected_model
    final_name = make_appliance_name(
        final_brand,
        final_category,
        final_model,
    )

    can_add = final_category != "Other" and bool(final_model)

    if st.button(
        "Add this appliance",
        type="primary",
        use_container_width=True,
        disabled=not can_add,
        key=f"add_appliance_{fingerprint}",
    ):
        add_detected_appliance(
            uploaded_file=uploaded_file,
            category=final_category,
            brand=final_brand,
            model=final_model,
        )


def render_saved_appliance(appliance: dict) -> None:
    """Render a simple saved appliance card."""

    appliance_id = int(appliance["id"])
    category = clean_value(appliance.get("category")) or "Other"
    icon = CATEGORY_ICONS.get(category, "🔌")
    name = escape(clean_value(appliance.get("appliance_name")) or "Appliance")
    brand = escape(clean_value(appliance.get("brand")))
    model = escape(clean_value(appliance.get("model_number")))

    if appliance.get("manual_processed"):
        badge = render_status_pill("AI ready", "good")
    elif appliance.get("manual_path"):
        badge = render_status_pill("Manual needs attention", "warning")
    else:
        badge = render_status_pill("No manual", "warning")

    with st.container(border=True):
        st.markdown(
            (
                f'<div class="hg-saved-title">{icon} {name}</div>'
                f'<div class="hg-saved-meta">{brand} {model}</div>'
                f'<div class="hg-saved-badge">{badge}</div>'
                '<div class="hg-saved-actions-space"></div>'
            ),
            unsafe_allow_html=True,
        )

        action_1, action_2 = st.columns(2)

        with action_1:
            if st.button(
                "Ask AI",
                key=f"ask_saved_{appliance_id}",
                use_container_width=True,
            ):
                st.session_state["preferred_appliance_id"] = appliance_id
                st.switch_page("pages/3_🤖_AI_Assistant.py")

        with action_2:
            with st.popover("Details", use_container_width=True):
                st.write(f"**Type:** {category}")
                st.write(f"**Brand:** {brand or 'Not detected'}")
                st.write(f"**Model:** {model or 'Not detected'}")

                confirm_delete = st.checkbox(
                    "Remove this appliance",
                    key=f"confirm_remove_{appliance_id}",
                )

                if st.button(
                    "Remove",
                    key=f"remove_{appliance_id}",
                    disabled=not confirm_delete,
                    use_container_width=True,
                ):
                    delete_appliance_files(appliance)
                    delete_appliance(appliance_id)
                    st.rerun()


def main() -> None:
    """Run the automatic Add Appliance page."""

    try:
        initialize_database()
        appliances = get_all_appliances()
    except Exception:
        st.error(
            "HomeGuardian could not load your appliances. Please restart the app and try again."
        )
        st.stop()

    render_hero(
        title="Add an appliance automatically.",
        subtitle=(
            "Upload its manual and HomeGuardian will identify everything for you. "
            "No name, room or appliance type form is needed."
        ),
        eyebrow="One-step setup",
    )

    success_message = st.session_state.pop("appliance_added_message", None)
    if success_message:
        st.success(success_message)

    add_tab, saved_tab = st.tabs(
        [
            "➕ Add appliance",
            f"🏠 My appliances ({len(appliances)})",
        ]
    )

    with add_tab:
        render_upload_flow()

    with saved_tab:
        if not appliances:
            st.info("No appliances have been added yet.")
        else:
            columns = st.columns(2)
            for index, appliance in enumerate(appliances):
                with columns[index % 2]:
                    render_saved_appliance(appliance)
                    st.write("")


if __name__ == "__main__":
    main()