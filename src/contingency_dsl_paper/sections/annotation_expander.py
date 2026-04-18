"""Expand bundled annotations into their unbundled equivalents.

Some DSL fixtures use bundled annotation shapes where a single annotation
carries a ``kwargs`` (or ``params``) dict with multiple sub-keywords, e.g.:

    {"keyword": "subjects", "kwargs": {"species": "pigeon", "n": 4}}
    {"keyword": "apparatus", "kwargs": {"chamber": "chamber_A"}}

Section generators downstream expect one annotation per sub-keyword:

    {"keyword": "species", "positional": "pigeon"}
    {"keyword": "n", "positional": 4}
    {"keyword": "chamber", "positional": "chamber_A"}

This module performs that expansion on a list of annotations without
modifying the originals. Unknown bundled keys pass through unchanged.
"""

from __future__ import annotations

from typing import Any

# Mapping of bundled keyword → the category's known sub-keywords, each
# labelled by whether the sub-keyword's value is positional-style
# (scalar/list rendered as positional) or params-style (rendered as params).
_BUNDLED_KEYS: dict[str, dict[str, str]] = {
    "subjects": {
        "species": "positional",
        "strain": "positional",
        "n": "positional",
        "deprivation": "params",
        "history": "positional",
    },
    "apparatus": {
        "chamber": "positional",
        "operandum": "positional",
        "interface": "positional",
        "hardware": "positional",
    },
}


def expand_bundled_annotations(anns: list[dict]) -> list[dict]:
    """Return a new list with bundled annotations expanded to sub-annotations.

    Non-bundled annotations pass through unchanged. Sub-keywords whose
    value is a dict are expanded as ``params``; scalar values become
    ``positional``. Unknown sub-keywords inside a bundled container are
    dropped silently rather than surfaced as raw prose.
    """
    out: list[dict] = []
    for ann in anns:
        if not isinstance(ann, dict):
            continue
        kw = ann.get("keyword", "")
        if kw in _BUNDLED_KEYS:
            bundle = ann.get("kwargs") or ann.get("params") or {}
            for sub_kw, sub_val in bundle.items():
                if sub_kw not in _BUNDLED_KEYS[kw]:
                    continue
                out.append(_make_sub_annotation(sub_kw, sub_val))
            continue
        out.append(ann)
    return out


def _make_sub_annotation(keyword: str, value: Any) -> dict:
    """Build one unbundled annotation from a bundle entry."""
    if isinstance(value, dict):
        return {
            "type": "Annotation",
            "keyword": keyword,
            "params": value,
        }
    return {
        "type": "Annotation",
        "keyword": keyword,
        "positional": value,
    }
