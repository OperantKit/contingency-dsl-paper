"""Output data model for compiled Method sections."""

from __future__ import annotations

from dataclasses import dataclass, field

from .references import Reference, ReferenceCollector
from .style import JEAB, Style


@dataclass(frozen=True)
class MethodSection:
    """Complete Method section of an academic paper.

    Each field contains a prose paragraph suitable for direct insertion
    into a manuscript. Fields may be empty strings when the corresponding
    annotations are absent from the source DSL program.

    The ``references`` list contains all citations collected during
    compilation (auto-collected + user-added), sorted alphabetically.
    """

    subjects: str = ""
    apparatus: str = ""
    procedure: str = ""
    references: tuple[Reference, ...] = ()
    style: Style = field(default_factory=lambda: JEAB)

    def to_text(self, heading_level: int = 2) -> str:
        """Render as a complete Method section with headings.

        Args:
            heading_level: Markdown heading depth for "Method" (default: ##).

        Returns:
            Formatted Method section with subsection headings and references.
        """
        s = self.style
        prefix = "#" * heading_level
        sub = "#" * (heading_level + 1)
        parts: list[str] = [f"{prefix} {s.heading_method}"]
        if self.subjects:
            parts.append(f"\n{sub} {s.heading_subjects}\n\n{self.subjects}")
        if self.apparatus:
            parts.append(f"\n{sub} {s.heading_apparatus}\n\n{self.apparatus}")
        if self.procedure:
            parts.append(f"\n{sub} {s.heading_procedure}\n\n{self.procedure}")
        if self.references:
            ref_lines = "\n".join(
                r.format(s.citation_format) for r in self.references
            )
            parts.append(f"\n{sub} {s.heading_references}\n\n{ref_lines}")
        return "\n".join(parts) + "\n"
