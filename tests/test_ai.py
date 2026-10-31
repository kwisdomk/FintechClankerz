import json

from app.ai import _validate


def test_model_cannot_replace_observed_evidence():
    supplied = ["Matching references: 75, 102"]
    response = {
        "finding": "Possible duplicate",
        "observed_evidence": ["The model's fabricated evidence"],
        "possible_explanations": ["Could be a duplicate"],
        "recommended_actions": ["Compare source records"],
        "learning": {"concept": "Duplicate review", "explanation": "Check matching references."},
    }

    result = _validate(json.dumps(response), supplied)

    assert result["observed_evidence"] == supplied
