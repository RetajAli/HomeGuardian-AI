from __future__ import annotations

import streamlit as st


# =========================================================
# Small sun / moon theme component
# =========================================================

COMPONENT_HTML = """
<div class="sun-moon-theme-control">
  <label
    for="homeguardian-theme-toggle"
    class="themeToggle st-sunMoonThemeToggleBtn"
  >
    <input
      type="checkbox"
      id="homeguardian-theme-toggle"
      class="themeToggleInput"
      aria-label="Switch light and dark mode"
    />

    <svg
      viewBox="0 0 20 20"
      fill="currentColor"
      stroke="none"
      aria-hidden="true"
      focusable="false"
    >
      <mask id="homeguardian-moon-mask">
        <rect
          x="0"
          y="0"
          width="20"
          height="20"
          fill="white"
        ></rect>

        <circle
          cx="11"
          cy="3"
          r="8"
          fill="black"
        ></circle>
      </mask>

      <circle
        class="sunMoon"
        cx="10"
        cy="10"
        r="8"
        mask="url(#homeguardian-moon-mask)"
      ></circle>

      <g>
        <circle
          class="sunRay sunRay1"
          cx="18"
          cy="10"
          r="1.5"
        ></circle>

        <circle
          class="sunRay sunRay2"
          cx="14"
          cy="16.928"
          r="1.5"
        ></circle>

        <circle
          class="sunRay sunRay3"
          cx="6"
          cy="16.928"
          r="1.5"
        ></circle>

        <circle
          class="sunRay sunRay4"
          cx="2"
          cy="10"
          r="1.5"
        ></circle>

        <circle
          class="sunRay sunRay5"
          cx="6"
          cy="3.1718"
          r="1.5"
        ></circle>

        <circle
          class="sunRay sunRay6"
          cx="14"
          cy="3.1718"
          r="1.5"
        ></circle>
      </g>
    </svg>
  </label>
</div>
"""


# Based on the open-source pure-CSS sun/moon toggle supplied by the user.
# Preserve any attribution required by the original source or licence.
COMPONENT_CSS = r"""
:host,
html,
body {
  display: block;
  width: 48px;
  height: 48px;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
  background: transparent !important;
  color: transparent;
  font-family: var(--st-font);
  scrollbar-width: none !important;
}

:host::-webkit-scrollbar,
html::-webkit-scrollbar,
body::-webkit-scrollbar,
*::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
}

* {
  box-sizing: border-box;
}

.sun-moon-theme-control {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background: transparent;
}

.themeToggle {
  position: relative;
  display: block;
  flex: 0 0 auto;
  width: 42px;
  height: 42px;
  margin: 0;
  padding: 0;
  overflow: visible;
  color: #dce8ff;
  cursor: pointer;
  border-radius: 50%;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
  transition:
    color 0.22s ease,
    filter 0.22s ease,
    transform 0.18s ease;
}

.st-sunMoonThemeToggleBtn .themeToggleInput {
  position: absolute;
  inset: 0;
  z-index: 2;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  opacity: 0;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  border: 0;
  outline: 0;
}

.st-sunMoonThemeToggleBtn svg {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
  padding: 3px;
  overflow: visible;
  color: inherit;
  pointer-events: none;
  transform: rotate(40deg);
  transform-origin: center;
  transition:
    transform 0.4s ease,
    color 0.25s ease,
    filter 0.25s ease;
}

.st-sunMoonThemeToggleBtn svg .sunMoon {
  transform-origin: center;
  transition: inherit;
  transform: scale(1);
}

.st-sunMoonThemeToggleBtn svg .sunRay {
  transform-origin: center;
  transform: scale(0);
}

.st-sunMoonThemeToggleBtn svg mask > circle {
  transition:
    transform
    0.64s
    cubic-bezier(
      0.41,
      0.64,
      0.32,
      1.575
    );
  transform: translate(0, 0);
}

.st-sunMoonThemeToggleBtn svg .sunRay2 {
  animation-delay: 0.05s !important;
}

.st-sunMoonThemeToggleBtn svg .sunRay3 {
  animation-delay: 0.10s !important;
}

.st-sunMoonThemeToggleBtn svg .sunRay4 {
  animation-delay: 0.17s !important;
}

.st-sunMoonThemeToggleBtn svg .sunRay5 {
  animation-delay: 0.25s !important;
}

.st-sunMoonThemeToggleBtn svg .sunRay6 {
  animation-delay: 0.29s !important;
}


/* Checked = light mode / sun */

.st-sunMoonThemeToggleBtn
.themeToggleInput:checked
+ svg {
  color: #f4b942;
  transform: rotate(90deg);
  filter:
    drop-shadow(
      0 0 5px
      rgba(244, 185, 66, 0.28)
    );
}

.st-sunMoonThemeToggleBtn
.themeToggleInput:checked
+ svg
mask > circle {
  transform: translate(16px, -3px);
}

.st-sunMoonThemeToggleBtn
.themeToggleInput:checked
+ svg
.sunMoon {
  transform: scale(0.55);
}

.st-sunMoonThemeToggleBtn
.themeToggleInput:checked
+ svg
.sunRay {
  animation:
    showRay1832
    0.4s ease
    0s
    1 forwards;
}


/* Calm interaction */

.themeToggle:hover {
  color: #f3f7ff;
  transform: scale(1.04);
}

.themeToggle:active {
  transform: scale(0.95);
}

.themeToggleInput:focus-visible + svg {
  border-radius: 50%;
  box-shadow:
    0 0 0 3px
    rgba(22, 140, 255, 0.28);
}

@keyframes showRay1832 {
  from {
    transform: scale(0);
  }

  to {
    transform: scale(1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .themeToggle,
  .st-sunMoonThemeToggleBtn svg,
  .st-sunMoonThemeToggleBtn svg *,
  .st-sunMoonThemeToggleBtn svg mask > circle {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }
}
"""


