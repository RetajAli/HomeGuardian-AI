from __future__ import annotations

from datetime import date
from html import escape

import streamlit as st

from core.database import (
    get_all_appliances,
    get_dashboard_statistics,
    get_maintenance_statistics,
    get_maintenance_tasks,
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
    page_title="Home | HomeGuardian AI",
    page_icon="🏠",
    layout="wide",
)

apply_app_style()


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

def get_appliance_icon(category: str) -> str:
    """Return an icon matching the appliance category."""

    return APPLIANCE_ICONS.get(
        category,
        "🔌",
    )


def get_nearest_task(
    appliance_id: int,
    tasks: list[dict],
) -> dict | None:
    """Return the nearest incomplete task for one appliance."""

    appliance_tasks = [
        task
        for task in tasks
        if int(task["appliance_id"]) == appliance_id
        and task["status"] != "Completed"
    ]

    if not appliance_tasks:
        return None

    return appliance_tasks[0]


def get_due_message(
    task: dict | None,
) -> str:
    """Create a friendly task due-date message."""

    if task is None:
        return "No care reminders yet"

    task_name = str(
        task.get("task_name")
        or "Care reminder"
    )

    due_value = task.get(
        "next_due_date"
    )

    if not due_value:
        return task_name

    try:
        due_date = date.fromisoformat(
            str(due_value)
        )

        difference = (
            due_date - date.today()
        ).days

    except ValueError:
        return task_name

    if difference < 0:
        overdue_days = abs(
            difference
        )

        day_word = (
            "day"
            if overdue_days == 1
            else "days"
        )

        return (
            f"{task_name} is "
            f"{overdue_days} "
            f"{day_word} overdue"
        )

    if difference == 0:
        return (
            f"{task_name} is due today"
        )

    if difference == 1:
        return (
            f"{task_name} is due tomorrow"
        )

    return (
        f"{task_name} is due on "
        f"{due_date.strftime('%d %b %Y')}"
    )


def open_ai_for_appliance(
    appliance_id: int,
) -> None:
    """
    Open the AI Assistant with the clicked appliance selected.

    The AI Assistant already reads preferred_appliance_id.
    """

    st.session_state[
        "preferred_appliance_id"
    ] = int(appliance_id)

    # Keep the second key too for compatibility with any older
    # AI Assistant selection logic.
    st.session_state[
        "selected_appliance_id"
    ] = int(appliance_id)

    st.switch_page(
        "pages/3_🤖_AI_Assistant.py"
    )


def open_care_for_appliance(
    appliance_id: int,
) -> None:
    """Open Maintenance filtered to the clicked appliance."""

    st.session_state[
        "selected_maintenance_appliance_id"
    ] = int(appliance_id)

    st.switch_page(
        "pages/4_📅_Maintenance.py"
    )


# =========================================================
# Appliance card
# =========================================================

def render_appliance_card(
    appliance: dict,
    task: dict | None,
) -> None:
    """Display one appliance card and its direct actions."""

    appliance_id = int(
        appliance["id"]
    )

    category = (
        appliance.get("category")
        or "Other"
    )

    icon = get_appliance_icon(
        category
    )

    if (
        task
        and task.get("status")
        == "Overdue"
    ):
        pill = render_status_pill(
            "Needs attention",
            "danger",
        )

    elif task:
        pill = render_status_pill(
            "Care coming up",
            "warning",
        )

    else:
        pill = render_status_pill(
            "Looking good",
            "good",
        )

    manual_ready = bool(
        appliance.get(
            "manual_processed"
        )
    )

    manual_text = (
        "AI manual ready"
        if manual_ready
        else "Add a manual for smarter help"
    )

    appliance_name = escape(
        str(
            appliance.get(
                "appliance_name"
            )
            or "Appliance"
        )
    )

    brand = escape(
        str(
            appliance.get("brand")
            or ""
        )
    )

    model = escape(
        str(
            appliance.get(
                "model_number"
            )
            or ""
        )
    )

    appliance_details = (
        f"{brand} {model}"
    ).strip()

    due_message = escape(
        get_due_message(task)
    )

    # Keep the HTML compact. Indented multiline HTML can be
    # interpreted by Markdown as a code block in Streamlit.
    card_html = (
        '<div class="hg-card">'
        f'<div class="hg-card-icon">{icon}</div>'
        f'<div class="hg-card-title">{appliance_name}</div>'
        f'<div class="hg-card-subtitle">{appliance_details}</div>'
        f'<div>{pill}</div>'
        f'<div class="hg-card-message">{due_message}</div>'
        f'<div class="hg-card-note">{escape(manual_text)}</div>'
        '</div>'
    )

    st.markdown(
        card_html,
        unsafe_allow_html=True,
    )

    # Add breathing room so the action buttons do not touch
    # or visually overlap the appliance card.
    st.markdown(
        '<div style="height: 0.75rem;"></div>',
        unsafe_allow_html=True,
    )

    action_1, action_2 = st.columns(
        2,
        gap="medium",
    )

    with action_1:
        if st.button(
            "🤖 Ask AI",
            key=(
                "dashboard_ask_ai_"
                f"{appliance_id}"
            ),
            use_container_width=True,
        ):
            open_ai_for_appliance(
                appliance_id
            )

    with action_2:
        if st.button(
            "📅 Care reminders",
            key=(
                "dashboard_care_"
                f"{appliance_id}"
            ),
            use_container_width=True,
        ):
            open_care_for_appliance(
                appliance_id
            )


