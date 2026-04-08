import streamlit as st
import json
import pandas as pd
from .service import service

st.set_page_config(
    page_title="AI Reliability & Risk Auditor",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .risk-card {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ AI Reliability & Risk Auditing System")
st.markdown("### Production-grade auditing engine for AI Safety & Compliance")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 New Audit")
    question = st.text_input("Original Question", placeholder="e.g. What is the capital of Japan?")
    model_output = st.text_area("Model Output", placeholder="e.g. The capital is Seoul.", height=150)
    
    if st.button("Run Audit"):
        if question and model_output:
            with st.spinner("Analyzing for hallucinations and risk..."):
                result = service.audit(question, model_output)
                st.session_state['last_result'] = result
        else:
            st.warning("Please provide both a question and a model response.")

with col2:
    st.subheader("📊 Audit Result")
    if 'last_result' in st.session_state:
        res = st.session_state['last_result']
        
        # Risk Badge
        risk_color = {
            "Critical": "red",
            "High": "orange",
            "Medium": "yellow",
            "Low": "green"
        }.get(res['risk_level'], "grey")
        
        st.markdown(f"""
            <div class="risk-card" style="border-left-color: {risk_color}">
                <h4 style="color: {risk_color}">Risk Level: {res['risk_level']}</h4>
                <p><strong>Is Hallucination:</strong> {'Yes ❌' if res['is_hallucination'] else 'No ✅'}</p>
                <p><strong>Confidence:</strong> {res['confidence']:.2f}</p>
                <p><strong>System Recommended Action:</strong> {res['recommended_action']}</p>
                <p><strong>Audit Score:</strong> {res['score']:.2f}/1.00</p>
                <hr>
                <p><strong>Explanation:</strong> {res['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Run an audit to see results here.")

st.divider()

st.subheader("📜 Audit History")
logs = service.get_logs()
if logs:
    log_data = []
    for entry in reversed(logs):
        log_data.append({
            "Timestamp": entry['output']['timestamp'],
            "Question": entry['input']['question'],
            "Hallucination": entry['output']['is_hallucination'],
            "Risk": entry['output']['risk_level'],
            "Score": entry['output']['score']
        })
    st.dataframe(pd.DataFrame(log_data), use_container_width=True)
else:
    st.write("No logs available.")
