"""Shared utilities for schedule visitors."""

from __future__ import annotations

from ...ast_types import ScheduleNode
from ...style import Style
from ...vocabulary import format_atomic_abbrev, format_atomic_full, format_combinator


def fmt_val(v: float | None) -> str:
    """Format a numeric value, dropping .0 for integers. None → empty."""
    if v is None:
        return ""
    try:
        if v == int(v):
            return str(int(v))
    except (TypeError, ValueError):
        return str(v)
    return str(v)


def humanize(name: str) -> str:
    """Convert DSL identifier to human-readable form: left_lever → left lever."""
    return name.replace("_", " ")


def format_component(
    node: ScheduleNode, *, style: Style, first_mention: bool = False,
) -> str:
    """Format a single component within a compound schedule (no framing sentence)."""
    node_type = node.get("type", "")
    if node_type == "Atomic":
        return (
            format_atomic_full(node, style)
            if first_mention
            else format_atomic_abbrev(node, style)
        )
    elif node_type == "Compound":
        comb = format_combinator(node.get("combinator", ""), style)
        parts = " ".join(
            format_component(c, style=style, first_mention=first_mention)
            for c in node.get("components", [])
        )
        return f"{comb} {parts}"
    elif node_type == "Special":
        kind = node.get("kind", "")
        return style.special_names.get(kind, kind)
    return ""


def format_duration(value: float, unit: str, style: Style) -> str:
    """Format a time duration string: '5-s' or '5 s'."""
    val_str = fmt_val(value)
    if style.time_unit_hyphen:
        return f"{val_str}-{unit}"
    return f"{val_str} {unit}"


# --- Leaf property decoration -------------------------------------------------

def decorate_leaf(
    base: str, node: ScheduleNode, *, style: Style,
) -> str:
    """Append LH / Timeout / ResponseCost clauses to a base description.

    The new AST (post schema reorganization) attaches LimitedHold, Timeout,
    and ResponseCost as optional properties on leaf schedule nodes. This
    helper appends the corresponding prose clauses to the schedule
    sentence in a style-aware way.
    """
    suffix_parts: list[str] = []

    # --- Limited Hold ---
    lh_val = node.get("limitedHold")
    if lh_val is not None:
        lh_unit = node.get("limitedHoldUnit", "s")
        dur = format_duration(lh_val, lh_unit, style)
        if style.locale == "ja":
            suffix_parts.append(f"{dur}のリミテッドホールドを併用した")
        else:
            suffix_parts.append(f"with a {dur} limited hold")

    # --- Timeout ---
    to_params = node.get("timeout")
    if to_params:
        to_dur = format_duration(
            to_params.get("duration", 0),
            to_params.get("durationUnit", "s"),
            style,
        )
        reset = bool(to_params.get("resetOnResponse", False))
        if style.locale == "ja":
            kind = "反応で再開する" if reset else "反応で再開しない"
            suffix_parts.append(f"{to_dur}のタイムアウト（{kind}）を伴う")
        else:
            kind = "resetting" if reset else "non-resetting"
            suffix_parts.append(f"with a {to_dur} {kind} timeout")

    # --- Response Cost ---
    rc = node.get("responseCost")
    if rc:
        amount = fmt_val(rc.get("amount", 0))
        unit = rc.get("unit", "token")
        if style.locale == "ja":
            unit_ja = {"token": "トークン", "point": "ポイント"}.get(unit, unit)
            suffix_parts.append(f"各反応で{amount}{unit_ja}が除去された")
        else:
            plural = "s" if amount != "1" else ""
            suffix_parts.append(
                f"with each target response removing {amount} {unit}{plural}"
            )

    if not suffix_parts:
        return base

    joined = "、".join(suffix_parts) if style.locale == "ja" else ", ".join(suffix_parts)

    if style.locale == "ja":
        # Strip trailing period and append
        trimmed = base.rstrip("。")
        return f"{trimmed}（{joined}）。"
    trimmed = base.rstrip(".")
    return f"{trimmed}, {joined}."


