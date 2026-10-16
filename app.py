import streamlit as st
import json
import pandas as pd
import altair as alt
import os
import glob
from llm_service import LLMService
from code_utils import get_sample_cobol, get_sample_vb6, generate_word_docs
from schemas import FullResponse, RecommendationResult
import io
import version_manager

st.set_page_config(page_title="CodeMorph AI", page_icon="🦋", layout="wide")

# Initialize Session State
if 'llm_service' not in st.session_state:
    st.session_state.llm_service = LLMService()
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'recommendation_result' not in st.session_state:
    st.session_state.recommendation_result = None
if 'raw_json' not in st.session_state:
    st.session_state.raw_json = None
if 'source_code' not in st.session_state:
    st.session_state.source_code = ""
if 'current_doc_id' not in st.session_state:
    st.session_state.current_doc_id = None
if 'current_metadata' not in st.session_state:
    st.session_state.current_metadata = None
if 'word_bytes' not in st.session_state:
    st.session_state.word_bytes = None

st.title("🦋 CodeMorph AI")
st.subheader("Legacy Code Analysis & Documentation")

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")

    status = st.session_state.llm_service.get_provider_status()
    available_providers = [p for p, is_available in status.items() if is_available]

    st.write("**LLM Provider:**")
    provider = st.selectbox("Select Provider", options=available_providers, index=0 if "Demo Mode" not in available_providers else available_providers.index("Demo Mode"))

    if provider == "Demo Mode":
        st.info("Demo Mode active. Analysis will return synthetic data for testing. Configure API keys in `.env` for full AI capabilities.")

    st.header("Language Settings")
    source_lang = st.selectbox("Source Language", ["COBOL", "VB6"])

    st.header("Optional: Modernization")
    do_modernize = st.checkbox("Also Generate Modernized Code", value=False)

    mode = "Cross-language conversion"
    target_lang = source_lang

    if do_modernize:
        mode = st.radio("Modernization Mode", ["Cross-language conversion", "Same-language refactoring"])
        if mode == "Cross-language conversion":
            # Dynamic default based on recommendation if it exists
            default_target = "Java 17"
            if st.session_state.recommendation_result and st.session_state.recommendation_result.status == "Success":
                 rec_lang = st.session_state.recommendation_result.recommended_language
                 if rec_lang in ["Java 17", "C#/.NET", "Python 3", "TypeScript/Node.js", "Go"]:
                     default_target = rec_lang

            options = ["Java 17", "C#/.NET", "Python 3", "TypeScript/Node.js", "Go"]
            idx = options.index(default_target) if default_target in options else 0
            target_lang = st.selectbox("Target Language", options, index=idx)
            if st.session_state.recommendation_result and st.session_state.recommendation_result.status == "Success":
                if target_lang != st.session_state.recommendation_result.recommended_language:
                    st.warning("You have manually overridden the AI Recommended language.")

    st.header("Load Examples")
    if st.button("Load Sample COBOL"):
        st.session_state.source_code = get_sample_cobol()
        st.session_state.recommendation_result = None
        st.session_state.current_doc_id = None
        st.session_state.current_metadata = None
        st.rerun()
    if st.button("Load Sample VB6"):
        st.session_state.source_code = get_sample_vb6()
        st.session_state.recommendation_result = None
        st.session_state.current_doc_id = None
        st.session_state.current_metadata = None
        st.rerun()

