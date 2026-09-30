
import streamlit as st
from code_explainer import explain_code, handle_user_query


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Code Explainer Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# SESSION STATE
# ==========================================

if "output_explanation" not in st.session_state:
    st.session_state.output_explanation = ""

if "followup_response" not in st.session_state:
    st.session_state.followup_response = ""

if "current_code" not in st.session_state:
    st.session_state.current_code = ""


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.main-title {
    font-size: 36px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: gray;
    font-size: 16px;
    margin-bottom: 25px;
}

div.stButton > button {
    width: 100%;
    border-radius: 10px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="main-title">🤖 AI Code Explainer Pro</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Understand code with AI-powered '
    'line-by-line explanations and step-by-step dry runs.</div>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.header("🤖 AI Assistant")

    st.caption("Your Personal Programming Tutor")

    st.divider()

    st.subheader("🌐 Explanation Language")

    output_language = st.selectbox(
        "Choose your preferred language:",
        [
            "English",
            "Hindi",
            "Telugu",
            "Tamil",
            "Malayalam",
            "Kannada",
            "Bengali",
            "Marathi",
            "Urdu",
            "Others"
        ],
        index=0
    )

    st.divider()

    st.subheader("💬 Ask Follow-up Questions")

    user_query = st.text_area(
        "Ask anything about your code:",
        placeholder=(
            "Example:\n"
            "Explain Kadane's Algorithm.\n"
            "Why do we reset sum to zero?\n"
            "Explain the dry run in Hinglish."
        ),
        height=150,
        key="follow_up_query"
    )

    followup_button = st.button(
        "🚀 Ask AI",
        key="ask_ai_button"
    )

    if followup_button:

        if not st.session_state.current_code:
            st.warning("Please enter or upload code first.")

        elif not user_query.strip():
            st.warning("Please enter your question.")

        else:

            with st.spinner("🤖 AI is thinking..."):

                response = handle_user_query(
                    st.session_state.current_code,
                    user_query,
                    output_language
                )

                st.session_state.followup_response = response

    if st.session_state.followup_response:

        st.divider()

        st.subheader("💡 AI Response")

        st.markdown(
            st.session_state.followup_response,
            unsafe_allow_html=False
        )

    st.divider()

    st.caption("Powered by Google Gemini AI")


# ==========================================
# MAIN LAYOUT
# ==========================================

col1, col2 = st.columns(
    [1, 1],
    gap="large"
)


# ==========================================
# LEFT SIDE: CODE INPUT
# ==========================================

with col1:

    st.subheader("🧾 Input Your Code")

    code_language = st.selectbox(
        "Select Programming Language:",
        [
            "Python",
            "C++",
            "Java",
            "JavaScript",
            "C#",
            "Ruby",
            "Go",
            "PHP",
            "Swift",
            "TypeScript",
            "Other"
        ]
    )

    tab1, tab2 = st.tabs(
        ["📝 Paste Code", "📁 Upload File"]
    )

    code_input = ""

    with tab1:

        code_input = st.text_area(
            "Code Editor",
            placeholder="""Paste your code here...

Example:

#include <iostream>
using namespace std;

int main() {
    cout << "Hello World";
    return 0;
}""",
            height=350,
            key="code_editor",
            label_visibility="collapsed"
        )

    with tab2:

        uploaded_file = st.file_uploader(
            "Upload your source code",
            type=[
                "py",
                "cpp",
                "cc",
                "c",
                "h",
                "hpp",
                "java",
                "js",
                "ts",
                "cs",
                "txt",
                "rb",
                "go",
                "php",
                "swift"
            ]
        )

        if uploaded_file is not None:

            try:

                file_content = uploaded_file.getvalue().decode(
                    "utf-8"
                )

                code_input = file_content

                st.success(
                    f"✅ File loaded: {uploaded_file.name}"
                )

                with st.expander("Preview Uploaded Code"):

                    st.code(
                        file_content,
                        language="cpp" if code_language == "C++"
                        else code_language.lower()
                    )

            except UnicodeDecodeError:

                st.error(
                    "Unable to read this file. "
                    "Please upload a UTF-8 text file."
                )

    # Store current code for follow-up questions
    if code_input and code_input.strip():

        st.session_state.current_code = code_input

    st.divider()

    st.subheader("⚙️ Explanation Settings")

    detail_level = st.select_slider(
        "Select explanation depth:",
        options=[
            "Brief",
            "Moderate",
            "Detailed",
            "Comprehensive"
        ],
        value="Detailed"
    )

    st.caption(
        "Comprehensive mode provides deeper explanations "
        "and algorithm dry runs."
    )

    explain_button = st.button(
        "✨ Explain My Code",
        type="primary",
        use_container_width=True
    )


# ==========================================
# RIGHT SIDE: AI OUTPUT
# ==========================================

with col2:

    st.subheader("📘 AI Code Explanation")

    if explain_button:

        if not code_input or not code_input.strip():

            st.warning(
                "⚠️ Please paste or upload code first."
            )

        else:

            st.session_state.current_code = code_input

            with st.spinner(
                "🤖 Gemini AI is analyzing your code..."
            ):

                explanation = explain_code(
                    code=code_input,
                    code_language=code_language,
                    level_of_detail=detail_level,
                    output_language=output_language
                )

                st.session_state.output_explanation = explanation

                # Clear old follow-up response
                st.session_state.followup_response = ""

    # Display saved explanation after every rerun
    if st.session_state.output_explanation:

        st.success("✅ Explanation Ready!")

        with st.container(height=600, border=True):

            st.markdown(
                st.session_state.output_explanation,
                unsafe_allow_html=False
            )

        st.download_button(
            label="⬇️ Download Explanation",
            data=st.session_state.output_explanation,
            file_name="code_explanation.md",
            mime="text/markdown",
            use_container_width=True
        )

    else:

        st.info(
            "💡 Your detailed code explanation will appear here."
        )

        st.markdown("""
        ### What you will get:

        - 📖 Code Overview
        - 🔍 Line-by-Line Explanation
        - 🧠 Important Concepts
        - 🔄 Step-by-Step Dry Run
        - 📊 Variable Tracking
        - 🎯 Final Output
        - ⏱️ Time Complexity
        - 💾 Space Complexity
        """)


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown(
    "<div style='text-align:center;color:gray;'>"
    "Built with using Python, Streamlit, LangChain "
    "and Google Gemini"
    "</div>",
    unsafe_allow_html=True
)