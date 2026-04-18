"""Schedule term -> natural language mapping.

Works with plain dict AST nodes (no contingency-dsl-py dependency).
Formatting is controlled by the Style object for journal-specific conventions.

JEAB conventions:
- Abbreviated schedule names in text: "VI 30-s" (space before value, hyphen-s)
- Full names on first mention: "variable-interval (VI) 30-s schedule"

J-ABA conventions:
- Abbreviated: "VI 30-s" (same as JEAB; abbreviations are kept in English)
- Full names on first mention: "変動時隔 (VI) 30-s スケジュール"
"""

from __future__ import annotations

from .ast_types import AtomicNode, CombinatorStr
from .style import JEAB, Style


def format_atomic_abbrev(node: AtomicNode, style: Style = JEAB) -> str:
    """Format an atomic schedule in abbreviated style.

    Examples (JEAB): FR 5, VI 30-s, FT 20-s, VR 20
    """
    dist = node["dist"]   # "F", "V", "R"
    domain = node["domain"]  # "R", "I", "T"
    abbrev = f"{dist}{domain}"
    value = _format_value(node["value"])

    if domain in ("I", "T"):
        unit = _format_time_unit(node.get("time_unit"), style)
        sep = " " if style.abbrev_space else ""
        return f"{abbrev}{sep}{value}{unit}"
    else:
        sep = " " if style.abbrev_space else ""
        return f"{abbrev}{sep}{value}"


def format_atomic_full(node: AtomicNode, style: Style = JEAB) -> str:
    """Format an atomic schedule with full name on first mention.

    Examples (JEAB): fixed-ratio (FR) 5, variable-interval (VI) 30-s
    Examples (JABA): 固定比率 (FR) 5, 変動時隔 (VI) 30-s
    """
    dist = node["dist"]
    domain = node["domain"]
    abbrev = f"{dist}{domain}"

    dist_name = style.distribution_names.get(dist, dist)
    domain_name = style.domain_names.get(domain, domain)
    value = _format_value(node["value"])

    if style.locale == "ja":
        full_name = f"{dist_name}{domain_name}"
    else:
        full_name = f"{dist_name}-{domain_name}"

    if domain in ("I", "T"):
        unit = _format_time_unit(node.get("time_unit"), style)
        return f"{full_name} ({abbrev}) {value}{unit}"
    else:
        return f"{full_name} ({abbrev}) {value}"


def format_combinator(combinator: CombinatorStr, style: Style = JEAB) -> str:
    """Return the full name of a combinator in the given style."""
    return style.combinator_names.get(combinator, combinator)


# --- Helpers ---

def _format_value(value: float | None) -> str:
    """Format a numeric value, dropping .0 for integers. None → empty."""
    if value is None:
        return ""
    try:
        if value == int(value):
            return str(int(value))
    except (TypeError, ValueError):
        return str(value)
    return str(value)


def _format_time_unit(unit: str | None, style: Style = JEAB) -> str:
    """Format time unit with style-appropriate separator.

    JEAB: "-s", "-ms", "-min" (hyphenated)
    """
    u = unit or "s"
    if style.time_unit_hyphen:
        return f"-{u}"
    else:
        return f" {u}"
