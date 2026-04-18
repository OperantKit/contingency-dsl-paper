"""Pre-expansion experiment-layer visitors.

``Shaping`` / ``ProgressiveTraining`` / ``PhaseRef`` are pre-expansion
schema primitives that a resolver normally desugars into Phase lists
before the AST reaches the compiler. Conformance fixtures are all
post-expansion, but handling the raw forms here keeps the compiler
tolerant of pre-expansion input from custom parsers.

References for phrasing:
    Skinner, B. F. (1953). Science and Human Behavior. Macmillan.
    Galbicka, G. (1994). Shaping in the 21st century. JABA, 27(4).
    Sidman, M. (1960). Tactics of Scientific Research. Basic Books.
"""

from __future__ import annotations

from ...ast_types import ScheduleNode
from ...references import ReferenceCollector
from ...style import Style


def visit_shaping(
    node: ScheduleNode, *, style: Style,
    refs: ReferenceCollector | None = None, first_mention: bool = True,
) -> str:
    target = node.get("target") or "target response"
    method = node.get("method", "artful")
    approximations = node.get("approximations") or []
    dimension = node.get("dimension")
    if refs is not None:
        refs.cite_if_known("skinner_1953")
        if method == "percentile":
            refs.cite_if_known("galbicka_1994")

    method_en = {
        "artful": "experimenter-directed successive-approximation",
        "percentile": "percentile-based",
        "staged": "staged",
    }.get(method, method)
    method_ja = {
        "artful": "実験者の判断による",
        "percentile": "パーセンタイル法による",
        "staged": "段階的",
    }.get(method, method)

    if style.locale == "ja":
        parts = [
            f"目標反応 {target} を{method_ja}シェイピングで形成した",
        ]
        if dimension:
            parts.append(f"（次元 {dimension}）")
        if approximations:
            parts.append(
                "（近似系列: " + "→".join(str(a) for a in approximations) + "）"
            )
        return "".join(parts) + "。"

    parts_en = [
        f"The {target} was shaped via {method_en} shaping"
    ]
    if dimension:
        parts_en.append(f" along the {dimension} dimension")
    if approximations:
        parts_en.append(
            ". Approximations followed the sequence: "
            + " → ".join(str(a) for a in approximations)
        )
    return "".join(parts_en) + "."


def visit_progressive_training(
    node: ScheduleNode, *, style: Style,
    refs: ReferenceCollector | None = None, first_mention: bool = True,
    bindings: dict[str, ScheduleNode] | None = None,
) -> str:
    steps = node.get("steps") or []
    label = node.get("label") or "Progression"

    sweeps_en: list[str] = []
    sweeps_ja: list[str] = []
    for step in steps:
        name = step.get("name", "")
        values = step.get("values") or []
        values_str = ", ".join(str(v) for v in values)
        if name:
            sweeps_en.append(f"{name} ∈ {{{values_str}}}")
            sweeps_ja.append(f"{name} ∈ {{{values_str}}}")

    if style.locale == "ja":
        body = f"パラメトリック訓練（{label}）を実施した"
        if sweeps_ja:
            body += "（スイープ: " + "、".join(sweeps_ja) + "）"
        return body + "。"

    body_en = f"A parametric training progression ({label}) was conducted"
    if sweeps_en:
        body_en += " with sweeps " + "; ".join(sweeps_en)
    return body_en + "."


def visit_phase_ref(
    node: ScheduleNode, *, style: Style,
    refs: ReferenceCollector | None = None, first_mention: bool = True,
) -> str:
    ref = node.get("ref", "")
    if not ref:
        return ""
    if style.locale == "ja":
        return f"フェーズ {ref} の手続きを反復した。"
    return f"The {ref} phase procedure was repeated."
