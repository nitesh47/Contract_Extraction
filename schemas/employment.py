from typing import Optional
from .generic import GenericContractSchema
class EmploymentSchema(GenericContractSchema):
    contract_type:str='employment'
    employee_name: Optional[str]=None
    employer_name: Optional[str]=None
    compensation: Optional[str]=None
    probation_period: Optional[str]=None
