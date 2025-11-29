import pandas as pd
from pathlib import Path
from src.utils.logger import write_log


class DataAgent:
    """
    Rule-based data summarizer.
    """

    def __init__(self, clean_data_path: str, config: dict):
        self.path = Path(clean_data_path)
        self.config = config
        self.df = None

    def load(self):
        self.df = pd.read_csv(self.path, parse_dates=["date"])
        self.df = self.df.sort_values("date")
        write_log({"event": "data_loaded", "rows": len(self.df)})

    def basic_summary(self):
        df = self.df
        return {
            "rows": int(len(df)),
            "spend_total": float(df["spend"].sum()),
            "revenue_total": float(df["revenue"].sum()),
            "avg_ctr": float(df["ctr"].mean()),
            "avg_roas": float(df["roas"].mean()),
            "date_min": str(df["date"].min()),
            "date_max": str(df["date"].max()),
        }

    def date_summary(self):
        grouped = (
            self.df.groupby("date")[["spend", "revenue", "ctr", "roas"]]
            .mean()
            .round(4)
            .reset_index()
        )
        return grouped.to_dict(orient="records")

    def creative_summary(self):
        if "creative_type" not in self.df.columns:
            return []
        grouped = (
            self.df.groupby("creative_type")[["ctr", "roas", "spend"]]
            .mean()
            .round(4)
            .reset_index()
        )
        return grouped.to_dict(orient="records")

    def audience_summary(self):
        if "audience_type" not in self.df.columns:
            return []
        grouped = (
            self.df.groupby("audience_type")[["ctr", "roas", "spend"]]
            .mean()
            .round(4)
            .reset_index()
        )
        return grouped.to_dict(orient="records")

    def platform_summary(self):
        if "platform" not in self.df.columns:
            return []
        grouped = (
            self.df.groupby("platform")[["ctr", "roas", "spend"]]
            .mean()
            .round(4)
            .reset_index()
        )
        return grouped.to_dict(orient="records")

    def low_ctr_creatives(self):
        threshold = self.config.get("low_ctr_threshold", 0.015)
        df = self.df.copy()
        low = df[df["ctr"] < threshold]
        cols = ["date", "creative_type", "ctr", "creative_message"]
        existing = [c for c in cols if c in low.columns]
        return low[existing].to_dict(orient="records")

    def run(self):
        self.load()
        summary = {
            "basic_summary": self.basic_summary(),
            "date_summary": self.date_summary(),
            "creative_summary": self.creative_summary(),
            "audience_summary": self.audience_summary(),
            "platform_summary": self.platform_summary(),
            "low_ctr_creatives": self.low_ctr_creatives(),
        }
        write_log({"event": "data_agent_summary_created"})
        return summary
