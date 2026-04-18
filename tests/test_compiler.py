"""Tests for the main compiler pipeline.

Input is plain dict (JSON AST), no contingency-dsl-py dependency.
"""

from contingency_dsl_paper import MethodSection, compile_method
from contingency_dsl_paper.references import Reference


def _program(schedule: dict, **kwargs) -> dict:
    """Helper: wrap a schedule node in a minimal Program dict."""
    return {
        "type": "Program",
        "param_decls": kwargs.get("param_decls", []),
        "bindings": [],
        "schedule": schedule,
        **({k: v for k, v in kwargs.items() if k != "param_decls"}),
    }


class TestCompileJEAB:
    """JEAB style (English, default)."""

    def test_simple_fr(self) -> None:
        ast = _program({"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0})
        method = compile_method(ast)
        assert isinstance(method, MethodSection)
        assert "fixed-ratio" in method.procedure
        assert "5" in method.procedure

    def test_simple_vi(self) -> None:
        ast = _program({"type": "Atomic", "dist": "V", "domain": "I", "value": 30.0, "time_unit": "s"})
        method = compile_method(ast)
        assert "variable-interval" in method.procedure
        assert "30-s" in method.procedure

    def test_concurrent(self) -> None:
        ast = _program({
            "type": "Compound",
            "combinator": "Conc",
            "components": [
                {"type": "Atomic", "dist": "V", "domain": "I", "value": 30.0, "time_unit": "s"},
                {"type": "Atomic", "dist": "V", "domain": "I", "value": 60.0, "time_unit": "s"},
            ],
        })
        method = compile_method(ast)
        assert "concurrent" in method.procedure
        assert "VI 30-s" in method.procedure
        assert "VI 60-s" in method.procedure

    def test_extinction(self) -> None:
        ast = _program({"type": "Special", "kind": "EXT"})
        method = compile_method(ast)
        assert "extinction" in method.procedure.lower()

    def test_crf(self) -> None:
        ast = _program({"type": "Special", "kind": "CRF"})
        method = compile_method(ast)
        assert "continuous reinforcement" in method.procedure.lower()

    def test_no_subjects_without_annotations(self) -> None:
        ast = _program({"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0})
        method = compile_method(ast)
        assert method.subjects == ""

    def test_cod_described(self) -> None:
        ast = _program({
            "type": "Compound",
            "combinator": "Conc",
            "components": [
                {"type": "Atomic", "dist": "V", "domain": "I", "value": 30.0, "time_unit": "s"},
                {"type": "Atomic", "dist": "V", "domain": "I", "value": 60.0, "time_unit": "s"},
            ],
            "params": {"COD": {"value": 2.0, "time_unit": "s"}},
        })
        method = compile_method(ast)
        assert "2-s" in method.procedure
        assert "changeover delay" in method.procedure


class TestCompileJABA:
    """J-ABA style (Japanese)."""

    def test_simple_vi_ja(self) -> None:
        ast = _program({"type": "Atomic", "dist": "V", "domain": "I", "value": 30.0, "time_unit": "s"})
        method = compile_method(ast, style="jaba")
        assert "変動時隔" in method.procedure
        assert "30-s" in method.procedure
        assert "スケジュール" in method.procedure

    def test_concurrent_ja(self) -> None:
        ast = _program({
            "type": "Compound",
            "combinator": "Conc",
            "components": [
                {"type": "Atomic", "dist": "V", "domain": "I", "value": 30.0, "time_unit": "s"},
                {"type": "Atomic", "dist": "V", "domain": "I", "value": 60.0, "time_unit": "s"},
            ],
        })
        method = compile_method(ast, style="jaba")
        assert "並立" in method.procedure

    def test_headings_ja(self) -> None:
        ast = _program({"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0})
        method = compile_method(ast, style="jaba")
        text = method.to_text()
        assert "## 方法" in text
        assert "### 手続き" in text


class TestAutoReferences:
    """Automatic citation collection."""

    def test_vi_cites_fleshler_hoffman(self) -> None:
        ast = _program({"type": "Atomic", "dist": "V", "domain": "I", "value": 30.0, "time_unit": "s"})
        method = compile_method(ast)
        keys = [r.key for r in method.references]
        assert "fleshler_hoffman_1962" in keys

    def test_fr_no_fh_citation(self) -> None:
        ast = _program({"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0})
        method = compile_method(ast)
        keys = [r.key for r in method.references]
        assert "fleshler_hoffman_1962" not in keys

    def test_extra_references(self) -> None:
        ast = _program({"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0})
        custom = Reference(
            key="custom_2024",
            authors="Author, A.",
            year=2024,
            title="Custom paper",
            source="Journal",
        )
        method = compile_method(ast, extra_references=[custom])
        keys = [r.key for r in method.references]
        assert "custom_2024" in keys


class TestMethodSectionToText:
    """MethodSection.to_text() formatting."""

    def test_renders_headings(self) -> None:
        from contingency_dsl_paper.style import JEAB
        section = MethodSection(
            subjects="Six rats served.",
            apparatus="Standard chambers.",
            procedure="FR 5 schedule.",
            style=JEAB,
        )
        text = section.to_text()
        assert "## Method" in text
        assert "### Subjects" in text
        assert "### Apparatus" in text
        assert "### Procedure" in text

    def test_omits_empty_sections(self) -> None:
        from contingency_dsl_paper.style import JEAB
        section = MethodSection(procedure="FR 5 schedule.", style=JEAB)
        text = section.to_text()
        assert "Subjects" not in text
        assert "Apparatus" not in text
        assert "### Procedure" in text

    def test_includes_references(self) -> None:
        from contingency_dsl_paper.references import FLESHLER_HOFFMAN_1962
        from contingency_dsl_paper.style import JEAB
        section = MethodSection(
            procedure="VI 30-s schedule.",
            references=(FLESHLER_HOFFMAN_1962,),
            style=JEAB,
        )
        text = section.to_text()
        assert "### References" in text
        assert "Fleshler" in text
