"""Extended tests for schedule description coverage.

Covers the full 3x3 atomic grid, LimitedHold, SecondOrder,
compound params, and multi-style output.
"""

import pytest

from contingency_dsl_paper import compile_method


def _program(schedule: dict, **kwargs) -> dict:
    return {
        "type": "Program",
        "param_decls": kwargs.get("param_decls", []),
        "bindings": [],
        "schedule": schedule,
        **({k: v for k, v in kwargs.items() if k != "param_decls"}),
    }


# --- 3x3 Atomic grid ---

_GRID = [
    ("F", "R", 5.0, None, "fixed-ratio (FR) 5"),
    ("V", "R", 20.0, None, "variable-ratio (VR) 20"),
    ("R", "R", 10.0, None, "random-ratio (RR) 10"),
    ("F", "I", 30.0, "s", "fixed-interval (FI) 30-s"),
    ("V", "I", 60.0, "s", "variable-interval (VI) 60-s"),
    ("R", "I", 45.0, "s", "random-interval (RI) 45-s"),
    ("F", "T", 20.0, "s", "fixed-time (FT) 20-s"),
    ("V", "T", 30.0, "s", "variable-time (VT) 30-s"),
    ("R", "T", 15.0, "s", "random-time (RT) 15-s"),
]


@pytest.mark.parametrize("dist,domain,value,unit,expected", _GRID)
def test_atomic_grid_jeab(dist: str, domain: str, value: float, unit: str | None, expected: str) -> None:
    node: dict = {"type": "Atomic", "dist": dist, "domain": domain, "value": value}
    if unit:
        node["time_unit"] = unit
    method = compile_method(_program(node))
    assert expected in method.procedure


@pytest.mark.parametrize("dist,domain,value,unit,expected", [
    ("F", "R", 5.0, None, "固定比率 (FR) 5"),
    ("V", "I", 60.0, "s", "変動時隔 (VI) 60-s"),
    ("F", "T", 20.0, "s", "固定時間 (FT) 20-s"),
])
def test_atomic_grid_jaba(dist: str, domain: str, value: float, unit: str | None, expected: str) -> None:
    node: dict = {"type": "Atomic", "dist": dist, "domain": domain, "value": value}
    if unit:
        node["time_unit"] = unit
    method = compile_method(_program(node), style="jaba")
    assert expected in method.procedure


# --- LimitedHold (leaf property on Atomic) ---

class TestLimitedHold:
    def test_fi_with_lh_jeab(self) -> None:
        ast = _program({
            "type": "Atomic",
            "dist": "F", "domain": "I", "value": 30.0, "time_unit": "s",
            "limitedHold": 5.0, "limitedHoldUnit": "s",
        })
        method = compile_method(ast)
        assert "limited hold" in method.procedure
        assert "5-s" in method.procedure

    def test_fi_with_lh_jaba(self) -> None:
        ast = _program({
            "type": "Atomic",
            "dist": "F", "domain": "I", "value": 30.0, "time_unit": "s",
            "limitedHold": 5.0, "limitedHoldUnit": "s",
        })
        method = compile_method(ast, style="jaba")
        assert "リミテッドホールド" in method.procedure


# --- SecondOrder ---

class TestSecondOrder:
    def test_fr5_fi30_jeab(self) -> None:
        ast = _program({
            "type": "SecondOrder",
            "overall": {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0},
            "unit": {"type": "Atomic", "dist": "F", "domain": "I", "value": 30.0, "time_unit": "s"},
        })
        method = compile_method(ast)
        assert "second-order" in method.procedure
        assert "FR 5" in method.procedure or "fixed-ratio" in method.procedure
        assert "FI 30-s" in method.procedure

    def test_second_order_jaba(self) -> None:
        ast = _program({
            "type": "SecondOrder",
            "overall": {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0},
            "unit": {"type": "Atomic", "dist": "F", "domain": "I", "value": 30.0, "time_unit": "s"},
        })
        method = compile_method(ast, style="jaba")
        assert "二次" in method.procedure


# --- Compound with all combinators ---

_COMBINATORS = [
    ("Conc", "concurrent", "並立"),
    ("Chain", "chained", "連鎖"),
    ("Alt", "alternative", "二択"),
    ("Conj", "conjunctive", "連言"),
    ("Tand", "tandem", "タンデム"),
    ("Mult", "multiple", "多元"),
    ("Mix", "mixed", "混合"),
]


@pytest.mark.parametrize("code,en_name,ja_name", _COMBINATORS)
def test_all_combinators_jeab(code: str, en_name: str, ja_name: str) -> None:
    ast = _program({
        "type": "Compound",
        "combinator": code,
        "components": [
            {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0},
            {"type": "Atomic", "dist": "F", "domain": "I", "value": 30.0, "time_unit": "s"},
        ],
    })
    method = compile_method(ast)
    assert en_name in method.procedure


@pytest.mark.parametrize("code,en_name,ja_name", _COMBINATORS)
def test_all_combinators_jaba(code: str, en_name: str, ja_name: str) -> None:
    ast = _program({
        "type": "Compound",
        "combinator": code,
        "components": [
            {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0},
            {"type": "Atomic", "dist": "F", "domain": "I", "value": 30.0, "time_unit": "s"},
        ],
    })
    method = compile_method(ast, style="jaba")
    assert ja_name in method.procedure


# --- Blackout parameter ---

class TestBlackout:
    def test_mult_with_bo(self) -> None:
        ast = _program({
            "type": "Compound",
            "combinator": "Mult",
            "components": [
                {"type": "Atomic", "dist": "V", "domain": "I", "value": 30.0, "time_unit": "s"},
                {"type": "Atomic", "dist": "V", "domain": "I", "value": 60.0, "time_unit": "s"},
            ],
            "params": {"BO": {"value": 5.0, "time_unit": "s"}},
        })
        method = compile_method(ast)
        assert "5-s" in method.procedure
        assert "blackout" in method.procedure


# --- Program-level param_decls ---

class TestParamDecls:
    def test_cod_param_decl(self) -> None:
        ast = _program(
            {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0},
            param_decls=[{"type": "ParamDecl", "name": "COD", "value": 2.0, "time_unit": "s"}],
        )
        method = compile_method(ast)
        assert "changeover delay" in method.procedure
        assert "2-s" in method.procedure

    def test_lh_param_decl(self) -> None:
        ast = _program(
            {"type": "Atomic", "dist": "F", "domain": "R", "value": 5.0},
            param_decls=[{"type": "ParamDecl", "name": "LH", "value": 10.0, "time_unit": "s"}],
        )
        method = compile_method(ast)
        assert "limited hold" in method.procedure
