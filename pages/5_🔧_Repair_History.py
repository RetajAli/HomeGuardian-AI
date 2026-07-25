from __future__ import annotations

from datetime import date
from html import escape

import streamlit as st

from core.database import (
    add_repair_record,
    delete_repair_record,
    get_all_appliances,
    get_repair_records,
    get_repair_statistics,
    initialize_database,
)
from core.ui import (
    apply_app_style,
    render_hero,
    render_status_pill,
)


# =========================================================
# Page setup
# =========================================================

st.set_page_config(
    page_title="Repair History | HomeGuardian AI",
    page_icon="🔧",
    layout="wide",
)

apply_app_style()


# =========================================================
# Page styling
# =========================================================

st.markdown(
    """
    <style>
    .hg-repair-shell {
        max-width: 1040px;
        margin: 0 auto;
    }

    .hg-repair-intro {
        margin-bottom: 1rem;
        padding: 1rem 1.1rem;
        color: var(--hg-muted);
        background:
            linear-gradient(
                135deg,
                var(--hg-surface),
                var(--hg-surface-second)
            );
        border: 1px solid var(--hg-border);
        border-radius: 17px;
        line-height: 1.55;
    }

    .hg-repair-section-label {
        margin-top: 1.2rem;
        margin-bottom: 0.55rem;
        color: var(--hg-muted);
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .hg-repair-card-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.7rem;
    }

    .hg-repair-title {
        color: var(--hg-text);
        font-size: 1.15rem;
        font-weight: 800;
        line-height: 1.35;
    }

    .hg-repair-appliance {
        margin-top: 0.22rem;
        color: var(--hg-muted);
        font-size: 0.86rem;
    }

    .hg-repair-problem {
        margin-top: 0.8rem;
        color: var(--hg-text);
        line-height: 1.58;
    }

    .hg-repair-solution {
        margin-top: 0.8rem;
        padding: 0.85rem 0.95rem;
        color: var(--hg-text);
        background: var(--hg-accent-soft);
        border: 1px solid var(--hg-border);
        border-radius: 14px;
        line-height: 1.55;
    }

    .hg-repair-solution-label {
        margin-bottom: 0.18rem;
        color: var(--hg-muted);
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .hg-repair-meta {
        margin-top: 0.8rem;
        color: var(--hg-muted);
        font-size: 0.82rem;
    }

    .hg-repair-detail-grid {
        display: grid;
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
        gap: 0.65rem;
        margin-top: 0.4rem;
    }

    .hg-repair-detail {
        padding: 0.75rem 0.85rem;
        background: var(--hg-surface);
        border: 1px solid var(--hg-border);
        border-radius: 13px;
    }

    .hg-repair-detail-label {
        color: var(--hg-muted);
        font-size: 0.74rem;
        font-weight: 750;
        text-transform: uppercase;
    }

    .hg-repair-detail-value {
        margin-top: 0.18rem;
        color: var(--hg-text);
        font-size: 0.88rem;
        line-height: 1.45;
    }

    .hg-empty-repairs {
        padding: 2rem 1.2rem;
        text-align: center;
        background:
            linear-gradient(
                135deg,
                var(--hg-surface),
                var(--hg-surface-second)
            );
        border: 1px solid var(--hg-border);
        border-radius: 20px;
    }

    .hg-empty-repairs-icon {
        margin-bottom: 0.7rem;
        font-size: 2.2rem;
    }

    .hg-empty-repairs-title {
        color: var(--hg-text);
        font-size: 1.1rem;
        font-weight: 800;
    }

    .hg-empty-repairs-text {
        max-width: 520px;
        margin: 0.35rem auto 0;
        color: var(--hg-muted);
        line-height: 1.55;
    }

    .hg-form-note {
        margin-bottom: 1rem;
        padding: 0.85rem 1rem;
        color: var(--hg-muted);
        background: var(--hg-accent-soft);
        border: 1px solid var(--hg-border);
        border-radius: 15px;
        font-size: 0.88rem;
        line-height: 1.5;
    }

    .hg-cost-note {
        color: var(--hg-muted);
        font-size: 0.82rem;
    }

    div[data-testid="stRadio"] > div {
        gap: 0.45rem;
    }

    div[data-testid="stRadio"] label {
        padding: 0.5rem 0.9rem;
        background: var(--hg-surface);
        border: 1px solid var(--hg-border);
        border-radius: 12px;
    }

    @media (max-width: 700px) {
        .hg-repair-card-top {
            flex-direction: column;
        }

        .hg-repair-detail-grid {
            grid-template-columns: 1fr;
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


# =========================================================
# Helpers
# =========================================================

def clean_text(value: object) -> str:
    """Return clean text."""

    return str(value or "").strip()


def get_appliance_icon(category: str) -> str:
    """Return an icon for the appliance category."""

    return APPLIANCE_ICONS.get(
        category,
        "🔌",
    )


def appliance_label(appliance: dict) -> str:
    """Return a friendly appliance label."""

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

    if details:
        return f"{name} — {details}"

    return name


def parse_date(value: object) -> date | None:
    """Parse an ISO date safely."""

    if not value:
        return None

    try:
        return date.fromisoformat(
            str(value)
        )
    except ValueError:
        return None


def display_date(value: object) -> str:
    """Return a friendly date."""

    parsed = parse_date(value)

    if parsed is None:
        return "Not added"

    return parsed.strftime(
        "%d %b %Y"
    )


def display_money(value: object) -> str:
    """Return a friendly EGP amount."""

    try:
        amount = float(value)
    except (TypeError, ValueError):
        amount = 0.0

    return f"EGP {amount:,.2f}"


def preferred_appliance_id(
    appliances: list[dict],
) -> int | None:
    """Resolve a selected appliance from another page."""

    valid_ids = {
        int(appliance["id"])
        for appliance in appliances
    }

    candidates = [
        st.session_state.get(
            "selected_repair_appliance_id"
        ),
        st.session_state.get(
            "selected_appliance_id"
        ),
    ]

    for candidate in candidates:
        try:
            candidate_id = int(candidate)
        except (TypeError, ValueError):
            continue

        if candidate_id in valid_ids:
            return candidate_id

    return None


# =========================================================
# Page navigation state
# =========================================================

REPAIR_FORM_KEYS = (
    "new_repair_appliance",
    "new_repair_problem",
    "new_repair_date",
    "new_repair_add_cost",
    "new_repair_cost",
    "new_repair_solution",
    "new_repair_technician",
    "new_repair_parts",
    "new_repair_has_warranty",
    "new_repair_warranty",
    "new_repair_notes",
)


def request_repair_view(
    view: str,
    *,
    reset_form: bool = False,
    show_saved_message: bool = False,
) -> None:
    """Queue a safe page-view change for the next rerun."""

    st.session_state["_repair_next_view"] = view

    if reset_form:
        st.session_state["_repair_reset_form"] = True

    if show_saved_message:
        st.session_state["_repair_show_saved_message"] = True


def apply_pending_repair_state() -> None:
    """Apply queued state before the repair-view widget is created."""

    if st.session_state.pop(
        "_repair_reset_form",
        False,
    ):
        for key in REPAIR_FORM_KEYS:
            st.session_state.pop(
                key,
                None,
            )

    next_view = st.session_state.pop(
        "_repair_next_view",
        None,
    )

    if next_view in {
        "My repairs",
        "Add repair",
    }:
        st.session_state["repair_view"] = next_view


# =========================================================
# Repair cards
# =========================================================

def render_repair_details(
    repair: dict,
) -> None:
    """Render optional repair information."""

    technician = clean_text(
        repair.get("technician_name")
    ) or "Not added"

    parts = clean_text(
        repair.get("replaced_parts")
    ) or "No parts recorded"

    warranty = display_date(
        repair.get(
            "repair_warranty_expiry"
        )
    )

    notes = clean_text(
        repair.get("notes")
    ) or "No notes"

    detail_html = (
        '<div class="hg-repair-detail-grid">'
        '<div class="hg-repair-detail">'
        '<div class="hg-repair-detail-label">Technician</div>'
        f'<div class="hg-repair-detail-value">{escape(technician)}</div>'
        "</div>"
        '<div class="hg-repair-detail">'
        '<div class="hg-repair-detail-label">Repair warranty</div>'
        f'<div class="hg-repair-detail-value">{escape(warranty)}</div>'
        "</div>"
        '<div class="hg-repair-detail">'
        '<div class="hg-repair-detail-label">Replaced parts</div>'
        f'<div class="hg-repair-detail-value">{escape(parts)}</div>'
        "</div>"
        '<div class="hg-repair-detail">'
        '<div class="hg-repair-detail-label">Notes</div>'
        f'<div class="hg-repair-detail-value">{escape(notes)}</div>'
        "</div>"
        "</div>"
    )

    st.markdown(
        detail_html,
        unsafe_allow_html=True,
    )


def render_repair_card(
    repair: dict,
) -> None:
    """Render one repair record."""

    repair_id = int(
        repair["id"]
    )

    category = clean_text(
        repair.get("category")
    ) or "Other"

    icon = get_appliance_icon(
        category
    )

    appliance_name = escape(
        clean_text(
            repair.get("appliance_name")
        )
        or "Appliance"
    )

    brand = clean_text(
        repair.get("brand")
    )

    model = clean_text(
        repair.get("model_number")
    )

    appliance_details = " ".join(
        part
        for part in [brand, model]
        if part
    )

    problem = escape(
        clean_text(
            repair.get(
                "problem_description"
            )
        )
        or "Repair"
    )

    solution = clean_text(
        repair.get("solution")
    )

    repair_date_text = display_date(
        repair.get("repair_date")
    )

    cost = repair.get("repair_cost")

    if cost is None:
        badge = render_status_pill(
            "Cost not added",
            "warning",
        )
    else:
        badge = render_status_pill(
            display_money(cost),
            "good",
        )

    subtitle = appliance_name

    if appliance_details:
        subtitle += (
            " · "
            + escape(appliance_details)
        )

    header_html = (
        '<div class="hg-repair-card-top">'
        '<div>'
        f'<div class="hg-repair-title">{icon} {problem}</div>'
        f'<div class="hg-repair-appliance">{subtitle}</div>'
        "</div>"
        f"<div>{badge}</div>"
        "</div>"
    )

    with st.container(border=True):
        st.markdown(
            header_html,
            unsafe_allow_html=True,
        )

        if solution:
            st.markdown(
                (
                    '<div class="hg-repair-solution">'
                    '<div class="hg-repair-solution-label">How it was fixed</div>'
                    f"{escape(solution)}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        st.markdown(
            (
                '<div class="hg-repair-meta">'
                f"Repair date: {escape(repair_date_text)}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        with st.expander(
            "Details",
            expanded=False,
        ):
            render_repair_details(
                repair
            )

            st.write("")

            st.caption(
                "Delete this record only if it was added by mistake."
            )

            confirm_delete = st.checkbox(
                "I want to delete this repair",
                key=f"confirm_delete_repair_{repair_id}",
            )

            if st.button(
                "Delete repair",
                key=f"delete_repair_{repair_id}",
                disabled=not confirm_delete,
                use_container_width=True,
            ):
                try:
                    delete_repair_record(
                        repair_id
                    )

                    st.toast(
                        "Repair deleted.",
                        icon="🗑️",
                    )

                    st.rerun()

                except Exception:
                    st.error(
                        "HomeGuardian could not delete this repair."
                    )


def render_empty_repairs() -> None:
    """Render a friendly empty state."""

    st.markdown(
        (
            '<div class="hg-empty-repairs">'
            '<div class="hg-empty-repairs-icon">🔧</div>'
            '<div class="hg-empty-repairs-title">No repairs saved yet</div>'
            '<div class="hg-empty-repairs-text">'
            "When an appliance is repaired, save what happened so you can "
            "remember the solution, cost, technician, and warranty later."
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    st.write("")

    if st.button(
        "Add the first repair",
        type="primary",
        use_container_width=True,
        key="empty_add_repair",
    ):
        request_repair_view(
            "Add repair",
        )

        st.rerun()


# =========================================================
# Repair history
# =========================================================

def render_repair_history(
    appliances: list[dict],
) -> None:
    """Render repair filters, metrics, and cards."""

    appliance_by_id = {
        int(appliance["id"]): appliance
        for appliance in appliances
    }

    appliance_options: list[int | str] = [
        "All"
    ] + list(appliance_by_id.keys())

    preferred_id = preferred_appliance_id(
        appliances
    )

    if preferred_id in appliance_options:
        default_index = appliance_options.index(
            preferred_id
        )
    else:
        default_index = 0

    selected_appliance = st.selectbox(
        "Show repairs for",
        options=appliance_options,
        index=default_index,
        format_func=lambda value: (
            "All appliances"
            if value == "All"
            else appliance_label(
                appliance_by_id[
                    int(value)
                ]
            )
        ),
        key="repair_filter_appliance",
    )

    appliance_id = (
        None
        if selected_appliance == "All"
        else int(selected_appliance)
    )

    repairs = get_repair_records(
        appliance_id=appliance_id
    )

    statistics = get_repair_statistics(
        appliance_id=appliance_id
    )

    repair_count = int(
        statistics.get(
            "total_repairs",
            0,
        )
    )

    total_cost = float(
        statistics.get(
            "total_cost",
            0,
        )
    )

    last_repair = statistics.get(
        "last_repair_date"
    )

    metric_1, metric_2, metric_3 = st.columns(
        3
    )

    with metric_1:
        st.metric(
            "Repairs",
            repair_count,
        )

    with metric_2:
        st.metric(
            "Total spent",
            display_money(
                total_cost
            ),
        )

    with metric_3:
        st.metric(
            "Last repair",
            (
                display_date(last_repair)
                if last_repair
                else "Not added"
            ),
        )

    st.write("")

    if not repairs:
        render_empty_repairs()
        return

    st.markdown(
        '<div class="hg-repair-section-label">Repair records</div>',
        unsafe_allow_html=True,
    )

    for repair in repairs:
        render_repair_card(
            repair
        )

        st.write("")


# =========================================================
# Add repair
# =========================================================

def render_add_repair(
    appliances: list[dict],
) -> None:
    """Render a simple repair form."""

    if not appliances:
        with st.container(border=True):
            st.markdown(
                "### Add an appliance first"
            )

            st.write(
                "A repair record must belong to an appliance."
            )

            if st.button(
                "Go to Add Appliance",
                type="primary",
                use_container_width=True,
            ):
                st.switch_page(
                    "pages/2_➕_Add_Appliance.py"
                )

        return

    st.markdown(
        (
            '<div class="hg-form-note">'
            "Only the appliance and what happened are required. "
            "Everything else can be added only when it is useful."
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    appliance_by_id = {
        int(appliance["id"]): appliance
        for appliance in appliances
    }

    appliance_ids = list(
        appliance_by_id.keys()
    )

    preferred_id = preferred_appliance_id(
        appliances
    )

    if preferred_id in appliance_ids:
        default_index = appliance_ids.index(
            preferred_id
        )
    else:
        default_index = 0

    selected_id = st.selectbox(
        "Appliance",
        options=appliance_ids,
        index=default_index,
        format_func=lambda appliance_id: (
            appliance_label(
                appliance_by_id[
                    int(appliance_id)
                ]
            )
        ),
        key="new_repair_appliance",
    )

    problem_description = st.text_area(
        "What happened?",
        placeholder=(
            "Example: The air conditioner stopped cooling "
            "and displayed error code E5."
        ),
        height=125,
        key="new_repair_problem",
    )

    repair_date = st.date_input(
        "Repair date",
        value=date.today(),
        max_value=date.today(),
        key="new_repair_date",
    )

    add_cost = st.toggle(
        "Add repair cost",
        value=False,
        key="new_repair_add_cost",
    )

    repair_cost: float | None = None

    if add_cost:
        repair_cost = float(
            st.number_input(
                "Cost in EGP",
                min_value=0.0,
                value=0.0,
                step=50.0,
                format="%.2f",
                key="new_repair_cost",
            )
        )

        st.markdown(
            '<div class="hg-cost-note">Enter 0 only when the repair was free.</div>',
            unsafe_allow_html=True,
        )

    with st.expander(
        "More details — optional",
        expanded=False,
    ):
        solution = st.text_area(
            "How was it fixed?",
            placeholder=(
                "Example: The technician cleaned the filter "
                "and replaced the capacitor."
            ),
            height=110,
            key="new_repair_solution",
        )

        detail_1, detail_2 = st.columns(
            2
        )

        with detail_1:
            technician_name = st.text_input(
                "Technician or company",
                placeholder="Optional",
                key="new_repair_technician",
            )

            replaced_parts = st.text_input(
                "Replaced parts",
                placeholder=(
                    "Example: Capacitor"
                ),
                key="new_repair_parts",
            )

        with detail_2:
            has_warranty = st.toggle(
                "This repair has a warranty",
                value=False,
                key="new_repair_has_warranty",
            )

            repair_warranty_expiry: date | None = None

            if has_warranty:
                repair_warranty_expiry = st.date_input(
                    "Warranty expiry",
                    value=date.today(),
                    min_value=repair_date,
                    key="new_repair_warranty",
                )

        notes = st.text_area(
            "Notes",
            placeholder=(
                "Anything else worth remembering."
            ),
            height=90,
            key="new_repair_notes",
        )

    if st.button(
        "Save repair",
        type="primary",
        use_container_width=True,
        key="save_repair",
    ):
        cleaned_problem = (
            problem_description.strip()
        )

        if not cleaned_problem:
            st.warning(
                "Describe what happened."
            )
            return

        try:
            add_repair_record(
                appliance_id=int(
                    selected_id
                ),
                repair_date=repair_date,
                problem_description=cleaned_problem,
                solution=(
                    solution.strip()
                    if solution.strip()
                    else None
                ),
                technician_name=(
                    technician_name.strip()
                    if technician_name.strip()
                    else None
                ),
                repair_cost=repair_cost,
                replaced_parts=(
                    replaced_parts.strip()
                    if replaced_parts.strip()
                    else None
                ),
                repair_warranty_expiry=(
                    repair_warranty_expiry
                ),
                notes=(
                    notes.strip()
                    if notes.strip()
                    else None
                ),
            )

        except Exception:
            st.error(
                "HomeGuardian could not save this repair. "
                "Please check the information and try again."
            )

            return

        request_repair_view(
            "My repairs",
            reset_form=True,
            show_saved_message=True,
        )

        st.rerun()


# =========================================================
# Main page
# =========================================================

def main() -> None:
    """Run the Repair History page."""

    try:
        initialize_database()

        appliances = get_all_appliances()

    except Exception:
        st.error(
            "HomeGuardian could not load repair history. "
            "Please restart the app and try again."
        )

        st.stop()

    render_hero(
        title="Repair history.",
        subtitle=(
            "Keep a simple record of what happened, how it was fixed, "
            "and how much it cost."
        ),
        eyebrow="Everything in one place",
    )

    st.markdown(
        '<div class="hg-repair-shell">',
        unsafe_allow_html=True,
    )

    apply_pending_repair_state()

    if "repair_view" not in st.session_state:
        st.session_state[
            "repair_view"
        ] = "My repairs"

    if st.session_state.pop(
        "_repair_show_saved_message",
        False,
    ):
        st.toast(
            "Repair saved successfully.",
            icon="✅",
        )

    view = st.radio(
        "Repair page",
        options=[
            "My repairs",
            "Add repair",
        ],
        horizontal=True,
        key="repair_view",
        label_visibility="collapsed",
    )

    st.write("")

    if view == "My repairs":
        render_repair_history(
            appliances
        )
    else:
        render_add_repair(
            appliances
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()