# =========================================================
# Main dashboard
# =========================================================

def main() -> None:
    """Run the HomeGuardian dashboard."""

    try:
        initialize_database()

        appliances = (
            get_all_appliances()
        )

        dashboard_statistics = (
            get_dashboard_statistics()
        )

        maintenance_statistics = (
            get_maintenance_statistics()
        )

        maintenance_tasks = (
            get_maintenance_tasks()
        )

    except Exception as error:
        st.error(
            "HomeGuardian could not load "
            "your home information. "
            f"Details: {error}"
        )

        st.stop()

    render_hero(
        title=(
            "Your home is under "
            "control."
        ),
        subtitle=(
            "Keep appliances healthy, "
            "solve problems using their "
            "manuals, and never miss "
            "important care."
        ),
        eyebrow="Smart home care",
    )

    total_appliances = int(
        dashboard_statistics.get(
            "total_appliances",
            0,
        )
    )

    pending_tasks = int(
        maintenance_statistics.get(
            "pending_tasks",
            0,
        )
    )

    overdue_tasks = int(
        maintenance_statistics.get(
            "overdue_tasks",
            0,
        )
    )

    metric_1, metric_2, metric_3 = (
        st.columns(3)
    )

    with metric_1:
        st.metric(
            "My appliances",
            total_appliances,
        )

    with metric_2:
        st.metric(
            "Care reminders",
            pending_tasks,
        )

    with metric_3:
        st.metric(
            "Needs attention",
            overdue_tasks,
        )

    st.write("")

    if overdue_tasks > 0:
        st.warning(
            "Some appliances need your "
            "attention."
        )
    else:
        st.success(
            "Everything looks good. "
            "No appliances need urgent "
            "attention."
        )

    st.write("")
    st.subheader(
        "What would you like to do?"
    )

    action_1, action_2, action_3 = (
        st.columns(3)
    )

    with action_1:
        if st.button(
            "➕ Add an appliance",
            type="primary",
            use_container_width=True,
            key="dashboard_add_appliance",
        ):
            st.switch_page(
                "pages/2_➕_Add_Appliance.py"
            )

    with action_2:
        if st.button(
            "🤖 Ask HomeGuardian",
            use_container_width=True,
            key="dashboard_open_ai",
        ):
            st.switch_page(
                "pages/3_🤖_AI_Assistant.py"
            )

    with action_3:
        if st.button(
            "📅 View care reminders",
            use_container_width=True,
            key="dashboard_open_care",
        ):
            st.switch_page(
                "pages/4_📅_Maintenance.py"
            )

    st.write("")
    st.subheader(
        "My appliances"
    )

    if not appliances:
        with st.container(
            border=True
        ):
            st.markdown(
                "### Add your first "
                "appliance ✨"
            )

            st.write(
                "Upload its manual and "
                "HomeGuardian will help "
                "you understand, maintain, "
                "and troubleshoot it."
            )

            if st.button(
                "Add my first appliance",
                type="primary",
                use_container_width=True,
                key=(
                    "dashboard_first_"
                    "appliance"
                ),
            ):
                st.switch_page(
                    "pages/"
                    "2_➕_Add_Appliance.py"
                )

        return

    appliance_columns = (
        st.columns(2)
    )

    for index, appliance in enumerate(
        appliances
    ):
        appliance_id = int(
            appliance["id"]
        )

        nearest_task = (
            get_nearest_task(
                appliance_id=appliance_id,
                tasks=maintenance_tasks,
            )
        )

        with appliance_columns[
            index % 2
        ]:
            render_appliance_card(
                appliance=appliance,
                task=nearest_task,
            )

            st.write("")

    st.write("")

    with st.container(
        border=True
    ):
        text_column, button_column = (
            st.columns(
                [3, 1]
            )
        )

        with text_column:
            st.subheader(
                "Something wrong with "
                "an appliance?"
            )

            st.write(
                "Describe the problem and "
                "HomeGuardian will search "
                "the official manual for "
                "a safe answer."
            )

        with button_column:
            st.write("")

            if st.button(
                "Ask for help 🤖",
                type="primary",
                use_container_width=True,
                key=(
                    "dashboard_bottom_"
                    "ask_help"
                ),
            ):
                st.switch_page(
                    "pages/"
                    "3_🤖_AI_Assistant.py"
                )


if __name__ == "__main__":
    main()