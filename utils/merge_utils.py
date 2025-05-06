from __future__ import annotations
from typing import List, Dict, Any
import json

def _dedup_list(lst: List[Any]) -> List[Any]:
    """
        Remove duplicate items from a list, preserving order.
        """

    seen = set()
    out = []
    for item in lst:
        key = json.dumps(item, sort_keys=True, default=str)
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out

def _dedup_parties(parties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
        Remove duplicate party entries by name (case‑insensitive), preserving order.
        Only the first occurrence of each non-empty, unique `name` is kept.
        """

    seen = set()
    out = []
    for party in parties:
        key = party.get("name", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(party)
    return out

def _dedup_clauses(clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
        Remove duplicate clause entries by (name, presence) tuple, preserving order.

        Each clause is considered unique by its "name" (case-insensitive) and
        boolean "present" flag. Only the first occurrence of each
        (name, present) combination is kept.
        """
    seen = set()
    out = []
    for clause in clauses:
        key = (clause.get("name", "").strip().lower(), bool(clause.get("present")))
        if key not in seen:
            seen.add(key)
            out.append(clause)
    return out

def _postprocess_contract(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove duplicates inside a single contract JSON."""
    if not isinstance(data, dict):
        return data
    if "parties" in data and isinstance(data["parties"], list):
        data["parties"] = _dedup_parties(data["parties"])
    if "clauses" in data and isinstance(data["clauses"], list):
        data["clauses"] = _dedup_clauses(data["clauses"])
    return data


def merge_json_objects(objs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
       Merge a list of JSON‑like dicts into a single consolidated dict.

       For each key across the objects:
       - Skip any “empty” values (None, empty list, empty dict, empty string, zero).
       - On first non‑empty value, set it in the result.
       - If both existing and new values are non‑empty:
         - If they’re both lists, concatenate and dedupe via `_dedup_list`.
         - If they’re both dicts, update with only non‑empty entries from the new dict.

       Finally, run `_postprocess_contract` to dedupe any "parties" or "clauses" sub‑lists.
       """
    if not objs:
        return {}
    result: Dict[str, Any] = {}
    for obj in objs:
        for k, v in obj.items():
            if v in (None, [], {}, "", 0):
                continue
            if k not in result or result[k] in (None, [], {}, "", 0):
                result[k] = v
            else:
                if isinstance(v, list) and isinstance(result[k], list):
                    result[k] = _dedup_list(result[k] + v)
                elif isinstance(v, dict) and isinstance(result[k], dict):
                    merged = result[k]
                    merged.update({kk: vv for kk, vv in v.items() if vv not in (None, [], {}, "", 0)})
                    result[k] = merged
    # Deduplicate inside final structure
    return _postprocess_contract(result)