from pathlib import Path
import json
from src.utils.llm import call_llm_json
from src.utils.logger import write_log


class InsightAgent:
    """
    LLM-based Insight Agent.
    """

    def __init__(self, data_summary: dict, config: dict | None = None, user_query: str = "Analyze ROAS performance"):
        self.data_summary = data_summary
        self.config = config or {}
        self.user_query = user_query
        self.model = self.config.get("llm_model", "gpt-4o-mini")
        self.prompt_path = Path("prompts/insight_prompt.md")

    def run(self):
        if self.prompt_path.exists():
            system_prompt = self.prompt_path.read_text(encoding="utf-8")
        else:
            system_prompt = (
                "You are an Insight Agent. Given a user_query and data_summary, "
                "return a JSON list of hypotheses explaining ROAS/CTR patterns."
            )

        compact_summary = {
            "basic_summary": self.data_summary.get("basic_summary", {}),
            "top_creatives": sorted(
            self.data_summary.get("creative_summary", []),
            key=lambda x: x.get("roas", 0),
            reverse=True
            )[:5],
            "low_ctr_creatives_sample": self.data_summary.get("low_ctr_creatives", [])[:5],
        }

        payload = {
            "user_query": self.user_query,
            "data_summary": compact_summary,
        }
        payload_json = json.dumps(payload, default=str)

        result = call_llm_json(system_prompt, payload_json, model=self.model)

        hypotheses = []

        if isinstance(result, list):
            hypotheses = result
        elif isinstance(result, dict) and "hypotheses" in result:
            hypotheses = result["hypotheses"]
        elif isinstance(result, dict) and {"hypothesis", "rationale"} <= result.keys():
            hypotheses = [result]
        else:
            hypotheses = []

        for i, h in enumerate(hypotheses, start=1):
            h.setdefault("id", i)

        write_log({"event": "insight_llm_completed", "num_hypotheses": len(hypotheses)})
        return hypotheses
