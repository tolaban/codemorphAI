from llm_service import LLMService

def run_tests():
    service = LLMService()

    print("Test 1: Analysis Only (Demo Mode)")
    res, _ = service.process_code("some code", "COBOL", "Python 3", "Cross-language conversion", provider="Demo Mode", do_modernize=False)
    assert res.analysis.defects[0].line_number == "Line 24"
    assert res.modernization is None
    print("PASS Test 1 Passed: line_number present, modernization omitted.")

    print("Test 2: Analysis + Modernization (Demo Mode)")
    res, _ = service.process_code("some code", "COBOL", "Python 3", "Cross-language conversion", provider="Demo Mode", do_modernize=True)
    assert res.modernization is not None
    assert res.modernization.target_language == "Python 3"
    print("PASS Test 2 Passed: modernization included.")

    print("Test 3: Recommendation - Successful Flow (Demo Mode)")
    rec = service.recommend_language("some cobol", "COBOL", "Target is AWS", provider="Demo Mode")
    assert rec.status == "Success"
    assert rec.recommended_language == "Python 3"
    assert rec.candidates[0].total_score == 85
    print("PASS Test 3 Passed: Recommendation returns expected success structure.")

    print("Test 4: Recommendation - Dynamic Language Shift (Demo Mode)")
    rec = service.recommend_language("some vb6", "VB6", "", provider="Demo Mode")
    assert rec.status == "Success"
    assert rec.recommended_language == "C#/.NET"
    print("PASS Test 4 Passed: Recommendation adapts based on input source.")

    print("Test 5: Recommendation - Insufficient Info (Demo Mode)")
    rec = service.recommend_language("some cobol", "COBOL", "trigger_insufficient", provider="Demo Mode")
    assert rec.status == "Insufficient information to recommend"
    print("PASS Test 5 Passed: Handled missing information correctly.")

if __name__ == "__main__":
    run_tests()
