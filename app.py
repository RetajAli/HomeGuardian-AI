import logging
import traceback
from pathlib import Path

import streamlit as st


# =========================================================
# Application configuration
# =========================================================

st.set_page_config(
    page_title="HomeGuardian AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Import after set_page_config so Streamlit initializes first.
from core.ui import apply_app_style  # noqa: E402


BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "data"
ERROR_LOG = LOG_DIR / "homeguardian_errors.log"


# =========================================================
# Error logging
# =========================================================

def configure_logging() -> None:
    """Save unexpected errors without showing raw crashes to users."""

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger = logging.getLogger(
        "homeguardian"
    )

    if logger.handlers:
        return

    handler = logging.FileHandler(
        ERROR_LOG,
        encoding="utf-8",
    )

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
    )

    logger.setLevel(
        logging.ERROR
    )

    logger.addHandler(
        handler
    )


def render_page_error(
    error: Exception,
) -> None:
    """Show a friendly recovery screen instead of a traceback."""

    logging.getLogger(
        "homeguardian"
    ).error(
        "Page failed to load:\n%s",
        traceback.format_exc(),
    )

    st.error(
        "This page could not finish loading. "
        "Your saved information is safe."
    )

    st.caption(
        "Try opening the page again. If the problem continues, "
        "restart Streamlit."
    )

    retry_column, home_column = st.columns(
        2
    )

    with retry_column:
        if st.button(
            "Try again",
            type="primary",
            use_container_width=True,
            key="global_retry_page",
        ):
            st.rerun()

    with home_column:
        if st.button(
            "Return to Dashboard",
            use_container_width=True,
            key="global_return_home",
        ):
            st.switch_page(
                "pages/1_🏠_Dashboard.py"
            )

    with st.expander(
        "Technical details",
        expanded=False,
    ):
        st.code(
            (
                f"{type(error).__name__}: "
                f"{error}"
            ),
            language="text",
        )


# =========================================================
# Navigation
# =========================================================

def build_navigation():
    """Create the HomeGuardian page navigation."""

    return {
        "app": [
            st.Page(
                "pages/1_🏠_Dashboard.py",
                title="Dashboard",
                icon="🏠",
                default=True,
            ),
            st.Page(
                "pages/2_➕_Add_Appliance.py",
                title="Add Appliance",
                icon="➕",
            ),
            st.Page(
                "pages/3_🤖_AI_Assistant.py",
                title="AI Assistant",
                icon="🤖",
            ),
            st.Page(
                "pages/4_📅_Maintenance.py",
                title="Maintenance",
                icon="📅",
            ),
            st.Page(
                "pages/5_🔧_Repair_History.py",
                title="Repair History",
                icon="🔧",
            ),
        ]
    }


# =========================================================
# Main application
# =========================================================

def main() -> None:
    """Run the stable HomeGuardian application shell."""

    configure_logging()

    # Render the dark application shell before loading a page.
    # Individual pages may also call apply_app_style(); the guard
    # inside core/ui.py prevents duplicate rendering.
    st.session_state[
        "_hg_shell_ready"
    ] = False

    apply_app_style()

    st.session_state[
        "_hg_shell_ready"
    ] = True

    navigation = build_navigation()

    selected_page = st.navigation(
        navigation,
        position="sidebar",
    )

    try:
        selected_page.run()

    except Exception as error:
        render_page_error(
            error
        )


if __name__ == "__main__":
    main()