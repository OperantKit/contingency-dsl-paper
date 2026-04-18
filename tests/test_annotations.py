"""Phase 2 tests: annotation integration."""

from contingency_dsl_paper import compile_method


def _full_program() -> dict:
    """Realistic program with all annotation types."""
    return {
        "type": "Program",
        "program_annotations": [
            {"type": "Annotation", "keyword": "species", "positional": "rat"},
            {"type": "Annotation", "keyword": "strain", "positional": "Sprague-Dawley"},
            {"type": "Annotation", "keyword": "n", "positional": 6},
            {"type": "Annotation", "keyword": "deprivation", "params": {"hours": 23, "target": "food"}},
            {"type": "Annotation", "keyword": "history", "positional": "naive"},
            {"type": "Annotation", "keyword": "chamber", "positional": "med-associates", "params": {"model": "ENV-007"}},
            {"type": "Annotation", "keyword": "operandum", "positional": "left_lever", "params": {"component": 1}},
            {"type": "Annotation", "keyword": "operandum", "positional": "right_lever", "params": {"component": 2}},
            {"type": "Annotation", "keyword": "hardware", "positional": "MED-PC IV"},
            {"type": "Annotation", "keyword": "reinforcer", "positional": "food pellet"},
            {"type": "Annotation", "keyword": "session_end", "params": {"rule": "first", "time": {"value": 60, "time_unit": "min"}, "reinforcers": 60}},
            {"type": "Annotation", "keyword": "steady_state", "params": {"window_sessions": 5, "max_change_pct": 10, "measure": "rate", "min_sessions": 10}},
        ],
        "param_decls": [{"type": "ParamDecl", "name": "COD", "value": 2.0, "time_unit": "s"}],
        "bindings": [],
        "schedule": {
            "type": "Compound",
            "combinator": "Conc",
            "components": [
                {"type": "Atomic", "dist": "V", "domain": "I", "value": 30.0, "time_unit": "s"},
                {"type": "Atomic", "dist": "V", "domain": "I", "value": 60.0, "time_unit": "s"},
            ],
        },
    }


class TestSubjectsJEAB:
    def test_species_and_n(self) -> None:
        method = compile_method(_full_program())
        assert "Six" in method.subjects
        assert "rats" in method.subjects

    def test_strain(self) -> None:
        method = compile_method(_full_program())
        assert "Sprague-Dawley" in method.subjects

    def test_deprivation(self) -> None:
        method = compile_method(_full_program())
        assert "23 hr" in method.subjects
        assert "food deprivation" in method.subjects

    def test_naive(self) -> None:
        method = compile_method(_full_program())
        assert "experimentally naive" in method.subjects

    def test_no_subjects_without_annotations(self) -> None:
        ast = {"type": "Program", "param_decls": [], "bindings": [],
               "schedule": {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0}}
        method = compile_method(ast)
        assert method.subjects == ""


class TestSubjectsJABA:
    def test_species_ja(self) -> None:
        method = compile_method(_full_program(), style="jaba")
        assert "ラット" in method.subjects
        assert "6匹" in method.subjects

    def test_strain_ja(self) -> None:
        method = compile_method(_full_program(), style="jaba")
        assert "Sprague-Dawley" in method.subjects

    def test_deprivation_ja(self) -> None:
        method = compile_method(_full_program(), style="jaba")
        assert "23時間" in method.subjects

    def test_naive_ja(self) -> None:
        method = compile_method(_full_program(), style="jaba")
        assert "実験経験がなかった" in method.subjects


class TestApparatusJEAB:
    def test_chamber(self) -> None:
        method = compile_method(_full_program())
        assert "med-associates" in method.apparatus
        assert "ENV-007" in method.apparatus

    def test_operanda(self) -> None:
        method = compile_method(_full_program())
        assert "left lever" in method.apparatus
        assert "right lever" in method.apparatus

    def test_hardware(self) -> None:
        method = compile_method(_full_program())
        assert "MED-PC IV" in method.apparatus


