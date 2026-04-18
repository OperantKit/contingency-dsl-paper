"""SecondOrder schedule visitor."""

from __future__ import annotations

from ...ast_types import ScheduleNode
from ...references import ReferenceCollector
from ...style import Style
from ...vocabulary import format_atomic_abbrev, format_atomic_full
from ._common import decorate_leaf, format_component


def visit_second_order(
    node: ScheduleNode, *, style: Style,
    refs: ReferenceCollector | None = None, first_mention: bool = True,
) -> str:
    overall = node.get("overall", {})
    unit_sched = node.get("unit", {})
    outer_name = (
        format_atomic_full(overall, style)
        if first_mention
        else format_atomic_abbrev(overall, style)
    )
    inner_name = format_component(unit_sched, style=style, first_mention=False)

    if style.locale == "ja":
        base = f"二次{outer_name}（{inner_name}:簡略刺激）スケジュールに従って反応が強化された。"
    else:
        base = (
            f"Responses were reinforced under a second-order "
            f"{outer_name} ({inner_name}:brief stimulus) schedule."
        )
    return decorate_leaf(base, node, style=style)
