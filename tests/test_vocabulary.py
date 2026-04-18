"""Tests for vocabulary mapping (schedule term -> natural language)."""

from contingency_dsl2procedure.style import JABA, JEAB
from contingency_dsl2procedure.vocabulary import (
    format_atomic_abbrev,
    format_atomic_full,
    format_combinator,
)


class TestFormatAtomicAbbrevJEAB:
    """JEAB abbreviated format: 'FR 5', 'VI 30-s'."""

    def test_fixed_ratio(self) -> None:
        node = {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0}
        assert format_atomic_abbrev(node, JEAB) == "FR 5"

    def test_variable_interval(self) -> None:
        node = {"type": "Atomic", "dist": "V", "domain": "I", "value": 30.0, "time_unit": "s"}
        assert format_atomic_abbrev(node, JEAB) == "VI 30-s"

    def test_fixed_time(self) -> None:
        node = {"type": "Atomic", "dist": "F", "domain": "T", "value": 20.0, "time_unit": "s"}
        assert format_atomic_abbrev(node, JEAB) == "FT 20-s"

    def test_variable_ratio(self) -> None:
        node = {"type": "Atomic", "dist": "V", "domain": "R", "value": 20.0}
        assert format_atomic_abbrev(node, JEAB) == "VR 20"

    def test_random_interval_ms(self) -> None:
        node = {"type": "Atomic", "dist": "R", "domain": "I", "value": 500.0, "time_unit": "ms"}
        assert format_atomic_abbrev(node, JEAB) == "RI 500-ms"


class TestFormatAtomicFullJEAB:
    """Full name on first mention: 'fixed-ratio (FR) 5'."""

    def test_fixed_ratio(self) -> None:
        node = {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0}
        assert format_atomic_full(node, JEAB) == "fixed-ratio (FR) 5"

    def test_variable_interval(self) -> None:
        node = {"type": "Atomic", "dist": "V", "domain": "I", "value": 30.0, "time_unit": "s"}
        assert format_atomic_full(node, JEAB) == "variable-interval (VI) 30-s"


class TestFormatAtomicFullJABA:
    """J-ABA full name: '固定比率 (FR) 5'."""

    def test_fixed_ratio(self) -> None:
        node = {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0}
        assert format_atomic_full(node, JABA) == "固定比率 (FR) 5"

    def test_variable_interval(self) -> None:
        node = {"type": "Atomic", "dist": "V", "domain": "I", "value": 30.0, "time_unit": "s"}
        assert format_atomic_full(node, JABA) == "変動時隔 (VI) 30-s"


class TestFormatCombinator:
    def test_concurrent_jeab(self) -> None:
        assert format_combinator("Conc", JEAB) == "concurrent"

    def test_concurrent_jaba(self) -> None:
        assert format_combinator("Conc", JABA) == "並立"

    def test_chained_jeab(self) -> None:
        assert format_combinator("Chain", JEAB) == "chained"

    def test_multiple_jaba(self) -> None:
        assert format_combinator("Mult", JABA) == "多元"
