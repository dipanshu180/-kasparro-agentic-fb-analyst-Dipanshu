import pandas as pd
from pathlib import Path


def clean_ads_data(input_path: str, output_path: str):
    df = pd.read_csv(input_path)

    # Strip whitespace from strings
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Parse date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    # Numeric conversion
    numeric_cols = ["spend", "impressions", "clicks", "purchases", "revenue", "ctr", "roas"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Recompute CTR
    if "clicks" in df.columns and "impressions" in df.columns:
        df["ctr"] = df.apply(
            lambda r: (r["clicks"] / r["impressions"]) if r["impressions"] > 0 else 0,
            axis=1,
        )

    # Recompute ROAS
    if "revenue" in df.columns and "spend" in df.columns:
        df["roas"] = df.apply(
            lambda r: (r["revenue"] / r["spend"]) if r["spend"] > 0 else 0,
            axis=1,
        )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    summary = {
        "rows": len(df),
        "date_min": str(df["date"].min()) if "date" in df.columns else None,
        "date_max": str(df["date"].max()) if "date" in df.columns else None,
    }
    return df, summary
