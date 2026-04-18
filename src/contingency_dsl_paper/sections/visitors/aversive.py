"""Aversive schedule visitors.

Covers the three ``AversiveSchedule`` kinds defined in
``schema/operant/ast.schema.json``:

- ``Sidman``: free-operant avoidance (Sidman, 1953).
- ``DiscrimAv``: discriminated avoidance with ``fixed`` or
  ``response_terminated`` US delivery mode (Solomon & Wynne, 1953).
- ``Escape``: free-operant escape (Dinsmoor, 1977;
  Dinsmoor & Hughes, 1956).
"""

from __future__ import annotations

from ...ast_types import ScheduleNode
from ...references import ReferenceCollector
from ...style import Style
from ._common import decorate_leaf, format_duration


def visit_aversive(
    node: ScheduleNode, *, style: Style,
    refs: ReferenceCollector | None = None, first_mention: bool = True,
) -> str:
    kind = node.get("kind", "")
    params = node.get("params", {}) or {}

    if kind == "Sidman":
        base = _sidman(params, style, refs)
    elif kind == "DiscrimAv":
        base = _discrim_av(params, style, refs)
    elif kind == "Escape":
        base = _escape(params, style, refs)
    else:
        return ""
    return decorate_leaf(base, node, style=style)


def _sidman(
    params: dict, style: Style, refs: ReferenceCollector | None,
) -> str:
    if refs is not None:
        refs.cite_if_known("sidman_1953")

    ssi = params.get("SSI", {}) or {}
    rsi = params.get("RSI", {}) or {}
    ssi_str = format_duration(ssi.get("value", 0), ssi.get("time_unit", "s"), style)
    rsi_str = format_duration(rsi.get("value", 0), rsi.get("time_unit", "s"), style)

    if style.locale == "ja":
        return (
            f"Sidman 回避スケジュールが使用された"
            f"（SS 間隔 {ssi_str}、RS 間隔 {rsi_str}）。"
        )
    return (
        f"A Sidman avoidance schedule was in effect "
        f"with a {ssi_str} shock-shock interval and a {rsi_str} response-shock interval."
    )


def _discrim_av(
    params: dict, style: Style, refs: ReferenceCollector | None,
) -> str:
    if refs is not None:
        refs.cite_if_known("solomon_wynne_1953")

    csus = params.get("CSUSInterval", {}) or {}
    iti = params.get("ITI", {}) or {}
    mode = params.get("mode", "fixed")
    csus_str = format_duration(csus.get("value", 0), csus.get("time_unit", "s"), style)
    iti_str = format_duration(iti.get("value", 0), iti.get("time_unit", "s"), style)

    extra_en = ""
    extra_ja = ""
    if mode == "fixed":
        sd = params.get("ShockDuration")
        if sd:
            sd_str = format_duration(sd.get("value", 0), sd.get("time_unit", "s"), style)
            extra_en = f"; US duration was {sd_str}"
            extra_ja = f"、US 持続 {sd_str}"
    elif mode == "response_terminated":
        max_s = params.get("MaxShock")
        if max_s:
            max_str = format_duration(max_s.get("value", 0), max_s.get("time_unit", "s"), style)
            extra_en = f"; a {max_str} maximum US duration cutoff was in effect"
            extra_ja = f"、最大 US {max_str}"

    if style.locale == "ja":
        mode_ja = {
            "fixed": "固定持続",
            "response_terminated": "反応終端",
        }.get(mode, mode)
        return (
            f"弁別回避手続き（{mode_ja}モード）が使用された"
            f"（CS-US 間隔 {csus_str}、試行間間隔 {iti_str}{extra_ja}）。"
        )
    mode_en = {
        "fixed": "fixed-duration",
        "response_terminated": "response-terminated",
    }.get(mode, mode)
    return (
        f"A discriminated avoidance procedure ({mode_en} mode) was in effect "
        f"with a {csus_str} CS-US interval and a {iti_str} intertrial interval{extra_en}."
    )


def _escape(
    params: dict, style: Style, refs: ReferenceCollector | None,
) -> str:
    if refs is not None:
        refs.cite_if_known("dinsmoor_1977")

    safe = params.get("SafeDuration", {}) or {}
    safe_str = format_duration(
        safe.get("value", 0), safe.get("time_unit", "s"), style,
    )

    max_shock = params.get("MaxShock")
    max_str = ""
    if max_shock:
        max_str = format_duration(
            max_shock.get("value", 0),
            max_shock.get("time_unit", "s"),
            style,
        )

    if style.locale == "ja":
        base = (
            f"自由オペラント逃避スケジュールを使用した"
            f"（安全期間 {safe_str}）。"
            f"各反応は {safe_str} の間、嫌悪刺激を終結させた。"
        )
        if max_str:
            base = base.rstrip("。") + f"（最大暴露時間 {max_str}）。"
        return base

    base = (
        f"A free-operant escape schedule was in effect with a {safe_str} "
        f"safe period. Each response terminated the aversive stimulus "
        f"for {safe_str}."
    )
    if max_str:
        base = base.rstrip(".") + (
            f". A {max_str} maximum uninterrupted exposure cutoff was "
            f"imposed."
        )
    return base
