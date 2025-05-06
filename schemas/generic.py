from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Party(BaseModel):
    role: str
    name: str

class Clause(BaseModel):
    name: str
    present: bool
    text: Optional[str] = None

class GenericContractSchema(BaseModel):
    """Fallback schema able to hold any contract."""
    contract_type: str
    parties: List[Party] = Field(default_factory=list)
    effective_date: Optional[str] = None
    termination_date: Optional[str] = None
    governing_law: Optional[str] = None
    renewal_terms: Optional[str] = None
    clauses: List[Clause] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
