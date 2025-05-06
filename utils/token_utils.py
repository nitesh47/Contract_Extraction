from __future__ import annotations
"""
Counting and splitting text by “tokens” using the `tiktoken` library
if available, falling back to a ~4‑chars-per-token approximation otherwise.
"""

from typing import List
import math, os
from dotenv import load_dotenv

load_dotenv()

TIKTOKEN = os.getenv("TIKTOKEN")
MAX_TOKENS_DEFAULT: int = int(os.getenv("TOKEN_LIMIT"))

def _get_encoder(model: str | None = None):
    """
    Return a tiktoken encoder if available; otherwise fall back to a 4‑chars≈1‑token
    approximation.  We import tiktoken lazily so that the whole package still works
    when the dependency is missing.
    """
    try:
        import tiktoken
        if model:
            return tiktoken.encoding_for_model(model)
        return tiktoken.get_encoding(TIKTOKEN)
    except Exception:
        class _Approx:
            def encode(self, text: str) -> list[int]:
                # ~4 characters per token
                return [0] * math.ceil(len(text) / 4)
        return _Approx()

def token_len(text: str, model: str | None = None) -> int:
    """
        Compute the number of tokens in `text`.

        Uses the real `tiktoken` encoder when available, otherwise falls back
        to a heuristic of 1 token per 4 characters.
        """
    try:
        return len(_get_encoder(model).encode(text))
    except Exception:
        return math.ceil(len(text) / 4)

def split_by_tokens(
    text: str,
    *,
    max_tokens: int = MAX_TOKENS_DEFAULT,
    model: str | None = None,
) -> List[str]:
    """
    Split *text* into chunks whose approximate token length ≤ *max_tokens*.
    Works with or without the real tiktoken encoder.
    """
    enc = _get_encoder(model)
    try:
        toks = enc.encode(text)
        chunk_lists = [toks[i:i+max_tokens] for i in range(0, len(toks), max_tokens)]
        if hasattr(enc, "decode"):
            return [enc.decode(chunk) for chunk in chunk_lists]
        raise AttributeError
    except AttributeError:
        char_step = max_tokens * 4
        return [text[i:i+char_step] for i in range(0, len(text), char_step)]