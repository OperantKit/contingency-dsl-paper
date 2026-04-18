"""Special schedule (EXT, CRF) visitor."""

from __future__ import annotations

from ...ast_types import ScheduleNode
from ...references import ReferenceCollector
from ...style import Style
from ._common import decorate_leaf


def visit_special(
    node: ScheduleNode, *, style: Style,
    refs: ReferenceCollector | None = None, first_mention: bool = True,
) -> str:
    kind = node.get("kind", "")
    if kind == "EXT":
        base = style.framing_extinction
    elif kind == "CRF":
        base = style.framing_crf
    else:
        return ""
    return decorate_leaf(base, node, style=style)
