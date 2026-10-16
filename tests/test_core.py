import pytest
import json
import os
import shutil
from schemas import FullResponse, RecommendationResult
from code_utils import generate_word_docs
from llm_service import LLMService, DEMO_RESPONSE, DEMO_MODERNIZATION, DEMO_RECOMMENDATION
import version_manager
import io
import zipfile
from datetime import datetime

# Setup/Teardown for version manager tests
def setup_module(module):
    os.makedirs(version_manager.METADATA_DIR, exist_ok=True)
    os.makedirs(version_manager.REPORTS_DIR, exist_ok=True)
    # clean out specific test files if they exist
    for f in os.listdir(version_manager.METADATA_DIR):
        if f.startswith("CMA-"):
            os.remove(os.path.join(version_manager.METADATA_DIR, f))

def test_schema_validation():
    response = FullResponse(**DEMO_RESPONSE)
    assert response.analysis.summary != ""
    assert len(response.analysis.business_rules) > 0
    assert response.modernization is None

def test_version_increments():
    # 1. Initial generation
    source_code = "print('hello')"
    target_lang = "None"
    analysis_json = '{"some": "analysis"}'
    rec_json = ""

    meta1, is_new1 = version_manager.create_or_update_version(None, source_code, target_lang, analysis_json, rec_json)
    doc_id = meta1["doc_id"]
    assert is_new1 is True
    assert meta1["current_version"] == "1.0"
    assert meta1["status"] == "Generated"
    assert "CMA-" in doc_id

    # 2. No changes -> No version bump
    meta2, is_new2 = version_manager.create_or_update_version(doc_id, source_code, target_lang, analysis_json, rec_json)
    assert is_new2 is False
    assert meta2["current_version"] == "1.0"

    # 3. Minor change (Analysis changed) -> Minor bump
    analysis_json_mod = '{"some": "different analysis"}'
    meta3, is_new3 = version_manager.create_or_update_version(doc_id, source_code, target_lang, analysis_json_mod, rec_json)
    assert is_new3 is True
    assert meta3["current_version"] == "1.1"

    # 4. Major change (Source Code changed) -> Major bump
    source_code_mod = "print('world')"
    meta4, is_new4 = version_manager.create_or_update_version(doc_id, source_code_mod, target_lang, analysis_json_mod, rec_json)
    assert is_new4 is True
    assert meta4["current_version"] == "2.0"

    # 5. Major change (Target Lang changed) -> Major bump
    target_lang_mod = "Java 17"
    meta5, is_new5 = version_manager.create_or_update_version(doc_id, source_code_mod, target_lang_mod, analysis_json_mod, rec_json)
    assert is_new5 is True
    assert meta5["current_version"] == "3.0"


def test_word_generation_with_metadata():
    resp_with_mod = DEMO_RESPONSE.copy()
    resp_with_mod["modernization"] = DEMO_MODERNIZATION
    response = FullResponse(**resp_with_mod)

    metadata = {
        "doc_id": "CMA-TEST-001",
        "current_version": "2.1",
        "status": "Revised",
        "revisions": [
             {"version": "2.1", "timestamp": "2023-10-27T10:00:00", "generated_by": "Test", "review_status": "Revised"}
        ]
    }

    docx_stream = generate_word_docs(response, None, metadata, "COBOL")
    assert zipfile.is_zipfile(docx_stream)

def test_llm_service_demo_mode():
    service = LLMService()
    result, raw_json = service.process_code(
        source_code="Some COBOL code",
        source_lang="COBOL",
        target_lang="Java 17",
        mode="Cross-language conversion",
        provider="Demo Mode",
        do_modernize=True
    )
    assert result.modernization.target_language == "Java 17"

    rec = service.recommend_language("code", "VB6", "", provider="Demo Mode")
    assert rec.recommended_language == "C#/.NET"

def test_empty_source_code():
    service = LLMService()
    with pytest.raises(ValueError, match="Source code cannot be empty"):
        service.process_code("", "COBOL", "Java", "conversion")
    with pytest.raises(ValueError, match="Source code cannot be empty"):
        service.recommend_language("", "COBOL", "")
