"""Apparatus section generator.

Consumes program_annotations:
    {"keyword": "chamber", "positional": "med-associates", "params": {"model": "ENV-007"}}
    {"keyword": "operandum", "positional": "left_lever", "params": {"component": 1}}
    {"keyword": "hardware", "positional": "MED-PC IV"}

Note on @operandum dual distribution (operandum-migration.md):
    @operandum carries both physical info (Apparatus) and procedural
    assignment (Procedure). This module extracts the physical aspects;
    sections/procedure.py extracts the procedural mapping (component=N).
"""

from __future__ import annotations

from ..ast_types import ProgramNode
from ..references import ReferenceCollector
from ..style import JEAB, Style
from .annotation_expander import expand_bundled_annotations


def render_apparatus(
    program: ProgramNode,
    style: Style = JEAB,
    refs: ReferenceCollector | None = None,
) -> str:
    """Generate the Apparatus subsection from annotations."""
    attrs = _extract_apparatus_attrs(program)
    if not attrs:
        return ""

    sentences: list[str] = []

    chamber = attrs.get("chamber")
    if chamber:
        sentences.append(_build_chamber_sentence(chamber, style))

    operanda = attrs.get("operanda", [])
    if operanda:
        sentences.append(_build_operanda_sentence(operanda, style))

    interface = attrs.get("interface")
    if interface:
        sentences.append(_build_interface_sentence(interface, style))

    hardware = attrs.get("hardware")
    if hardware:
        if style.locale == "ja":
            sentences.append(
                f"実験事象の制御およびデータ記録には{hardware}を使用した。"
            )
        else:
            sentences.append(
                f"Experimental events were controlled and data were recorded "
                f"by {hardware}."
            )

    return " ".join(sentences)


def _extract_apparatus_attrs(program: ProgramNode) -> dict:
    """Extract apparatus-related attributes from program_annotations.

    Accepts both unbundled (``@chamber("med-associates")``) and bundled
    (``@apparatus(chamber="chamber_A")``) annotation shapes.
    """
    result: dict = {}
    operanda: list[dict] = []
    anns = expand_bundled_annotations(
        list(program.get("program_annotations", []) or [])
    )
    for ann in anns:
        kw = ann.get("keyword", "")
        if kw == "chamber":
            result["chamber"] = {
                "name": ann.get("positional", ""),
                **(ann.get("params", {}) or {}),
            }
        elif kw == "operandum":
            operanda.append({
                "name": ann.get("positional", ""),
                **(ann.get("params", {}) or {}),
            })
        elif kw == "interface":
            result["interface"] = {
                "name": ann.get("positional", ""),
                **(ann.get("params", {}) or {}),
            }
        elif kw in ("hardware", "hw"):
            # ``hw`` is the schema-declared alias for ``hardware``
            result["hardware"] = ann.get("positional", "")
    if operanda:
        result["operanda"] = operanda
    return result


def _build_chamber_sentence(chamber: dict, style: Style) -> str:
    name = chamber.get("name", "")
    model = chamber.get("model", "")
    model_part = f" (Model {model})" if model else ""
    if style.locale == "ja":
        return f"実験は{name}{model_part}のオペラント実験箱で実施した。"
    return f"Sessions were conducted in {name}{model_part} operant conditioning chambers."


def _build_operanda_sentence(operanda: list[dict], style: Style) -> str:
    """Build operandum physical description for Apparatus section.

    Only physical identity is described here. Component assignment
    ("left_lever → component 1") is handled by procedure.py.
    """
    names = [_humanize(op.get("name", "response device")) for op in operanda]
    if style.locale == "ja":
        items = "、".join(names)
        return f"実験箱内には{items}が設置された。"
    else:
        if len(names) == 1:
            return f"Each chamber contained a {names[0]}."
        items = ", ".join(names[:-1]) + f", and {names[-1]}"
        return f"Each chamber contained {items}."


def _build_interface_sentence(interface: dict, style: Style) -> str:
    name = interface.get("name", "")
    port = interface.get("port", "")
    port_part_en = f" (port: {port})" if port else ""
    port_part_ja = f"（ポート: {port}）" if port else ""
    if style.locale == "ja":
        return f"ハードウェアインターフェースとして{name}{port_part_ja}を使用した。"
    return (
        f"The {name} interface{port_part_en} was used to bridge the "
        f"controller and the apparatus."
    )


def _humanize(name: str) -> str:
    """Convert DSL identifier to human-readable form: left_lever → left lever."""
    return name.replace("_", " ")
