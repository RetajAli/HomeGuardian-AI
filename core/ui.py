from __future__ import annotations

import base64
from html import escape
from pathlib import Path

import streamlit as st

from core.cosmic_theme_toggle import cosmic_theme_toggle


APP_NAME = "HomeGuardian AI"
APP_TAGLINE = "Smarter care for every appliance"

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_WIDE_PATH = ASSETS_DIR / "homeguardian_logo.svg"
LOGO_ICON_PATH = ASSETS_DIR / "homeguardian_icon.svg"


LOGO_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
<defs>
  <linearGradient id="g" x1="28" y1="22" x2="224" y2="232" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#168CFF"/>
    <stop offset="0.55" stop-color="#00C7D9"/>
    <stop offset="1" stop-color="#32E0A1"/>
  </linearGradient>
  <filter id="s" x="-20%" y="-20%" width="140%" height="150%">
    <feDropShadow dx="0" dy="9" stdDeviation="9" flood-color="#076AA8" flood-opacity="0.30"/>
  </filter>
</defs>
<path d="M128 18L222 53V119C222 178 184 222 128 239C72 222 34 178 34 119V53L128 18Z" fill="url(#g)" filter="url(#s)"/>
<path d="M66 126L128 75L190 126" fill="none" stroke="#FFFFFF" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M82 120V174C82 186 92 196 104 196H152C164 196 174 186 174 174V120" fill="none" stroke="#FFFFFF" stroke-width="13" stroke-linecap="round"/>
<rect x="116" y="146" width="24" height="50" rx="8" fill="#FFFFFF"/>
<path d="M100 56C117 42 139 42 156 56" fill="none" stroke="#E9FBFF" stroke-width="8" stroke-linecap="round"/>
<path d="M111 68C121 60 135 60 145 68" fill="none" stroke="#E9FBFF" stroke-width="7" stroke-linecap="round"/>
<circle cx="128" cy="78" r="5" fill="#FFF3B0"/>
<path d="M195 58L199 70L211 74L199 78L195 90L191 78L179 74L191 70Z" fill="#FFFFFF" opacity="0.95"/>
</svg>"""


LOGO_WIDE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 170">
<defs>
  <linearGradient id="g" x1="14" y1="12" x2="150" y2="160" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#168CFF"/>
    <stop offset="0.55" stop-color="#00C7D9"/>
    <stop offset="1" stop-color="#32E0A1"/>
  </linearGradient>
  <linearGradient id="word" x1="170" y1="50" x2="585" y2="120" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#F7FBFF"/>
    <stop offset="0.45" stop-color="#DFF7FF"/>
    <stop offset="0.72" stop-color="#28BFFF"/>
    <stop offset="1" stop-color="#00D0C7"/>
  </linearGradient>
  <filter id="s" x="-20%" y="-20%" width="140%" height="150%">
    <feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#076AA8" flood-opacity="0.28"/>
  </filter>
</defs>
<g transform="translate(6 5)">
  <path d="M78 3L148 29V79C148 123 120 155 78 168C36 155 8 123 8 79V29L78 3Z" fill="url(#g)" filter="url(#s)"/>
  <path d="M33 84L78 47L123 84" fill="none" stroke="#FFFFFF" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M45 79V119C45 128 52 135 61 135H95C104 135 111 128 111 119V79" fill="none" stroke="#FFFFFF" stroke-width="9" stroke-linecap="round"/>
  <rect x="70" y="98" width="17" height="37" rx="5" fill="#FFFFFF"/>
  <path d="M58 32C70 22 86 22 98 32" fill="none" stroke="#E9FBFF" stroke-width="6" stroke-linecap="round"/>
  <path d="M66 42C73 37 83 37 90 42" fill="none" stroke="#E9FBFF" stroke-width="5" stroke-linecap="round"/>
  <circle cx="78" cy="49" r="4" fill="#FFF3B0"/>
</g>
<text x="170" y="93" fill="url(#word)" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="55" font-weight="800" letter-spacing="-2">HomeGuardian</text>
<rect x="173" y="108" width="174" height="34" rx="17" fill="#168CFF" fill-opacity="0.14" stroke="#22BFFF" stroke-opacity="0.34"/>
<text x="191" y="132" fill="#63D9FF" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="20" font-weight="800" letter-spacing="3">AI HOME CARE</text>
</svg>"""


def _ensure_logo_files() -> None:
    """Create the logo files automatically inside the project."""

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    if not LOGO_ICON_PATH.exists() or LOGO_ICON_PATH.read_text(encoding="utf-8") != LOGO_ICON_SVG:
        LOGO_ICON_PATH.write_text(LOGO_ICON_SVG, encoding="utf-8")

    if not LOGO_WIDE_PATH.exists() or LOGO_WIDE_PATH.read_text(encoding="utf-8") != LOGO_WIDE_SVG:
        LOGO_WIDE_PATH.write_text(LOGO_WIDE_SVG, encoding="utf-8")


def _svg_data_uri(svg: str) -> str:
    """Convert SVG markup into an embeddable image URL."""

    encoded = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"


def render_app_logo() -> None:
    """Display a large HomeGuardian logo at the top of the sidebar."""

    logo_uri = _svg_data_uri(LOGO_WIDE_SVG)

    logo_html = (
        '<div class="hg-floating-sidebar-logo">'
        f'<img src="{logo_uri}" alt="{APP_NAME} logo">'
        '</div>'
    )

    with st.sidebar:
        st.markdown(
            logo_html,
            unsafe_allow_html=True,
        )

# =========================================================
# Theme
# =========================================================


def render_theme_control() -> bool:
    """Render the cosmic theme switch at the top-right of the app."""

    with st.container(
        key="hg_theme_float",
    ):
        dark_mode = cosmic_theme_toggle(
            key="homeguardian_cosmic_theme",
            default_dark=True,
        )

    return dark_mode



def get_theme() -> dict[str, str]:
    """Return the single stable HomeGuardian dark theme."""

    return {
        "background": "#07111F",
        "sidebar": "#081321",
        "surface": "#10233A",
        "surface_second": "#0C1D31",
        "surface_soft": "#0E2035",
        "text": "#F4F8FD",
        "muted": "#9DAFC3",
        "border": "rgba(255,255,255,0.09)",
        "input": "#0D2035",
        "accent": "#168CFF",
        "accent_second": "#00BFD2",
        "accent_soft": "rgba(24,140,255,0.12)",
        "shadow": "rgba(0,0,0,0.22)",
        "success": "#55DCA3",
        "warning": "#FFC66D",
        "danger": "#FF858F",
    }


# =========================================================
# Global styling
# =========================================================


