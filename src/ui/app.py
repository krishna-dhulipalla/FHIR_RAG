import streamlit as st
import json
import sys
import os

# Add src to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import run_pipeline
from db.database import SessionLocal
from db.models import AuditLog

st.set_page_config(page_title="Pre-Rounding Assistant", layout="wide")

st.title("🏥 Pre-Rounding Assistant")
st.markdown("Evidence-Based Clinical Summaries from FHIR")

# Sidebar
with st.sidebar:
    st.header("Patient Selector")
    patient_id = st.text_input("Patient ID", value="patient-1")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    if st.button("Generate Summary", type="primary"):
        if not api_key:
            st.warning("Please provide an OpenAI API Key.")
        else:
            with st.spinner("Fetching FHIR data & generating summary..."):
                try:
                    results = run_pipeline(patient_id, api_key=api_key)
                    st.session_state["results"] = results
                except Exception as e:
                    st.error(f"Error: {e}")

# Main Layout
if "results" in st.session_state:
    res = st.session_state["results"]
    
    if "error" in res:
        st.error(res["error"])
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(f"Summary: {res['patient_name']}")
            st.markdown(res["summary"])
            
            if res.get("audit_id"):
                st.caption(f"Audit Log ID: {res['audit_id']}")

        with col2:
            st.subheader("Evidence Panel")
            
            # Extract citations for a dropdown
            facts = res["facts_raw"]
            fact_options = {f"{f.type.value} - {f.name} ({f.timestamp.strftime('%H:%M')})": f for f in facts}
            
            selected_fact_label = st.selectbox("Select a Fact to View Source:", options=list(fact_options.keys()))
            
            if selected_fact_label:
                fact = fact_options[selected_fact_label]
                st.info(f"Source ID: {fact.source_id}")
                st.json({
                    "resourceType": fact.source_id.split("/")[0],
                    "id": fact.source_id.split("/")[1] if "/" in fact.source_id else "",
                    "value": fact.value,
                    "unit": fact.unit,
                    "status": fact.status,
                    "timestamp": fact.timestamp.isoformat()
                })
                # In a real app, we'd fetch the full raw resource here using client.get_resource(source_id)

st.divider()

# Audit Log Section (Simple View)
with st.expander("Audit Log History (Recent)"):
    db = SessionLocal()
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10).all()
    db.close()
    
    for log in logs:
        st.text(f"{log.timestamp} - {log.patient_id} - {log.llm_model}")
