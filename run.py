from src.orchestrator.pipeline import run_pipeline
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kasparro Agentic FB Analyst")
    parser.add_argument("query", type=str, help="User query, e.g. 'Analyze ROAS drop'")
    args = parser.parse_args()

    run_pipeline(args.query)