def apply_app_style() -> None:
    """Apply the shared HomeGuardian design once in the current app run."""

    # app.py renders the shared shell before the selected page. Existing page
    # files may still call this function, so skip the duplicate safely.
    if st.session_state.get("_hg_shell_ready", False):
        return

    theme = get_theme()
    sidebar_logo_uri = _svg_data_uri(LOGO_WIDE_SVG)

    css = f"""
<style>
:root {{
    --hg-background: {theme['background']};
    --hg-sidebar: {theme['sidebar']};
    --hg-surface: {theme['surface']};
    --hg-surface-second: {theme['surface_second']};
    --hg-surface-soft: {theme['surface_soft']};
    --hg-text: {theme['text']};
    --hg-muted: {theme['muted']};
    --hg-border: {theme['border']};
    --hg-input: {theme['input']};
    --hg-accent: {theme['accent']};
    --hg-accent-second: {theme['accent_second']};
    --hg-accent-soft: {theme['accent_soft']};
    --hg-shadow: {theme['shadow']};
    --hg-success: {theme['success']};
    --hg-warning: {theme['warning']};
    --hg-danger: {theme['danger']};
    --hg-sidebar-logo: url("{sidebar_logo_uri}");
}}

html[data-hg-theme="light"] {{
    --hg-background: #F4F7FB;
    --hg-sidebar: #F7FAFE;
    --hg-surface: #FFFFFF;
    --hg-surface-second: #F7FBFF;
    --hg-surface-soft: #FFFFFF;
    --hg-text: #142235;
    --hg-muted: #64768A;
    --hg-border: rgba(25, 55, 85, 0.13);
    --hg-input: #FFFFFF;
    --hg-accent: #087EE6;
    --hg-accent-second: #00A9BD;
    --hg-accent-soft: rgba(8, 126, 230, 0.09);
    --hg-shadow: rgba(25, 55, 85, 0.10);
    --hg-success: #14855C;
    --hg-warning: #AF6800;
    --hg-danger: #C63F4D;
}}

html, body, [class*="css"] {{
    font-family: Inter, "Segoe UI", Arial, sans-serif;
}}

html {{
    color-scheme: dark;
    background: var(--hg-background) !important;
}}

html[data-hg-theme="light"] {{
    color-scheme: light;
}}

body,
[data-testid="stAppViewContainer"] {{
    background: var(--hg-background) !important;
}}

.stApp {{
    color: var(--hg-text);
    background: var(--hg-background);
}}

.block-container {{
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}}

p, label, li, span, .stMarkdown, [data-testid="stWidgetLabel"] {{
    color: var(--hg-text);
}}

small, [data-testid="stCaptionContainer"] {{
    color: var(--hg-muted) !important;
}}

section[data-testid="stSidebar"] {{
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(
            circle at 18% 2%,
            rgba(22, 140, 255, 0.18),
            transparent 24%
        ),
        linear-gradient(
            180deg,
            color-mix(in srgb, var(--hg-sidebar) 92%, #102A47 8%) 0%,
            var(--hg-sidebar) 48%,
            color-mix(in srgb, var(--hg-sidebar) 94%, #020812 6%) 100%
        );
    border-right: 1px solid var(--hg-border);
    box-shadow:
        inset -1px 0 0 rgba(255, 255, 255, 0.025),
        18px 0 55px rgba(0, 0, 0, 0.08);
}}

section[data-testid="stSidebar"]::before {{
    content: "";
    position: absolute;
    top: -120px;
    left: -100px;
    width: 290px;
    height: 290px;
    border-radius: 50%;
    background: rgba(0, 199, 217, 0.08);
    filter: blur(12px);
    pointer-events: none;
}}

section[data-testid="stSidebar"] > div {{
    position: relative;
    z-index: 1;
    padding-top: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
    padding-bottom: 1.25rem;
}}

/* Brand panel is part of the navigation flow, so it never overlaps controls. */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {{
    padding-top: 0 !important;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarNav"]::before {{
    content: "";
    display: block;
    box-sizing: border-box;
    width: 100%;
    height: 94px;
    margin: 0.15rem 0 1.15rem;
    background-image:
        var(--hg-sidebar-logo),
        linear-gradient(
            135deg,
            rgba(16, 48, 78, 0.96),
            rgba(7, 25, 44, 0.96)
        );
    background-repeat: no-repeat, no-repeat;
    background-position: center, center;
    background-size: calc(100% - 28px) auto, cover;
    border: 1px solid rgba(116, 215, 255, 0.18);
    border-radius: 22px;
    box-shadow:
        0 15px 34px rgba(0, 0, 0, 0.16),
        inset 0 1px 0 rgba(255, 255, 255, 0.07);
}}

/* Hide the old floating implementation if a cached page still contains it. */
.hg-floating-sidebar-logo {{
    display: none !important;
}}

/* Navigation group label. */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] > div:first-child {{
    margin-bottom: 0.45rem;
    color: var(--hg-muted);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}}

/* Navigation items. */
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {{
    min-height: 50px;
    margin: 0.28rem 0;
    padding: 0.15rem 0.72rem;
    border: 1px solid transparent;
    border-radius: 15px;
    transition:
        transform 180ms ease,
        background 180ms ease,
        border-color 180ms ease,
        box-shadow 180ms ease;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {{
    transform: translateX(4px);
    background: rgba(22, 140, 255, 0.09);
    border-color: rgba(94, 200, 255, 0.12);
}}

section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {{
    background:
        linear-gradient(
            105deg,
            rgba(22, 140, 255, 0.25),
            rgba(0, 191, 210, 0.13)
        );
    border-color: rgba(75, 196, 255, 0.22);
    box-shadow:
        0 10px 28px rgba(3, 99, 175, 0.13),
        inset 3px 0 0 var(--hg-accent-second);
}}

section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span {{
    font-weight: 650;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] span {{
    color: var(--hg-text) !important;
    font-weight: 780;
}}

/* Sidebar separators are subtle gradients instead of harsh rules. */
section[data-testid="stSidebar"] hr {{
    height: 1px;
    margin: 1.25rem 0;
    border: 0;
    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(121, 166, 207, 0.24),
            transparent
        );
}}

.hg-sidebar-footer-space {{
    height: 1.1rem;
}}

/* Glass appearance card. */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {{
    margin-top: 0.25rem;
    padding: 0.1rem;
    overflow: hidden;
    background:
        linear-gradient(
            145deg,
            rgba(255, 255, 255, 0.075),
            rgba(255, 255, 255, 0.025)
        );
    border: 1px solid rgba(126, 199, 255, 0.15) !important;
    border-radius: 20px;
    box-shadow:
        0 14px 34px rgba(0, 0, 0, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(14px);
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    padding: 0.95rem 1rem 0.9rem;
}}

.hg-theme-card-heading {{
    display: flex;
    align-items: center;
    gap: 0.68rem;
    margin-bottom: 0.75rem;
}}

.hg-theme-card-icon {{
    display: flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    color: #FFFFFF;
    background:
        linear-gradient(
            135deg,
            var(--hg-accent),
            var(--hg-accent-second)
        );
    border-radius: 12px;
    box-shadow: 0 8px 20px rgba(0, 141, 224, 0.20);
    font-size: 1rem;
    font-weight: 800;
}}

.hg-theme-card-title {{
    color: var(--hg-text);
    font-size: 0.92rem;
    font-weight: 780;
    letter-spacing: -0.015em;
}}

.hg-theme-card-subtitle {{
    margin-top: 0.08rem;
    color: var(--hg-muted);
    font-size: 0.72rem;
}}

section[data-testid="stSidebar"] div[data-testid="stToggle"] {{
    margin: 0.1rem 0 0.55rem;
    padding: 0.5rem 0.65rem;
    background: rgba(0, 0, 0, 0.09);
    border: 1px solid rgba(126, 199, 255, 0.08);
    border-radius: 13px;
}}

section[data-testid="stSidebar"] div[data-testid="stToggle"] label {{
    font-weight: 680;
}}

section[data-testid="stSidebar"] div[data-testid="stToggle"] [role="switch"] {{
    background: rgba(115, 140, 165, 0.30) !important;
    border: 1px solid rgba(255, 255, 255, 0.13) !important;
    transition: background 180ms ease, box-shadow 180ms ease;
}}

section[data-testid="stSidebar"] div[data-testid="stToggle"] [role="switch"][aria-checked="true"] {{
    background:
        linear-gradient(
            90deg,
            var(--hg-accent),
            var(--hg-accent-second)
        ) !important;
    box-shadow: 0 0 0 3px rgba(22, 140, 255, 0.10);
}}

.hg-fixed-theme-row {{
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin: 0.1rem 0 0.65rem;
    padding: 0.65rem 0.7rem;
    background: rgba(0, 0, 0, 0.10);
    border: 1px solid rgba(126, 199, 255, 0.09);
    border-radius: 13px;
}}

.hg-fixed-theme-moon {{
    font-size: 1rem;
}}

.hg-fixed-theme-title {{
    color: var(--hg-text);
    font-size: 0.82rem;
    font-weight: 720;
}}

.hg-fixed-theme-copy {{
    margin-top: 0.05rem;
    color: var(--hg-muted);
    font-size: 0.68rem;
}}

.hg-fixed-theme-check {{
    margin-left: auto;
    color: #07111F !important;
    background: var(--hg-success);
    width: 20px;
    height: 20px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-size: 0.72rem;
    font-weight: 900;
}}

.hg-theme-status {{
    display: flex;
    align-items: center;
    gap: 0.45rem;
    color: var(--hg-muted);
    font-size: 0.72rem;
}}

.hg-theme-status-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #40DBA0;
    box-shadow: 0 0 0 4px rgba(64, 219, 160, 0.10);
}}

@media (max-width: 700px) {{
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"]::before {{
        height: 84px;
        margin-bottom: 0.9rem;
        background-size: calc(100% - 24px) auto, cover;
        border-radius: 18px;
    }}
}}


h1, h2, h3 {{
    color: var(--hg-text) !important;
}}

h1 {{
    font-size: clamp(2rem, 4vw, 3.15rem) !important;
    font-weight: 800 !important;
    letter-spacing: -0.04em !important;
}}

h2, h3 {{
    letter-spacing: -0.025em !important;
}}

.hg-hero {{
    position: relative;
    overflow: hidden;
    margin-bottom: 1.5rem;
    padding: 2.3rem;
    background: linear-gradient(135deg, var(--hg-surface), var(--hg-surface-second));
    border: 1px solid var(--hg-border);
    border-radius: 25px;
    box-shadow: 0 16px 46px var(--hg-shadow);
}}

.hg-hero::after {{
    content: "";
    position: absolute;
    top: -100px;
    right: -70px;
    width: 250px;
    height: 250px;
    background: radial-gradient(circle, rgba(32,163,255,0.20), transparent 68%);
}}

.hg-hero-logo {{
    position: absolute;
    z-index: 1;
    top: 1.45rem;
    right: 1.55rem;
    width: 78px;
    height: 78px;
}}

.hg-hero-logo img {{
    display: block;
    width: 100%;
    height: 100%;
}}

.hg-eyebrow {{
    position: relative;
    z-index: 2;
    display: inline-block;
    margin-bottom: 0.9rem;
    padding: 0.4rem 0.75rem;
    color: var(--hg-accent);
    background: var(--hg-accent-soft);
    border: 1px solid var(--hg-border);
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 750;
}}

.hg-hero-title {{
    position: relative;
    z-index: 2;
    max-width: 760px;
    margin-bottom: 0.55rem;
    padding-right: 95px;
    color: var(--hg-text);
    font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 820;
    letter-spacing: -0.045em;
    line-height: 1.05;
}}

.hg-hero-text {{
    position: relative;
    z-index: 2;
    max-width: 720px;
    margin: 0;
    padding-right: 90px;
    color: var(--hg-muted);
    font-size: 1.02rem;
    line-height: 1.65;
}}

.hg-page-loading {{
    display: flex;
    align-items: center;
    gap: 0.85rem;
    max-width: 1040px;
    margin: 1rem auto;
    padding: 1rem 1.1rem;
    color: var(--hg-muted);
    background: linear-gradient(135deg, var(--hg-surface), var(--hg-surface-second));
    border: 1px solid var(--hg-border);
    border-radius: 17px;
    box-shadow: 0 12px 32px var(--hg-shadow);
}}

.hg-page-loading-dot {{
    width: 11px;
    height: 11px;
    flex: 0 0 auto;
    border-radius: 50%;
    background: var(--hg-accent-second);
    box-shadow: 0 0 0 0 rgba(0, 191, 210, 0.45);
    animation: hg-loading-pulse 1.2s ease-out infinite;
}}

@keyframes hg-loading-pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(0, 191, 210, 0.45); }}
    70% {{ box-shadow: 0 0 0 10px rgba(0, 191, 210, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(0, 191, 210, 0); }}
}}

div[data-testid="stMetric"] {{
    min-height: 120px;
    padding: 1.2rem;
    background: linear-gradient(145deg, var(--hg-surface), var(--hg-surface-second));
    border: 1px solid var(--hg-border);
    border-radius: 19px;
    box-shadow: 0 10px 30px var(--hg-shadow);
}}

div[data-testid="stMetricLabel"] {{ color: var(--hg-muted); }}
div[data-testid="stMetricValue"] {{ color: var(--hg-text); font-weight: 800; }}

.hg-card {{
    height: 100%;
    padding: 1.35rem;
    background: linear-gradient(145deg, var(--hg-surface), var(--hg-surface-second));
    border: 1px solid var(--hg-border);
    border-radius: 20px;
    box-shadow: 0 10px 30px var(--hg-shadow);
}}

.hg-card-icon {{ margin-bottom: 0.7rem; font-size: 2.1rem; }}
.hg-card-title {{ margin-bottom: 0.3rem; color: var(--hg-text); font-size: 1.12rem; font-weight: 750; }}
.hg-card-subtitle {{ margin-bottom: 0.8rem; color: var(--hg-muted); font-size: 0.9rem; }}
.hg-card-message {{ margin-top: 0.8rem; color: var(--hg-text); font-weight: 650; }}
.hg-card-note {{ margin-top: 0.25rem; color: var(--hg-muted); font-size: 0.83rem; }}

.hg-pill {{
    display: inline-block;
    padding: 0.32rem 0.65rem;
    border-radius: 999px;
    font-size: 0.77rem;
    font-weight: 750;
}}

.hg-pill-good {{ color: var(--hg-success); background: rgba(42,190,135,0.11); border: 1px solid rgba(42,190,135,0.22); }}
.hg-pill-warning {{ color: var(--hg-warning); background: rgba(255,174,63,0.11); border: 1px solid rgba(255,174,63,0.22); }}
.hg-pill-danger {{ color: var(--hg-danger); background: rgba(230,70,85,0.10); border: 1px solid rgba(230,70,85,0.21); }}

div.stButton > button {{
    min-height: 46px;
    color: var(--hg-text);
    background: var(--hg-surface);
    border: 1px solid var(--hg-border);
    border-radius: 13px;
    font-weight: 700;
}}

div.stButton > button:hover {{ color: var(--hg-text); border-color: var(--hg-accent); }}

div.stButton > button[kind="primary"] {{
    color: white;
    background: linear-gradient(100deg, var(--hg-accent), var(--hg-accent-second));
    border: none;
}}

div.stButton > button[kind="primary"]:hover {{ color: white; }}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div,
textarea {{
    color: var(--hg-text) !important;
    background: var(--hg-input) !important;
    border-color: var(--hg-border) !important;
    border-radius: 12px !important;
}}

input, textarea {{ color: var(--hg-text) !important; }}
input::placeholder, textarea::placeholder {{ color: var(--hg-muted) !important; opacity: 0.85; }}

div[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stForm"],
[data-testid="stExpander"] {{
    background: var(--hg-surface-soft);
    border-color: var(--hg-border) !important;
    border-radius: 17px;
}}

[data-testid="stFileUploaderDropzone"] {{
    color: var(--hg-text);
    background: var(--hg-surface-soft);
    border-color: var(--hg-border);
    border-radius: 15px;
}}

div[data-testid="stAlert"] {{ border-radius: 14px; }}
button[data-baseweb="tab"] {{ color: var(--hg-text); font-weight: 700; }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: var(--hg-accent); }}

[data-testid="stChatMessage"] {{
    background: var(--hg-surface-soft);
    border: 1px solid var(--hg-border);
    border-radius: 16px;
}}

#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}

@media (max-width: 700px) {{
    .block-container {{ padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; }}
    .hg-hero {{ padding: 1.5rem; border-radius: 20px; }}
    .hg-hero-logo {{ top: 1rem; right: 1rem; width: 58px; height: 58px; }}
    .hg-hero-title {{ padding-right: 65px; font-size: 2rem; }}
    .hg-hero-text {{ padding-right: 0; }}
}}

html,
body,
.stApp,
[data-testid="stAppViewContainer"],
section[data-testid="stSidebar"],
.hg-hero,
.hg-card,
div[data-testid="stMetric"],
div[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stForm"],
[data-testid="stExpander"] {{
    transition:
        background-color 150ms ease,
        background 150ms ease,
        color 150ms ease,
        border-color 150ms ease,
        box-shadow 150ms ease;
}}

html[data-hg-theme="light"]
section[data-testid="stSidebar"] {{
    background:
        radial-gradient(
            circle at 18% 2%,
            rgba(22, 140, 255, 0.12),
            transparent 24%
        ),
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #F5F9FD 52%,
            #EEF5FB 100%
        );
}}

html[data-hg-theme="light"]
section[data-testid="stSidebar"]
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background:
        linear-gradient(
            145deg,
            rgba(255, 255, 255, 0.97),
            rgba(244, 249, 253, 0.94)
        );
    border-color:
        rgba(25, 92, 140, 0.14) !important;
    box-shadow:
        0 14px 34px rgba(37, 79, 116, 0.10),
        inset 0 1px 0
        rgba(255, 255, 255, 0.86);
}}

html[data-hg-theme="light"]
section[data-testid="stSidebar"]
[data-testid="stSidebarNavLink"]:hover {{
    background: rgba(8, 126, 230, 0.08);
}}

html[data-hg-theme="light"]
section[data-testid="stSidebar"]
[data-testid="stSidebarNavLink"]
[aria-current="page"] {{
    background:
        linear-gradient(
            105deg,
            rgba(8, 126, 230, 0.16),
            rgba(0, 169, 189, 0.10)
        );
    border-color: rgba(8, 126, 230, 0.18);
}}

html[data-hg-theme="light"]
div[data-baseweb="popover"],
html[data-hg-theme="light"]
div[data-baseweb="menu"],
html[data-hg-theme="light"]
ul[role="listbox"],
html[data-hg-theme="light"]
div[role="dialog"] {{
    color: var(--hg-text) !important;
    background: #FFFFFF !important;
    border-color: var(--hg-border) !important;
}}

html[data-hg-theme="light"]
li[role="option"] {{
    color: var(--hg-text) !important;
    background: #FFFFFF !important;
}}

html[data-hg-theme="light"]
li[role="option"]:hover,
html[data-hg-theme="light"]
li[role="option"][aria-selected="true"] {{
    background: var(--hg-accent-soft) !important;
}}

html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"],
html[data-hg-theme="light"]
[data-testid="stChatInput"] {{
    background: #FFFFFF !important;
    border-color: var(--hg-border) !important;
}}

html[data-hg-theme="light"]
[data-testid="stDataFrame"] {{
    background: #FFFFFF;
    border-color: var(--hg-border);
}}

.hg-theme-status-light .hg-theme-status-dot {{
    background: #FFB44A;
    box-shadow:
        0 0 0 4px
        rgba(255, 180, 74, 0.13);
}}

.hg-theme-status-dark .hg-theme-status-dot {{
    background: #40DBA0;
    box-shadow:
        0 0 0 4px
        rgba(64, 219, 160, 0.10);
}}


/* Floating sun/moon theme switch */
.st-key-hg_theme_float,
[class*="st-key-hg_theme_float"] {{
    position: fixed !important;
    top: 0.55rem !important;
    right: 7.35rem !important;
    z-index: 1000000 !important;

    width: 48px !important;
    max-width: 48px !important;
    height: 48px !important;
    max-height: 48px !important;

    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;

    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}}

.st-key-hg_theme_float > div,
.st-key-hg_theme_float [data-testid="stVerticalBlock"],
.st-key-hg_theme_float [data-testid="stVerticalBlockBorderWrapper"],
.st-key-hg_theme_float [data-testid="stCustomComponentV2"],
[class*="st-key-hg_theme_float"] > div,
[class*="st-key-hg_theme_float"] [data-testid="stVerticalBlock"],
[class*="st-key-hg_theme_float"] [data-testid="stVerticalBlockBorderWrapper"],
[class*="st-key-hg_theme_float"] [data-testid="stCustomComponentV2"] {{
    width: 48px !important;
    max-width: 48px !important;
    height: 48px !important;
    max-height: 48px !important;

    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;

    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}}

.st-key-hg_theme_float iframe,
[class*="st-key-hg_theme_float"] iframe {{
    display: block !important;

    width: 48px !important;
    min-width: 48px !important;
    max-width: 48px !important;

    height: 48px !important;
    min-height: 48px !important;
    max-height: 48px !important;

    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;

    border: 0 !important;
    background: transparent !important;

    scrollbar-width: none !important;
}}

.st-key-hg_theme_float iframe::-webkit-scrollbar,
[class*="st-key-hg_theme_float"] iframe::-webkit-scrollbar {{
    display: none !important;
    width: 0 !important;
    height: 0 !important;
}}

@media (max-width: 700px) {{
    .st-key-hg_theme_float,
    [class*="st-key-hg_theme_float"] {{
        top: 0.45rem !important;
        right: 4.45rem !important;

        width: 44px !important;
        max-width: 44px !important;
        height: 44px !important;
        max-height: 44px !important;

        transform: scale(0.92);
        transform-origin: top right;
    }}
}}


/* Strong light-mode readability */
html[data-hg-theme="light"] body,
html[data-hg-theme="light"] .stApp,
html[data-hg-theme="light"] p,
html[data-hg-theme="light"] label,
html[data-hg-theme="light"] li,
html[data-hg-theme="light"] h1,
html[data-hg-theme="light"] h2,
html[data-hg-theme="light"] h3,
html[data-hg-theme="light"] h4,
html[data-hg-theme="light"] h5,
html[data-hg-theme="light"] h6,
html[data-hg-theme="light"] .stMarkdown,
html[data-hg-theme="light"] [data-testid="stWidgetLabel"],
html[data-hg-theme="light"] [data-testid="stMetricValue"],
html[data-hg-theme="light"] [data-testid="stMetricLabel"],
html[data-hg-theme="light"] [data-testid="stExpander"] summary,
html[data-hg-theme="light"] [data-testid="stAlert"] {{
    color: #142235 !important;
}}

html[data-hg-theme="light"]
[data-testid="stCaptionContainer"],
html[data-hg-theme="light"]
[data-testid="stCaptionContainer"] *,
html[data-hg-theme="light"]
small {{
    color: #5E7186 !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
section[data-testid="stSidebar"]
[data-testid="stSidebarNavLink"],
html[data-hg-theme="light"]
section[data-testid="stSidebar"]
[data-testid="stSidebarNavLink"] span,
html[data-hg-theme="light"]
section[data-testid="stSidebar"]
[data-testid="stSidebarNavLink"] p,
html[data-hg-theme="light"]
section[data-testid="stSidebar"]
[data-testid="stSidebarNavLink"] div {{
    color: #183047 !important;
    opacity: 1 !important;
    filter: none !important;
}}

html[data-hg-theme="light"]
section[data-testid="stSidebar"]
[data-testid="stSidebarNavLink"] svg {{
    color: #087EE6 !important;
    fill: currentColor !important;
    opacity: 1 !important;
    filter: none !important;
}}

html[data-hg-theme="light"]
div.stButton > button:not([kind="primary"]),
html[data-hg-theme="light"]
div.stButton > button:not([kind="primary"]) *,
html[data-hg-theme="light"]
button[data-baseweb="tab"],
html[data-hg-theme="light"]
button[data-baseweb="tab"] * {{
    color: #183047 !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
div.stButton > button[kind="primary"],
html[data-hg-theme="light"]
div.stButton > button[kind="primary"] * {{
    color: #FFFFFF !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
input,
html[data-hg-theme="light"]
textarea,
html[data-hg-theme="light"]
div[data-baseweb="select"] *,
html[data-hg-theme="light"]
div[data-baseweb="input"] *,
html[data-hg-theme="light"]
div[data-baseweb="textarea"] * {{
    color: #142235 !important;
    -webkit-text-fill-color: #142235 !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
input::placeholder,
html[data-hg-theme="light"]
textarea::placeholder {{
    color: #718397 !important;
    -webkit-text-fill-color: #718397 !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"],
html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] *,
html[data-hg-theme="light"]
[data-testid="stChatMessage"],
html[data-hg-theme="light"]
[data-testid="stChatMessage"] *,
html[data-hg-theme="light"]
[data-testid="stChatInput"],
html[data-hg-theme="light"]
[data-testid="stChatInput"] * {{
    color: #142235 !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
div[data-baseweb="popover"] *,
html[data-hg-theme="light"]
div[data-baseweb="menu"] *,
html[data-hg-theme="light"]
ul[role="listbox"] *,
html[data-hg-theme="light"]
li[role="option"] * {{
    color: #142235 !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
.hg-card-icon,
html[data-hg-theme="light"]
button,
html[data-hg-theme="light"]
[data-testid="stSidebarNavLink"] {{
    font-variant-emoji: emoji;
    text-shadow: none !important;
}}

html[data-hg-theme="light"]
[data-testid="stSidebarNavLink"] span,
html[data-hg-theme="light"]
button span,
html[data-hg-theme="light"]
button p,
html[data-hg-theme="light"]
.hg-card-icon {{
    visibility: visible !important;
    opacity: 1 !important;
}}


/* =========================================================
   Complete polished light-mode controls
========================================================= */

html[data-hg-theme="light"] {{
    --hg-light-control: #FFFFFF;
    --hg-light-control-hover: #F5F9FD;
    --hg-light-control-active: #EAF4FC;
    --hg-light-control-border: rgba(30, 73, 110, 0.16);
    --hg-light-control-border-strong: rgba(8, 126, 230, 0.40);
    --hg-light-control-text: #172B40;
    --hg-light-control-muted: #687C91;
    --hg-light-control-shadow: 0 8px 22px rgba(32, 71, 105, 0.08);
}}


/* Main content and fixed page areas */

html[data-hg-theme="light"]
[data-testid="stAppViewContainer"],
html[data-hg-theme="light"]
[data-testid="stMain"],
html[data-hg-theme="light"]
[data-testid="stMainBlockContainer"] {{
    background: #F4F7FB !important;
}}

html[data-hg-theme="light"]
header[data-testid="stHeader"] {{
    background:
        rgba(244, 247, 251, 0.94) !important;

    backdrop-filter: blur(12px);
}}


/* Standard secondary buttons */

html[data-hg-theme="light"]
div.stButton > button:not([kind="primary"]),
html[data-hg-theme="light"]
div[data-testid="stPopover"] > button,
html[data-hg-theme="light"]
div[data-testid="stPopover"] button,
html[data-hg-theme="light"]
button[data-testid="stBaseButton-secondary"],
html[data-hg-theme="light"]
button[data-testid="stBaseButton-minimal"] {{
    color:
        var(--hg-light-control-text) !important;

    background:
        var(--hg-light-control) !important;

    border:
        1px solid
        var(--hg-light-control-border) !important;

    box-shadow:
        var(--hg-light-control-shadow) !important;

    opacity: 1 !important;
}}

html[data-hg-theme="light"]
div.stButton > button:not([kind="primary"]) *,
html[data-hg-theme="light"]
div[data-testid="stPopover"] button *,
html[data-hg-theme="light"]
button[data-testid="stBaseButton-secondary"] *,
html[data-hg-theme="light"]
button[data-testid="stBaseButton-minimal"] * {{
    color:
        var(--hg-light-control-text) !important;

    -webkit-text-fill-color:
        var(--hg-light-control-text) !important;

    opacity: 1 !important;
}}

html[data-hg-theme="light"]
div.stButton > button:not([kind="primary"]):hover,
html[data-hg-theme="light"]
div[data-testid="stPopover"] button:hover,
html[data-hg-theme="light"]
button[data-testid="stBaseButton-secondary"]:hover,
html[data-hg-theme="light"]
button[data-testid="stBaseButton-minimal"]:hover {{
    color: #087EE6 !important;

    background:
        var(--hg-light-control-hover) !important;

    border-color:
        rgba(8, 126, 230, 0.38) !important;

    transform: translateY(-1px);
}}

html[data-hg-theme="light"]
div.stButton > button:disabled,
html[data-hg-theme="light"]
div.stButton > button:disabled * {{
    color: #8C9BAB !important;

    -webkit-text-fill-color:
        #8C9BAB !important;

    background:
        #EDF2F6 !important;

    border-color:
        rgba(38, 69, 96, 0.10) !important;

    opacity: 1 !important;
}}


/* Primary buttons */

html[data-hg-theme="light"]
div.stButton > button[kind="primary"],
html[data-hg-theme="light"]
button[data-testid="stBaseButton-primary"] {{
    color: #FFFFFF !important;

    background:
        linear-gradient(
            100deg,
            #168CFF,
            #00BFD2
        ) !important;

    border: 0 !important;

    box-shadow:
        0 10px 24px
        rgba(8, 126, 230, 0.18) !important;
}}

html[data-hg-theme="light"]
div.stButton > button[kind="primary"] *,
html[data-hg-theme="light"]
button[data-testid="stBaseButton-primary"] * {{
    color: #FFFFFF !important;

    -webkit-text-fill-color:
        #FFFFFF !important;
}}


/* Select boxes */

html[data-hg-theme="light"]
[data-testid="stSelectbox"]
div[data-baseweb="select"] > div,
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
div[data-baseweb="select"] > div,
html[data-hg-theme="light"]
div[data-baseweb="select"] > div {{
    color:
        var(--hg-light-control-text) !important;

    background:
        var(--hg-light-control) !important;

    border:
        1px solid
        var(--hg-light-control-border) !important;

    box-shadow:
        0 5px 15px
        rgba(32, 71, 105, 0.05) !important;
}}

html[data-hg-theme="light"]
[data-testid="stSelectbox"]
div[data-baseweb="select"] *,
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
div[data-baseweb="select"] *,
html[data-hg-theme="light"]
div[data-baseweb="select"] * {{
    color:
        var(--hg-light-control-text) !important;

    -webkit-text-fill-color:
        var(--hg-light-control-text) !important;

    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stSelectbox"]
div[data-baseweb="select"] > div:hover,
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
div[data-baseweb="select"] > div:hover {{
    border-color:
        var(--hg-light-control-border-strong) !important;
}}


/* Text inputs, dates, number fields and text areas */

html[data-hg-theme="light"]
div[data-baseweb="input"] > div,
html[data-hg-theme="light"]
div[data-baseweb="textarea"] > div,
html[data-hg-theme="light"]
[data-testid="stDateInput"]
div[data-baseweb="input"] > div,
html[data-hg-theme="light"]
[data-testid="stNumberInput"]
div[data-baseweb="input"] > div,
html[data-hg-theme="light"]
textarea {{
    color:
        var(--hg-light-control-text) !important;

    background:
        var(--hg-light-control) !important;

    border:
        1px solid
        var(--hg-light-control-border) !important;

    box-shadow:
        0 5px 15px
        rgba(32, 71, 105, 0.05) !important;
}}

html[data-hg-theme="light"]
div[data-baseweb="input"] > div:focus-within,
html[data-hg-theme="light"]
div[data-baseweb="textarea"] > div:focus-within,
html[data-hg-theme="light"]
[data-testid="stDateInput"]
div[data-baseweb="input"] > div:focus-within,
html[data-hg-theme="light"]
[data-testid="stNumberInput"]
div[data-baseweb="input"] > div:focus-within {{
    border-color:
        #168CFF !important;

    box-shadow:
        0 0 0 3px
        rgba(22, 140, 255, 0.11) !important;
}}

html[data-hg-theme="light"]
input,
html[data-hg-theme="light"]
textarea {{
    color:
        var(--hg-light-control-text) !important;

    -webkit-text-fill-color:
        var(--hg-light-control-text) !important;

    background:
        transparent !important;

    caret-color: #087EE6 !important;

    opacity: 1 !important;
}}

html[data-hg-theme="light"]
input::placeholder,
html[data-hg-theme="light"]
textarea::placeholder {{
    color:
        #788B9F !important;

    -webkit-text-fill-color:
        #788B9F !important;

    opacity: 1 !important;
}}


/* File uploader */

html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] {{
    color:
        var(--hg-light-control-text) !important;

    background:
        var(--hg-light-control) !important;

    border:
        1px solid
        var(--hg-light-control-border) !important;

    box-shadow:
        var(--hg-light-control-shadow) !important;
}}

html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] *,
html[data-hg-theme="light"]
[data-testid="stFileUploader"] * {{
    color:
        var(--hg-light-control-text) !important;

    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] button,
html[data-hg-theme="light"]
[data-testid="stFileUploader"] button {{
    color: #FFFFFF !important;

    background:
        linear-gradient(
            100deg,
            #168CFF,
            #00BFD2
        ) !important;

    border: 0 !important;

    box-shadow:
        0 8px 18px
        rgba(8, 126, 230, 0.18) !important;
}}

html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] button *,
html[data-hg-theme="light"]
[data-testid="stFileUploader"] button * {{
    color: #FFFFFF !important;

    -webkit-text-fill-color:
        #FFFFFF !important;
}}

html[data-hg-theme="light"]
[data-testid="stFileUploaderFile"],
html[data-hg-theme="light"]
[data-testid="stFileUploaderFile"] * {{
    color:
        var(--hg-light-control-text) !important;

    background:
        #F1F7FC !important;

    opacity: 1 !important;
}}


/* Expanders */

html[data-hg-theme="light"]
[data-testid="stExpander"] {{
    color:
        var(--hg-light-control-text) !important;

    background:
        var(--hg-light-control) !important;

    border:
        1px solid
        var(--hg-light-control-border) !important;

    box-shadow:
        0 6px 18px
        rgba(32, 71, 105, 0.05) !important;
}}

html[data-hg-theme="light"]
[data-testid="stExpander"] summary,
html[data-hg-theme="light"]
[data-testid="stExpander"] summary *,
html[data-hg-theme="light"]
[data-testid="stExpander"] details,
html[data-hg-theme="light"]
[data-testid="stExpander"] details * {{
    color:
        var(--hg-light-control-text) !important;

    opacity: 1 !important;
}}


/* Tabs */

html[data-hg-theme="light"]
[data-testid="stTabs"] {{
    border-bottom:
        1px solid
        rgba(30, 73, 110, 0.13);
}}

html[data-hg-theme="light"]
button[data-baseweb="tab"] {{
    color:
        var(--hg-light-control-text) !important;

    background:
        transparent !important;

    border:
        0 !important;

    box-shadow: none !important;

    opacity: 1 !important;
}}

html[data-hg-theme="light"]
button[data-baseweb="tab"] * {{
    color:
        var(--hg-light-control-text) !important;

    opacity: 1 !important;
}}

html[data-hg-theme="light"]
button[data-baseweb="tab"][aria-selected="true"],
html[data-hg-theme="light"]
button[data-baseweb="tab"][aria-selected="true"] * {{
    color: #087EE6 !important;

    font-weight: 800 !important;
}}

html[data-hg-theme="light"]
[data-testid="stTabs"]
div[data-baseweb="tab-highlight"] {{
    background-color:
        #168CFF !important;
}}


/* Radio-button navigation pills */

html[data-hg-theme="light"]
div[data-testid="stRadio"] label {{
    color:
        var(--hg-light-control-text) !important;

    background:
        var(--hg-light-control) !important;

    border:
        1px solid
        var(--hg-light-control-border) !important;

    box-shadow:
        0 5px 14px
        rgba(32, 71, 105, 0.05) !important;

    opacity: 1 !important;
}}

html[data-hg-theme="light"]
div[data-testid="stRadio"] label *,
html[data-hg-theme="light"]
div[data-testid="stRadio"] label p,
html[data-hg-theme="light"]
div[data-testid="stRadio"] label span {{
    color:
        var(--hg-light-control-text) !important;

    opacity: 1 !important;
}}

html[data-hg-theme="light"]
div[data-testid="stRadio"]
label:has(input:checked) {{
    color: #087EE6 !important;

    background:
        #EAF5FE !important;

    border-color:
        rgba(8, 126, 230, 0.30) !important;
}}


/* Native toggles inside forms */

html[data-hg-theme="light"]
div[data-testid="stToggle"]
[role="switch"] {{
    background:
        #D9E5EF !important;

    border:
        1px solid
        rgba(30, 73, 110, 0.14) !important;
}}

html[data-hg-theme="light"]
div[data-testid="stToggle"]
[role="switch"][aria-checked="true"] {{
    background:
        linear-gradient(
            100deg,
            #168CFF,
            #00BFD2
        ) !important;
}}

html[data-hg-theme="light"]
div[data-testid="stToggle"] label,
html[data-hg-theme="light"]
div[data-testid="stToggle"] label * {{
    color:
        var(--hg-light-control-text) !important;

    opacity: 1 !important;
}}


/* Chat input and fixed bottom bar */

html[data-hg-theme="light"]
[data-testid="stBottomBlockContainer"],
html[data-hg-theme="light"]
[data-testid="stBottom"],
html[data-hg-theme="light"]
.stChatFloatingInputContainer {{
    background:
        linear-gradient(
            180deg,
            rgba(244, 247, 251, 0),
            rgba(244, 247, 251, 0.97) 28%,
            #F4F7FB 100%
        ) !important;
}}

html[data-hg-theme="light"]
[data-testid="stChatInput"] {{
    color:
        var(--hg-light-control-text) !important;

    background:
        var(--hg-light-control) !important;

    border:
        1px solid
        var(--hg-light-control-border) !important;

    box-shadow:
        0 14px 32px
        rgba(32, 71, 105, 0.13) !important;
}}

html[data-hg-theme="light"]
[data-testid="stChatInput"] > div,
html[data-hg-theme="light"]
[data-testid="stChatInput"] textarea,
html[data-hg-theme="light"]
[data-testid="stChatInput"] button {{
    color:
        var(--hg-light-control-text) !important;

    background:
        var(--hg-light-control) !important;

    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stChatInput"] button {{
    color: #FFFFFF !important;

    background:
        linear-gradient(
            100deg,
            #168CFF,
            #00BFD2
        ) !important;

    border-radius: 11px !important;
}}

html[data-hg-theme="light"]
[data-testid="stChatInput"] button * {{
    color: #FFFFFF !important;
}}


/* Dropdown menus and date popovers */

html[data-hg-theme="light"]
div[data-baseweb="popover"],
html[data-hg-theme="light"]
div[data-baseweb="menu"],
html[data-hg-theme="light"]
ul[role="listbox"],
html[data-hg-theme="light"]
div[role="dialog"],
html[data-hg-theme="light"]
[data-baseweb="calendar"] {{
    color:
        var(--hg-light-control-text) !important;

    background:
        #FFFFFF !important;

    border:
        1px solid
        var(--hg-light-control-border) !important;

    box-shadow:
        0 18px 42px
        rgba(32, 71, 105, 0.16) !important;
}}

html[data-hg-theme="light"]
div[data-baseweb="popover"] *,
html[data-hg-theme="light"]
div[data-baseweb="menu"] *,
html[data-hg-theme="light"]
ul[role="listbox"] *,
html[data-hg-theme="light"]
div[role="dialog"] *,
html[data-hg-theme="light"]
[data-baseweb="calendar"] * {{
    color:
        var(--hg-light-control-text) !important;

    opacity: 1 !important;
}}

html[data-hg-theme="light"]
li[role="option"] {{
    color:
        var(--hg-light-control-text) !important;

    background:
        #FFFFFF !important;
}}

html[data-hg-theme="light"]
li[role="option"]:hover,
html[data-hg-theme="light"]
li[role="option"][aria-selected="true"] {{
    color: #087EE6 !important;

    background:
        #EAF5FE !important;
}}


/* Cards and task / repair content */

html[data-hg-theme="light"]
.hg-card,
html[data-hg-theme="light"]
.hg-appliance-summary,
html[data-hg-theme="light"]
.hg-welcome-card,
html[data-hg-theme="light"]
.hg-task-card,
html[data-hg-theme="light"]
.hg-repair-card {{
    color:
        var(--hg-light-control-text) !important;

    background:
        linear-gradient(
            145deg,
            #FFFFFF,
            #F8FBFE
        ) !important;

    border-color:
        var(--hg-light-control-border) !important;
}}

html[data-hg-theme="light"]
.hg-card *,
html[data-hg-theme="light"]
.hg-appliance-summary *,
html[data-hg-theme="light"]
.hg-welcome-card *,
html[data-hg-theme="light"]
.hg-task-card *,
html[data-hg-theme="light"]
.hg-repair-card * {{
    opacity: 1 !important;
}}


/* Never let emoji/icons fade in light mode */

html[data-hg-theme="light"]
.hg-card-icon,
html[data-hg-theme="light"]
.hg-appliance-summary-icon,
html[data-hg-theme="light"]
.hg-welcome-icon,
html[data-hg-theme="light"]
button span,
html[data-hg-theme="light"]
button p,
html[data-hg-theme="light"]
[data-testid="stSidebarNavLink"] span {{
    visibility: visible !important;
    opacity: 1 !important;
    filter: none !important;
}}


/* =========================================================
   FINAL LIGHT MODE OVERRIDES
   These rules intentionally target Streamlit's inner
   BaseWeb layers, not only the outer widget wrappers.
========================================================= */

html[data-hg-theme="light"] {{
    --background-color: #F4F7FB;
    --secondary-background-color: #FFFFFF;
    --text-color: #142235;
    --primary-color: #168CFF;
    --border-color: rgba(30, 73, 110, 0.16);
    --default-backgroundColor: #FFFFFF;
    --default-textColor: #142235;
    --default-borderColor: rgba(30, 73, 110, 0.16);
}}


/* ---------------------------------------------------------
   SELECT BOXES
--------------------------------------------------------- */

html[data-hg-theme="light"]
[data-testid="stSelectbox"],
html[data-hg-theme="light"]
[data-testid="stMultiSelect"] {{
    color: #142235 !important;
}}

html[data-hg-theme="light"]
[data-testid="stSelectbox"]
[data-baseweb="select"],
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
[data-baseweb="select"],
html[data-hg-theme="light"]
[data-testid="stSelectbox"]
[data-baseweb="select"] > div,
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
[data-baseweb="select"] > div,
html[data-hg-theme="light"]
[data-testid="stSelectbox"]
[data-baseweb="select"] > div > div,
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
[data-baseweb="select"] > div > div {{
    color: #142235 !important;
    background-color: #FFFFFF !important;
    background-image: none !important;
    border-color: rgba(30, 73, 110, 0.17) !important;
    box-shadow: none !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stSelectbox"]
[data-baseweb="select"] span,
html[data-hg-theme="light"]
[data-testid="stSelectbox"]
[data-baseweb="select"] input,
html[data-hg-theme="light"]
[data-testid="stSelectbox"]
[data-baseweb="select"] svg,
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
[data-baseweb="select"] span,
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
[data-baseweb="select"] input,
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
[data-baseweb="select"] svg {{
    color: #142235 !important;
    fill: currentColor !important;
    -webkit-text-fill-color: #142235 !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stSelectbox"]
[data-baseweb="select"] > div:hover,
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
[data-baseweb="select"] > div:hover {{
    background-color: #F8FBFE !important;
    border-color: rgba(8, 126, 230, 0.42) !important;
}}

html[data-hg-theme="light"]
[data-testid="stSelectbox"]
[data-baseweb="select"] > div:focus-within,
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
[data-baseweb="select"] > div:focus-within {{
    background-color: #FFFFFF !important;
    border-color: #168CFF !important;
    box-shadow:
        0 0 0 3px
        rgba(22, 140, 255, 0.10) !important;
}}


/* ---------------------------------------------------------
   TEXT, NUMBER, DATE AND TEXTAREA WIDGETS
--------------------------------------------------------- */

html[data-hg-theme="light"]
[data-testid="stTextInput"]
[data-baseweb="input"],
html[data-hg-theme="light"]
[data-testid="stNumberInput"]
[data-baseweb="input"],
html[data-hg-theme="light"]
[data-testid="stDateInput"]
[data-baseweb="input"],
html[data-hg-theme="light"]
[data-testid="stTextArea"]
[data-baseweb="textarea"],
html[data-hg-theme="light"]
[data-testid="stTextInput"]
[data-baseweb="base-input"],
html[data-hg-theme="light"]
[data-testid="stNumberInput"]
[data-baseweb="base-input"],
html[data-hg-theme="light"]
[data-testid="stDateInput"]
[data-baseweb="base-input"],
html[data-hg-theme="light"]
[data-testid="stTextArea"]
[data-baseweb="base-input"],
html[data-hg-theme="light"]
[data-testid="stTextInput"]
[data-baseweb="input"] > div,
html[data-hg-theme="light"]
[data-testid="stNumberInput"]
[data-baseweb="input"] > div,
html[data-hg-theme="light"]
[data-testid="stDateInput"]
[data-baseweb="input"] > div,
html[data-hg-theme="light"]
[data-testid="stTextArea"]
[data-baseweb="textarea"] > div,
html[data-hg-theme="light"]
[data-testid="stTextArea"]
[data-baseweb="textarea"] > div > div,
html[data-hg-theme="light"]
[data-testid="stTextArea"]
div:has(> textarea) {{
    color: #142235 !important;
    background-color: #FFFFFF !important;
    background-image: none !important;
    border-color: rgba(30, 73, 110, 0.17) !important;
    box-shadow: none !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stTextInput"] input,
html[data-hg-theme="light"]
[data-testid="stNumberInput"] input,
html[data-hg-theme="light"]
[data-testid="stDateInput"] input,
html[data-hg-theme="light"]
[data-testid="stTextArea"] textarea {{
    color: #142235 !important;
    background-color: #FFFFFF !important;
    background-image: none !important;
    -webkit-text-fill-color: #142235 !important;
    caret-color: #168CFF !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stTextInput"] input::placeholder,
html[data-hg-theme="light"]
[data-testid="stNumberInput"] input::placeholder,
html[data-hg-theme="light"]
[data-testid="stDateInput"] input::placeholder,
html[data-hg-theme="light"]
[data-testid="stTextArea"] textarea::placeholder {{
    color: #75889D !important;
    -webkit-text-fill-color: #75889D !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stTextInput"]
[data-baseweb="input"]:focus-within,
html[data-hg-theme="light"]
[data-testid="stNumberInput"]
[data-baseweb="input"]:focus-within,
html[data-hg-theme="light"]
[data-testid="stDateInput"]
[data-baseweb="input"]:focus-within,
html[data-hg-theme="light"]
[data-testid="stTextArea"]
[data-baseweb="textarea"]:focus-within {{
    border-color: #168CFF !important;
    box-shadow:
        0 0 0 3px
        rgba(22, 140, 255, 0.10) !important;
}}


/* ---------------------------------------------------------
   FILE UPLOADER
--------------------------------------------------------- */

html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"],
html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] > div,
html[data-hg-theme="light"]
[data-testid="stFileUploader"] section {{
    color: #142235 !important;
    background-color: #FFFFFF !important;
    background-image: none !important;
    border-color: rgba(30, 73, 110, 0.17) !important;
    box-shadow:
        0 8px 22px
        rgba(32, 71, 105, 0.07) !important;
}}

html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] span,
html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] small,
html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] p,
html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] svg {{
    color: #142235 !important;
    fill: currentColor !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] button,
html[data-hg-theme="light"]
[data-testid="stFileUploader"] button {{
    color: #FFFFFF !important;
    background:
        linear-gradient(
            100deg,
            #168CFF,
            #00BFD2
        ) !important;
    border: 0 !important;
    box-shadow:
        0 7px 17px
        rgba(8, 126, 230, 0.18) !important;
}}

html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] button *,
html[data-hg-theme="light"]
[data-testid="stFileUploader"] button * {{
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}}


/* ---------------------------------------------------------
   BUTTONS, POPOVERS AND DETAILS BUTTONS
--------------------------------------------------------- */

html[data-hg-theme="light"]
button[data-testid="stBaseButton-secondary"],
html[data-hg-theme="light"]
button[data-testid="stBaseButton-minimal"],
html[data-hg-theme="light"]
div[data-testid="stPopover"] button,
html[data-hg-theme="light"]
div.stButton > button:not([kind="primary"]) {{
    color: #142235 !important;
    background-color: #FFFFFF !important;
    background-image: none !important;
    border-color: rgba(30, 73, 110, 0.16) !important;
    box-shadow:
        0 6px 16px
        rgba(32, 71, 105, 0.06) !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
button[data-testid="stBaseButton-secondary"] *,
html[data-hg-theme="light"]
button[data-testid="stBaseButton-minimal"] *,
html[data-hg-theme="light"]
div[data-testid="stPopover"] button *,
html[data-hg-theme="light"]
div.stButton > button:not([kind="primary"]) * {{
    color: #142235 !important;
    -webkit-text-fill-color: #142235 !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
button[data-testid="stBaseButton-secondary"]:hover,
html[data-hg-theme="light"]
button[data-testid="stBaseButton-minimal"]:hover,
html[data-hg-theme="light"]
div[data-testid="stPopover"] button:hover,
html[data-hg-theme="light"]
div.stButton > button:not([kind="primary"]):hover {{
    color: #087EE6 !important;
    background-color: #F5FAFE !important;
    border-color: rgba(8, 126, 230, 0.36) !important;
}}

html[data-hg-theme="light"]
button[data-testid="stBaseButton-primary"],
html[data-hg-theme="light"]
div.stButton > button[kind="primary"] {{
    color: #FFFFFF !important;
    background:
        linear-gradient(
            100deg,
            #168CFF,
            #00BFD2
        ) !important;
    border: 0 !important;
    box-shadow:
        0 9px 22px
        rgba(8, 126, 230, 0.16) !important;
}}

html[data-hg-theme="light"]
button[data-testid="stBaseButton-primary"] *,
html[data-hg-theme="light"]
div.stButton > button[kind="primary"] * {{
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}}


/* ---------------------------------------------------------
   EXPANDERS AND FORM SURFACES
--------------------------------------------------------- */

html[data-hg-theme="light"]
[data-testid="stExpander"],
html[data-hg-theme="light"]
[data-testid="stForm"],
html[data-hg-theme="light"]
div[data-testid="stVerticalBlockBorderWrapper"] {{
    color: #142235 !important;
    background-color: #FFFFFF !important;
    background-image: none !important;
    border-color: rgba(30, 73, 110, 0.14) !important;
    box-shadow:
        0 7px 20px
        rgba(32, 71, 105, 0.055) !important;
}}

html[data-hg-theme="light"]
[data-testid="stExpander"] summary,
html[data-hg-theme="light"]
[data-testid="stExpander"] summary *,
html[data-hg-theme="light"]
[data-testid="stExpander"] details,
html[data-hg-theme="light"]
[data-testid="stExpander"] details * {{
    color: #142235 !important;
    -webkit-text-fill-color: #142235 !important;
    opacity: 1 !important;
}}


/* ---------------------------------------------------------
   RADIO / SEGMENTED NAVIGATION PILLS
--------------------------------------------------------- */

html[data-hg-theme="light"]
div[data-testid="stRadio"] label {{
    color: #142235 !important;
    background-color: #FFFFFF !important;
    background-image: none !important;
    border-color: rgba(30, 73, 110, 0.14) !important;
    box-shadow:
        0 5px 14px
        rgba(32, 71, 105, 0.05) !important;
}}

html[data-hg-theme="light"]
div[data-testid="stRadio"] label *,
html[data-hg-theme="light"]
div[data-testid="stRadio"] label span,
html[data-hg-theme="light"]
div[data-testid="stRadio"] label p {{
    color: #142235 !important;
    -webkit-text-fill-color: #142235 !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
div[data-testid="stRadio"]
label:has(input:checked) {{
    color: #087EE6 !important;
    background-color: #EAF5FE !important;
    border-color: rgba(8, 126, 230, 0.30) !important;
}}


/* ---------------------------------------------------------
   DROPDOWN MENUS AND CALENDARS
--------------------------------------------------------- */

html[data-hg-theme="light"]
div[data-baseweb="popover"],
html[data-hg-theme="light"]
div[data-baseweb="menu"],
html[data-hg-theme="light"]
ul[role="listbox"],
html[data-hg-theme="light"]
div[role="dialog"],
html[data-hg-theme="light"]
[data-baseweb="calendar"] {{
    color: #142235 !important;
    background-color: #FFFFFF !important;
    background-image: none !important;
    border-color: rgba(30, 73, 110, 0.16) !important;
    box-shadow:
        0 18px 42px
        rgba(32, 71, 105, 0.15) !important;
}}

html[data-hg-theme="light"]
div[data-baseweb="popover"] *,
html[data-hg-theme="light"]
div[data-baseweb="menu"] *,
html[data-hg-theme="light"]
ul[role="listbox"] *,
html[data-hg-theme="light"]
div[role="dialog"] *,
html[data-hg-theme="light"]
[data-baseweb="calendar"] * {{
    color: #142235 !important;
    -webkit-text-fill-color: #142235 !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
li[role="option"] {{
    color: #142235 !important;
    background-color: #FFFFFF !important;
}}

html[data-hg-theme="light"]
li[role="option"]:hover,
html[data-hg-theme="light"]
li[role="option"][aria-selected="true"] {{
    color: #087EE6 !important;
    background-color: #EAF5FE !important;
}}


/* ---------------------------------------------------------
   CHAT INPUT: REMOVE THE DARK STRIP AND HEAVY SHADOW
--------------------------------------------------------- */

html[data-hg-theme="light"]
[data-testid="stBottomBlockContainer"],
html[data-hg-theme="light"]
[data-testid="stBottomBlockContainer"]::before,
html[data-hg-theme="light"]
[data-testid="stBottomBlockContainer"]::after,
html[data-hg-theme="light"]
[data-testid="stBottom"],
html[data-hg-theme="light"]
[data-testid="stBottom"]::before,
html[data-hg-theme="light"]
[data-testid="stBottom"]::after,
html[data-hg-theme="light"]
.stChatFloatingInputContainer,
html[data-hg-theme="light"]
div:has(> [data-testid="stChatInput"]),
html[data-hg-theme="light"]
div:has(> div > [data-testid="stChatInput"]) {{
    background-color: transparent !important;
    background-image: none !important;
    box-shadow: none !important;
    border: 0 !important;
}}

html[data-hg-theme="light"]
[data-testid="stBottomBlockContainer"] > div,
html[data-hg-theme="light"]
[data-testid="stBottomBlockContainer"] > div > div,
html[data-hg-theme="light"]
[data-testid="stBottom"] > div,
html[data-hg-theme="light"]
[data-testid="stBottom"] > div > div {{
    background-color: transparent !important;
    background-image: none !important;
    box-shadow: none !important;
}}

html[data-hg-theme="light"]
[data-testid="stChatInput"] {{
    color: #142235 !important;
    background-color: #FFFFFF !important;
    background-image: none !important;
    border:
        1px solid
        rgba(30, 73, 110, 0.16) !important;
    border-radius: 15px !important;
    box-shadow:
        0 8px 24px
        rgba(32, 71, 105, 0.10) !important;
}}

html[data-hg-theme="light"]
[data-testid="stChatInput"] > div,
html[data-hg-theme="light"]
[data-testid="stChatInput"]
[data-baseweb="textarea"],
html[data-hg-theme="light"]
[data-testid="stChatInput"]
[data-baseweb="base-input"],
html[data-hg-theme="light"]
[data-testid="stChatInput"]
div:has(> textarea),
html[data-hg-theme="light"]
textarea[data-testid="stChatInput"],
html[data-hg-theme="light"]
textarea[data-testid="stChatInputTextArea"],
html[data-hg-theme="light"]
[data-testid="stChatInput"] textarea {{
    color: #142235 !important;
    background-color: #FFFFFF !important;
    background-image: none !important;
    -webkit-text-fill-color: #142235 !important;
    border: 0 !important;
    box-shadow: none !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stChatInput"] textarea::placeholder,
html[data-hg-theme="light"]
textarea[data-testid="stChatInput"]::placeholder,
html[data-hg-theme="light"]
textarea[data-testid="stChatInputTextArea"]::placeholder {{
    color: #71859A !important;
    -webkit-text-fill-color: #71859A !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stChatInput"] button {{
    color: #FFFFFF !important;
    background:
        linear-gradient(
            135deg,
            #168CFF,
            #00BFD2
        ) !important;
    border: 0 !important;
    border-radius: 11px !important;
    box-shadow: none !important;
}}

html[data-hg-theme="light"]
[data-testid="stChatInput"] button * {{
    color: #FFFFFF !important;
    fill: currentColor !important;
}}


/* ---------------------------------------------------------
   EMOJI AND ICON VISIBILITY
--------------------------------------------------------- */

html[data-hg-theme="light"]
.hg-card-icon,
html[data-hg-theme="light"]
.hg-appliance-summary-icon,
html[data-hg-theme="light"]
.hg-welcome-icon,
html[data-hg-theme="light"]
button span,
html[data-hg-theme="light"]
button p,
html[data-hg-theme="light"]
[data-testid="stSidebarNavLink"] span {{
    visibility: visible !important;
    opacity: 1 !important;
    filter: none !important;
}}


/* =========================================================
   LAST LIGHT-MODE READABILITY FALLBACK
========================================================= */

html[data-hg-theme="light"]
[data-testid="stSelectbox"]
[data-baseweb="select"],
html[data-hg-theme="light"]
[data-testid="stSelectbox"]
[data-baseweb="select"] *,
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
[data-baseweb="select"],
html[data-hg-theme="light"]
[data-testid="stMultiSelect"]
[data-baseweb="select"] * {{
    background-color: #FFFFFF !important;
    background-image: none !important;
    color: #142235 !important;
    -webkit-text-fill-color: #142235 !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stTextInput"]
[data-baseweb],
html[data-hg-theme="light"]
[data-testid="stTextInput"]
[data-baseweb] *,
html[data-hg-theme="light"]
[data-testid="stTextArea"]
[data-baseweb],
html[data-hg-theme="light"]
[data-testid="stTextArea"]
[data-baseweb] *,
html[data-hg-theme="light"]
[data-testid="stNumberInput"]
[data-baseweb],
html[data-hg-theme="light"]
[data-testid="stNumberInput"]
[data-baseweb] *,
html[data-hg-theme="light"]
[data-testid="stDateInput"]
[data-baseweb],
html[data-hg-theme="light"]
[data-testid="stDateInput"]
[data-baseweb] * {{
    background-color: #FFFFFF !important;
    background-image: none !important;
    color: #142235 !important;
    -webkit-text-fill-color: #142235 !important;
    opacity: 1 !important;
}}

html[data-hg-theme="light"]
[data-testid="stFileUploader"] button,
html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] button {{
    background: #EAF5FE !important;
    color: #087EE6 !important;
    border:
        1px solid
        rgba(8, 126, 230, 0.34) !important;
    box-shadow: none !important;
}}

html[data-hg-theme="light"]
[data-testid="stFileUploader"] button *,
html[data-hg-theme="light"]
[data-testid="stFileUploaderDropzone"] button * {{
    color: #087EE6 !important;
    fill: currentColor !important;
    -webkit-text-fill-color: #087EE6 !important;
}}

</style>
"""

    st.markdown(css, unsafe_allow_html=True)

    render_theme_control()


