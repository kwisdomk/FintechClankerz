from typing import Any, Literal
from pydantic import BaseModel, Field


class UploadResult(BaseModel):
    success: bool = True
    message: str
    total_records: int
    successful: int
    rejected: int
    findings_detected: int
    errors: list[str] = Field(default_factory=list)


class ReviewRequest(BaseModel):
    decision: Literal["confirmed", "dismissed", "needs_review"]
    notes: str | None = Field(default=None, max_length=2000)
    reviewer: str | None = Field(default=None, max_length=200)


class Explanation(BaseModel):
    finding_id: int
    model_used: str
    finding: str
    observed_evidence: list[str]
    possible_explanations: list[str]
    recommended_actions: list[str]
    learning: dict[str, str]
    generated_at: str


class Finding(BaseModel):
    id: int
    transaction_id: int
    finding_type: str
    severity: str
    evidence: list[Any]
    evidence_json: str
    status: str
    created_at: str
    date: str
    description: str
    amount: float
    currency: str
    supplier: str | None
    reference: str | None


class Health(BaseModel):
    status: str
    service: str
    database: str


class Transaction(BaseModel):
    id: int
    date: str
    description: str
    amount: float
    currency: str
    supplier: str | None
    reference: str | None
    source_row: int
    created_at: str


class TransactionPage(BaseModel):
    items: list[Transaction]
    total: int
    limit: int
    offset: int


class Summary(BaseModel):
    transaction_count: int
    total_amount: float
    finding_count: int
    open_finding_count: int


class Review(BaseModel):
    id: int
    finding_id: int
    decision: Literal["confirmed", "dismissed", "needs_review"]
    notes: str | None
    reviewer: str | None
    created_at: str
