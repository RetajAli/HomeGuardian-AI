from __future__ import annotations

import os
import re
from html import escape

import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_core.documents import Document

from core.database import (
    get_appliances_with_manuals,
    initialize_database,
)
from core.rag_engine import (
    VectorStoreError,
    search_manual,
)
from core.ui import (
    apply_app_style,
    render_hero,
    render_status_pill,
)


# =========================================================
# Page setup
# =========================================================

load_dotenv()

st.set_page_config(
    page_title="Ask HomeGuardian | HomeGuardian AI",
    page_icon="🤖",
    layout="wide",
)

apply_app_style()


# =========================================================
# Page-specific styling
# =========================================================

st.markdown(
    """
    <style>
    .hg-assistant-wrap {
        max-width: 980px;
        margin: 0 auto;
    }

    .hg-safety-box {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding: 0.9rem 1rem;
        background: rgba(255, 174, 63, 0.10);
        border: 1px solid rgba(255, 174, 63, 0.22);
        border-radius: 15px;
    }

    .hg-safety-box strong {
        display: block;
        margin-bottom: 0.12rem;
        color: var(--hg-warning);
    }

    .hg-safety-box span {
        color: var(--hg-muted);
        font-size: 0.86rem;
        line-height: 1.5;
    }

    .hg-selected-appliance {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin: 0.85rem 0 1rem;
        padding: 1rem 1.1rem;
        background:
            linear-gradient(
                135deg,
                var(--hg-surface),
                var(--hg-surface-second)
            );
        border: 1px solid var(--hg-border);
        border-radius: 17px;
    }

    .hg-selected-main {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        min-width: 0;
    }

    .hg-selected-icon {
        display: flex;
        flex: 0 0 auto;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        background: var(--hg-accent-soft);
        border: 1px solid var(--hg-border);
        border-radius: 15px;
        font-size: 1.45rem;
    }

    .hg-selected-name {
        color: var(--hg-text);
        font-size: 1rem;
        font-weight: 800;
    }

    .hg-selected-meta {
        margin-top: 0.15rem;
        color: var(--hg-muted);
        font-size: 0.84rem;
    }

    .hg-mini-heading {
        margin-top: 1.15rem;
        margin-bottom: 0.55rem;
        color: var(--hg-muted);
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .hg-welcome-card {
        display: flex;
        gap: 0.9rem;
        margin-top: 0.25rem;
        margin-bottom: 1rem;
        padding: 1rem 1.1rem;
        background:
            linear-gradient(
                135deg,
                var(--hg-surface),
                var(--hg-surface-second)
            );
        border: 1px solid var(--hg-border);
        border-radius: 18px;
    }

    .hg-welcome-icon {
        display: flex;
        flex: 0 0 auto;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 42px;
        background:
            linear-gradient(
                135deg,
                var(--hg-accent),
                var(--hg-accent-second)
            );
        border-radius: 13px;
        color: white;
        font-size: 1.1rem;
    }

    .hg-welcome-title {
        color: var(--hg-text);
        font-weight: 800;
    }

    .hg-welcome-text {
        margin-top: 0.2rem;
        color: var(--hg-muted);
        font-size: 0.9rem;
        line-height: 1.55;
    }

    [data-testid="stChatMessage"] {
        margin-bottom: 0.65rem;
        padding: 0.2rem 0.35rem;
    }

    [data-testid="stChatMessage"] p {
        line-height: 1.62;
    }

    [data-testid="stChatInput"] {
        border: 1px solid var(--hg-border);
        border-radius: 17px;
        box-shadow: 0 12px 35px var(--hg-shadow);
    }

    @media (max-width: 700px) {
        .hg-selected-appliance {
            align-items: flex-start;
            flex-direction: column;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Constants
# =========================================================

APPLIANCE_ICONS = {
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

DANGER_TERMS = {
    "smoke",
    "fire",
    "burning smell",
    "gas smell",
    "electric shock",
    "sparking",
    "exposed wire",
    "exposed wiring",
    "serious leak",
    "refrigerant leak",
}

TECHNICAL_TERMS = {
    "compressor",
    "refrigerant",
    "capacitor",
    "circuit board",
    "pcb",
    "wiring",
    "voltage",
    "current",
    "inverter",
    "motor",
    "pressure",
}


# =========================================================
# Helpers
# =========================================================

def clean_text(value: object) -> str:
    """Return a clean single-line text value."""

    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def get_icon(category: str) -> str:
    """Return an appliance category icon."""

    return APPLIANCE_ICONS.get(
        category,
        "🔌",
    )


def appliance_label(appliance: dict) -> str:
    """Build a clear appliance selector label."""

    name = clean_text(
        appliance.get("appliance_name")
    ) or "Appliance"

    brand = clean_text(
        appliance.get("brand")
    )

    model = clean_text(
        appliance.get("model_number")
    )

    details = " ".join(
        part
        for part in [brand, model]
        if part
    )

    return (
        f"{name} — {details}"
        if details
        else name
    )


def preferred_appliance_id(
    appliances: list[dict],
) -> int:
    """Use the appliance selected on Dashboard or Add Appliance."""

    valid_ids = {
        int(appliance["id"])
        for appliance in appliances
    }

    for key in (
        "preferred_appliance_id",
        "selected_appliance_id",
    ):
        try:
            candidate = int(
                st.session_state.get(key)
            )
        except (TypeError, ValueError):
            continue

        if candidate in valid_ids:
            return candidate

    return int(appliances[0]["id"])


def get_history(
    appliance_id: int,
) -> list[dict]:
    """Return chat history for one appliance."""

    if "hg_chat_history" not in st.session_state:
        st.session_state["hg_chat_history"] = {}

    histories = st.session_state[
        "hg_chat_history"
    ]

    return histories.setdefault(
        str(appliance_id),
        [],
    )


def clear_history(
    appliance_id: int,
) -> None:
    """Clear one appliance conversation."""

    if "hg_chat_history" in st.session_state:
        st.session_state[
            "hg_chat_history"
        ][str(appliance_id)] = []


def suggested_questions(
    category: str,
) -> list[tuple[str, str]]:
    """Return category-specific quick questions."""

    questions = {
        "Air Conditioner": [
            (
                "❄️ Not cooling",
                "My air conditioner is running but not cooling. What should I check?",
            ),
            (
                "🧼 Clean the filter",
                "How do I safely clean the air conditioner filter?",
            ),
            (
                "🔊 Strange noise",
                "The air conditioner is making a strange noise. What could it mean?",
            ),
        ],
        "Refrigerator": [
            (
                "🧊 Not cold",
                "My refrigerator is not cold enough. What should I check?",
            ),
            (
                "💧 Water leak",
                "There is water leaking from my refrigerator. What should I do?",
            ),
            (
                "🧼 Clean it",
                "How do I safely clean and maintain this refrigerator?",
            ),
        ],
        "Washing Machine": [
            (
                "🌀 Not spinning",
                "The washing machine is not spinning. What should I check?",
            ),
            (
                "💧 Not draining",
                "The washing machine is not draining water. What should I do?",
            ),
            (
                "🧼 Clean the drum",
                "How do I safely clean the washing machine drum?",
            ),
        ],
        "Television": [
            (
                "📺 No picture",
                "The television turns on but there is no picture. What should I check?",
            ),
            (
                "🔊 No sound",
                "The television has a picture but no sound. What should I do?",
            ),
            (
                "⚙️ Restart help",
                "How can I safely restart or reset this television?",
            ),
        ],
    }

    return questions.get(
        category,
        [
            (
                "🧼 How do I clean it?",
                "How do I safely clean and maintain this appliance?",
            ),
            (
                "⚠️ It is not working",
                "This appliance is not working. What should I check first?",
            ),
            (
                "🛡️ Safety advice",
                "Show me the important safety advice for this appliance.",
            ),
        ],
    )


# =========================================================
# RAG answer generation
# =========================================================

def is_dangerous(question: str) -> bool:
    """Detect an urgent hazard in the user's description."""

    lowered = question.lower()

    return any(
        term in lowered
        for term in DANGER_TERMS
    )


def source_records(
    documents: list[Document],
) -> list[dict]:
    """Convert retrieved chunks to display-safe source records."""

    records: list[dict] = []
    seen: set[tuple[object, str]] = set()

    for document in documents:
        page = document.metadata.get("page")
        excerpt = clean_text(
            document.page_content
        )

        if len(excerpt) > 420:
            excerpt = (
                excerpt[:417].rstrip()
                + "..."
            )

        key = (page, excerpt)

        if key in seen:
            continue

        seen.add(key)

        records.append(
            {
                "page": page,
                "excerpt": excerpt,
            }
        )

    return records


def build_context(
    documents: list[Document],
) -> str:
    """Build a page-labelled context for the AI model."""

    parts: list[str] = []

    for document in documents:
        page = document.metadata.get(
            "page",
            "Unknown",
        )

        text = clean_text(
            document.page_content
        )

        parts.append(
            f"[Manual page {page}]\n{text}"
        )

    return "\n\n".join(parts)[:14000]


def generate_model_answer(
    appliance: dict,
    question: str,
    documents: list[Document],
) -> str | None:
    """Use Hugging Face when an HF token is configured."""

    token = os.getenv("HF_TOKEN")

    if not token:
        return None

    model_name = os.getenv(
        "HOMEGUARDIAN_MODEL",
        "Qwen/Qwen2.5-7B-Instruct",
    )

    system_prompt = """
You are HomeGuardian, a cautious home-appliance assistant.

Use only the provided manual excerpts. Never invent information.
Write for a normal appliance owner, not a technician.

Rules:
- Start with the direct answer.
- Give short numbered steps when useful.
- Separate safe user checks from technician-only work.
- Never instruct the user to open electrical panels, handle refrigerant,
  repair wiring, bypass safety devices, or perform dangerous service work.
- If the manual does not provide enough information, say so clearly.
- Cite relevant pages using the exact form: Manual page 12.
- Keep the answer clear and concise.

For smoke, fire, a gas smell, electric shock, sparking, exposed wiring,
or a serious leak, tell the user to stop using the appliance and contact
a qualified technician or emergency service as appropriate.
""".strip()

    prompt = f"""
Appliance: {clean_text(appliance.get('appliance_name'))}
Brand: {clean_text(appliance.get('brand')) or 'Not detected'}
Model: {clean_text(appliance.get('model_number')) or 'Not detected'}

Question:
{question}

Relevant manual excerpts:
{build_context(documents)}
""".strip()

    try:
        client = InferenceClient(
            token=token
        )

        response = client.chat_completion(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=750,
            temperature=0.15,
        )

        content = (
            response.choices[0]
            .message
            .content
        )

        if content:
            return content.strip()

    except Exception:
        return None

    return None


def score_sentence(
    sentence: str,
    question_words: set[str],
) -> int:
    """Score a manual sentence for the no-token fallback."""

    lowered = sentence.lower()

    sentence_words = set(
        re.findall(
            r"[a-z0-9]+",
            lowered,
        )
    )

    score = len(
        sentence_words & question_words
    ) * 4

    for term in (
        "check",
        "clean",
        "remove",
        "press",
        "turn off",
        "disconnect",
        "replace",
        "make sure",
        "do not",
        "warning",
        "caution",
        "cause",
        "solution",
    ):
        if term in lowered:
            score += 1

    return score


def generate_fallback_answer(
    question: str,
    documents: list[Document],
) -> str:
    """Build a clear extractive answer when no model is available."""

    question_words = {
        word
        for word in re.findall(
            r"[a-z0-9]+",
            question.lower(),
        )
        if len(word) > 2
    }

    candidates: list[
        tuple[int, str, object]
    ] = []

    for document in documents:
        page = document.metadata.get(
            "page",
            "Unknown",
        )

        text = clean_text(
            document.page_content
        )

        for sentence in re.split(
            r"(?<=[.!?])\s+|\n+",
            text,
        ):
            sentence = clean_text(sentence)

            if not 35 <= len(sentence) <= 300:
                continue

            candidates.append(
                (
                    score_sentence(
                        sentence,
                        question_words,
                    ),
                    sentence,
                    page,
                )
            )

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    chosen: list[tuple[str, object]] = []
    seen: set[str] = set()

    for score, sentence, page in candidates:
        normalized = sentence.lower()

        if normalized in seen:
            continue

        if score <= 0 and chosen:
            continue

        seen.add(normalized)
        chosen.append((sentence, page))

        if len(chosen) == 5:
            break

    if not chosen:
        first_document = documents[0]
        chosen = [
            (
                clean_text(
                    first_document.page_content
                )[:650],
                first_document.metadata.get(
                    "page",
                    "Unknown",
                ),
            )
        ]

    lines: list[str] = []

    if is_dangerous(question):
        lines.extend(
            [
                "### Stop using the appliance",
                (
                    "This may be unsafe. Move away from the appliance and "
                    "disconnect its power only if you can do so safely. "
                    "Contact a qualified technician or emergency service."
                ),
                "",
            ]
        )

    lines.append("### What the manual says")

    for sentence, page in chosen[:3]:
        lines.append(
            f"- {sentence} *(Manual page {page})*"
        )

    safe_items = [
        (sentence, page)
        for sentence, page in chosen
        if not any(
            term in sentence.lower()
            for term in TECHNICAL_TERMS
        )
    ]

    technical_items = [
        (sentence, page)
        for sentence, page in chosen
        if any(
            term in sentence.lower()
            for term in TECHNICAL_TERMS
        )
    ]

    if safe_items:
        lines.extend(
            [
                "",
                "### Safe checks to try",
            ]
        )

        for index, (
            sentence,
            page,
        ) in enumerate(
            safe_items[:3],
            start=1,
        ):
            lines.append(
                f"{index}. {sentence} *(Manual page {page})*"
            )

    if technical_items:
        lines.extend(
            [
                "",
                "### When to call a technician",
                (
                    "The relevant manual section includes internal or technical "
                    "work. Do not open electrical panels or handle wiring, "
                    "refrigerant, pressure systems, or internal components yourself."
                ),
            ]
        )

    lines.extend(
        [
            "",
            (
                "_This answer is based only on the uploaded manual. "
                "Open the source pages below before acting._"
            ),
        ]
    )

    return "\n".join(lines)


def answer_question(
    appliance: dict,
    question: str,
) -> tuple[str, list[dict]]:
    """Search the selected manual and create the answer."""

    documents = search_manual(
        appliance_id=int(appliance["id"]),
        question=question,
        number_of_results=5,
    )

    if not documents:
        return (
            "I could not find a relevant section in this manual. "
            "Try describing the symptom more specifically.",
            [],
        )

    answer = generate_model_answer(
        appliance=appliance,
        question=question,
        documents=documents,
    )

    if not answer:
        answer = generate_fallback_answer(
            question=question,
            documents=documents,
        )

    return answer, source_records(documents)


# =========================================================
# Chat functions
# =========================================================

def process_question(
    appliance: dict,
    question: str,
) -> None:
    """Add a user question and assistant answer to history."""

    question = question.strip()

    if not question:
        return

    history = get_history(
        int(appliance["id"])
    )

    history.append(
        {
            "role": "user",
            "content": question,
        }
    )

    try:
        with st.spinner(
            "Checking the appliance manual..."
        ):
            answer, sources = answer_question(
                appliance,
                question,
            )

    except VectorStoreError:
        answer = (
            "This appliance manual is not ready yet. Open "
            "**Add Appliance → My appliances** and upload or prepare it again."
        )
        sources = []

    except Exception:
        answer = (
            "I could not read the manual right now. "
            "Please try the question again."
        )
        sources = []

    history.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
        }
    )