# Document History Explorer (Top of Main Area)
with st.expander("📚 Document History & Archives"):
    st.write("View previous assessment reports.")
    metadata_files = glob.glob(os.path.join(version_manager.METADATA_DIR, "*.json"))
    if metadata_files:
        doc_options = []
        for f in metadata_files:
             bn = os.path.basename(f).replace('.json', '')
             meta = version_manager.get_metadata(bn)
             if meta:
                 doc_options.append((bn, meta.get("current_version"), meta.get("status")))
        doc_options.sort(reverse=True)

        selected_arch = st.selectbox("Select Past Assessment", [f"{d[0]} (v{d[1]} - {d[2]})" for d in doc_options])
        if selected_arch:
            arch_id = selected_arch.split()[0]
            arch_meta = version_manager.get_metadata(arch_id)
            if arch_meta:
                 v = arch_meta.get('current_version')
                 report_path = os.path.join(version_manager.REPORTS_DIR, f"CodeMorph_Assessment_{arch_id}_v{v}.docx")
                 if os.path.exists(report_path):
                     with open(report_path, "rb") as rp:
                         st.download_button(f"Download Historical Report ({arch_id} v{v})", data=rp, file_name=f"CodeMorph_Assessment_{arch_id}_v{v}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                 else:
                     st.write(f"Report file {report_path} not found on disk.")

                 st.write("**Revision History for this ID:**")
                 st.dataframe(arch_meta.get("revisions", []))
    else:
        st.write("No historical assessments found.")

st.write("### Source Code")

uploaded_file = st.file_uploader("Upload Legacy File (.cbl, .frm, .bas, .cls, .txt)", type=["cbl", "frm", "bas", "cls", "txt"])
if uploaded_file is not None:
    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    st.session_state.source_code = stringio.read()
    st.session_state.recommendation_result = None
    st.session_state.current_doc_id = None
    st.session_state.current_metadata = None

source_code = st.text_area("Or Paste legacy code here:", value=st.session_state.source_code, height=300)

with st.expander("🤖 AI Target Language Recommendation (Optional)", expanded=True):
    st.write("Automatically infer the optimal target language based on observable code characteristics.")
    ctx_optional = st.text_input("Optional Extra Context (Only if code is insufficient, e.g., 'Targeting AWS, team knows Python')")

    if st.button("AI Recommend Target"):
        if not source_code.strip():
            st.error("Please provide source code first.")
        else:
             with st.spinner("Analyzing code architecture and inferring optimal target..."):
                 try:
                     rec_result = st.session_state.llm_service.recommend_language(
                         source_code, source_lang, ctx_optional, provider
                     )
                     st.session_state.recommendation_result = rec_result
                 except Exception as e:
                     st.error(f"Error during recommendation: {str(e)}")

    if st.session_state.recommendation_result:
        rec: RecommendationResult = st.session_state.recommendation_result
        if provider == "Demo Mode":
             st.caption("🏷️ **Demo/Illustrative Data:** Results are synthetic fixtures.")

        if rec.status == "Success":
            st.success(f"### 🏆 Recommended Target: {rec.recommended_language}")

            st.write("*Scores represent multi-dimensional decision support based on inferred traits, not probabilities of migration success.*")

            chart_data = [{"Language": c.language, "Score": c.total_score} for c in rec.candidates]
            df_chart = pd.DataFrame(chart_data)

            bars = alt.Chart(df_chart).mark_bar().encode(
                x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 100]), title='Suitability Score (0-100)'),
                y=alt.Y('Language:N', sort='-x', title=''),
                color=alt.condition(
                    alt.datum.Language == rec.recommended_language,
                    alt.value('#1f77b4'),
                    alt.value('lightgray')
                )
            )
            text = bars.mark_text(align='left', baseline='middle', dx=3).encode(text='Score:Q')
            st.altair_chart((bars + text).properties(height=250), use_container_width=True)

            st.write("#### Justification")
            st.write(rec.business_justification)

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.write("**Migration Challenges & Risks:**")
                for chal in rec.migration_challenges:
                    st.write(f"- {chal}")
            with col_d2:
                st.write("**Assumptions & Missing Info:**")
                for asm in rec.assumptions_missing_info:
                    st.write(f"- {asm}")

            st.info("The AI Recommended language has automatically populated the 'Target Language' selection in the sidebar. You can manually override it there before clicking 'Analyze'.")

        else:
            st.error(f"### ⚠️ {rec.status}")
            st.write("Insufficient context could be inferred from the code alone. Please provide details in the 'Optional Extra Context' field above.")


