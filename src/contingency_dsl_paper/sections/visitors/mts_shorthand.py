"""Shorthand MTS visitor used for stimulus-equivalence programs.

Schema ``{type: MTS, params: {samples, comparisons}}`` is a Tier-B
stimulus-classes shorthand, distinct from the full
``{type: TrialBased, trial_type: MTS, consequence, ITI, ...}`` form
handled by ``visitors/trial_based.py``. Programs that use this shorthand
typically carry the procedural detail in ``@stimulus_classes`` /
``@training`` / ``@testing`` annotations instead of in-node fields.
"""

from __future__ import annotations

from ...ast_types import ScheduleNode
from ...references import ReferenceCollector
from ...style import Style
from ._common import decorate_leaf


def visit_mts_shorthand(
    node: ScheduleNode, *, style: Style,
    refs: ReferenceCollector | None = None, first_mention: bool = True,
) -> str:
    params = node.get("params", {}) or {}
    samples = params.get("samples")
    comparisons = params.get("comparisons")
    if refs is not None:
        refs.cite_if_known("cumming_berryman_1965")

    if style.locale == "ja":
        parts = ["見本合わせ（MTS）手続きを使用した"]
        detail: list[str] = []
        if samples is not None:
            detail.append(f"見本刺激 {int(samples)}個")
        if comparisons is not None:
            detail.append(f"比較刺激 {int(comparisons)}個")
        if detail:
            parts.append(f"（{'、'.join(detail)}）")
        base = "".join(parts) + "。"
    else:
        detail_en: list[str] = []
        if samples is not None:
            detail_en.append(f"{int(samples)} samples")
        if comparisons is not None:
            detail_en.append(f"{int(comparisons)} comparison stimuli")
        suffix = f" with {' and '.join(detail_en)}" if detail_en else ""
        base = (
            f"A matching-to-sample (MTS) procedure was used{suffix}."
        )

    return decorate_leaf(base, node, style=style)
