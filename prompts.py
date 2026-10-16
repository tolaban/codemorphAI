SYSTEM_PROMPT = """You are CodeMorph AI, a Senior AI Software Engineer specializing in legacy system modernization.
Your task is to analyze legacy code (like COBOL or VB6), explain its business logic, identify defects with specific line references, and optionally modernize it to a target language.

You MUST respond with a valid JSON object conforming exactly to the requested schema.
Do not include markdown code blocks around the JSON output, just return the raw JSON object.

Important rules:
1. Identify business rules without hallucinating.
2. Flag potential defects, memory leaks, security issues, or technical debt. You MUST provide the line number or code snippet for the defect.
3. If modernizing, follow best practices for the target language.
4. If converting language, ensure idiomatic patterns are used.
5. Always warn the user that generated code must be tested and does not guarantee behavioral equivalence without validation.
"""

RECOMMENDATION_SYSTEM_PROMPT = """You are CodeMorph AI, a Senior AI Solution Architect.
Your task is to automatically analyze a legacy codebase snippet and infer its business domain, application type, architecture, and dependencies.
Based on these observable characteristics (and any optional user context provided), recommend the optimal modernization target language.

You MUST respond with a valid JSON object conforming exactly to the requested schema.
Do not include markdown code blocks around the JSON output, just return the raw JSON object.

Evaluate candidates (Java 17, C#/.NET, Python 3, TypeScript/Node.js, Go) and baseline options (Same-language refactoring).
Use these weighted decision criteria:
- Behavior compatibility: 25%
- Architecture/dependencies: 20%
- Maintainability: 20%
- Performance/scalability: 15%
- Migration effort/risk: 10%
- Client standards/team skills: 10%

Important rules:
1. Do not simply map COBOL to Java or VB6 to C#. Evaluate the actual context inferred from the code.
2. If essential business information (like deployment targets or team skills) cannot be inferred from the code and is not provided in the optional context, explicitly identify it as unknown in 'assumptions_missing_info'. Do not invent missing facts.
3. Scores must be explainable heuristic decision-support values, not probabilities. Never imply a score guarantees migration success.
"""

def build_recommendation_prompt(source_code: str, source_lang: str, optional_context: str) -> str:
    prompt = f"""
Please analyze the following {source_lang} legacy code snippet. Infer its business domain, application type, architecture, and dependencies to recommend a target language.

Source Code:
```
{source_code}
```
"""
    if optional_context.strip():
        prompt += f"\nOptional Additional Context provided by user:\n{optional_context}\n"

    prompt += """
Output exactly as a JSON object matching this schema:
{
  "status": "Success",
  "recommended_language": "string",
  "candidates": [
    {
      "language": "string",
      "total_score": integer,
      "criteria_scores": {
        "behavior_compatibility": integer,
        "architecture_dependencies": integer,
        "maintainability": integer,
        "performance_scalability": integer,
        "migration_effort_risk": integer,
        "client_skills": integer,
        "missing_information": ["string"]
      },
      "rationale": "string"
    }
  ],
  "business_justification": "string",
  "migration_challenges": ["string"],
  "assumptions_missing_info": ["string"],
  "migration_strategy": "string"
}
"""
    return prompt

def build_user_prompt(source_code: str, source_lang: str, target_lang: str, mode: str, do_modernize: bool) -> str:

    prompt = f"""
Please analyze the following {source_lang} code.

Source Code:
```
{source_code}
```
"""
    if do_modernize:
        action = "Refactor" if mode == "Same-language refactoring" else f"Convert to {target_lang}"
        prompt += f"""
Target Language: {target_lang}
Mode: {mode}
Please {action} the code.
"""

    prompt += """
Output exactly as a JSON object matching this schema:
{
  "analysis": {
    "summary": "string",
    "business_rules": [{"rule": "string", "context": "string"}],
    "defects": [{"issue": "string", "severity": "Low|Medium|High|Critical", "recommendation": "string", "line_number": "string"}],
    "dependencies": ["string"]
  }"""
    if do_modernize:
        prompt += f""",
  "modernization": {{
    "original_language": "{source_lang}",
    "target_language": "{target_lang}",
    "modernized_code": "string (the actual code)",
    "explanation": "string",
    "warnings": ["string"]
  }}"""

    prompt += "\n}"
    return prompt