def render_sources(
    sources: list[dict],
) -> None:
    """Show manual sources below an answer."""

    if not sources:
        return

    with st.expander(
        f"Manual sources ({len(sources)})",
        expanded=False,
    ):
        for index, source in enumerate(
            sources,
            start=1,
        ):
            page = source.get(
                "page",
                "Unknown",
            )

            st.markdown(
                f"**Source {index} · Manual page {page}**"
            )

            st.write(
                source.get(
                    "excerpt",
                    "",
                )
            )

            if index < len(sources):
                st.divider()


def render_history(
    appliance_id: int,
) -> None:
    """Render the conversation for one appliance."""

    history = get_history(
        appliance_id
    )

    if not history:
        st.markdown(
            (
                '<div class="hg-welcome-card">'
                '<div class="hg-welcome-icon">✦</div>'
                '<div>'
                '<div class="hg-welcome-title">How can I help?</div>'
                '<div class="hg-welcome-text">'
                'Describe the problem in your own words. HomeGuardian will '
                'search this appliance’s official manual and show the source pages.'
                '</div>'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )
        return

    for message in history:
        role = message.get(
            "role",
            "assistant",
        )

        with st.chat_message(
            role,
            avatar=(
                "👤"
                if role == "user"
                else "🏠"
            ),
        ):
            st.markdown(
                message.get(
                    "content",
                    "",
                )
            )

            if role == "assistant":
                render_sources(
                    message.get(
                        "sources",
                        [],
                    )
                )


# =========================================================
# UI components
# =========================================================

def render_selected_appliance(
    appliance: dict,
) -> None:
    """Render a compact selected-appliance card."""

    category = clean_text(
        appliance.get("category")
    ) or "Other"

    name = escape(
        clean_text(
            appliance.get("appliance_name")
        )
        or "Appliance"
    )

    brand = escape(
        clean_text(
            appliance.get("brand")
        )
    )

    model = escape(
        clean_text(
            appliance.get("model_number")
        )
    )

    details = " ".join(
        part
        for part in [brand, model]
        if part
    ) or escape(category)

    badge = render_status_pill(
        "Manual ready",
        "good",
    )

    html = (
        '<div class="hg-selected-appliance">'
        '<div class="hg-selected-main">'
        f'<div class="hg-selected-icon">{get_icon(category)}</div>'
        '<div>'
        f'<div class="hg-selected-name">{name}</div>'
        f'<div class="hg-selected-meta">{details}</div>'
        '</div>'
        '</div>'
        f'<div>{badge}</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def render_empty_state(
    manual_appliances: list[dict],
) -> None:
    """Render setup help if no manual is AI-ready."""

    with st.container(border=True):
        st.markdown(
            "### HomeGuardian needs an appliance manual"
        )

        if manual_appliances:
            st.write(
                "Your appliance is saved, but its manual is not ready for questions yet."
            )
        else:
            st.write(
                "Upload an appliance PDF manual. HomeGuardian will identify and prepare it automatically."
            )

        if st.button(
            "Go to Add Appliance",
            type="primary",
            use_container_width=True,
        ):
            st.switch_page(
                "pages/2_➕_Add_Appliance.py"
            )


# =========================================================
# Main page
# =========================================================

def main() -> None:
    """Run the HomeGuardian assistant."""

    try:
        initialize_database()
        manual_appliances = (
            get_appliances_with_manuals()
        )

    except Exception:
        st.error(
            "HomeGuardian could not load your appliances. "
            "Please restart the app and try again."
        )
        st.stop()

    ready_appliances = [
        appliance
        for appliance in manual_appliances
        if bool(
            appliance.get("manual_processed")
        )
    ]

    render_hero(
        title="Ask HomeGuardian.",
        subtitle=(
            "Choose an appliance and describe what is happening. "
            "You will get clear guidance based on its official manual."
        ),
        eyebrow="Manual-powered help",
    )

    st.markdown(
        '<div class="hg-assistant-wrap">',
        unsafe_allow_html=True,
    )

    st.markdown(
        (
            '<div class="hg-safety-box">'
            '<div>🛡️</div>'
            '<div>'
            '<strong>Safety first</strong>'
            '<span>For smoke, fire, a gas smell, electric shock, sparking, '
            'exposed wiring, or a serious leak, stop using the appliance and '
            'contact a qualified technician or emergency service.</span>'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    if not ready_appliances:
        render_empty_state(
            manual_appliances
        )
        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )
        return

    chosen_id = preferred_appliance_id(
        ready_appliances
    )

    appliance_ids = [
        int(appliance["id"])
        for appliance in ready_appliances
    ]

    appliances_by_id = {
        int(appliance["id"]): appliance
        for appliance in ready_appliances
    }

    selected_id = st.selectbox(
        "Which appliance needs help?",
        options=appliance_ids,
        index=appliance_ids.index(chosen_id),
        format_func=lambda appliance_id: (
            appliance_label(
                appliances_by_id[appliance_id]
            )
        ),
    )

    selected_appliance = appliances_by_id[
        int(selected_id)
    ]

    st.session_state[
        "preferred_appliance_id"
    ] = int(selected_id)

    render_selected_appliance(
        selected_appliance
    )

    st.markdown(
        '<div class="hg-mini-heading">Popular questions</div>',
        unsafe_allow_html=True,
    )

    prompts = suggested_questions(
        clean_text(
            selected_appliance.get("category")
        )
    )

    quick_question: str | None = None
    prompt_columns = st.columns(
        len(prompts)
    )

    for index, (
        label,
        question,
    ) in enumerate(prompts):
        with prompt_columns[index]:
            if st.button(
                label,
                key=f"prompt_{selected_id}_{index}",
                use_container_width=True,
            ):
                quick_question = question

    history = get_history(
        int(selected_id)
    )

    if history:
        clear_column, _ = st.columns(
            [1, 4]
        )

        with clear_column:
            if st.button(
                "Clear conversation",
                use_container_width=True,
            ):
                clear_history(
                    int(selected_id)
                )
                st.rerun()

    if quick_question:
        process_question(
            selected_appliance,
            quick_question,
        )
        st.rerun()

    st.markdown(
        '<div class="hg-mini-heading">Conversation</div>',
        unsafe_allow_html=True,
    )

    render_history(
        int(selected_id)
    )

    typed_question = st.chat_input(
        "Describe what is happening..."
    )

    if typed_question:
        process_question(
            selected_appliance,
            typed_question,
        )
        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()