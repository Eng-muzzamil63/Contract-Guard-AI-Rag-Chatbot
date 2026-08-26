from typing import List, Optional
from pydantic import BaseModel, Field

class Obligation(BaseModel):
    title: str
    description: str
    due_date: Optional[str] = None
    owner: Optional[str] = None
    consequence: Optional[str] = None

class Clause(BaseModel):
    title: str
    text: str
    category: str = "general"
    risk_level: str = "medium"

class ContractExtraction(BaseModel):
    contract_title: str
    contract_type: str = "Vendor Agreement"
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    auto_renewal: Optional[bool] = None
    company: str
    vendor: str
    products: List[str] = Field(default_factory=list)
    departments: List[str] = Field(default_factory=list)
    obligations: List[Obligation] = Field(default_factory=list)
    clauses: List[Clause] = Field(default_factory=list)
    summary: str = ""
