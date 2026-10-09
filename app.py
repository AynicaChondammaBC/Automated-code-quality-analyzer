import streamlit as st
from analyzer import analyze_code, analyze_complexity
import pandas as pd

st.set_page_config(
    page_title="Code Quality Analyzer",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Automated Code Quality Analyzer")

st.write(
    "Analyze Python code automatically, "
    "identify quality issues, and discover ways to improve it."
)

st.divider()

input_method = st.radio(
    "Choose your input method:",
    ["Paste Code", "Upload Python File"],
    horizontal=True
)

code = ""

if input_method == "Paste Code":
    code = st.text_area(
        "Enter your Python code:",
        height=300,
        placeholder="Paste your Python code here..."
    )

else:
    uploaded_file = st.file_uploader(
        "Upload a Python file",
        type=["py"]
    )

    if uploaded_file is not None:
        code = uploaded_file.getvalue().decode(
            "utf-8",
            errors="replace"
        )

if code.strip():
    with st.expander("Preview submitted code"):
        st.code(code, language="python")

if st.button("Analyze Code", type="primary"):
    if not code.strip():
        st.warning("Please enter or upload Python code first.")

    else:
        with st.spinner("Analyzing your code..."):
            result = analyze_code(code)

        st.subheader("📊 Analysis Results")

        # Dashboard metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Code Quality Score",
                f"{result['score']}/10"
            )

        with col2:
            st.metric(
                "Issues Detected",
                len(result["issues"])
            )

        with col3:
            if result["score"] >= 8:
                quality = "Good"
            elif result["score"] >= 5:
                quality = "Average"
            else:
                quality = "Needs Improvement"

            st.metric("Quality Level", quality)

        # Quality score visualization
        st.subheader("📊 Code Quality Dashboard")

        score_percentage = max(
            0,
            min(100, result["score"] * 10)
        )

        st.progress(
            int(score_percentage),
            text=f"Code Quality: {score_percentage:.1f}%"
        )

        # Issue reporting
        st.subheader("📈 Issue Distribution")

        issue_data = {
            "Category": [
                "Errors",
                "Warnings",
                "Code Quality Suggestions"
            ],
            "Count": [
                len(result["errors"]),
                len(result["warnings"]),
                len(result["conventions"])
            ]
        }

        df = pd.DataFrame(issue_data)

        st.bar_chart(
            df.set_index("Category")
        )
        st.subheader("🐛 Issues Found")
        
        if result["issues"]:
            for issue in result["issues"]:
                st.warning(issue)
        else:
            st.success(
                "No issues were extracted from the Pylint report."
            )

        # Improvement suggestions
        st.subheader("💡 Improvement Suggestions")

        if result["score"] >= 8:
            st.write(
                "Your code has a good Pylint score. "
                "Continue following Python coding standards."
            )
        elif result["score"] >= 5:
            st.write(
                "Review naming conventions, documentation, "
                "and code structure."
            )
        else:
            st.write(
                "Review the Pylint report and address "
                "the errors, warnings, and coding violations."
            )

        st.subheader("🧠 Code Complexity Analysis")

        complexity_results = analyze_complexity(code)

        if isinstance(complexity_results, dict) and "error" in complexity_results:
            st.error(complexity_results["error"])

        elif complexity_results:
            st.write(
                "Cyclomatic complexity estimates the number "
                "of independent paths through a function."
            )

            for item in complexity_results:
                st.write(
                    f"**{item['name']}** — "
                    f"Complexity: {item['complexity']} "
                    f"(Line {item['line']})"
                )

                if item["complexity"] <= 5:
                    st.success("Relatively simple function")
                elif item["complexity"] <= 10:
                    st.warning("Moderately complex function")
                else:
                    st.error(
                        "Highly complex function. "
                        "Consider simplifying it."
                    )

        else:
            st.info("No functions or classes requiring complexity analysis were found.")

        # Downloadable report
        st.subheader("📥 Download Analysis Report")

        report = f"""
AUTOMATED CODE QUALITY ANALYZER
================================

Code Quality Score: {result['score']}/10
Total Issues Detected: {len(result['issues'])}

ISSUES:
-------
{chr(10).join(result['issues']) if result['issues'] else 'No issues extracted.'}

COMPLETE PYLINT REPORT:
-----------------------
{result['output']}
"""

        st.download_button(
            label="Download Analysis Report",
            data=report,
            file_name="code_quality_report.txt",
            mime="text/plain"
        )

        # Full report
        with st.expander("View Complete Pylint Report"):
            st.text(result["output"])

        