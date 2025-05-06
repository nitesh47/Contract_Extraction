from __future__ import annotations
"""Lightweight wrapper convert invalid JSON into valid JSON."""

import json, re, logging
log = logging.getLogger(__name__)

_JSON_FENCE_RE = re.compile(r"```[a-zA-Z0-9_]*|```")

def _strip_markdown_fence(text:str)->str:
    return _JSON_FENCE_RE.sub("", text).strip()

def _remove_trailing_commas(s:str)->str:
    # commas before } or ]
    return re.sub(r",\s*([}\]])", r"\\1", s)

def _add_missing_commas(s:str)->str:
    # naive: "value" "next_key" -> "value", "next_key"
    return re.sub(r'("\s*)("[a-zA-Z0-9_]+"\s*:)', r'", \2', s)

CLEAN_STEPS = (_strip_markdown_fence, _remove_trailing_commas, _add_missing_commas)

def fix_and_load(blob:str)->dict|None:
    """Try json.loads; if it fails run heuristics and retry."""
    try:
        return json.loads(blob)
    except Exception as e:
        cleaned = blob
        for fn in CLEAN_STEPS:
            cleaned = fn(cleaned)
        try:
            return json.loads(cleaned)
        except Exception as e2:
            log.debug("JSON repair failed: %s", e2)
            return None
