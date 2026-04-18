"""Respondent (Pavlovian) schedule visitors.

Covers the 14 Tier A primitives defined in schema/respondent/ast.schema.json.
These translate directly to Method-section sentences describing CS-US
pairings, unpaired controls, intertrial intervals, and compound/serial CS
arrangements.
"""

from __future__ import annotations

from ...ast_types import ScheduleNode
from ...references import ReferenceCollector
from ...style import Style
from ._common import format_duration, humanize


def visit_respondent(
    node: ScheduleNode, *, style: Style,
    refs: ReferenceCollector | None = None, first_mention: bool = True,
) -> str:
    t = node.get("type", "")
    fn = _DISPATCH.get(t)
    if fn is None:
        return ""
    return fn(node, style, refs)


# --- R1-R4: Pair.* -----------------------------------------------------------

def _forward_delay(node: dict, style: Style, refs) -> str:
    if refs is not None:
        refs.cite_if_known("pavlov_1927")
    cs = humanize(str(node.get("cs", "")))
    us = humanize(str(node.get("us", "")))
    isi = _dur(node.get("isi"), style)
    cs_dur = _dur(node.get("cs_duration"), style)
    if style.locale == "ja":
        return (
            f"{cs}を条件刺激、{us}を無条件刺激とする順行遅延対呈示を実施した"
            f"（CS-US 間隔 {isi}、CS 持続 {cs_dur}）。"
        )
    return (
        f"{cs} served as the conditioned stimulus and {us} as the "
        f"unconditioned stimulus in a forward-delay pairing procedure "
        f"(CS-US interval {isi}; CS duration {cs_dur})."
    )


def _forward_trace(node: dict, style: Style, refs) -> str:
    if refs is not None:
        refs.cite_if_known("pavlov_1927")
    cs = humanize(str(node.get("cs", "")))
    us = humanize(str(node.get("us", "")))
    trace = _dur(node.get("trace_interval"), style)
    cs_dur = node.get("cs_duration")
    cs_dur_str = _dur(cs_dur, style) if cs_dur else ""
    if style.locale == "ja":
        extra = f"、CS 持続 {cs_dur_str}" if cs_dur_str else ""
        return (
            f"{cs}を条件刺激、{us}を無条件刺激とする順行トレース対呈示を実施した"
            f"（トレース間隔 {trace}{extra}）。"
        )
    extra = f"; CS duration {cs_dur_str}" if cs_dur_str else ""
    return (
        f"{cs} served as the conditioned stimulus and {us} as the "
        f"unconditioned stimulus in a forward-trace pairing procedure "
        f"(trace interval {trace}{extra})."
    )


def _simultaneous(node: dict, style: Style, refs) -> str:
    cs = humanize(str(node.get("cs", "")))
    us = humanize(str(node.get("us", "")))
    if style.locale == "ja":
        return f"{cs}と{us}の同時対呈示を実施した。"
    return (
        f"{cs} and {us} were presented simultaneously in a Pavlovian "
        f"pairing procedure."
    )


def _backward(node: dict, style: Style, refs) -> str:
    us = humanize(str(node.get("us", "")))
    cs = humanize(str(node.get("cs", "")))
    isi = _dur(node.get("isi"), style)
    if style.locale == "ja":
        return (
            f"{us}の直後に{cs}を呈示する逆行対呈示を実施した"
            f"（US-CS 間隔 {isi}）。"
        )
    return (
        f"{us} was followed by {cs} in a backward pairing procedure "
        f"(US-CS interval {isi})."
    )


# --- R5-R10: controls --------------------------------------------------------

def _extinction(node: dict, style: Style, refs) -> str:
    cs = humanize(str(node.get("cs", "")))
    if style.locale == "ja":
        return f"{cs}の単独呈示により消去を実施した。"
    return f"{cs} was presented alone for extinction testing."


def _cs_only(node: dict, style: Style, refs) -> str:
    cs = humanize(str(node.get("cs", "")))
    trials = node.get("trials", 0)
    if style.locale == "ja":
        return f"{cs}を単独で{int(trials)}試行呈示した。"
    return f"{cs} was presented alone on {int(trials)} trials."


def _us_only(node: dict, style: Style, refs) -> str:
    us = humanize(str(node.get("us", "")))
    trials = node.get("trials", 0)
    if style.locale == "ja":
        return f"{us}を単独で{int(trials)}試行呈示した。"
    return f"{us} was presented alone on {int(trials)} trials."


def _contingency(node: dict, style: Style, refs) -> str:
    if refs is not None:
        refs.cite_if_known("rescorla_1967")
    p_cs = node.get("p_us_given_cs")
    p_no = node.get("p_us_given_no_cs")
    if style.locale == "ja":
        return (
            f"p(US|CS)={p_cs}、p(US|¬CS)={p_no}の"
            f"随伴性条件づけ手続きを実施した。"
        )
    return (
        f"Pavlovian contingency procedure with "
        f"p(US|CS)={p_cs} and p(US|no CS)={p_no}."
    )


