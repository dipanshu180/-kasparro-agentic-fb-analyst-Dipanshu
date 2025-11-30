# Testing
from src.agents.evaluator_agent import rule_based_evaluator


def test_rule_based_evaluator_structure():
    config = {
        "low_roas_threshold": 2.0,
        "low_ctr_threshold": 0.015,
    }

    data_summary = {
        "basic_summary": {"avg_roas": 1.8},
        "creative_summary": [
            {"creative_type": "Image", "roas": 1.5, "ctr": 0.01, "spend": 100},
            {"creative_type": "Video", "roas": 4.0, "ctr": 0.02, "spend": 200},
        ],
        "audience_summary": [
            {"audience_type": "Broad", "roas": 1.7, "ctr": 0.017, "spend": 150},
        ],
    }

    hypotheses = [
        {"id": 1, "hypothesis": "Creative underperformance is causing ROAS drop."}
    ]

    result = rule_based_evaluator(hypotheses, data_summary, config)
    assert len(result) == 1
    r = result[0]

    assert "validated" in r
    assert "confidence" in r
    assert 0.0 <= r["confidence"] <= 1.0
    assert isinstance(r["evidence"], list)