def describe_annotations(
    node: ScheduleNode, *, style: Style,
) -> list[str]:
    """Render schedule-level annotations on a node as sentences.

    Returns an empty list when no annotations are attached. Each entry
    is a full sentence ready to be appended to the Procedure prose.
    """
    anns = node.get("annotations", []) or []
    out: list[str] = []
    for ann in anns:
        s = _render_schedule_annotation(ann, style)
        if s:
            out.append(s)
    return out


def _render_schedule_annotation(ann: dict, style: Style) -> str:
    kw = ann.get("keyword", "")
    params = ann.get("params", {}) or {}
    positional = ann.get("positional")

    if kw == "operandum":
        op_name = humanize(str(positional or ""))
        if style.locale == "ja":
            return f"該当成分は{op_name}への反応に割り当てられた。"
        return f"Responses were assigned to the {op_name}."

    if kw == "sd":
        sd_name = humanize(str(positional or ""))
        if style.locale == "ja":
            return f"{sd_name}が弁別刺激として点灯された。"
        return f"{sd_name} served as the discriminative stimulus."

    if kw == "cs":
        cs_name = humanize(str(positional or ""))
        if style.locale == "ja":
            return f"{cs_name}を条件刺激として用いた。"
        return f"{cs_name} served as the conditioned stimulus."

    if kw == "us":
        us_name = humanize(str(positional or ""))
        if style.locale == "ja":
            return f"{us_name}を無条件刺激として用いた。"
        return f"{us_name} served as the unconditioned stimulus."

    if kw in ("reinforcer", "punisher", "consequentStimulus"):
        # Reinforcer declarations at schedule level
        name = humanize(str(positional or ""))
        role = {
            "reinforcer": ("reinforcer", "強化子"),
            "punisher": ("punisher", "罰刺激"),
            "consequentStimulus": ("consequent stimulus", "結果刺激"),
        }[kw]
        if style.locale == "ja":
            return f"{name}を{role[1]}として用いた。"
        return f"{name} served as the {role[0]}."

    if kw == "context":
        ctx = str(positional or "")
        if style.locale == "ja":
            return f"文脈{ctx}で実施された。"
        return f"The procedure was conducted in context {ctx}."

    if kw == "brief":
        if positional == "none":
            return ""
        brief_name = humanize(str(positional or ""))
        if style.locale == "ja":
            return f"{brief_name}が簡略刺激として呈示された。"
        return f"{brief_name} served as the brief stimulus."

    if kw == "iti":
        return _render_iti_schedule_level(params, positional, style)

    if kw == "cs_interval":
        return _render_cs_interval_schedule_level(params, positional, style)

    return ""


def _render_iti_schedule_level(
    params: dict, positional, style: Style,
) -> str:
    """Render a schedule-level @iti annotation.

    Accepts the same ``{distribution, mean}`` payload as the program-level
    annotation but localized for the attached schedule. Keeping rendering
    here ensures it survives ``AnnotatedSchedule`` unwrap where the
    annotation is moved onto the inner expression.
    """
    dist = params.get("distribution") or positional
    mean = params.get("mean")
    if not dist:
        return ""
    mean_str = ""
    if isinstance(mean, dict):
        mean_val = mean.get("value", 0)
        mean_unit = mean.get("time_unit") or mean.get("unit", "s")
        mean_str = format_duration(mean_val, mean_unit, style)
    elif mean is not None:
        mean_str = format_duration(float(mean), "s", style)
    if style.locale == "ja":
        dist_ja = {
            "fixed": "固定", "uniform": "一様", "exponential": "指数",
        }.get(str(dist), str(dist))
        if mean_str:
            return f"試行間間隔は平均{mean_str}の{dist_ja}分布に従った。"
        return f"試行間間隔は{dist_ja}分布に従った。"
    if mean_str:
        return (
            f"The inter-trial interval followed a {dist} distribution "
            f"with a mean of {mean_str}."
        )
    return f"The inter-trial interval followed a {dist} distribution."


def _render_cs_interval_schedule_level(
    params: dict, positional, style: Style,
) -> str:
    val = params.get("value", positional)
    unit = params.get("time_unit") or params.get("unit", "s")
    if val is None:
        return ""
    dur = format_duration(float(val), unit, style)
    if style.locale == "ja":
        return f"CS-US 間隔は{dur}であった。"
    return f"The CS-US interval was {dur}."
