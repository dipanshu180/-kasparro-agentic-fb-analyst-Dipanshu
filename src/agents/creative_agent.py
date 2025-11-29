from pathlib import Path
from src.utils.llm import call_llm_json
from src.utils.logger import write_log


class CreativeAgent:
    def __init__(self, config: dict):
        self.model = config.get("llm_model", "gpt-4o-mini")
        self.prompt_path = Path("prompts/creative_prompt.md")

    def run(self, data_summary: dict):
        low_ctr = data_summary.get("low_ctr_creatives", [])[:3]
        creative_summary = data_summary.get("creative_summary", [])

        # Top patterns: best by ROAS
        top = sorted(creative_summary, key=lambda c: c.get("roas", 0), reverse=True)[:3]
        top_patterns = [c.get("creative_type") for c in top]

        if self.prompt_path.exists():
            system_prompt = self.prompt_path.read_text(encoding="utf-8")
        else:
            system_prompt = (
                "You are a creative agent. Given low_ctr_creatives and top_creative_patterns, "
                "output improved creative variants as JSON."
            )

        payload = {
            "low_ctr_creatives": low_ctr,
            "top_creative_patterns": top_patterns,
        }

        result = call_llm_json(system_prompt, str(payload), model=self.model)

        recommendations = []
        if isinstance(result, list):
            recommendations = result
        elif isinstance(result, dict) and "recommendations" in result:
            recommendations = result["recommendations"]
        elif isinstance(result, dict):
            recommendations = [result]
        else:
            recommendations = []

        write_log({"event": "creative_llm_completed", "num_recommendations": len(recommendations)})
        return recommendations