class TestApparatusJABA:
    def test_chamber_ja(self) -> None:
        method = compile_method(_full_program(), style="jaba")
        assert "オペラント実験箱" in method.apparatus

    def test_hardware_ja(self) -> None:
        method = compile_method(_full_program(), style="jaba")
        assert "MED-PC IV" in method.apparatus


class TestProcedureAnnotations:
    def test_reinforcer(self) -> None:
        method = compile_method(_full_program())
        assert "food pellet" in method.procedure

    def test_operandum_component_assignment(self) -> None:
        method = compile_method(_full_program())
        assert "left lever" in method.procedure
        assert "VI 30-s" in method.procedure

    def test_session_end(self) -> None:
        method = compile_method(_full_program())
        assert "60 min" in method.procedure
        assert "60 reinforcer" in method.procedure
        assert "whichever occurred first" in method.procedure

    def test_steady_state(self) -> None:
        method = compile_method(_full_program())
        assert "5 sessions" in method.procedure
        assert "10%" in method.procedure

    def test_cod(self) -> None:
        method = compile_method(_full_program())
        assert "changeover delay" in method.procedure


class TestProcedureAnnotationsJABA:
    def test_session_end_ja(self) -> None:
        method = compile_method(_full_program(), style="jaba")
        assert "60 min" in method.procedure
        assert "60回" in method.procedure

    def test_steady_state_ja(self) -> None:
        method = compile_method(_full_program(), style="jaba")
        assert "5セッション" in method.procedure
        assert "10%" in method.procedure


class TestSessionEndVariants:
    def test_time_only(self) -> None:
        ast = {
            "type": "Program",
            "program_annotations": [
                {"type": "Annotation", "keyword": "session_end",
                 "params": {"rule": "time_only", "time": {"value": 60, "time_unit": "min"}}},
            ],
            "param_decls": [], "bindings": [],
            "schedule": {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0},
        }
        method = compile_method(ast)
        assert "60 min" in method.procedure
        assert "whichever" not in method.procedure

    def test_reinforcers_only(self) -> None:
        ast = {
            "type": "Program",
            "program_annotations": [
                {"type": "Annotation", "keyword": "session_end",
                 "params": {"rule": "reinforcers_only", "reinforcers": 100}},
            ],
            "param_decls": [], "bindings": [],
            "schedule": {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0},
        }
        method = compile_method(ast)
        assert "100 reinforcer" in method.procedure


class TestBaseline:
    def test_baseline_en(self) -> None:
        ast = {
            "type": "Program",
            "program_annotations": [
                {"type": "Annotation", "keyword": "baseline",
                 "params": {"pre_training_sessions": 3}},
            ],
            "param_decls": [], "bindings": [],
            "schedule": {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0},
        }
        method = compile_method(ast)
        assert "3 pretraining" in method.procedure

    def test_baseline_ja(self) -> None:
        ast = {
            "type": "Program",
            "program_annotations": [
                {"type": "Annotation", "keyword": "baseline",
                 "params": {"pre_training_sessions": 3}},
            ],
            "param_decls": [], "bindings": [],
            "schedule": {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0},
        }
        method = compile_method(ast, style="jaba")
        assert "3セッション" in method.procedure


class TestFullMethodToText:
    """Full integration: all annotations → complete Method section text."""

    def test_full_method_jeab(self) -> None:
        method = compile_method(_full_program())
        text = method.to_text()
        # All sections present
        assert "### Subjects" in text
        assert "### Apparatus" in text
        assert "### Procedure" in text
        assert "### References" in text
        # Key content
        assert "Sprague-Dawley" in text
        assert "concurrent" in text
        assert "Fleshler" in text

    def test_full_method_jaba(self) -> None:
        method = compile_method(_full_program(), style="jaba")
        text = method.to_text()
        assert "### 被験体" in text
        assert "### 装置" in text
        assert "### 手続き" in text
        assert "ラット" in text
        assert "並立" in text
