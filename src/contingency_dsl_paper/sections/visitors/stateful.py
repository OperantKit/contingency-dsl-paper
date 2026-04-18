"""Operant stateful schedule visitors.

Covers the three stateful primitives defined in schema/operant/stateful/
ast.schema.json:

- ``AdjustingSchedule``: parameter adjusted at runtime based on behavior
  (Mazur, 1987; Richards et al., 1997).
- ``InterlockingSchedule``: ratio decreases linearly with elapsed time
  (Ferster & Skinner, 1957).
- ``PercentileSchedule``: handled by visitors/modifier.py ``_pctl``
  because the schema encodes it as Modifier(modifier=Pctl).
"""

from __future__ import annotations

from ...ast_types import ScheduleNode
from ...references import ReferenceCollector
from ...style import Style
from ._common import decorate_leaf, fmt_val, format_duration


def visit_adjusting(
    node: ScheduleNode, *, style: Style,
    refs: ReferenceCollector | None = None, first_mention: bool = True,
) -> str:
    target = node.get("adj_target", "")
    start = node.get("adj_start") or {}
    step = node.get("adj_step") or {}
    adj_min = node.get("adj_min")
    adj_max = node.get("adj_max")

    if refs is not None:
        if target == "delay":
            refs.cite_if_known("mazur_1987")
        elif target == "amount":
            refs.cite_if_known("richards_1997")
        else:
            refs.cite_if_known("ferster_skinner_1957")

    target_labels_en = {
        "delay": "reinforcement delay",
        "ratio": "ratio requirement",
        "amount": "reinforcer magnitude",
    }
    target_labels_ja = {
        "delay": "強化遅延",
        "ratio": "比率要件",
        "amount": "強化子量",
    }

    start_str = _adj_value_str(start, style)
    step_str = _adj_value_str(step, style)
    min_str = _adj_value_str(adj_min, style) if adj_min else ""
    max_str = _adj_value_str(adj_max, style) if adj_max else ""

    if style.locale == "ja":
        label = target_labels_ja.get(target, target)
        parts = [
            f"{label}を調整する調整スケジュールを使用した"
            f"（初期値 {start_str}、調整幅 {step_str}）。"
        ]
        bounds: list[str] = []
        if min_str:
            bounds.append(f"下限 {min_str}")
        if max_str:
            bounds.append(f"上限 {max_str}")
        if bounds:
            parts.append(f"パラメータは{'、'.join(bounds)}に制約された。")
        base = "".join(parts)
    else:
        label = target_labels_en.get(target, target)
        parts = [
            f"An adjusting schedule varied the {label} "
            f"(initial value {start_str}; step {step_str})."
        ]
        bounds_en: list[str] = []
        if min_str:
            bounds_en.append(f"a lower bound of {min_str}")
        if max_str:
            bounds_en.append(f"an upper bound of {max_str}")
        if bounds_en:
            parts.append("The parameter was constrained by " + " and ".join(bounds_en) + ".")
        base = " ".join(parts)

    return decorate_leaf(base, node, style=style)


def visit_interlocking(
    node: ScheduleNode, *, style: Style,
    refs: ReferenceCollector | None = None, first_mention: bool = True,
) -> str:
    r0 = node.get("interlock_R0")
    t = node.get("interlock_T") or {}

    if refs is not None:
        refs.cite_if_known("ferster_skinner_1957")

    t_str = (
        format_duration(t.get("value", 0), t.get("time_unit", "s"), style)
        if t else ""
    )

    if style.locale == "ja":
        base = (
            f"インターロッキングスケジュールを使用した"
            f"（初期比率 R0={int(r0) if r0 is not None else '?'}、"
            f"時間窓 T={t_str}）。"
            f"比率要件は前強化からの経過時間に比例して線形に減少した。"
        )
    else:
        base = (
            f"An interlocking schedule was in effect "
            f"(initial ratio R0={int(r0) if r0 is not None else '?'}; "
            f"time window T={t_str}). The ratio requirement decreased "
            f"linearly with elapsed time since the previous reinforcer."
        )
    return decorate_leaf(base, node, style=style)


# --- helpers -----------------------------------------------------------------

def _adj_value_str(value: dict | None, style: Style) -> str:
    if not value:
        return ""
    v = value.get("value")
    unit = value.get("time_unit")
    if unit:
        return format_duration(v or 0, unit, style)
    return fmt_val(v)