def _truly_random(node: dict, style: Style, refs) -> str:
    if refs is not None:
        refs.cite_if_known("rescorla_1967")
    cs = humanize(str(node.get("cs", "")))
    us = humanize(str(node.get("us", "")))
    p = node.get("p")
    if style.locale == "ja":
        p_str = f"（p={p}）" if p is not None else ""
        return f"{cs}と{us}を真のランダム統制として配置した{p_str}。"
    p_str = f" (p={p})" if p is not None else ""
    return (
        f"{cs} and {us} were arranged as a truly random control{p_str}."
    )


def _explicitly_unpaired(node: dict, style: Style, refs) -> str:
    cs = humanize(str(node.get("cs", "")))
    us = humanize(str(node.get("us", "")))
    sep = node.get("min_separation")
    sep_str = _dur(sep, style) if sep else ""
    if style.locale == "ja":
        extra = f"（最小分離 {sep_str}）" if sep_str else ""
        return f"{cs}と{us}を明示的に非対呈示で配置した{extra}。"
    extra = f" (minimum separation {sep_str})" if sep_str else ""
    return (
        f"{cs} and {us} were arranged as an explicitly unpaired "
        f"control{extra}."
    )


# --- R11-R14: compound / serial / ITI / differential ------------------------

def _compound(node: dict, style: Style, refs) -> str:
    cs_list = node.get("cs_list", []) or []
    names = [humanize(str(c)) for c in cs_list]
    if style.locale == "ja":
        return (
            f"{'、'.join(names)}を同時に複合条件刺激として呈示した。"
        )
    return (
        f"{', '.join(names)} were presented simultaneously as a "
        f"compound conditioned stimulus."
    )


def _serial(node: dict, style: Style, refs) -> str:
    cs_list = node.get("cs_list", []) or []
    names = [humanize(str(c)) for c in cs_list]
    isi = _dur(node.get("isi"), style)
    if style.locale == "ja":
        return (
            f"{'→'.join(names)}の順に条件刺激を連続呈示した"
            f"（刺激間間隔 {isi}）。"
        )
    return (
        f"Conditioned stimuli {' → '.join(names)} were presented in "
        f"serial order (inter-stimulus interval {isi})."
    )


def _iti(node: dict, style: Style, refs) -> str:
    dist = node.get("distribution", "fixed")
    mean_str = _dur(node.get("mean"), style)
    dist_en = {"fixed": "fixed", "uniform": "uniform", "exponential": "exponential"}[dist]
    dist_ja = {"fixed": "固定", "uniform": "一様", "exponential": "指数"}[dist]
    if style.locale == "ja":
        return f"試行間間隔は平均{mean_str}の{dist_ja}分布に従った。"
    return (
        f"The inter-trial interval followed a {dist_en} distribution with "
        f"mean {mean_str}."
    )


def _differential(node: dict, style: Style, refs) -> str:
    if refs is not None:
        refs.cite_if_known("pavlov_1927")
    csp = humanize(str(node.get("cs_positive", "")))
    csn = humanize(str(node.get("cs_negative", "")))
    us = node.get("us")
    if style.locale == "ja":
        us_part = f"（US: {humanize(str(us))}）" if us else ""
        return f"{csp}を CS+、{csn}を CS− とする弁別条件づけを実施した{us_part}。"
    us_part = f" (US: {humanize(str(us))})" if us else ""
    return (
        f"Differential conditioning with {csp} as CS+ and {csn} as "
        f"CS−{us_part}."
    )


def _extension(node: dict, style: Style, refs) -> str:
    name = node.get("name", "")
    if style.locale == "ja":
        return f"拡張レスポンデント手続き {name} を実施した。"
    return f"A {name} respondent procedure was conducted."


_DISPATCH = {
    "PairForwardDelay": _forward_delay,
    "PairForwardTrace": _forward_trace,
    "PairSimultaneous": _simultaneous,
    "PairBackward": _backward,
    "Extinction": _extinction,
    "CSOnly": _cs_only,
    "USOnly": _us_only,
    "Contingency": _contingency,
    "TrulyRandom": _truly_random,
    "ExplicitlyUnpaired": _explicitly_unpaired,
    # Compound (respondent) has cs_list; operant Compound has components.
    # Dispatch by type+cs_list presence is done in visitors/__init__.py.
    "RespondentCompound": _compound,
    "Serial": _serial,
    "ITI": _iti,
    "Differential": _differential,
    "ExtensionPrimitive": _extension,
}


# --- helpers -----------------------------------------------------------------

def _dur(duration: dict | None, style: Style) -> str:
    if not duration:
        return ""
    return format_duration(
        duration.get("value", 0), duration.get("unit", "s"), style,
    )


def is_respondent_node(node: dict) -> bool:
    """Return True when a node belongs to the respondent Tier A set.

    Called from visitors/__init__.py to route ambiguous ``type`` values
    (operant Compound vs. respondent Compound). Respondent Compound has a
    ``cs_list`` key; operant Compound has ``components``.
    """
    t = node.get("type", "")
    if t in {
        "PairForwardDelay", "PairForwardTrace", "PairSimultaneous",
        "PairBackward", "Extinction", "CSOnly", "USOnly",
        "Contingency", "TrulyRandom", "ExplicitlyUnpaired",
        "Serial", "ITI", "Differential", "ExtensionPrimitive",
    }:
        return True
    if t == "Compound" and "cs_list" in node:
        return True
    return False
