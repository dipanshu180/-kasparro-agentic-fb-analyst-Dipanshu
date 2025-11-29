from pathlib import Path
from src.utils.llm import call_llm_json
from src.utils.logger import write_log
import json


def rule_based_evaluator(hypotheses, data_summary, config):
    """
    Simple deterministic evaluator used in tests (no LLM).
    """
    results = []
    low_roas_threshold = config.get("low_roas_threshold", 2.0)
    low_ctr_threshold = config.get("low_ctr_threshold", 0.015)

    creative_summary = data_summary.get("creative_summary", [])
    audience_summary = data_summary.get("audience_summary", [])
    avg_roas = data_summary.get("basic_summary", {}).get("avg_roas", 0)

    for h in hypotheses:
        confidence = 0.2
        evidence = []

        text = (h.get("hypothesis") or "").lower()

        if "creative" in text and creative_summary:
            worst = min(creative_summary, key=lambda c: c.get("roas", 0))
            evidence.append(
                f"worst creative_type={worst.get('creative_type')} roas={worst.get('roas',0)}"
            )
            if worst.get("roas", 0) < low_roas_threshold:
                confidence += 0.5

        if "audience" in text and audience_summary:
            low = [a for a in audience_summary if a.get("roas", 0) < low_roas_threshold]
            if low:
                evidence.append("low ROAS audiences present")
                confidence += 0.3

        if "roas" in text:
            evidence.append(f"avg_roas={avg_roas}")
            if avg_roas < low_roas_threshold:
                confidence += 0.2

        validated = confidence >= 0.5

        results.append({
            "id": h.get("id"),
            "hypothesis": h.get("hypothesis"),
            "validated": validated,
            "confidence": round(min(confidence, 1.0), 2),
            "evidence": evidence,
        })

    return results



# ================================
#       LLM EVALUATOR AGENT
# ================================

class EvaluatorLLMAgent:
    def __init__(self, config: dict):
        self.model = config.get("llm_model", "gpt-4o-mini")
        self.prompt_path = Path("prompts/evaluator_prompt.md")
        self.config = config

    # ---------------------------------------------------------
    # Compact data before sending to LLM (fix for token overflow)
    # ---------------------------------------------------------
    def _build_compact_summary(self, data_summary: dict):
        return {
            "basic_summary": data_summary.get("basic_summary", {}),
            "creative_summary": data_summary.get("creative_summary", [])[:5],
            "audience_summary": data_summary.get("audience_summary", [])[:5],
            # DO NOT include:
            # - date_summary
            # - low_ctr_creatives
            # - platform summary
            # - full dataset
        }

    # ---------------------------------------------------------
    # First evaluation function
    # ---------------------------------------------------------
    def _evaluate_once(self, hypothesis: str, data_summary: dict):
        if self.prompt_path.exists():
            system_prompt = self.prompt_path.read_text(encoding="utf-8")
        else:
            system_prompt = (
                "You are an evaluator agent. Given a hypothesis and compact numeric data, "
                "return validated, confidence, evidence, needs_reflection."
            )

        thresholds = {
            "low_roas_threshold": self.config.get("low_roas_threshold", 2.0),
            "low_ctr_threshold": self.config.get("low_ctr_threshold", 0.015),
        }

        compact_summary = self._build_compact_summary(data_summary)

        payload = {
            "hypothesis": hypothesis,
            "data_summary": compact_summary,
            "thresholds": thresholds,
        }

        payload_str = json.dumps(payload, default=str)

        result = call_llm_json(system_prompt, payload_str, model=self.model)
        return result

    # ---------------------------------------------------------
    # Main run loop
    # ---------------------------------------------------------
    def run(self, hypotheses, data_summary):
        results = []

        for h in hypotheses:
            hyp_text = h.get("hypothesis", "")
            if not hyp_text:
                continue

            # ========== First pass ==========
            first = self._evaluate_once(hyp_text, data_summary)

            if not isinstance(first, dict):
                first = {
                    "validated": False,
                    "confidence": 0.0,
                    "evidence": [],
                    "needs_reflection": False,
                }

            conf = float(first.get("confidence", 0.0) or 0.0)
            needs_reflection = bool(first.get("needs_reflection", False))

            # ========== Reflection pass ==========
            if conf < 0.6 or needs_reflection:
                reflection_prompt = (
                    "You previously evaluated this hypothesis with low confidence. "
                    "Re-check the compact numeric data and refine your judgement. "
                    "Return the same JSON structure."
                )

                compact_summary = self._build_compact_summary(data_summary)

                payload = {
                    "hypothesis": hyp_text,
                    "data_summary": compact_summary,
                    "previous_evaluation": first,
                }

                payload_str = json.dumps(payload, default=str)

                second = call_llm_json(reflection_prompt, payload_str, model=self.model)

                if isinstance(second, dict) and "confidence" in second:
                    final = second
                else:
                    final = first
            else:
                final = first

            results.append({
                "id": h.get("id"),
                "hypothesis": hyp_text,
                "validated": bool(final.get("validated", False)),
                "confidence": float(final.get("confidence", conf)),
                "evidence": final.get("evidence", []),
            })

        write_log({"event": "evaluator_llm_completed", "num_hypotheses": len(results)})
        return results
