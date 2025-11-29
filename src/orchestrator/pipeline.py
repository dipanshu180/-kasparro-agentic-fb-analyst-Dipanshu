import json
from pathlib import Path
import yaml

from src.utils.logger import write_log
from src.utils.data_cleaning import clean_ads_data
from src.agents.data_agent import DataAgent
from src.agents.planner import PlannerLLMAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator_agent import EvaluatorLLMAgent
from src.agents.creative_agent import CreativeAgent


REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


def load_config():
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_pipeline(user_query: str):
    config = load_config()
    write_log({"event": "pipeline_start", "query": user_query})

    # 1) Clean dataset
    df, summary = clean_ads_data(config["data_path"], config["clean_data_path"])
    write_log({"event": "data_cleaned", "summary": summary})

    # 2) Data summary
    data_agent = DataAgent(config["clean_data_path"], config)
    data_summary = data_agent.run()

    # Build small overview for Planner
    bs = data_summary["basic_summary"]
    data_overview = {
        "rows": bs["rows"],
        "date_min": bs["date_min"],
        "date_max": bs["date_max"],
        "avg_roas": bs["avg_roas"],
        "avg_ctr": bs["avg_ctr"],
    }

    # 3) Planner
    planner = PlannerLLMAgent(config)
    subtasks = planner.run(user_query, data_overview)

    # 4) Insight
    insight_agent = InsightAgent(data_summary=data_summary, config=config, user_query=user_query)
    hypotheses = insight_agent.run()

    # 5) Evaluator
    evaluator = EvaluatorLLMAgent(config)
    evaluated = evaluator.run(hypotheses, data_summary)

    # 6) Creative
    creative_agent = CreativeAgent(config)
    creative_recos = creative_agent.run(data_summary)

    # 7) Save outputs
    insights_payload = {
        "hypotheses": hypotheses,
        "evaluated": evaluated,
    }
    (REPORTS_DIR / "insights.json").write_text(json.dumps(insights_payload, indent=2), encoding="utf-8")
    (REPORTS_DIR / "creatives.json").write_text(json.dumps(creative_recos, indent=2), encoding="utf-8")

    # report.md
    report_lines = [
        "# Facebook Ads Performance Report",
        "",
        "## User Query",
        "",
        user_query,
        "",
        "## Planner Subtasks",
        "",
        json.dumps(subtasks, indent=2),
        "",
        "## Hypotheses (InsightAgent)",
        "",
        json.dumps(hypotheses, indent=2),
        "",
        "## Evaluated Hypotheses (EvaluatorAgent)",
        "",
        json.dumps(evaluated, indent=2),
        "",
        "## Creative Recommendations (CreativeAgent)",
        "",
        json.dumps(creative_recos, indent=2),
    ]
    (REPORTS_DIR / "report.md").write_text("\n".join(report_lines), encoding="utf-8")

    write_log({"event": "pipeline_end"})
    print("✅ Pipeline complete. Check reports/ and logs/.")

    return insights_payload, creative_recos
