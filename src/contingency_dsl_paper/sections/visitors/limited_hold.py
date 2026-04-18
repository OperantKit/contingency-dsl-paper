"""Deprecated: LimitedHold wrapper was removed from the AST.

LimitedHold is now represented as optional ``limitedHold`` /
``limitedHoldUnit`` properties on leaf schedule nodes (Atomic, Special,
DRModifier, SecondOrder, TrialBased, AversiveSchedule). Rendering is
handled by ``_common.decorate_leaf``. This module is retained only as a
compatibility shim for imports that may linger in downstream code.
"""

from __future__ import annotations

from ...ast_types import ScheduleNode
from ...references import ReferenceCollector
from ...style import Style


def visit_limited_hold(
    node: ScheduleNode, *, style: Style,
    refs: ReferenceCollector | None = None, first_mention: bool = True,
) -> str:
    return ""
