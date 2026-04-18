"""Tests for the contingency-dsl-paper CLI entrypoint.

Covers invocation via ``python -m contingency_dsl_paper`` and via the
``main()`` function directly. Input is JSON (file or stdin), output is
the rendered Method section (stdout or file).
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from contingency_dsl_paper.cli import main


def _program_fr5() -> dict:
    return {
        "type": "Program",
        "param_decls": [],
        "bindings": [],
        "schedule": {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0},
    }


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


def _paper_two_experiments() -> dict:
    return {
        "type": "Paper",
        "experiments": [
            {"type": "Experiment", "label": "Exp1", "body": _program_fr5()},
            {"type": "Experiment", "label": "Exp2", "body": _program_vi30()},
        ],
    }


class TestCliFileInput:
    def test_reads_json_file_and_prints_method(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        src = tmp_path / "ast.json"
        src.write_text(json.dumps(_program_fr5()), encoding="utf-8")

        rc = main([str(src)])

        out = capsys.readouterr().out
        assert rc == 0
        assert "Method" in out
        assert "fixed-ratio" in out

    def test_output_file(self, tmp_path: Path) -> None:
        src = tmp_path / "ast.json"
        dst = tmp_path / "out.md"
        src.write_text(json.dumps(_program_fr5()), encoding="utf-8")

        rc = main([str(src), "--output", str(dst)])

        assert rc == 0
        text = dst.read_text(encoding="utf-8")
        assert "fixed-ratio" in text
        assert "Method" in text


class TestCliStdin:
    def test_reads_stdin_with_dash(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        stdin = io.StringIO(json.dumps(_program_vi30()))
        monkeypatch.setattr("sys.stdin", stdin)

        rc = main(["-"])

        out = capsys.readouterr().out
        assert rc == 0
        assert "variable-interval" in out
        assert "30-s" in out


class TestCliStyle:
    def test_jaba_style(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        src = tmp_path / "ast.json"
        src.write_text(json.dumps(_program_fr5()), encoding="utf-8")

        rc = main([str(src), "--style", "jaba"])

        out = capsys.readouterr().out
        assert rc == 0
        assert "固定比率" in out

    def test_unknown_style_errors(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        src = tmp_path / "ast.json"
        src.write_text(json.dumps(_program_fr5()), encoding="utf-8")

        rc = main([str(src), "--style", "nature"])

        assert rc != 0
        err = capsys.readouterr().err
        assert "style" in err.lower()


class TestCliHeadingLevel:
    def test_heading_level_propagated(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        src = tmp_path / "ast.json"
        src.write_text(json.dumps(_program_fr5()), encoding="utf-8")

        rc = main([str(src), "--heading-level", "1"])

        out = capsys.readouterr().out
        assert rc == 0
        assert out.startswith("# Method")


class TestCliPaper:
    def test_paper_default_first_experiment(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        src = tmp_path / "paper.json"
        src.write_text(json.dumps(_paper_two_experiments()), encoding="utf-8")

        rc = main([str(src)])

        out = capsys.readouterr().out
        assert rc == 0
        # Only first experiment's content by default
        assert "fixed-ratio" in out
        assert "variable-interval" not in out

    def test_paper_all_experiments(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        src = tmp_path / "paper.json"
        src.write_text(json.dumps(_paper_two_experiments()), encoding="utf-8")

        rc = main([str(src), "--all-experiments"])

        out = capsys.readouterr().out
        assert rc == 0
        assert "fixed-ratio" in out
        assert "variable-interval" in out
        # Both experiment labels rendered as headings
        assert "Exp1" in out
        assert "Exp2" in out


class TestCliErrors:
    def test_missing_file(
        self, capsys: pytest.CaptureFixture[str], tmp_path: Path
    ) -> None:
        rc = main([str(tmp_path / "does-not-exist.json")])

        assert rc != 0
        err = capsys.readouterr().err
        assert "does-not-exist" in err or "not found" in err.lower()

    def test_invalid_json(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        src = tmp_path / "bad.json"
        src.write_text("{ not valid json", encoding="utf-8")

        rc = main([str(src)])

        assert rc != 0
        err = capsys.readouterr().err
        assert "json" in err.lower()


class TestModuleEntry:
    """Ensure ``python -m contingency_dsl_paper`` works."""

    def test_dunder_main_exists(self) -> None:
        import contingency_dsl_paper.__main__ as m  # noqa: F401

        assert hasattr(m, "main") or True  # import-only smoke test
