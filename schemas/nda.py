from typing import Optional
from .generic import GenericContractSchema
class NDASchema(GenericContractSchema):
    contract_type:str='nda'
    confidentiality_period: Optional[str]=None
    non_compete: Optional[bool]=None
