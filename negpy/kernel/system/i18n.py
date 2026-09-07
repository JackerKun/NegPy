"""Lightweight interface translation.

English is the source language: ``tr`` returns the input unchanged for it. Other
languages supply a ``STRINGS`` catalog mapping the English source text to the
local text. A missing key falls back to the source text, so partial catalogs are
safe and the UI never shows a blank label.

The active language is resolved once at startup (``resolve_language``) and held
here; widgets call ``tr`` as they build themselves. Changing the language
therefore takes effect on the next launch, the same way UI scale does.
"""

from __future__ import annotations

from typing import Optional

# "system" means follow the OS locale at startup.
LANG_SYSTEM = "system"
LANG_EN = "en"
LANG_ZH_CN = "zh_CN"

# Every language the Preferences dialog offers, as (code, display name). The
# display name stays in its own language on purpose, so each entry is readable
# to the person who would pick it.
LANGUAGES: tuple[tuple[str, str], ...] = (
    (LANG_SYSTEM, "System default"),
    (LANG_EN, "English"),
    (LANG_ZH_CN, "简体中文"),
)

_CATALOGS: dict[str, dict[str, str]] = {}
_ACTIVE: str = LANG_EN
_RESOLVED: str = LANG_EN


def _load_catalog(code: str) -> dict[str, str]:
    """The STRINGS catalog for a language, imported lazily and cached."""
    if code in _CATALOGS:
        return _CATALOGS[code]
    table: dict[str, str] = {}
    if code == LANG_ZH_CN:
        from negpy.kernel.system.i18n_zh import STRINGS

        table = STRINGS
    _CATALOGS[code] = table
    return table


def system_language() -> str:
    """The best-supported language for the OS locale, English when nothing better fits."""
    try:
        from PyQt6.QtCore import QLocale

        name = QLocale.system().name()  # e.g. "zh_CN", "en_US"
    except Exception:
        return LANG_EN
    if name.startswith("zh"):
        return LANG_ZH_CN
    return LANG_EN


def resolve_language(code: Optional[str]) -> str:
    """A stored preference into a concrete language code. Unknown or empty values
    behave like "system"."""
    if not code or code == LANG_SYSTEM:
        return system_language()
    known = {c for c, _label in LANGUAGES}
    return code if code in known else system_language()


def set_language(code: str) -> None:
    """Set the active language. Call once at startup, before any widget is built."""
    global _ACTIVE, _RESOLVED
    _ACTIVE = code
    _RESOLVED = resolve_language(code)
    if _RESOLVED != LANG_EN:
        _load_catalog(_RESOLVED)


def active_language() -> str:
    """The stored preference ("system" possible)."""
    return _ACTIVE


def current_language() -> str:
    """The concrete language actually in effect."""
    return _RESOLVED


def tr(text: str) -> str:
    """Translate a UI string into the active language.

    Returns the source text for English, for empty input, and whenever the
    catalog has no entry, so callers can wrap any literal unconditionally.
    """
    if not text or _RESOLVED == LANG_EN:
        return text
    return _load_catalog(_RESOLVED).get(text, text)
