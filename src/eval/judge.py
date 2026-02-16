from openai import OpenAI
import os
import json
import logging

logger = logging.getLogger(__name__)

JUDGE_SYSTEM_PROMPT = """You are an expert clinical evaluator. Your specific task is to evaluate the "Groundedness" of a generated clinical summary against a provided set of Facts.

Input Format:
1. FACTS: A list of clinical facts (JSON or Text).
2. SUMMARY: The generated summary to evaluate.

Evaluation Criteria:
- **Groundedness**: Every claim in the summary must be directly supported by a Fact.
- **Citation Accuracy**: Every claim must verify the citation points to the correct source ID.
- **Completeness**: Does the summary capture the most critical issues (e.g. Data Quality Warnings)?

Output Format (JSON ONLY):
{
    "score": <0-10 integer>,
    "reasoning": "<Constructive feedback>",
    "hallucinations": ["<List specific claims that are unsupported>"],
    "missed_critical_findings": ["<List major facts missed>"]
}

Scoring Guide:
- 10: Perfect. All claims supported, citations correct, critical issues found.
- 8-9: Good. Minor precision issues or missing minor details.
- 5-7: Mixed. Some supported claims, but 1-2 minor hallucinations or wrong citations.
- 0-4: Bad. Major hallucinations, invented numbers, or completely missed critical safety warnings.
"""

class LLMJudge:
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def evaluate(self, facts_text: str, summary_text: str) -> dict:
        """
        Runs the evaluation logic.
        """
        user_prompt = f"""
### FACTS
{facts_text}

### SUMMARY
{summary_text}

Rate the summary now. JSON only.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"Judge Evaluation failed: {e}")
            return {"score": 0, "reasoning": f"Evaluation Failed: {e}", "hallucinations": []}
