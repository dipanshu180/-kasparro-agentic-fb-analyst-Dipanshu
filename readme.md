# Kasparro Agentic Facebook Performance Analyst (LLM-Based System)

This project implements a complete LLM-powered, multi-agent system designed to function as an autonomous Facebook Ads Performance Analyst.
The system identifies reasons behind ROAS/CTR fluctuations, validates insights with numeric evidence, and generates new creative recommendations based on existing messaging patterns.

The architecture follows Kasparro’s evaluation requirements, including structured LLM prompts, agent reasoning, logging, reproducibility, and report generation.

---

## Quick Start

### 1. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2. Install required libraries

```bash
pip install -r requirements.txt
```

### 3. Add your OpenAI API key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_api_key_here
```

### 4. Add your dataset

Place the CSV dataset in:

```
data/synthetic_fb_ads_undergarments.csv
```

The dataset should contain at least these columns:

* campaign_name
* adset_name
* date
* spend
* impressions
* clicks
* ctr
* purchases
* revenue
* roas
* creative_type
* creative_message
* audience_type
* platform
* country

A sample file is included in the repository.

### 5. Run the pipeline

```bash
python run.py "Analyze why my ROAS changed this week"
```

This will generate:

* `reports/insights.json`
* `reports/creatives.json`
* `reports/report.md`
* `logs/agent_log.json`

---

## System Architecture

The system follows a modular, multi-agent design. Each agent performs one specific part of the reasoning chain.

```
User Query
   ↓
Planner Agent
   (Breaks query into subtasks)
   ↓
Data Agent
   (Loads and summarizes dataset)
   ↓
Insight Agent (LLM)
   (Produces hypotheses explaining ROAS/CTR changes)
   ↓
Evaluator Agent (LLM)
   (Validates hypotheses using numeric evidence)
   ↓
Creative Agent (LLM)
   (Generates new creative recommendations)
   ↓
Reports (insights.json, creatives.json, report.md)
Logs (agent_log.json)
```

Each agent logs its outputs to ensure transparency.

---

## Agent Descriptions

### PlannerLLMAgent

Uses the user query and a compact dataset overview to generate a clear set of structured subtasks.
This ensures the system has a consistent reasoning path.

---

### DataAgent

Loads, cleans, and summarizes the dataset. Produces:

* basic_summary (averages, counts, min/max dates)
* creative_summary
* audience_summary
* platform_summary
* low_ctr_creatives
* date_summary

This summary is later compressed before being sent to the LLM agents to avoid token overflow.

---

### InsightAgent (LLM)

Uses structured prompts and compacted numeric summaries to produce 3–5 hypotheses explaining possible reasons behind ROAS or CTR changes.
Each hypothesis includes a rationale and the type of numeric evidence needed for validation.

Example:

```json
{
  "id": 1,
  "hypothesis": "ROAS may have dropped due to weak performance of Image creatives.",
  "rationale": "CTR and ROAS for images appear substantially lower.",
  "evidence_required": ["creative_summary"]
}
```

---

### EvaluatorLLMAgent

Validates each hypothesis using:

* creative ROAS comparison
* audience ROAS comparison
* CTR and ROAS thresholds
* compacted numeric data

It performs two passes:

1. First evaluation
2. Reflection pass if confidence is low

Example output:

```json
{
  "id": 1,
  "validated": true,
  "confidence": 0.82,
  "evidence": ["Image creatives have significantly lower ROAS"]
}
```

---

### CreativeAgent (LLM)

Based on low-CTR creatives and high-performing creative types, this agent generates new creative ideas such as:

* Headlines
* Primary texts
* CTAs

These are grounded in the brand’s existing tone and messaging.

Example:

```json
{
  "old_message": "Invisible under tees — seamless men boxers.",
  "creative_type": "Image",
  "variants": [
    {
      "headline": "No Lines. All Comfort.",
      "primary_text": "Stay smooth under every outfit with ultra-soft seamless boxers.",
      "cta": "Try Now"
    }
  ]
}
```

---

## Example Output: insights.json

```json
{
  "hypotheses": [
    {
      "id": 1,
      "hypothesis": "ROAS decline is driven by underperforming Image creatives.",
      "rationale": "Image creatives have noticeably lower CTR and ROAS.",
      "evidence_required": ["creative_summary"]
    }
  ],
  "evaluated": [
    {
      "id": 1,
      "validated": true,
      "confidence": 0.78,
      "evidence": ["Image roas=1.9 vs Video roas=6.3"]
    }
  ]
}
```

---

## Example Output: creatives.json

```json
[
  {
    "old_message": "Invisible under tees — seamless men boxers.",
    "creative_type": "Image",
    "variants": [
      {
        "headline": "No Lines. All Comfort.",
        "primary_text": "Stay smooth under every outfit with ultra-soft seamless boxers.",
        "cta": "Try Now"
      },
      {
        "headline": "Stay Invisible, Feel Incredible",
        "primary_text": "Seam-free comfort designed to disappear under your tees.",
        "cta": "Upgrade Your Basics"
      }
    ]
  }
]
```

---

## Validation Logic

The system includes two validation approaches:
### LLM-Based Validation

Compares:

* ROAS across creative types
* ROAS across audiences
* CTR and ROAS threshold violations
* Directional shifts

It ensures insights are grounded in numeric reality, not hallucinated.

---

## Reproducibility

* All thresholds and dataset paths are in `config/config.yaml`.
* Randomness minimized through consistent summarization.
* Logs and reports are saved for every run.
* A sample dataset is included so that results can be reproduced.

---

## Running Tests

```bash
pytest -q
```

Unit tests check evaluator outputs, JSON structure, and basic behavior.

---

## CLI Example

```bash
python run.py "Analyze why my ROAS changed this week"
```

---

## Conclusion

This project demonstrates a modular, transparent multi-agent system capable of:

* Understanding marketer queries
* Summarizing large datasets
* Generating structured hypotheses
* Validating them with numeric data
* Proposing new ad creative variants
* Producing human-readable reports.