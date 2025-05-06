from typing import Optional
from .generic import GenericContractSchema
class MSASchema(GenericContractSchema):
    contract_type:str='service agreement'
    payment_terms: Optional[str]=None
    indemnification: Optional[bool]=None
    limitation_of_liability: Optional[str]=None
