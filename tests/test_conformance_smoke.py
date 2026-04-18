"""Conformance-fixture smoke test.

Loads every ``expected`` AST from ``contingency-dsl/conformance/**/*.json``
and runs it through ``compile_method`` with both JEAB and JABA styles.

Two invariants are checked:

1. The compiler must never raise for a conformant expected AST.
2. When the expected AST is a program-like root (``Program`` /
   ``Experiment`` / ``Paper`` / ``PhaseSequence``), the compiled
   ``MethodSection`` must contain non-empty prose in at least one of
   ``subjects`` / ``apparatus`` / ``procedure``. An empty output for a
   program-like fixture counts as a coverage regression.

Fixtures whose ``expected`` does not describe a program (e.g. the
``representations/t-tau`` transformations whose ``expected`` is a
``{T, tau, duty_cycle}`` record) are only checked for invariant (1):
they must not raise.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from contingency_dsl_paper import compile_method

_REPO = Path(__file__).resolve().parents[2]
_CONFORMANCE_DIR = _REPO / "contingency-dsl" / "conformance"
_PROGRAM_LIKE = {"Program", "Experiment", "Paper", "PhaseSequence"}


def _collect_expected_asts() -> list[tuple[str, dict]]:
    """Return (id, expected_ast) pairs drawn from every conformance fixture."""
    if not _CONFORMANCE_DIR.exists():
        return []
    pairs: list[tuple[str, dict]] = []
    for path in sorted(_CONFORMANCE_DIR.rglob("*.json")):
        try:
            fixtures = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(fixtures, list):
            continue
        for entry in fixtures:
            if not isinstance(entry, dict):
                continue
            expected = entry.get("expected")
            fid = entry.get("id") or f"{path.stem}_{len(pairs)}"
            if isinstance(expected, dict):
                pairs.append((f"{path.parent.name}/{fid}", expected))
    return pairs


_FIXTURES = _collect_expected_asts()


@pytest.mark.skipif(
    not _FIXTURES,
    reason="contingency-dsl conformance fixtures not co-located",
)
@pytest.mark.parametrize("fid,ast", _FIXTURES, ids=[fid for fid, _ in _FIXTURES])
def test_fixture_compiles_without_error(fid: str, ast: dict) -> None:
    """Every conformance fixture must compile under both styles.

    Additionally, program-like fixtures must produce non-empty prose
    somewhere in the resulting Method section (subjects / apparatus /
    procedure). Non-program fixtures (e.g. representation records)
    are only checked for non-raising behavior.
    """
    method_en = compile_method(ast, style="jeab")
    method_ja = compile_method(ast, style="jaba")
    assert method_en is not None
    assert method_ja is not None

    if ast.get("type") in _PROGRAM_LIKE:
        has_prose_en = bool(
            method_en.subjects.strip()
            or method_en.apparatus.strip()
            or method_en.procedure.strip()
        )
        has_prose_ja = bool(
            method_ja.subjects.strip()
            or method_ja.apparatus.strip()
            or method_ja.procedure.strip()
        )
        assert has_prose_en, (
            f"program-like fixture {fid!r} produced an empty JEAB method"
        )
        assert has_prose_ja, (
            f"program-like fixture {fid!r} produced an empty JABA method"
        )
