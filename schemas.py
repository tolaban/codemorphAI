from pydantic import BaseModel, Field
from typing import List, Optional

class Defect(BaseModel):
    issue: str = Field(description="Description of the defect or technical debt")
    severity: str = Field(description="Severity: Low, Medium, High, Critical")
    recommendation: str = Field(description="How to fix or improve this")
    line_number: str = Field(description="Source line number, file reference, or snippet where the issue occurs")

class BusinessRule(BaseModel):
    rule: str = Field(description="A business rule extracted from the code")
    context: str = Field(description="Context or conditions for this rule")

class AnalysisResult(BaseModel):
    summary: str = Field(description="High-level summary of what the code does")
    business_rules: List[BusinessRule] = Field(description="Extracted business rules")
    defects: List[Defect] = Field(description="Identified defects and tech debt")
    dependencies: List[str] = Field(description="External dependencies or system calls identified")

class ModernizationResult(BaseModel):
    original_language: str = Field(description="The detected source language")
    target_language: str = Field(description="The requested target language")
    modernized_code: str = Field(description="The refactored or converted code")
    explanation: str = Field(description="Explanation of the changes made and design decisions")
    warnings: List[str] = Field(description="Warnings about potential behavioral changes or unsupported features")

class CriteriaScores(BaseModel):
    behavior_compatibility: int = Field(description="Score out of 25")
    architecture_dependencies: int = Field(description="Score out of 20")
    maintainability: int = Field(description="Score out of 20")
    performance_scalability: int = Field(description="Score out of 15")
    migration_effort_risk: int = Field(description="Score out of 10")
    client_skills: int = Field(description="Score out of 10")
    missing_information: List[str] = Field(description="List of criteria where information was unknown or guessed")

class TargetCandidate(BaseModel):
    language: str = Field(description="Target language (e.g., Java 17, C#/.NET, Python 3, TypeScript/Node.js, Go, or Same-language refactoring)")
    total_score: int = Field(description="Total weighted score out of 100")
    criteria_scores: CriteriaScores
    rationale: str = Field(description="Transparent justification for this score")

class RecommendationResult(BaseModel):
    status: str = Field(description="'Success'")
    recommended_language: str = Field(description="The single most suitable language")
    candidates: List[TargetCandidate] = Field(description="Top 3 candidates, including same-language baseline")
    business_justification: str = Field(description="Business justification covering maintainability, risk, effort, and benefits")
    migration_challenges: List[str] = Field(description="Known dependencies and migration challenges")
    assumptions_missing_info: List[str] = Field(description="Assumptions made and missing information")
    migration_strategy: str = Field(description="Recommended migration strategy")

class FullResponse(BaseModel):
    analysis: AnalysisResult
    modernization: Optional[ModernizationResult] = None
