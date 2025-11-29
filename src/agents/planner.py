from pathlib import Path
from src.utils.llm import call_llm_json
from src.utils.logger import write_log


class PlannerLLMAgent:
    def __init__(self, config: dict):
        self.model = config.get("llm_model", "gpt-4o-mini")
        self.prompt_path = Path("prompts/planner_prompt.md")

    def run(self, user_query: str, data_overview: dict):
        if self.prompt_path.exists():
            system_prompt = self.prompt_path.read_text(encoding="utf-8")
        else:
            system_prompt = (
                "You are a planner agent. Given a query and a data overview, "
                "produce a JSON object with a 'subtasks' list."
            )

        user_payload = {
            "user_query": user_query,
            "data_overview": data_overview,
        }

        result = call_llm_json(system_prompt, str(user_payload), model=self.model)

        subtasks = []
        if isinstance(result, dict) and "subtasks" in result:
            subtasks = result["subtasks"]
        elif isinstance(result, list):
            subtasks = result
        else:
            subtasks = [
                "clean_dataset",
                "summarize_data",
                "generate_insights",
                "validate_insights",
                "generate_creatives",
                "build_report",
            ]

        write_log({"event": "planner_completed", "subtasks": subtasks})
        return subtasks