# Important:
# This component changes the theme directly in the browser.
# It intentionally does NOT call setStateValue when clicked.
# Therefore Streamlit does not rerun the Python app and the page does not flash.
COMPONENT_JS = r"""
export default function(component) {
  const {
    parentElement,
    data
  } = component;

  const checkbox = parentElement.querySelector(
    "#homeguardian-theme-toggle"
  );

  const storageKey = "homeguardian-theme";
  const patchAttribute = "data-hg-light-patched";

  function readStoredTheme() {
    try {
      const stored =
        window.localStorage.getItem(
          storageKey
        );

      if (stored === "light") {
        return false;
      }

      if (stored === "dark") {
        return true;
      }
    } catch (_) {
      // Browser storage may be unavailable.
    }

    return null;
  }

  function storeTheme(dark) {
    try {
      window.localStorage.setItem(
        storageKey,
        dark ? "dark" : "light"
      );
    } catch (_) {
      // The current page still switches correctly.
    }
  }

  function rgbValues(value) {
    const match = String(value).match(
      /rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)/
    );

    if (!match) {
      return null;
    }

    return [
      Number(match[1]),
      Number(match[2]),
      Number(match[3])
    ];
  }

  function isDarkBackground(value) {
    const rgb = rgbValues(value);

    if (!rgb) {
      return false;
    }

    const [red, green, blue] = rgb;

    const luminance =
      0.2126 * red
      + 0.7152 * green
      + 0.0722 * blue;

    return luminance < 105;
  }

  function rememberAndSet(
    element,
    property,
    value
  ) {
    if (!element.hasAttribute(patchAttribute)) {
      element.setAttribute(
        patchAttribute,
        "true"
      );
    }

    element.style.setProperty(
      property,
      value,
      "important"
    );
  }

  function clearLightPatches() {
    document.querySelectorAll(
      `[${patchAttribute}]`
    ).forEach((element) => {
      [
        "background",
        "background-color",
        "background-image",
        "color",
        "-webkit-text-fill-color",
        "border-color",
        "box-shadow",
        "opacity",
        "fill"
      ].forEach((property) => {
        element.style.removeProperty(
          property
        );
      });

      element.removeAttribute(
        patchAttribute
      );
    });
  }

  function makeTextReadable(root) {
    if (!root) {
      return;
    }

    const elements = [
      root,
      ...root.querySelectorAll("*")
    ];

    elements.forEach((element) => {
      const tagName =
        element.tagName?.toLowerCase();

      if (
        tagName === "style"
        || tagName === "script"
      ) {
        return;
      }

      rememberAndSet(
        element,
        "opacity",
        "1"
      );

      rememberAndSet(
        element,
        "color",
        "#142235"
      );

      rememberAndSet(
        element,
        "-webkit-text-fill-color",
        "#142235"
      );

      if (
        tagName === "svg"
        || tagName === "path"
      ) {
        rememberAndSet(
          element,
          "fill",
          "currentColor"
        );
      }
    });
  }

  function makeDarkSurfacesWhite(root) {
    if (!root) {
      return;
    }

    const elements = [
      root,
      ...root.querySelectorAll("*")
    ];

    elements.forEach((element) => {
      const computed =
        window.getComputedStyle(element);

      if (
        isDarkBackground(
          computed.backgroundColor
        )
      ) {
        rememberAndSet(
          element,
          "background",
          "#FFFFFF"
        );

        rememberAndSet(
          element,
          "background-color",
          "#FFFFFF"
        );

        rememberAndSet(
          element,
          "background-image",
          "none"
        );
      }

      if (
        computed.borderStyle !== "none"
      ) {
        rememberAndSet(
          element,
          "border-color",
          "rgba(30, 73, 110, 0.18)"
        );
      }

      if (
        computed.boxShadow !== "none"
      ) {
        rememberAndSet(
          element,
          "box-shadow",
          "none"
        );
      }
    });

    makeTextReadable(root);
  }

  function patchSelectBoxes() {
    document.querySelectorAll(
      [
        '[data-testid="stSelectbox"]',
        '[data-testid="stMultiSelect"]'
      ].join(",")
    ).forEach((root) => {
      makeDarkSurfacesWhite(root);

      root.querySelectorAll(
        [
          '[data-baseweb="select"]',
          '[data-baseweb="select"] > div',
          '[data-baseweb="select"] > div > div'
        ].join(",")
      ).forEach((element) => {
        rememberAndSet(
          element,
          "background",
          "#FFFFFF"
        );

        rememberAndSet(
          element,
          "background-color",
          "#FFFFFF"
        );

        rememberAndSet(
          element,
          "background-image",
          "none"
        );

        rememberAndSet(
          element,
          "color",
          "#142235"
        );

        rememberAndSet(
          element,
          "-webkit-text-fill-color",
          "#142235"
        );

        rememberAndSet(
          element,
          "border-color",
          "rgba(30, 73, 110, 0.18)"
        );

        rememberAndSet(
          element,
          "box-shadow",
          "none"
        );
      });
    });
  }

  function patchInputs() {
    document.querySelectorAll(
      [
        '[data-testid="stTextInput"]',
        '[data-testid="stTextArea"]',
        '[data-testid="stNumberInput"]',
        '[data-testid="stDateInput"]'
      ].join(",")
    ).forEach((root) => {
      makeDarkSurfacesWhite(root);

      root.querySelectorAll(
        "input, textarea"
      ).forEach((element) => {
        rememberAndSet(
          element,
          "background",
          "#FFFFFF"
        );

        rememberAndSet(
          element,
          "background-color",
          "#FFFFFF"
        );

        rememberAndSet(
          element,
          "color",
          "#142235"
        );

        rememberAndSet(
          element,
          "-webkit-text-fill-color",
          "#142235"
        );

        rememberAndSet(
          element,
          "opacity",
          "1"
        );
      });
    });
  }

  function patchFileUploader() {
    document.querySelectorAll(
      '[data-testid="stFileUploader"]'
    ).forEach((root) => {
      makeDarkSurfacesWhite(root);

      root.querySelectorAll(
        "button"
      ).forEach((button) => {
        rememberAndSet(
          button,
          "background",
          "#EAF5FE"
        );

        rememberAndSet(
          button,
          "background-color",
          "#EAF5FE"
        );

        rememberAndSet(
          button,
          "background-image",
          "none"
        );

        rememberAndSet(
          button,
          "color",
          "#087EE6"
        );

        rememberAndSet(
          button,
          "-webkit-text-fill-color",
          "#087EE6"
        );

        rememberAndSet(
          button,
          "border-color",
          "rgba(8, 126, 230, 0.34)"
        );

        rememberAndSet(
          button,
          "box-shadow",
          "none"
        );

        button.querySelectorAll("*")
          .forEach((child) => {
            rememberAndSet(
              child,
              "color",
              "#087EE6"
            );

            rememberAndSet(
              child,
              "-webkit-text-fill-color",
              "#087EE6"
            );

            rememberAndSet(
              child,
              "fill",
              "currentColor"
            );
          });
      });
    });
  }

  function patchChatInput() {
    document.querySelectorAll(
      '[data-testid="stChatInput"]'
    ).forEach((root) => {
      makeDarkSurfacesWhite(root);

      rememberAndSet(
        root,
        "background",
        "#FFFFFF"
      );

      rememberAndSet(
        root,
        "background-color",
        "#FFFFFF"
      );

      rememberAndSet(
        root,
        "border-color",
        "rgba(30, 73, 110, 0.16)"
      );

      rememberAndSet(
        root,
        "box-shadow",
        "0 8px 20px rgba(32, 71, 105, 0.09)"
      );

      root.querySelectorAll(
        "textarea"
      ).forEach((textarea) => {
        rememberAndSet(
          textarea,
          "background",
          "#FFFFFF"
        );

        rememberAndSet(
          textarea,
          "background-color",
          "#FFFFFF"
        );

        rememberAndSet(
          textarea,
          "color",
          "#142235"
        );

        rememberAndSet(
          textarea,
          "-webkit-text-fill-color",
          "#142235"
        );
      });

      root.querySelectorAll(
        "button"
      ).forEach((button) => {
        rememberAndSet(
          button,
          "background",
          "linear-gradient(135deg, #168CFF, #00BFD2)"
        );

        rememberAndSet(
          button,
          "color",
          "#FFFFFF"
        );

        rememberAndSet(
          button,
          "border-color",
          "transparent"
        );

        button.querySelectorAll("*")
          .forEach((child) => {
            rememberAndSet(
              child,
              "color",
              "#FFFFFF"
            );

            rememberAndSet(
              child,
              "fill",
              "currentColor"
            );
          });
      });
    });

    document.querySelectorAll(
      [
        '[data-testid="stBottomBlockContainer"]',
        '[data-testid="stBottom"]',
        '.stChatFloatingInputContainer'
      ].join(",")
    ).forEach((element) => {
      rememberAndSet(
        element,
        "background",
        "transparent"
      );

      rememberAndSet(
        element,
        "background-color",
        "transparent"
      );

      rememberAndSet(
        element,
        "background-image",
        "none"
      );

      rememberAndSet(
        element,
        "box-shadow",
        "none"
      );
    });
  }

  function patchMenusAndDialogs() {
    document.querySelectorAll(
      [
        'div[data-baseweb="popover"]',
        'div[data-baseweb="menu"]',
        'ul[role="listbox"]',
        'li[role="option"]',
        'div[role="dialog"]',
        '[data-baseweb="calendar"]'
      ].join(",")
    ).forEach((root) => {
      makeDarkSurfacesWhite(root);
    });
  }

  function patchLightWidgets() {
    patchSelectBoxes();
    patchInputs();
    patchFileUploader();
    patchChatInput();
    patchMenusAndDialogs();
  }

  function applyTheme(dark) {
    const themeName =
      dark ? "dark" : "light";

    document.documentElement.dataset.hgTheme =
      themeName;

    document.documentElement.style.colorScheme =
      themeName;

    document.body.dataset.hgTheme =
      themeName;

    checkbox.checked = !dark;

    checkbox.setAttribute(
      "aria-checked",
      String(!dark)
    );

    checkbox.setAttribute(
      "aria-label",
      dark
        ? "Switch to light mode"
        : "Switch to dark mode"
    );

    if (dark) {
      clearLightPatches();
      return;
    }

    window.requestAnimationFrame(
      patchLightWidgets
    );

    window.setTimeout(
      patchLightWidgets,
      60
    );

    window.setTimeout(
      patchLightWidgets,
      250
    );
  }

  const defaultDark = Boolean(
    data?.default_dark ?? true
  );

  const storedTheme =
    readStoredTheme();

  const activeTheme =
    storedTheme === null
      ? defaultDark
      : storedTheme;

  let patchScheduled = false;

  const observer = new MutationObserver(() => {
    if (
      document.documentElement
        .dataset.hgTheme !== "light"
    ) {
      return;
    }

    if (patchScheduled) {
      return;
    }

    patchScheduled = true;

    window.requestAnimationFrame(() => {
      patchScheduled = false;
      patchLightWidgets();
    });
  });

  observer.observe(
    document.body,
    {
      childList: true,
      subtree: true
    }
  );

  const periodicPatch =
    window.setInterval(() => {
      if (
        document.documentElement
          .dataset.hgTheme === "light"
      ) {
        patchLightWidgets();
      }
    }, 700);

  applyTheme(activeTheme);

  checkbox.onchange = () => {
    const dark =
      !checkbox.checked;

    storeTheme(dark);
    applyTheme(dark);
  };

  return () => {
    checkbox.onchange = null;
    observer.disconnect();
    window.clearInterval(
      periodicPatch
    );
  };
}
"""