# =========================================================
# Reusable components
# =========================================================


def render_hero(
    title: str,
    subtitle: str,
    eyebrow: str = APP_NAME,
) -> None:
    """Render a page hero containing the app icon."""

    icon_uri = _svg_data_uri(LOGO_ICON_SVG)

    hero_html = (
        '<section class="hg-hero">'
        '<div class="hg-hero-logo">'
        f'<img src="{icon_uri}" alt="{APP_NAME} logo">'
        "</div>"
        f'<div class="hg-eyebrow">✦ {escape(eyebrow)}</div>'
        f'<div class="hg-hero-title">{escape(title)}</div>'
        f'<p class="hg-hero-text">{escape(subtitle)}</p>'
        "</section>"
    )

    st.markdown(hero_html, unsafe_allow_html=True)


def render_status_pill(text: str, status: str = "good") -> str:
    """Return safe HTML for a status pill."""

    class_name = {
        "good": "hg-pill-good",
        "warning": "hg-pill-warning",
        "danger": "hg-pill-danger",
    }.get(status, "hg-pill-good")

    return f'<span class="hg-pill {class_name}">{escape(text)}</span>'


def render_empty_state(icon: str, title: str, message: str) -> None:
    """Render a friendly empty-state card."""

    html = (
        '<div class="hg-card">'
        f'<div class="hg-card-icon">{escape(icon)}</div>'
        f'<div class="hg-card-title">{escape(title)}</div>'
        f'<div class="hg-card-subtitle">{escape(message)}</div>'
        "</div>"
    )

    st.markdown(html, unsafe_allow_html=True)


def render_information_card(
    icon: str,
    title: str,
    subtitle: str,
    message: str | None = None,
    note: str | None = None,
) -> None:
    """Render a reusable information card."""

    html = (
        '<div class="hg-card">'
        f'<div class="hg-card-icon">{escape(icon)}</div>'
        f'<div class="hg-card-title">{escape(title)}</div>'
        f'<div class="hg-card-subtitle">{escape(subtitle)}</div>'
    )

    if message:
        html += f'<div class="hg-card-message">{escape(message)}</div>'

    if note:
        html += f'<div class="hg-card-note">{escape(note)}</div>'

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)