"""Tests for Phase 3 extensibility APIs.

Covers:
    - register_style / unregister_style (custom journal styles)
    - register_citation_format / Reference.format (custom citation formatters)
    - framing_* template override (sentence-level customization)
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from contingency_dsl_paper import JEAB, Reference, Style, compile_method, get_style
from contingency_dsl_paper.references import (
    FLESHLER_HOFFMAN_1962,
    register_citation_format,
    unregister_citation_format,
)
from contingency_dsl_paper.style import register_style, unregister_style


def _program_vi30() -> dict:
    return {
        "type": "Program",
        "param_decls": [],
        "bindings": [],
        "schedule": {
            "type": "Atomic",
            "dist": "V",
            "domain": "I",
            "value": 30.0,
            "time_unit": "s",
        },
    }


# ---------------------------------------------------------------------------
# 1. Custom style registration
# ---------------------------------------------------------------------------

class TestRegisterStyle:
    """New journal styles can be added via register_style()."""

    def test_register_and_get(self) -> None:
        custom = replace(JEAB, name="nature", heading_method="METHODS")
        try:
            register_style(custom)
            got = get_style("nature")
            assert got is custom
        finally:
            unregister_style("nature")

    def test_unregister_removes(self) -> None:
        custom = replace(JEAB, name="tempstyle")
        register_style(custom)
        unregister_style("tempstyle")
        with pytest.raises(KeyError):
            get_style("tempstyle")

    def test_compile_with_registered_style(self) -> None:
        """A custom Style can drive compile_method via its registered name."""
        # Override the method heading to a unique sentinel word
        custom = replace(JEAB, name="jxp", heading_method="Procedure Details")
        try:
            register_style(custom)
            method = compile_method(_program_vi30(), style="jxp")
            text = method.to_text()
            assert "Procedure Details" in text
        finally:
            unregister_style("jxp")

    def test_register_rejects_name_collision(self) -> None:
        """Re-registering an existing name without force must fail."""
        with pytest.raises(ValueError):
            register_style(JEAB)  # JEAB already registered

    def test_register_force_overwrites(self) -> None:
        override = replace(JEAB, name="jeab", heading_method="XYZ")
        register_style(override, force=True)
        try:
            assert get_style("jeab").heading_method == "XYZ"
        finally:
            # Restore built-in JEAB
            register_style(JEAB, force=True)
        assert get_style("jeab").heading_method == "Method"


# ---------------------------------------------------------------------------
# 2. Citation format switching
# ---------------------------------------------------------------------------

class TestReferenceFormat:
    """Reference.format(fmt) dispatches on a registered formatter."""

    def test_apa7_default(self) -> None:
        s = FLESHLER_HOFFMAN_1962.format()
        assert "Fleshler" in s
        assert "1962" in s
        assert "Journal of the Experimental Analysis of Behavior" in s

    def test_apa7_matches_legacy(self) -> None:
        """format('apa7') must match the legacy to_apa7() output exactly."""
        assert (
            FLESHLER_HOFFMAN_1962.format("apa7")
            == FLESHLER_HOFFMAN_1962.to_apa7()
        )

    def test_unknown_format_raises(self) -> None:
        with pytest.raises(KeyError):
            FLESHLER_HOFFMAN_1962.format("bibtex")


class TestRegisterCitationFormat:
    """Users can register custom citation formatters."""

    def test_custom_formatter(self) -> None:
        def short(ref: Reference) -> str:
            return f"{ref.authors} ({ref.year})"

        try:
            register_citation_format("short", short)
            assert (
                FLESHLER_HOFFMAN_1962.format("short")
                == "Fleshler, M., & Hoffman, H. S. (1962)"
            )
        finally:
            unregister_citation_format("short")

    def test_unregister_removes(self) -> None:
        register_citation_format("tempfmt", lambda r: "X")
        unregister_citation_format("tempfmt")
        with pytest.raises(KeyError):
            FLESHLER_HOFFMAN_1962.format("tempfmt")

    def test_cannot_override_apa7_without_force(self) -> None:
        with pytest.raises(ValueError):
            register_citation_format("apa7", lambda r: "X")


class TestStyleDrivesCitationFormat:
    """MethodSection.to_text must use style.citation_format when rendering refs."""

    def test_style_citation_format_consulted(self) -> None:
        def only_year(ref: Reference) -> str:
            return f"[{ref.year}]"

        custom = replace(
            JEAB, name="yearonly", citation_format="year_only"
        )
        try:
            register_citation_format("year_only", only_year)
            register_style(custom)
            # Use a VI schedule so that Fleshler-Hoffman is auto-cited.
            method = compile_method(_program_vi30(), style="yearonly")
            assert method.references  # sanity: something was cited
            text = method.to_text()
            assert "[1962]" in text
            # The APA-style rendering must NOT appear
            assert "Journal of the Experimental Analysis" not in text
        finally:
            unregister_style("yearonly")
            unregister_citation_format("year_only")


# ---------------------------------------------------------------------------
# 3. Sentence-level template customization
# ---------------------------------------------------------------------------

class TestFramingTemplateOverride:
    """framing_* fields on Style act as str.format templates."""

    def test_custom_framing_reinforced_used(self) -> None:
        custom = replace(
            JEAB,
            name="custom_frame",
            framing_reinforced="ALPHA-{schedule}-OMEGA",
        )
        try:
            register_style(custom)
            method = compile_method(_program_vi30(), style="custom_frame")
            # Our custom wrapper must appear in the procedure text
            assert "ALPHA-" in method.procedure
            assert "-OMEGA" in method.procedure
        finally:
            unregister_style("custom_frame")