if st.button("Analyze & Generate Reports", type="primary"):
    if not source_code.strip():
        st.error("Please provide source code to analyze.")
    else:
        with st.spinner(f"Analyzing with {provider}..."):
            try:
                result, raw_json_str = st.session_state.llm_service.process_code(
                    source_code=source_code,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    mode=mode,
                    provider=provider,
                    do_modernize=do_modernize
                )
                st.session_state.analysis_result = result
                st.session_state.raw_json = raw_json_str

                # Trigger Versioning Logic
                rec_json_str = ""
                if st.session_state.recommendation_result:
                    rec_json_str = st.session_state.recommendation_result.model_dump_json()

                metadata, is_new_version = version_manager.create_or_update_version(
                    doc_id=st.session_state.current_doc_id,
                    source_code=source_code,
                    target_lang=target_lang if do_modernize else "None",
                    analysis_json_str=raw_json_str,
                    rec_json_str=rec_json_str
                )
                st.session_state.current_doc_id = metadata["doc_id"]
                st.session_state.current_metadata = metadata

                # Generate Word Doc bytes
                docx_bytes = generate_word_docs(result, st.session_state.recommendation_result, metadata, source_lang)
                st.session_state.word_bytes = docx_bytes

                # Save the new version distinctively to disk if a new version was created
                if is_new_version:
                    v = metadata["current_version"]
                    filepath = os.path.join(version_manager.REPORTS_DIR, f"CodeMorph_Assessment_{metadata['doc_id']}_v{v}.docx")
                    with open(filepath, "wb") as f:
                        f.write(docx_bytes.getvalue())

                if is_new_version:
                     st.success(f"Analysis Complete! Created new report version: {metadata['doc_id']} v{metadata['current_version']}")
                else:
                     st.info(f"Analysis Complete! No changes detected. Loaded existing report: {metadata['doc_id']} v{metadata['current_version']}")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Display Results
if st.session_state.analysis_result and st.session_state.current_metadata:
    res: FullResponse = st.session_state.analysis_result
    meta = st.session_state.current_metadata

    tabs = ["Analysis & Rules", "Export & Docs"]
    if res.modernization:
         tabs.insert(0, "Code Comparison")

    selected_tabs = st.tabs(tabs)
    current_tab_idx = 0

    if res.modernization:
        with selected_tabs[current_tab_idx]:
            st.write("⚠️ *Generated code should be thoroughly tested. Behavior equivalence is not guaranteed.*")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Original ({res.modernization.original_language})**")
                st.code(source_code, language="cobol" if source_lang == "COBOL" else "vb")
            with col2:
                st.write(f"**Modernized ({res.modernization.target_language})**")
                st.code(res.modernization.modernized_code, language=target_lang.split()[0].lower() if target_lang != "C#/.NET" else "csharp")

            st.info(f"**Explanation:** {res.modernization.explanation}")
            if res.modernization.warnings:
                for w in res.modernization.warnings:
                    st.warning(w)
        current_tab_idx += 1

    with selected_tabs[current_tab_idx]:
        st.write("### Executive Summary")
        st.write(res.analysis.summary)

        col_rules, col_defects = st.columns(2)
        with col_rules:
            st.write("### Business Rules")
            for r in res.analysis.business_rules:
                with st.expander(r.rule):
                    st.write(f"**Context:** {r.context}")

            st.write("### Dependencies")
            for dep in res.analysis.dependencies:
                st.write(f"- {dep}")

        with col_defects:
            st.write("### Defects & Refactoring Candidates")
            for d in res.analysis.defects:
                severity_color = "red" if d.severity in ["High", "Critical"] else "orange" if d.severity == "Medium" else "green"
                st.markdown(f"- **:{severity_color}[[{d.severity}]]** {d.issue}")
                st.markdown(f"  - *Line Ref:* `{d.line_number}`")
                st.write(f"  - *Fix:* {d.recommendation}")
    current_tab_idx += 1

    with selected_tabs[current_tab_idx]:
        st.write("### Artifacts & Document Control")
        st.write(f"**Current Document:** {meta['doc_id']} | **Version:** {meta['current_version']} | **Status:** {meta['status']}")

        filename = f"CodeMorph_Assessment_{meta['doc_id']}_v{meta['current_version']}.docx"

        st.download_button(
            label=f"📄 Download Word Report ({filename})",
            data=st.session_state.word_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        if res.modernization:
            st.download_button("Download Modernized Code", data=res.modernization.modernized_code, file_name=f"modernized_code.txt", mime="text/plain")

        st.download_button("Download Raw JSON Analysis", data=st.session_state.raw_json, file_name="analysis.json", mime="application/json")