# =========================================================
# Component registration
# =========================================================

def _component_v2_available() -> bool:
    """Return whether Components v2 is available."""

    return bool(
        getattr(
            getattr(
                st,
                "components",
                None,
            ),
            "v2",
            None,
        )
    )


if _component_v2_available():
    _THEME_TOGGLE = (
        st.components.v2.component(
            name=(
                "homeguardian_"
                "smooth_sun_moon_toggle"
            ),
            html=COMPONENT_HTML,
            css=COMPONENT_CSS,
            js=COMPONENT_JS,
            isolate_styles=True,
        )
    )
else:
    _THEME_TOGGLE = None


# =========================================================
# Public function
# =========================================================

def cosmic_theme_toggle(
    *,
    key: str = (
        "homeguardian_cosmic_theme"
    ),
    default_dark: bool = True,
) -> bool:
    """
    Render the no-rerun sun/moon switch.

    The old function name is kept so core/ui.py
    does not need a new import.
    """

    if _THEME_TOGGLE is None:
        st.warning(
            "Upgrade Streamlit to use the "
            "animated theme switch."
        )

        st.caption(
            "Run: pip install --upgrade streamlit"
        )

        return default_dark

    _THEME_TOGGLE(
        data={
            "default_dark": default_dark,
        },
        key=key,
        width=48,
        height=48,
    )

    return default_dark