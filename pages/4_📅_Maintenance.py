from __future__ import annotations

from datetime import date, timedelta
from html import escape

import streamlit as st

from core.database import (
    add_maintenance_task,
    complete_maintenance_task,
    delete_maintenance_task,
    get_all_appliances,
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
    page_title="Care Reminders | HomeGuardian AI",
    page_icon="📅",
    layout="wide",
)

apply_app_style()


# =========================================================
# Page styling
# =========================================================

st.markdown(
    """
    <style>
    .hg-care-shell {
        max-width: 1040px;
        margin: 0 auto;
    }

    .hg-care-intro {
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

    .hg-care-section-label {
        margin-top: 1.2rem;
        margin-bottom: 0.55rem;
        color: var(--hg-muted);
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .hg-task-heading {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.75rem;
    }

    .hg-task-title {
        color: var(--hg-text);
        font-size: 1.15rem;
        font-weight: 800;
        line-height: 1.3;
    }

    .hg-task-appliance {
        margin-top: 0.22rem;
        color: var(--hg-muted);
        font-size: 0.86rem;
    }

    .hg-task-description {
        margin-top: 0.75rem;
        color: var(--hg-text);
        line-height: 1.58;
    }

    .hg-task-meta {
        margin-top: 0.8rem;
        color: var(--hg-muted);
        font-size: 0.82rem;
    }

    .hg-task-spacer {
        height: 0.35rem;
    }

    .hg-empty-care {
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

    .hg-empty-care-icon {
        margin-bottom: 0.7rem;
        font-size: 2.2rem;
    }

    .hg-empty-care-title {
        color: var(--hg-text);
        font-size: 1.1rem;
        font-weight: 800;
    }

    .hg-empty-care-text {
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
        .hg-task-heading {
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

REPEAT_OPTIONS = {
    "Every week": 7,
    "Every month": 30,
    "Every 3 months": 90,
    "Every 6 months": 180,
    "Every year": 365,
    "Custom": None,
}


# =========================================================
# Helpers
# =========================================================

def clean_text(value: object) -> str:
    """Return clean text."""

    return str(value or "").strip()


def get_appliance_icon(category: str) -> str:
    """Return the icon for an appliance category."""

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


def selected_appliance_default(
    appliances: list[dict],
) -> int:
    """Resolve an appliance selected from another page."""

    valid_ids = {
        int(appliance["id"])
        for appliance in appliances
    }

    preferred = st.session_state.get(
        "selected_maintenance_appliance_id"
    )

    try:
        preferred_id = int(preferred)
    except (TypeError, ValueError):
        preferred_id = None

    if preferred_id in valid_ids:
        return preferred_id

    return 0


def parse_date(value: object) -> date | None:
    """Convert an ISO date to a date object."""

    if not value:
        return None

    try:
        return date.fromisoformat(
            str(value)
        )
    except ValueError:
        return None


def due_status(task: dict) -> tuple[str, str]:
    """Return friendly due text and badge style."""

    status = clean_text(
        task.get("status")
    )

    if status == "Completed":
        completed_value = parse_date(
            task.get("last_completed_date")
        )

        if completed_value:
            return (
                f"Done {completed_value.strftime('%d %b %Y')}",
                "good",
            )

        return "Completed", "good"

    due_date = parse_date(
        task.get("next_due_date")
    )

    if due_date is None:
        return "No due date", "warning"

    difference = (
        due_date - date.today()
    ).days

    if difference < 0:
        overdue_days = abs(difference)

        if overdue_days == 1:
            return "1 day overdue", "danger"

        return (
            f"{overdue_days} days overdue",
            "danger",
        )

    if difference == 0:
        return "Due today", "danger"

    if difference == 1:
        return "Due tomorrow", "warning"

    if difference <= 30:
        return (
            f"Due in {difference} days",
            "warning",
        )

    return (
        f"Due {due_date.strftime('%d %b %Y')}",
        "warning",
    )


def recurrence_text(task: dict) -> str:
    """Return friendly recurrence information."""

    frequency = task.get(
        "frequency_days"
    )

    due_date = parse_date(
        task.get("next_due_date")
    )

    parts: list[str] = []

    try:
        frequency_days = int(frequency)
    except (TypeError, ValueError):
        frequency_days = 0

    if frequency_days > 0:
        if frequency_days == 7:
            parts.append("Repeats weekly")
        elif frequency_days == 30:
            parts.append("Repeats monthly")
        elif frequency_days == 90:
            parts.append("Repeats every 3 months")
        elif frequency_days == 180:
            parts.append("Repeats every 6 months")
        elif frequency_days == 365:
            parts.append("Repeats yearly")
        else:
            parts.append(
                f"Repeats every {frequency_days} days"
            )
    else:
        parts.append("One-time reminder")

    if due_date:
        parts.append(
            f"Next: {due_date.strftime('%d %b %Y')}"
        )

    return " · ".join(parts)


def task_matches_filter(
    task: dict,
    selected_status: str,
) -> bool:
    """Check whether a task belongs to a selected filter."""

    status = clean_text(
        task.get("status")
    )

    if selected_status == "All":
        return True

    if selected_status == "Upcoming":
        return status == "Pending"

    if selected_status == "Overdue":
        return status == "Overdue"

    if selected_status == "Completed":
        return status == "Completed"

    return True


# =========================================================
# Task cards
# =========================================================

def render_task_card(task: dict) -> None:
    """Render one reminder as a clean card."""

    task_id = int(
        task["id"]
    )

    title = escape(
        clean_text(
            task.get("task_name")
        )
        or "Care reminder"
    )

    appliance_name = escape(
        clean_text(
            task.get("appliance_name")
        )
        or "Appliance"
    )

    category = clean_text(
        task.get("category")
    ) or "Other"

    brand = escape(
        clean_text(
            task.get("brand")
        )
    )

    model = escape(
        clean_text(
            task.get("model_number")
        )
    )

    details = " ".join(
        part
        for part in [brand, model]
        if part
    )

    appliance_line = appliance_name

    if details:
        appliance_line += f" · {details}"

    description = escape(
        clean_text(
            task.get("description")
        )
    )

    badge_text, badge_style = due_status(
        task
    )

    badge = render_status_pill(
        badge_text,
        badge_style,
    )

    icon = get_appliance_icon(
        category
    )

    heading_html = (
        '<div class="hg-task-heading">'
        '<div>'
        f'<div class="hg-task-title">{icon} {title}</div>'
        f'<div class="hg-task-appliance">{appliance_line}</div>'
        '</div>'
        f'<div>{badge}</div>'
        '</div>'
    )

    with st.container(border=True):
        st.markdown(
            heading_html,
            unsafe_allow_html=True,
        )

        if description:
            st.markdown(
                (
                    '<div class="hg-task-description">'
                    f"{description}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        st.markdown(
            (
                '<div class="hg-task-meta">'
                f"{escape(recurrence_text(task))}"
                "</div>"
                '<div class="hg-task-spacer"></div>'
            ),
            unsafe_allow_html=True,
        )

        status = clean_text(
            task.get("status")
        )

        if status != "Completed":
            action_column, more_column = st.columns(
                [3, 1]
            )

            with action_column:
                if st.button(
                    "✅ Mark as done",
                    type="primary",
                    use_container_width=True,
                    key=f"complete_task_{task_id}",
                ):
                    try:
                        complete_maintenance_task(
                            task_id=task_id,
                            completed_date=date.today(),
                        )

                        st.toast(
                            "Reminder completed.",
                            icon="✅",
                        )

                        st.rerun()

                    except Exception:
                        st.error(
                            "HomeGuardian could not complete this reminder."
                        )

            with more_column:
                with st.expander(
                    "More",
                    expanded=False,
                ):
                    st.caption(
                        "Delete this reminder only when you no longer need it."
                    )

                    if st.button(
                        "Delete reminder",
                        key=f"delete_task_{task_id}",
                        use_container_width=True,
                    ):
                        try:
                            delete_maintenance_task(
                                task_id
                            )

                            st.toast(
                                "Reminder deleted.",
                                icon="🗑️",
                            )

                            st.rerun()

                        except Exception:
                            st.error(
                                "HomeGuardian could not delete this reminder."
                            )

        else:
            action_column, delete_column = st.columns(
                [3, 1]
            )

            with action_column:
                st.success(
                    "This reminder is completed."
                )

            with delete_column:
                if st.button(
                    "Delete",
                    key=f"delete_completed_{task_id}",
                    use_container_width=True,
                ):
                    try:
                        delete_maintenance_task(
                            task_id
                        )

                        st.rerun()

                    except Exception:
                        st.error(
                            "HomeGuardian could not delete this reminder."
                        )


def render_empty_tasks(
    selected_status: str,
) -> None:
    """Render a friendly empty state."""

    if selected_status == "Overdue":
        icon = "✨"
        title = "Nothing is overdue"
        text = "You are all caught up. No appliance care is late."

    elif selected_status == "Completed":
        icon = "✅"
        title = "No completed reminders yet"
        text = "Completed care tasks will appear here."

    elif selected_status == "Upcoming":
        icon = "📅"
        title = "No upcoming care"
        text = "Add a reminder when you want HomeGuardian to help you remember appliance care."

    else:
        icon = "🏠"
        title = "No care reminders yet"
        text = "Add a simple reminder for cleaning, filter changes, inspections, or other appliance care."

    st.markdown(
        (
            '<div class="hg-empty-care">'
            f'<div class="hg-empty-care-icon">{icon}</div>'
            f'<div class="hg-empty-care-title">{title}</div>'
            f'<div class="hg-empty-care-text">{text}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


# =========================================================
# Reminder list
# =========================================================

def render_reminders(
    appliances: list[dict],
) -> None:
    """Render reminder filters, metrics, and cards."""

    appliance_by_id = {
        int(appliance["id"]): appliance
        for appliance in appliances
    }

    appliance_options: list[int | str] = [
        "All"
    ] + list(appliance_by_id.keys())

    preferred_id = selected_appliance_default(
        appliances
    )

    if preferred_id:
        default_index = appliance_options.index(
            preferred_id
        )
    else:
        default_index = 0

    selected_appliance = st.selectbox(
        "Show reminders for",
        options=appliance_options,
        index=default_index,
        format_func=lambda value: (
            "All appliances"
            if value == "All"
            else appliance_label(
                appliance_by_id[int(value)]
            )
        ),
    )

    appliance_id = (
        None
        if selected_appliance == "All"
        else int(selected_appliance)
    )

    tasks = get_maintenance_tasks(
        appliance_id=appliance_id
    )

    statistics = get_maintenance_statistics(
        appliance_id=appliance_id
    )

    upcoming = int(
        statistics.get(
            "pending_tasks",
            0,
        )
    )

    overdue = int(
        statistics.get(
            "overdue_tasks",
            0,
        )
    )

    completed = int(
        statistics.get(
            "completed_tasks",
            0,
        )
    )

    metric_1, metric_2, metric_3 = st.columns(
        3
    )

    with metric_1:
        st.metric(
            "Upcoming",
            upcoming,
        )

    with metric_2:
        st.metric(
            "Overdue",
            overdue,
        )

    with metric_3:
        st.metric(
            "Completed",
            completed,
        )

    st.markdown(
        '<div class="hg-care-section-label">Show</div>',
        unsafe_allow_html=True,
    )

    selected_status = st.radio(
        "Reminder status",
        options=[
            "All",
            "Upcoming",
            "Overdue",
            "Completed",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    filtered_tasks = [
        task
        for task in tasks
        if task_matches_filter(
            task,
            selected_status,
        )
    ]

    st.write("")

    if not filtered_tasks:
        render_empty_tasks(
            selected_status
        )
        return

    for task in filtered_tasks:
        render_task_card(
            task
        )
        st.write("")


# =========================================================
# Add reminder
# =========================================================

def render_add_reminder(
    appliances: list[dict],
) -> None:
    """Render a minimal reminder form."""

    if not appliances:
        with st.container(border=True):
            st.markdown(
                "### Add an appliance first"
            )

            st.write(
                "Care reminders belong to an appliance. "
                "Upload a manual to add your first appliance."
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
            "Keep it simple: choose the appliance, write the care task, "
            "and decide when HomeGuardian should remind you."
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

    preferred_id = selected_appliance_default(
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
        key="new_reminder_appliance",
    )

    task_name = st.text_input(
        "What should be done?",
        placeholder=(
            "Example: Clean filter"
        ),
        key="new_reminder_name",
    )

    due_date = st.date_input(
        "Remind me on",
        value=date.today() + timedelta(
            days=30
        ),
        min_value=date.today(),
        key="new_reminder_due",
    )

    repeats = st.toggle(
        "Repeat this reminder",
        value=False,
        key="new_reminder_repeats",
    )

    frequency_days: int | None = None

    if repeats:
        repeat_choice = st.selectbox(
            "How often?",
            options=list(
                REPEAT_OPTIONS.keys()
            ),
            key="new_reminder_repeat_choice",
        )

        frequency_days = REPEAT_OPTIONS[
            repeat_choice
        ]

        if repeat_choice == "Custom":
            frequency_days = int(
                st.number_input(
                    "Repeat every how many days?",
                    min_value=1,
                    max_value=3650,
                    value=30,
                    step=1,
                    key="new_reminder_custom_days",
                )
            )

    with st.expander(
        "Add instructions — optional",
        expanded=False,
    ):
        description = st.text_area(
            "Instructions",
            placeholder=(
                "Example: Turn off the appliance before removing the filter."
            ),
            height=100,
            key="new_reminder_description",
        )

    if st.button(
        "Add reminder",
        type="primary",
        use_container_width=True,
        key="save_new_reminder",
    ):
        cleaned_name = task_name.strip()

        if not cleaned_name:
            st.warning(
                "Write what needs to be done."
            )
            return

        try:
            add_maintenance_task(
                appliance_id=int(
                    selected_id
                ),
                task_name=cleaned_name,
                description=(
                    description.strip()
                    if description.strip()
                    else None
                ),
                frequency_days=frequency_days,
                next_due_date=due_date,
                status="Pending",
            )

            st.session_state[
                "maintenance_view"
            ] = "My reminders"

            st.toast(
                "Reminder added.",
                icon="✅",
            )

            st.rerun()

        except Exception:
            st.error(
                "HomeGuardian could not add this reminder. "
                "Please check the information and try again."
            )


# =========================================================
# Main page
# =========================================================

def main() -> None:
    """Run the maintenance page."""

    try:
        initialize_database()

        appliances = get_all_appliances()

    except Exception:
        st.error(
            "HomeGuardian could not load care reminders. "
            "Please restart the app and try again."
        )
        st.stop()

    render_hero(
        title="Care reminders.",
        subtitle=(
            "Simple reminders that help your appliances last longer "
            "and work better."
        ),
        eyebrow="Easy home care",
    )

    st.markdown(
        '<div class="hg-care-shell">',
        unsafe_allow_html=True,
    )

    if "maintenance_view" not in st.session_state:
        st.session_state[
            "maintenance_view"
        ] = "My reminders"

    view = st.radio(
        "Maintenance page",
        options=[
            "My reminders",
            "Add reminder",
        ],
        horizontal=True,
        key="maintenance_view",
        label_visibility="collapsed",
    )

    st.write("")

    if view == "My reminders":
        render_reminders(
            appliances
        )
    else:
        render_add_reminder(
            appliances
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()