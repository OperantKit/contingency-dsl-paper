"""Journal style definitions for Method section compilation.

Each Style provides locale-specific vocabulary, typographical conventions,
heading labels, and citation format rules. New journals can be added by
subclassing Style or creating a new instance.

Built-in styles:
    JEAB  — Journal of the Experimental Analysis of Behavior (English, APA 7th)
    JABA  — Japanese Association for Behavior Analysis (日本語, APA-based)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Style:
    """Defines how a Method section is rendered for a specific journal.

    Attributes:
        name: Short identifier (e.g., "jeab", "jaba").
        locale: Language code ("en", "ja").
        heading_method: Heading text for the Method section.
        heading_subjects: Heading text for Subjects subsection.
        heading_apparatus: Heading text for Apparatus subsection.
        heading_procedure: Heading text for Procedure subsection.
        heading_references: Heading text for References section.
        abbrev_space: Whether to insert space in schedule abbreviations
            (True: "VI 30-s", False: "VI30-s"). JEAB uses True.
        time_unit_hyphen: Whether to hyphenate time units
            (True: "30-s", False: "30 s"). JEAB uses True.
        spell_numbers_below: Numbers below this threshold are spelled out
            (APA: 10). Set to 0 to always use digits.
        distribution_names: Full names for F/V/R distributions.
        domain_names: Full names for R/I/T domains.
        combinator_names: Full names for compound combinators.
        special_names: Full names for CRF/EXT.
        citation_format: "apa7" or "jaba" (slight variations).
        framing_reinforced: Sentence frame for "responses were reinforced under..."
        framing_extinction: Sentence for extinction.
        framing_crf: Sentence for continuous reinforcement.
    """

    name: str
    locale: Literal["en", "ja"]

    # --- Headings ---
    heading_method: str = "Method"
    heading_subjects: str = "Subjects"
    heading_apparatus: str = "Apparatus"
    heading_procedure: str = "Procedure"
    heading_references: str = "References"

    # --- Typographical conventions ---
    abbrev_space: bool = True
    time_unit_hyphen: bool = True
    spell_numbers_below: int = 10

    # --- Vocabulary ---
    distribution_names: dict[str, str] = field(default_factory=dict)
    domain_names: dict[str, str] = field(default_factory=dict)
    combinator_names: dict[str, str] = field(default_factory=dict)
    special_names: dict[str, str] = field(default_factory=dict)

    # --- Citation format ---
    citation_format: str = "apa7"

    # --- Sentence frames ---
    framing_reinforced: str = "Responses were reinforced under a {schedule} schedule."
    framing_extinction: str = "Responses had no programmed consequences (extinction)."
    framing_crf: str = "Each response produced a reinforcer (continuous reinforcement)."


# ---------------------------------------------------------------------------
# Built-in styles
# ---------------------------------------------------------------------------

JEAB = Style(
    name="jeab",
    locale="en",
    heading_method="Method",
    heading_subjects="Subjects",
    heading_apparatus="Apparatus",
    heading_procedure="Procedure",
    heading_references="References",
    abbrev_space=True,
    time_unit_hyphen=True,
    spell_numbers_below=10,
    distribution_names={"F": "fixed", "V": "variable", "R": "random"},
    domain_names={"R": "ratio", "I": "interval", "T": "time"},
    combinator_names={
        "Conc": "concurrent", "Chain": "chained", "Alt": "alternative",
        "Conj": "conjunctive", "Tand": "tandem", "Mult": "multiple",
        "Mix": "mixed", "Overlay": "overlay", "Interpolate": "interpolated",
    },
    special_names={"CRF": "continuous reinforcement", "EXT": "extinction"},
    citation_format="apa7",
    framing_reinforced="Responses were reinforced under a {schedule} schedule.",
    framing_extinction="Responses had no programmed consequences (extinction).",
    framing_crf="Each response produced a reinforcer (continuous reinforcement).",
)

JABA = Style(
    name="jaba",
    locale="ja",
    heading_method="方法",
    heading_subjects="被験体",
    heading_apparatus="装置",
    heading_procedure="手続き",
    heading_references="引用文献",
    abbrev_space=True,
    time_unit_hyphen=True,
    spell_numbers_below=0,  # 日本語では数字をそのまま使用
    distribution_names={"F": "固定", "V": "変動", "R": "ランダム"},
    domain_names={"R": "比率", "I": "時隔", "T": "時間"},
    combinator_names={
        "Conc": "並立", "Chain": "連鎖", "Alt": "二択",
        "Conj": "連言", "Tand": "タンデム", "Mult": "多元",
        "Mix": "混合", "Overlay": "重畳", "Interpolate": "挿入",
    },
    special_names={"CRF": "連続強化", "EXT": "消去"},
    citation_format="apa7",
    framing_reinforced="{schedule}スケジュールに従って反応が強化された。",
    framing_extinction="反応に対してプログラムされた結果は呈示されなかった（消去）。",
    framing_crf="すべての反応に対して強化子が呈示された（連続強化）。",
)


STYLES: dict[str, Style] = {
    "jeab": JEAB,
    "jaba": JABA,
}


def get_style(name: str) -> Style:
    """Look up a registered style by name.

    Raises:
        KeyError: If the style name is not registered.
    """
    return STYLES[name]


def register_style(style: Style, *, force: bool = False) -> None:
    """Register a Style so that it can be looked up via ``get_style``.

    Args:
        style: The Style to register. Its ``name`` field becomes the key.
        force: If False (default), raise ValueError on name collision with
            an existing registered style. If True, overwrite silently.

    Raises:
        ValueError: If ``style.name`` is already registered and ``force`` is
            False.
    """
    if not force and style.name in STYLES:
        raise ValueError(
            f"style {style.name!r} is already registered; "
            f"pass force=True to overwrite"
        )
    STYLES[style.name] = style


def unregister_style(name: str) -> None:
    """Remove a registered style by name.

    Raises:
        KeyError: If the style name is not registered.
    """
    del STYLES[name]
