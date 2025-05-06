from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Type

from parsers.pdf_loader import load_pdf_text
from models.llm_client import LLMClient, ChatMessage
from schemas.generic import GenericContractSchema
from prompts.meta_extraction_prompt import PROMPT
from schemas.employment import EmploymentSchema
from schemas.nda import NDASchema
from schemas.service_agreement import MSASchema
from utils.token_utils import MAX_TOKENS_DEFAULT, split_by_tokens, token_len
from utils.merge_utils import merge_json_objects
from utils.json_fix import fix_and_load

log = logging.getLogger(__name__)

SCHEMA_MAP: Dict[str, Type[GenericContractSchema]] = {
    EmploymentSchema().contract_type.lower(): EmploymentSchema,
    NDASchema().contract_type.lower(): NDASchema,
    MSASchema().contract_type.lower(): MSASchema,
}


def _extract_json(blob: str) -> str | None:
    """
    Extract the *largest* JSON object embedded in `blob`.

    Using the first "{" and the last "}" is a robust way to keep the whole
    object even when the model spills log‑probs or other text before / after.
    """
    start = blob.find("{")
    end = blob.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return blob[start : end + 1]

def _schema_menu_json() -> str:
    menu = {}
    for name, schema_cls in SCHEMA_MAP.items():
        menu[name] = schema_cls.schema()
    menu["generic"] = GenericContractSchema.schema()
    return json.dumps(menu, indent=2)


async def _extract_single(
    pdf: Path, text: str, client: LLMClient
) -> GenericContractSchema:
    """
    Call the LLM once for a text *chunk* and return a parsed schema instance.

    Includes automatic JSON‑repair fallback.
    """
    prompt = PROMPT.format(schema_menu=_schema_menu_json(), contract_text=text)
    messages = [ChatMessage(role="system", content=prompt)]

    start_ts = time.perf_counter()
    raw = await client.chat_completion(messages)
    latency = time.perf_counter() - start_ts

    json_blob = _extract_json(raw) or raw
    data = fix_and_load(json_blob)
    if data is None:
        log.error(
            "Unrecoverable JSON for %s (first 120 chars): %s",
            pdf.name,
            json_blob[:120],
        )
        return GenericContractSchema(contract_type="unknown", parties=[])

    schema_cls: Type[GenericContractSchema] = SCHEMA_MAP.get(
        data.get("contract_type", "").lower(), GenericContractSchema
    )
    extraction = schema_cls(**data)
    log.info("Extracted chunk for %s in %.1fs", pdf.name, latency)
    return extraction


async def extract_metadata(
    pdf: Path,
    client: LLMClient,
    *,
    save: bool = True,
    output_dir: Optional[Path] = None,
    max_tokens: int = MAX_TOKENS_DEFAULT,
) -> GenericContractSchema:
    """
    High‑level orchestration for a *single PDF*.

    1. Load & (if necessary) chunk the PDF text.
    2. Run `_extract_single` on each chunk (concurrently limited by caller).
    3. Merge the partial JSONs → deduplicate lists.
    4. Persist result to disk (optional).
    """
    text = load_pdf_text(pdf)
    model_name = client.model

    if token_len(text, model_name) <= max_tokens:
        final_extraction = await _extract_single(pdf, text, client)
    else:
        chunks = split_by_tokens(text, max_tokens=max_tokens, model=model_name)
        extractions: List[GenericContractSchema] = []
        for idx, chunk in enumerate(chunks):
            log.info("Processing chunk %d/%d for %s", idx + 1, len(chunks), pdf.name)
            ext = await _extract_single(pdf, chunk, client)
            extractions.append(ext)

        merged_json = merge_json_objects(
            [e.model_dump(mode="json", exclude_none=True) for e in extractions]
        )
        schema_cls: Type[GenericContractSchema] = SCHEMA_MAP.get(
            merged_json.get("contract_type", "").lower(), GenericContractSchema
        )
        final_extraction = schema_cls(**merged_json)

    if save:
        import hashlib

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            short_hash = hashlib.md5(str(pdf).encode()).hexdigest()[:6]
            json_name = f"{pdf.stem}_{short_hash}.json"
            out_path = output_dir / json_name
        else:
            out_path = pdf.with_suffix(".json")

        out_path.write_text(
            final_extraction.model_dump_json(indent=2, exclude_none=True),
            encoding="utf-8",
        )
        log.info("Wrote %s", out_path)

    return final_extraction