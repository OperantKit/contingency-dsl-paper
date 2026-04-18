"""contingency-dsl2procedure: Compile contingency-dsl AST to academic paper Method sections.

Zero external dependencies. Input is a plain dict conforming to
contingency-dsl/ast-schema.json. Supports multiple journal styles
(JEAB, J-ABA) and automatic reference collection.
"""

try:
    from ._version import __version__, __version_tuple__  # type: ignore[attr-defined]
except ImportError:  # source checkout without build-time hatch-vcs hook
    __version__ = "0.0.0+unknown"
    __version_tuple__ = (0, 0, 0, "unknown")

from .compiler import compile_method, compile_paper
from .model import MethodSection
from .references import (
    Reference,
    ReferenceCollector,
    register_citation_format,
    unregister_citation_format,
)
from .style import (
    JABA,
    JEAB,
    Style,
    get_style,
    register_style,
    unregister_style,
)
from .vocabulary import format_atomic_abbrev, format_atomic_full, format_combinator

__all__ = [
    # Version
    "__version__",
    # Compiler
    "compile_method",
    "compile_paper",
    # Model
    "MethodSection",
    # Style
    "Style",
    "JEAB",
    "JABA",
    "get_style",
    "register_style",
    "unregister_style",
    # References
    "Reference",
    "ReferenceCollector",
    "register_citation_format",
    "unregister_citation_format",
    # Vocabulary
    "format_atomic_abbrev",
    "format_atomic_full",
    "format_combinator",
]
