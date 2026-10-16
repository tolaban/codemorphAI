import os
import json
import copy
from typing import Dict, Any, Tuple
from dotenv import load_dotenv
from schemas import FullResponse, RecommendationResult
from prompts import SYSTEM_PROMPT, RECOMMENDATION_SYSTEM_PROMPT, build_user_prompt, build_recommendation_prompt

load_dotenv()

# Demo response for testing/when API keys are missing
DEMO_RESPONSE = {
    "analysis": {
        "summary": "This is a demonstration summary of a legacy module calculating interest.",
        "business_rules": [
            {"rule": "Calculate 5% interest", "context": "When account balance > 1000"}
        ],
        "defects": [
            {"issue": "Magic numbers used for interest rates", "severity": "Medium", "recommendation": "Extract to configuration or constants", "line_number": "Line 24"}
        ],
        "dependencies": ["File System", "Database Table ACCOUNT"]
    }
}
DEMO_MODERNIZATION = {
    "original_language": "COBOL",
    "target_language": "Python 3",
    "modernized_code": "def calculate_interest(balance: float) -> float:\n    INTEREST_RATE = 0.05\n    if balance > 1000:\n        return balance * INTEREST_RATE\n    return 0.0",
    "explanation": "Converted procedural COBOL to a Python function. Replaced magic numbers with constants.",
    "warnings": ["Ensure float precision is sufficient for your financial requirements. Consider using decimal.Decimal."]
}

DEMO_RECOMMENDATION = {
  "status": "Success",
  "recommended_language": "Python 3",
  "candidates": [
    {
      "language": "Python 3",
      "total_score": 85,
      "criteria_scores": {
        "behavior_compatibility": 22,
        "architecture_dependencies": 18,
        "maintainability": 18,
        "performance_scalability": 12,
        "migration_effort_risk": 7,
        "client_skills": 8,
        "missing_information": []
      },
      "rationale": "Strong fit for batch processing and data manipulation tasks commonly found in legacy systems, with excellent maintainability."
    },
    {
      "language": "Java 17",
      "total_score": 75,
      "criteria_scores": {
        "behavior_compatibility": 20,
        "architecture_dependencies": 15,
        "maintainability": 15,
        "performance_scalability": 13,
        "migration_effort_risk": 5,
        "client_skills": 7,
        "missing_information": []
      },
      "rationale": "Enterprise standard with robust ecosystem, but higher migration effort from procedural code compared to Python."
    },
    {
      "language": "Same-language refactoring",
      "total_score": 60,
      "criteria_scores": {
        "behavior_compatibility": 25,
        "architecture_dependencies": 20,
        "maintainability": 5,
        "performance_scalability": 5,
        "migration_effort_risk": 5,
        "client_skills": 0,
        "missing_information": ["Current team skills unknown, assumed low for legacy language"]
      },
      "rationale": "Lowest risk for behavioral change, but does not address long-term maintainability or skill shortage issues."
    }
  ],
  "business_justification": "Migrating to Python 3 offers the best balance of addressing immediate technical debt while paving the way for easier integration with modern data pipelines. The migration effort is moderate, but the long-term maintainability gains and larger talent pool justify the investment.",
  "migration_challenges": ["Mapping flat file structures to relational databases or modern document stores.", "Translating complex procedural GOTO logic into structured functions."],
  "assumptions_missing_info": ["Assumed target deployment is a standard cloud Linux environment.", "Exact team Python proficiency is missing; scored based on general market availability."],
  "migration_strategy": "Phased approach: wrap existing legacy modules with APIs, migrate non-critical calculation modules first (like FEE-CALC), then transition core processing."
}

class LLMService:
    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        # Configure clients if keys exist
        self.anthropic_client = None
        if self.anthropic_key:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
            except ImportError:
                pass

        self.openai_client = None
        if self.openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_key)
            except ImportError:
                pass

    def get_provider_status(self) -> Dict[str, bool]:
        return {
            "Anthropic": bool(self.anthropic_client),
            "OpenAI": bool(self.openai_client),
            "Demo Mode": True
        }

    def _clean_json_str(self, raw_json_str: str) -> str:
        raw_json_str = raw_json_str.strip()
        if raw_json_str.startswith("```json"):
            raw_json_str = raw_json_str[7:]
        if raw_json_str.startswith("```"):
            raw_json_str = raw_json_str[3:]
        if raw_json_str.endswith("```"):
            raw_json_str = raw_json_str[:-3]
        return raw_json_str

    def recommend_language(self, source_code: str, source_lang: str, optional_context: str, provider: str = "Demo Mode") -> RecommendationResult:
        if not source_code.strip():
            raise ValueError("Source code cannot be empty.")

        prompt = build_recommendation_prompt(source_code, source_lang, optional_context)
        raw_json_str = ""

        if provider == "Demo Mode":
            # For testing: if specific missing info context is passed, trigger insufficient status
            if optional_context == "trigger_insufficient":
                 demo_resp = copy.deepcopy(DEMO_RECOMMENDATION)
                 demo_resp["status"] = "Insufficient information to recommend"
                 return RecommendationResult(**demo_resp)

            demo_resp = copy.deepcopy(DEMO_RECOMMENDATION)
            # Dynamic adjustment for demo based on source to show it's "working"
            if source_lang == "VB6":
                 demo_resp["recommended_language"] = "C#/.NET"
                 demo_resp["candidates"][0]["language"] = "C#/.NET"
                 demo_resp["candidates"][0]["rationale"] = "Natural migration path for VB6 desktop apps with strong UI framework support."

            return RecommendationResult(**demo_resp)

        elif provider == "Anthropic" and self.anthropic_client:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                system=RECOMMENDATION_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            raw_json_str = response.content[0].text

        elif provider == "OpenAI" and self.openai_client:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": RECOMMENDATION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={ "type": "json_object" }
            )
            raw_json_str = response.choices[0].message.content
        else:
            raise ValueError(f"Provider {provider} selected but not configured properly.")

        parsed_data = json.loads(self._clean_json_str(raw_json_str))
        return RecommendationResult(**parsed_data)

    def process_code(self, source_code: str, source_lang: str, target_lang: str, mode: str, provider: str = "Demo Mode", do_modernize: bool = False) -> Tuple[FullResponse, str]:
        if not source_code.strip():
            raise ValueError("Source code cannot be empty.")

        prompt = build_user_prompt(source_code, source_lang, target_lang, mode, do_modernize)
        raw_json_str = ""

        if provider == "Demo Mode":
            demo_resp = copy.deepcopy(DEMO_RESPONSE)
            if do_modernize:
                mod_copy = copy.deepcopy(DEMO_MODERNIZATION)
                mod_copy["original_language"] = source_lang
                mod_copy["target_language"] = target_lang
                demo_resp["modernization"] = mod_copy
            return FullResponse(**demo_resp), json.dumps(demo_resp, indent=2)

        elif provider == "Anthropic" and self.anthropic_client:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            raw_json_str = response.content[0].text

        elif provider == "OpenAI" and self.openai_client:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={ "type": "json_object" }
            )
            raw_json_str = response.choices[0].message.content

        else:
            raise ValueError(f"Provider {provider} selected but not configured properly.")

        parsed_data = json.loads(self._clean_json_str(raw_json_str))
        return FullResponse(**parsed_data), raw_json_str
