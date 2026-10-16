# 🦋 CodeMorph AI

CodeMorph AI is a 3-hour hackathon MVP designed to analyze legacy codebases (like COBOL and VB6), explain business logic, flag defects, and modernize the code into target languages like Java, Python, C#, TypeScript, and Go.

## Features
- **Code Modernization:** Refactor legacy code or convert to modern languages.
- **Business Logic Extraction:** AI identifies and documents business rules.
- **Defect Detection:** Highlights potential bugs, technical debt, and assigns severity.
- **Side-by-Side Comparison:** View original vs. modern code with explanations.
- **Exporting Artifacts:** Download converted code, generated markdown documentation, and raw JSON analysis.
- **Demo Mode:** Fully functional testing mode without requiring live LLM API keys.

## Setup Instructions

1. **Install dependencies:**
   Ensure you have Python 3.12+ installed.
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys (Optional for Demo Mode):**
   Create a `.env` file in the root directory:
   ```env
   ANTHROPIC_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ```
   *Note: If no keys are provided, the app will gracefully default to a fully featured Demo Mode.*

3. **Run the Streamlit App:**
   ```bash
   streamlit run app.py
   ```

4. **Run Tests:**
   ```bash
   pytest tests/
   ```

## Tech Stack
- **Frontend:** Streamlit
- **Backend/LLM Routing:** Python 3.12, Anthropic API, OpenAI API
- **Data Validation:** Pydantic
- **Testing:** pytest
