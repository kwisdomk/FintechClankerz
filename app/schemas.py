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
    status: str
    created_at: str
