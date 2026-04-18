"""Trial-based schedule visitor: MTS (matching-to-sample) and Go/NoGo."""

from __future__ import annotations

from ...ast_types import ScheduleNode
from ...references import ReferenceCollector
from ...style import Style
from ._common import decorate_leaf, fmt_val, format_component, format_duration


def visit_trial_based(
    node: ScheduleNode, *, style: Style,
    refs: ReferenceCollector | None = None, first_mention: bool = True,
) -> str:
    trial_type = node.get("trial_type", "")
    if trial_type == "MTS":
        base = _mts(node, style, refs, first_mention)
    elif trial_type == "GoNoGo":
        base = _gonogo(node, style, refs, first_mention)
    else:
        return ""
    return decorate_leaf(base, node, style=style)


def _mts(
    node: ScheduleNode, style: Style,
    refs: ReferenceCollector | None, first_mention: bool,
) -> str:
    comparisons: int = node.get("comparisons", 3)
    consequence = node.get("consequence", {})
    incorrect = node.get("incorrect", {"type": "Special", "kind": "EXT"})
    iti: float = node.get("ITI", 0)
    iti_unit: str = node.get("ITI_unit", "s")
    mts_type: str = node.get("mts_type", "arbitrary")

    iti_str = format_duration(iti, iti_unit, style)
    comp_str = _spell_comparisons(comparisons, style)
    consequence_str = _describe_consequence(consequence, style)
    incorrect_str = _describe_incorrect(incorrect, style)

    if style.locale == "ja":
        type_label = "同一" if mts_type == "identity" else "任意"
        sentences = [
            f"{type_label}見本合わせ（MTS）手続きを使用し、"
            f"各試行において{comp_str}個の比較刺激を呈示した。",
            f"正反応に対しては{consequence_str}。",
            f"誤反応に対しては{incorrect_str}。",
            f"試行間間隔は{iti_str}であった。",
        ]
    else:
        type_label = "identity" if mts_type == "identity" else "arbitrary"
        label = (
            f"An {type_label} matching-to-sample (MTS) procedure"
            if first_mention
            else "The MTS procedure"
        )
        sentences = [
            f"{label} was used with {comp_str} comparison stimuli.",
            f"Correct responses {consequence_str}.",
            f"Incorrect responses {incorrect_str}.",
            f"A {iti_str} inter-trial interval separated successive trials.",
        ]
    return " ".join(sentences)


def _gonogo(
    node: ScheduleNode, style: Style,
    refs: ReferenceCollector | None, first_mention: bool,
) -> str:
    response_window: float = node.get("responseWindow", 0)
    # Schema field: responseWindowUnit. Accept the snake-case variant as
    # a defensive fallback for older fixtures.
    rw_unit: str = node.get("responseWindowUnit") or node.get(
        "responseWindow_unit", "s",
    )
    consequence = node.get("consequence", {})
    incorrect = node.get("incorrect", {"type": "Special", "kind": "EXT"})
    false_alarm = node.get("falseAlarm")
    iti: float = node.get("ITI", 0)
    iti_unit: str = node.get("ITI_unit", "s")

    rw_str = format_duration(response_window, rw_unit, style)
    iti_str = format_duration(iti, iti_unit, style)
    consequence_str = _describe_consequence(consequence, style)
    incorrect_str = _describe_incorrect(incorrect, style)
    false_alarm_str = (
        _describe_incorrect(false_alarm, style) if false_alarm else ""
    )

    if style.locale == "ja":
        pieces = [
            "Go/NoGo 弁別手続きを使用した。",
            f"Go 試行では{rw_str}の反応ウィンドウ内の反応に対して{consequence_str}。",
        ]
        if false_alarm_str:
            pieces.append(f"NoGo 試行での反応には{false_alarm_str}。")
        else:
            pieces.append(f"誤反応（見逃し／誤警報）に対しては{incorrect_str}。")
        pieces.append(f"試行間間隔は{iti_str}であった。")
        return "".join(pieces)

    pieces_en = [
        "A Go/NoGo discrimination procedure was used.",
        (
            f"Responses during the {rw_str} response window on Go trials "
            f"{consequence_str}."
        ),
    ]
    if false_alarm_str:
        pieces_en.append(
            f"Responses on NoGo trials (false alarms) {false_alarm_str}."
        )
    else:
        pieces_en.append(f"Misses and false alarms {incorrect_str}.")
    pieces_en.append(
        f"A {iti_str} inter-trial interval separated successive trials."
    )
    return " ".join(pieces_en)


def _spell_comparisons(n: int, style: Style) -> str:
    if style.spell_numbers_below > 0 and n < style.spell_numbers_below:
        words = {
            2: "two", 3: "three", 4: "four", 5: "five",
            6: "six", 7: "seven", 8: "eight", 9: "nine",
        }
        return words.get(n, str(n))
    return str(n)


def _describe_consequence(node: ScheduleNode, style: Style) -> str:
    kind = node.get("kind", "") if node.get("type") == "Special" else ""
    if kind == "CRF":
        if style.locale == "ja":
            return "強化子が呈示された（連続強化）"
        return "produced a reinforcer (continuous reinforcement)"
    if kind == "EXT":
        if style.locale == "ja":
            return "プログラムされた結果は呈示されなかった（消去）"
        return "had no programmed consequences (extinction)"
    sched = format_component(node, style=style, first_mention=False)
    if style.locale == "ja":
        return f"{sched}スケジュールに従って強化された"
    return f"were reinforced under a {sched} schedule"


def _describe_incorrect(node: ScheduleNode, style: Style) -> str:
    kind = node.get("kind", "") if node.get("type") == "Special" else ""
    if kind == "EXT":
        if style.locale == "ja":
            return "プログラムされた結果は呈示されなかった（消去）"
        return "had no programmed consequences (extinction)"
    if kind == "CRF":
        if style.locale == "ja":
            return "強化子が呈示された（連続強化）"
        return "produced a reinforcer (continuous reinforcement)"
    sched = format_component(node, style=style, first_mention=False)
    domain = node.get("domain", "")
    if domain == "T":
        dur = format_duration(node.get("value", 0), node.get("time_unit", "s"), style)
        if style.locale == "ja":
            return f"{dur}のタイムアウトが設定された"
        return f"were followed by a {dur} timeout"
    if style.locale == "ja":
        return f"{sched}スケジュールが適用された"
    return f"were followed by a {sched} schedule"
