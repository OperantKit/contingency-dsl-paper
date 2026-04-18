"""Lightweight TypedDict definitions mirroring contingency-dsl schemas.

Defines Python types for the language-independent JSON AST so that
contingency-dsl2procedure has ZERO runtime dependency on a specific parser.
Any parser (Python, Rust, etc.) emitting conformant JSON feeds this compiler.

Type discrimination follows the ``type`` field. For ``Modifier`` nodes the
``modifier`` field further discriminates (DRL / DRH / DRO / PR / Repeat /
Lag / Pctl). For ``AversiveSchedule``, ``kind`` discriminates (Sidman /
DiscrimAv). Wrapper nodes for LimitedHold / Timeout / ResponseCost no
longer exist — they are absorbed as optional ``limitedHold`` /
``limitedHoldUnit`` / ``timeout`` / ``responseCost`` properties on leaf
schedule nodes, along with a ``annotations`` array for schedule-level
annotations.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict, Union


# --- Primitives ---

TimeUnit = Literal["s", "ms", "min"]
DistributionStr = Literal["F", "V", "R"]
DomainStr = Literal["R", "I", "T"]
CombinatorStr = Literal[
    "Conc", "Alt", "Conj", "Chain", "Tand", "Mult", "Mix",
    "Overlay", "Interpolate",
]


# --- Annotation ---

AnnotationValue = Union[str, float, int, bool, list, dict]


class Annotation(TypedDict, total=False):
    type: Literal["Annotation"]
    keyword: str
    positional: AnnotationValue
    params: dict[str, AnnotationValue]


# --- ParamDecl ---

ParamDeclName = Literal["LH", "COD", "FRCO", "BO", "RD"]


class ParamDecl(TypedDict, total=False):
    type: Literal["ParamDecl"]
    name: ParamDeclName
    value: float
    time_unit: TimeUnit


# --- Binding ---

class Binding(TypedDict):
    type: Literal["Binding"]
    name: str
    value: ScheduleNode


# --- Leaf-property objects ---

class TimeoutParams(TypedDict, total=False):
    duration: float
    durationUnit: TimeUnit
    resetOnResponse: bool
    contingentResponse: int


class ResponseCostParams(TypedDict, total=False):
    amount: float
    unit: str


# Common leaf-node properties shared by Atomic/Special/DRModifier/SecondOrder
# etc. Each individual TypedDict restates them for clarity.


# --- Schedule nodes (discriminated union on "type") ---

class AtomicNode(TypedDict, total=False):
    type: Literal["Atomic"]
    dist: DistributionStr
    domain: DomainStr
    value: float
    time_unit: TimeUnit
    limitedHold: float
    limitedHoldUnit: TimeUnit
    timeout: TimeoutParams
    responseCost: ResponseCostParams
    annotations: list[Annotation]


class SpecialNode(TypedDict, total=False):
    type: Literal["Special"]
    kind: Literal["EXT", "CRF"]
    limitedHold: float
    limitedHoldUnit: TimeUnit
    timeout: TimeoutParams
    responseCost: ResponseCostParams
    annotations: list[Annotation]


# CombinatorParams keys: COD / FRCO / BO / count / onset / target / PUNISH

class CODSymmetric(TypedDict, total=False):
    value: float
    time_unit: TimeUnit


class CODDirectionalEntry(TypedDict, total=False):
    from_: int  # actual key "from"
    to: int
    value: float
    time_unit: TimeUnit


class CODDirectional(TypedDict, total=False):
    base: CODSymmetric
    directional: list[dict]  # CODDirectionalEntry (with "from" key)


CODValue = Union[CODSymmetric, CODDirectional]


class FRCOValue(TypedDict):
    value: int


class BOValue(TypedDict, total=False):
    value: float
    time_unit: TimeUnit


class CountValue(TypedDict):
    value: int


class OnsetValue(TypedDict, total=False):
    value: float
    time_unit: TimeUnit


class PunishDirectionalEntry(TypedDict, total=False):
    from_: int
    to: int
    schedule: "ScheduleNode"


class PunishComponentEntry(TypedDict):
    component: int
    schedule: "ScheduleNode"


class PunishParams(TypedDict, total=False):
    changeover: "ScheduleNode"
    directional: list[dict]
    component: list[PunishComponentEntry]


class CombinatorParams(TypedDict, total=False):
    COD: CODValue
    FRCO: FRCOValue
    BO: BOValue
    count: CountValue
    onset: OnsetValue
    target: Literal["changeover", "all"]
    PUNISH: PunishParams


class CompoundNode(TypedDict, total=False):
    type: Literal["Compound"]
    combinator: CombinatorStr
    components: list["ScheduleNode"]
    params: CombinatorParams
    annotations: list[Annotation]


class SecondOrderNode(TypedDict, total=False):
    type: Literal["SecondOrder"]
    overall: AtomicNode
    unit: AtomicNode
    limitedHold: float
    limitedHoldUnit: TimeUnit
    timeout: TimeoutParams
    responseCost: ResponseCostParams
    annotations: list[Annotation]


# --- Modifier subtypes (discriminated on "modifier") ---

class DRModifierNode(TypedDict, total=False):
    type: Literal["Modifier"]
    modifier: Literal["DRL", "DRH", "DRO"]
    value: float
    time_unit: TimeUnit
    limitedHold: float
    limitedHoldUnit: TimeUnit
    timeout: TimeoutParams
    responseCost: ResponseCostParams
    annotations: list[Annotation]


class PRModifierNode(TypedDict, total=False):
    type: Literal["Modifier"]
    modifier: Literal["PR"]
    pr_step: Literal["hodos", "exponential", "linear", "geometric"]
    pr_start: int
    pr_increment: int
    pr_ratio: float
    annotations: list[Annotation]


class RepeatModifierNode(TypedDict, total=False):
    type: Literal["Modifier"]
    modifier: Literal["Repeat"]
    value: int
    inner: "ScheduleNode"
    annotations: list[Annotation]


class LagModifierNode(TypedDict, total=False):
    type: Literal["Modifier"]
    modifier: Literal["Lag"]
    value: float
    length: int
    annotations: list[Annotation]


class PctlModifierNode(TypedDict, total=False):
    type: Literal["Modifier"]
    modifier: Literal["Pctl"]
    pctl_target: Literal["IRT", "latency", "duration", "force", "rate"]
    pctl_rank: int
    pctl_window: int
    pctl_dir: Literal["below", "above"]
    annotations: list[Annotation]


ModifierNode = Union[
    DRModifierNode, PRModifierNode, RepeatModifierNode,
    LagModifierNode, PctlModifierNode,
]


# --- Aversive schedule ---

class SidmanInterval(TypedDict):
    value: float
    time_unit: TimeUnit


class SidmanParams(TypedDict):
    SSI: SidmanInterval
    RSI: SidmanInterval


class DiscrimAvParams(TypedDict, total=False):
    CSUSInterval: SidmanInterval
    ITI: SidmanInterval
    mode: Literal["fixed", "escape"]
    ShockDuration: SidmanInterval
    MaxShock: SidmanInterval


class AversiveNode(TypedDict, total=False):
    type: Literal["AversiveSchedule"]
    kind: Literal["Sidman", "DiscrimAv"]
    params: Union[SidmanParams, DiscrimAvParams]
    responseCost: ResponseCostParams
    annotations: list[Annotation]


# --- Trial-based ---

class TrialBasedNode(TypedDict, total=False):
    type: Literal["TrialBased"]
    trial_type: Literal["MTS", "GoNoGo"]
    comparisons: int
    consequence: "ScheduleNode"
    incorrect: "ScheduleNode"
    ITI: float
    ITI_unit: TimeUnit
    mts_type: Literal["identity", "arbitrary"]
    responseWindow: float
    responseWindow_unit: TimeUnit
    limitedHold: float
    limitedHoldUnit: TimeUnit
    timeout: TimeoutParams
    responseCost: ResponseCostParams
    annotations: list[Annotation]


# --- Identifier reference (pre-expansion) ---

class IdentifierRefNode(TypedDict):
    type: Literal["IdentifierRef"]
    name: str


# --- Respondent nodes (Tier A primitives R1-R14) ---

class DurationValue(TypedDict):
    value: float
    unit: TimeUnit


class PairForwardDelayNode(TypedDict, total=False):
    type: Literal["PairForwardDelay"]
    cs: str
    us: str
    isi: DurationValue
    cs_duration: DurationValue


class PairForwardTraceNode(TypedDict, total=False):
    type: Literal["PairForwardTrace"]
    cs: str
    us: str
    trace_interval: DurationValue
    cs_duration: DurationValue


class PairSimultaneousNode(TypedDict):
    type: Literal["PairSimultaneous"]
    cs: str
    us: str


class PairBackwardNode(TypedDict, total=False):
    type: Literal["PairBackward"]
    us: str
    cs: str
    isi: DurationValue


class ExtinctionRespNode(TypedDict):
    type: Literal["Extinction"]
    cs: str


class CSOnlyNode(TypedDict):
    type: Literal["CSOnly"]
    cs: str
    trials: int


class USOnlyNode(TypedDict):
    type: Literal["USOnly"]
    us: str
    trials: int


class ContingencyNode(TypedDict):
    type: Literal["Contingency"]
    p_us_given_cs: float
    p_us_given_no_cs: float


class TrulyRandomNode(TypedDict, total=False):
    type: Literal["TrulyRandom"]
    cs: str
    us: str
    p: float


class ExplicitlyUnpairedNode(TypedDict, total=False):
    type: Literal["ExplicitlyUnpaired"]
    cs: str
    us: str
    min_separation: DurationValue


class RespondentCompoundNode(TypedDict, total=False):
    type: Literal["Compound"]  # collides with operant Compound; disambiguated by presence of cs_list
    cs_list: list[str]
    mode: Literal["Simultaneous"]


class RespondentSerialNode(TypedDict):
    type: Literal["Serial"]
    cs_list: list[str]
    isi: DurationValue


class RespondentITINode(TypedDict):
    type: Literal["ITI"]
    distribution: Literal["fixed", "uniform", "exponential"]
    mean: DurationValue


class DifferentialNode(TypedDict, total=False):
    type: Literal["Differential"]
    cs_positive: str
    cs_negative: str
    us: str


class RespondentExtensionNode(TypedDict, total=False):
    type: Literal["ExtensionPrimitive"]
    name: str
    positional: list
    params: dict


RespondentNode = Union[
    PairForwardDelayNode, PairForwardTraceNode, PairSimultaneousNode,
    PairBackwardNode, ExtinctionRespNode, CSOnlyNode, USOnlyNode,
    ContingencyNode, TrulyRandomNode, ExplicitlyUnpairedNode,
    RespondentCompoundNode, RespondentSerialNode, RespondentITINode,
    DifferentialNode, RespondentExtensionNode,
]


# --- Union of all schedule expression types ---

ScheduleNode = Union[
    AtomicNode, SpecialNode, CompoundNode, SecondOrderNode,
    DRModifierNode, PRModifierNode, RepeatModifierNode,
    LagModifierNode, PctlModifierNode,
    AversiveNode, TrialBasedNode, IdentifierRefNode,
    # Respondent primitives are also permitted at the top-level schedule
    # slot: a respondent-only Program has a respondent primitive as its
    # schedule. The grammar accepts this at Phase 3 parsing.
    PairForwardDelayNode, PairForwardTraceNode, PairSimultaneousNode,
    PairBackwardNode, ExtinctionRespNode, CSOnlyNode, USOnlyNode,
    ContingencyNode, TrulyRandomNode, ExplicitlyUnpairedNode,
    RespondentCompoundNode, RespondentSerialNode, RespondentITINode,
    DifferentialNode, RespondentExtensionNode,
    dict,  # fallback for forward compatibility
]


# --- Program (operant-rooted single-schedule design) ---

class ProgramNode(TypedDict, total=False):
    type: Literal["Program"]
    program_annotations: list[Annotation]
    param_decls: list[ParamDecl]
    bindings: list[Binding]
    schedule: ScheduleNode


# --- Experiment / Paper / PhaseSequence (Experiment layer) ---

CriterionNode = dict[str, Any]  # Stability | FixedSessions | PerformanceCriterion | CumulativeReinforcements | ExperimenterJudgment


class PhaseNode(TypedDict, total=False):
    type: Literal["Phase"]
    label: str
    schedule: ScheduleNode | None
    phase_annotations: list[Annotation]
    phase_param_decls: list[ParamDecl]
    criterion: CriterionNode


class PhaseSequenceNode(TypedDict, total=False):
    type: Literal["PhaseSequence"]
    shared_annotations: list[Annotation]
    shared_param_decls: list[ParamDecl]
    phases: list[PhaseNode]


class ExperimentNode(TypedDict, total=False):
    type: Literal["Experiment"]
    label: str
    body: Union[ProgramNode, PhaseSequenceNode]


class PaperNode(TypedDict, total=False):
    type: Literal["Paper"]
    experiments: list[ExperimentNode]


# --- Top-level root alias ---

# A top-level AST may be a Program (most common), an Experiment, a Paper,
# or a PhaseSequence. Compilers accept any of these.
RootNode = Union[ProgramNode, ExperimentNode, PaperNode, PhaseSequenceNode, dict]
