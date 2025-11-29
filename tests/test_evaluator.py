# from src.agents.evaluator_agent import rule_based_evaluator
# import yaml


# def test_evaluator_basic():
#     """Test rule-based evaluator with sample data."""
#     config = {"low_roas_threshold": 2.0, "low_ctr_threshold": 0.015}

#     data_summary = {
#         "creative_summary": [
#             {"creative_type": "Image", "ctr": 0.01, "roas": 1.5},
#             {"creative_type": "Video", "ctr": 0.03, "roas": 4.2}
#         ],
#         "audience_summary": [
#             {"audience_type": "Broad", "roas": 1.8},
#             {"audience_type": "Lookalike", "roas": 3.1}
#         ],
#         "basic_summary": {"avg_roas": 1.6}
#     }

#     hypotheses = [
#         {
#             "id": 1,
#             "hypothesis": "Creative underperformance is causing ROAS drop",
#             "evidence_required": ["creative_summary"]
#         },
#         {
#             "id": 2,
#             "hypothesis": "Audience fatigue is affecting performance",
#             "evidence_required": ["audience_summary"]
#         }
#     ]

#     result = rule_based_evaluator(hypotheses, data_summary, config)
#     assert len(result) == 2
#     assert result[0]["validated"] in [True, False]
#     assert 0 <= result[0]["confidence"] <= 1.0
#     assert result[1]["id"] == 2


# def test_evaluator_high_roas():
#     """Test evaluator with strong performance data."""
#     config = {"low_roas_threshold": 2.0, "low_ctr_threshold": 0.015}

#     data_summary = {
#         "creative_summary": [
#             {"creative_type": "Video", "ctr": 0.05, "roas": 8.5}
#         ],
#         "audience_summary": [
#             {"audience_type": "Retargeting", "roas": 12.0}
#         ],
#         "basic_summary": {"avg_roas": 9.0}
#     }

#     hypotheses = [
#         {
#             "id": 1,
#             "hypothesis": "ROAS has improved due to strong creative performance",
#             "evidence_required": ["creative_summary", "basic_summary"]
#         }
#     ]

#     result = rule_based_evaluator(hypotheses, data_summary, config)
#     assert len(result) == 1
#     assert 0 <= result[0]["confidence"] <= 1.0  # Confidence should be in valid range
#     assert "creative_type" in str(result[0]["evidence"])  # Evidence should contain creative data





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
