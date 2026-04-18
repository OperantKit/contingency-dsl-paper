"""Phase 3 tests: Modifier and Aversive schedule descriptions."""

import pytest
from contingency_dsl2procedure import compile_method


def _program(schedule: dict) -> dict:
    return {"type": "Program", "param_decls": [], "bindings": [], "schedule": schedule}


# === DRL / DRH / DRO ===

class TestDR:
    def test_drl_jeab(self) -> None:
        m = compile_method(_program({"type": "Modifier", "modifier": "DRL", "value": 5.0, "time_unit": "s"}))
        assert "differential-reinforcement-of-low-rate" in m.procedure
        assert "DRL" in m.procedure
        assert "5-s" in m.procedure

    def test_drh_jeab(self) -> None:
        m = compile_method(_program({"type": "Modifier", "modifier": "DRH", "value": 10.0}))
        assert "differential-reinforcement-of-high-rate" in m.procedure
        assert "DRH" in m.procedure

    def test_dro_jeab(self) -> None:
        m = compile_method(_program({"type": "Modifier", "modifier": "DRO", "value": 20.0, "time_unit": "s"}))
        assert "differential-reinforcement-of-other-behavior" in m.procedure
        assert "20-s" in m.procedure

    def test_drl_jaba(self) -> None:
        m = compile_method(_program({"type": "Modifier", "modifier": "DRL", "value": 5.0, "time_unit": "s"}), style="jaba")
        assert "低反応率分化強化" in m.procedure
        assert "DRL" in m.procedure


# === Progressive Ratio ===

class TestPR:
    def test_pr_linear_jeab(self) -> None:
        m = compile_method(_program({
            "type": "Modifier", "modifier": "PR", "pr_step": "linear",
            "pr_start": 1.0, "pr_increment": 5.0,
        }))
        assert "progressive-ratio" in m.procedure
        assert "linear" in m.procedure

    def test_pr_hodos_cites(self) -> None:
        m = compile_method(_program({
            "type": "Modifier", "modifier": "PR", "pr_step": "hodos",
        }))
        assert "progressive-ratio" in m.procedure
        keys = [r.key for r in m.references]
        assert "hodos_1961" in keys

    def test_pr_jaba(self) -> None:
        m = compile_method(_program({
            "type": "Modifier", "modifier": "PR", "pr_step": "linear",
        }), style="jaba")
        assert "漸進比率" in m.procedure


# === Lag ===

class TestLag:
    def test_lag5_jeab(self) -> None:
        m = compile_method(_program({"type": "Modifier", "modifier": "Lag", "length": 5}))
        assert "Lag 5" in m.procedure

    def test_lag_jaba(self) -> None:
        m = compile_method(_program({"type": "Modifier", "modifier": "Lag", "length": 3}), style="jaba")
        assert "Lag 3" in m.procedure


# === Sidman avoidance ===

class TestSidman:
    def test_sidman_jeab(self) -> None:
        m = compile_method(_program({
            "type": "AversiveSchedule", "kind": "Sidman",
            "params": {
                "SSI": {"value": 5.0, "time_unit": "s"},
                "RSI": {"value": 20.0, "time_unit": "s"},
            },
        }))
        assert "Sidman avoidance" in m.procedure
        assert "5-s" in m.procedure
        assert "shock-shock" in m.procedure
        assert "20-s" in m.procedure
        assert "response-shock" in m.procedure
        keys = [r.key for r in m.references]
        assert "sidman_1953" in keys

    def test_sidman_jaba(self) -> None:
        m = compile_method(_program({
            "type": "AversiveSchedule", "kind": "Sidman",
            "params": {
                "SSI": {"value": 5.0, "time_unit": "s"},
                "RSI": {"value": 20.0, "time_unit": "s"},
            },
        }), style="jaba")
        assert "Sidman 回避" in m.procedure
        assert "SS 間隔" in m.procedure
        assert "RS 間隔" in m.procedure


# === Discriminated avoidance ===

class TestDiscrimAv:
    def test_discrim_av_jeab(self) -> None:
        m = compile_method(_program({
            "type": "AversiveSchedule", "kind": "DiscrimAv",
            "params": {
                "CSUSInterval": {"value": 10.0, "time_unit": "s"},
                "ITI": {"value": 30.0, "time_unit": "s"},
                "mode": "fixed",
            },
        }))
        assert "discriminated avoidance" in m.procedure
        assert "10-s" in m.procedure
        assert "CS-US" in m.procedure
        assert "30-s" in m.procedure
        assert "intertrial" in m.procedure

    def test_discrim_av_jaba_response_terminated(self) -> None:
        m = compile_method(_program({
            "type": "AversiveSchedule", "kind": "DiscrimAv",
            "params": {
                "CSUSInterval": {"value": 10.0, "time_unit": "s"},
                "ITI": {"value": 30.0, "time_unit": "s"},
                "mode": "response_terminated",
            },
        }), style="jaba")
        assert "弁別回避" in m.procedure
        assert "反応終端モード" in m.procedure


class TestEscape:
    def test_escape_basic_jeab(self) -> None:
        m = compile_method(_program({
            "type": "AversiveSchedule", "kind": "Escape",
            "params": {"SafeDuration": {"value": 5.0, "time_unit": "s"}},
        }))
        assert "free-operant escape" in m.procedure
        assert "5-s" in m.procedure
        assert "safe period" in m.procedure

    def test_escape_with_max_shock_jeab(self) -> None:
        m = compile_method(_program({
            "type": "AversiveSchedule", "kind": "Escape",
            "params": {
                "SafeDuration": {"value": 5.0, "time_unit": "s"},
                "MaxShock": {"value": 60.0, "time_unit": "s"},
            },
        }))
        assert "60-s" in m.procedure
        assert "cutoff" in m.procedure or "maximum" in m.procedure

    def test_escape_jaba(self) -> None:
        m = compile_method(_program({
            "type": "AversiveSchedule", "kind": "Escape",
            "params": {"SafeDuration": {"value": 5.0, "time_unit": "s"}},
        }), style="jaba")
        assert "逃避" in m.procedure
        assert "安全期間" in m.procedure
