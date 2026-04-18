"""Schedule node visitors for prose generation.

Each visitor takes (node, style, refs, first_mention) and returns a prose string.
The dispatch function routes by ``node["type"]`` and, for Compound nodes,
disambiguates operant vs. respondent Compound via the ``cs_list`` key.
"""

from __future__ import annotations

from ...ast_types import ScheduleNode
from ...references import ReferenceCollector
from ...style import JEAB, Style
from .atomic import visit_atomic
from .aversive import visit_aversive
from .compound import visit_compound
from .experiment_layer import (
    visit_phase_ref,
    visit_progressive_training,
    visit_shaping,
)
from .mts_shorthand import visit_mts_shorthand
from .modifier import visit_modifier
from .respondent import is_respondent_node, visit_respondent
from .second_order import visit_second_order
from .special import visit_special
from .stateful import visit_adjusting, visit_interlocking
from .trial_based import visit_trial_based


def describe_schedule(
    node: ScheduleNode,
    *,
    style: Style = JEAB,
    refs: ReferenceCollector | None = None,
    first_mention: bool = True,
    bindings: dict[str, ScheduleNode] | None = None,
) -> str:
    """Dispatch to the appropriate visitor based on node type.

    Args:
        node: A ScheduleExpr AST node.
        style: Journal style to render in.
        refs: Reference collector for automatic citations.
        first_mention: True on the first reference within a section.
        bindings: Optional map of let-bound schedule names to expressions.
            Used to resolve IdentifierRef nodes in pre-expansion AST.
    """
    if not isinstance(node, dict):
        return ""

    # Unwrap AnnotatedSchedule wrapper: {type: AnnotatedSchedule, expr, annotations}.
    if node.get("type") == "AnnotatedSchedule":
        inner = dict(node.get("expr", {}) or {})
        # Merge schedule-level annotations onto the wrapped expression so
        # decorate_leaf/describe_annotations pick them up.
        merged_anns = list(node.get("annotations", []) or [])
        existing = list(inner.get("annotations", []) or [])
        inner["annotations"] = existing + merged_anns
        return describe_schedule(
            inner, style=style, refs=refs,
            first_mention=first_mention, bindings=bindings,
        )

    # Resolve IdentifierRef via the program's bindings.
    if node.get("type") == "IdentifierRef":
        name = node.get("name", "")
        if bindings and name in bindings:
            return describe_schedule(
                bindings[name], style=style, refs=refs,
                first_mention=first_mention, bindings=bindings,
            )
        if not name:
            return ""
        if style.locale == "ja":
            return f"宣言されたスケジュール「{name}」に従って反応が強化された。"
        return (
            f"Responses were reinforced under the schedule bound to "
            f"``{name}``."
        )

    node_type = node.get("type", "")

    # Respondent primitives (discriminated upstream; takes priority over
    # the operant Compound dispatch when a node carries cs_list).
    if is_respondent_node(node):
        # Normalize Compound → RespondentCompound for dispatch.
        if node_type == "Compound" and "cs_list" in node:
            resp_node = dict(node)
            resp_node["type"] = "RespondentCompound"
            return visit_respondent(
                resp_node, style=style, refs=refs, first_mention=first_mention,
            )
        return visit_respondent(
            node, style=style, refs=refs, first_mention=first_mention,
        )

    # MTS shorthand: {type: MTS, params: {samples, comparisons}} — distinct
    # from TrialBased MTS which has ITI/consequence/etc.
    if node_type == "MTS" and "params" in node and "consequence" not in node:
        return visit_mts_shorthand(
            node, style=style, refs=refs, first_mention=first_mention,
        )

    # Pre-expansion experiment-layer primitives
    if node_type == "Shaping":
        return visit_shaping(
            node, style=style, refs=refs, first_mention=first_mention,
        )
    if node_type == "ProgressiveTraining":
        return visit_progressive_training(
            node, style=style, refs=refs, first_mention=first_mention,
            bindings=bindings,
        )
    if node_type == "PhaseRef":
        return visit_phase_ref(
            node, style=style, refs=refs, first_mention=first_mention,
        )

    dispatch = {
        "Atomic": visit_atomic,
        "Compound": visit_compound,
        "SecondOrder": visit_second_order,
        "Special": visit_special,
        "Modifier": visit_modifier,
        "AversiveSchedule": visit_aversive,
        "TrialBased": visit_trial_based,
        "AdjustingSchedule": visit_adjusting,
        "InterlockingSchedule": visit_interlocking,
    }

    visitor = dispatch.get(node_type)
    if visitor is None:
        return ""
    return visitor(node, style=style, refs=refs, first_mention=first_mention)
