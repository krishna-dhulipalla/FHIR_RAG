import logging
import os
import json
from datetime import datetime
from fhir.client import FHIRClient
from ingestion.engine import FactTableBuilder
from llm.client import LLMClient
from llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from db.database import SessionLocal, init_db
from db.models import AuditLog

# Config Init
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pipeline(patient_id: str, api_key: str = None):
    """
    Runs the full summarization pipeline for a given patient_id.
    Returns a dictionary with facts, summary, and audit_id.
    """
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
        
    client = FHIRClient(base_url="http://localhost:8080/fhir")
    
    # 1. Fetch Patient Details
    patient = client.get_patient(patient_id)
    if not patient:
        return {"error": f"Patient {patient_id} not found"}
        
    name = "Unknown"
    if "name" in patient:
        family = patient["name"][0].get("family", "")
        given = " ".join(patient["name"][0].get("given", []))
        name = f"{given} {family}"
            
    logger.info(f"Generating Summary for Patient: {name} (ID: {patient_id})")

    # 2. Build Fact Table
    builder = FactTableBuilder(client)
    facts = builder.build_fact_table(patient_id)
    
    # Convert to Markdown
    facts_markdown = "\n".join([f.to_markdown() for f in facts])
    
    # Serialized facts for Audit Log
    facts_json = [
        {
            "timestamp": f.timestamp.isoformat(),
            "type": f.type.value,
            "name": f.name,
            "value": f.value,
            "unit": f.unit,
            "source_id": f.source_id
        }
        for f in facts
    ]

    # 3. Generate Summary
    llm = LLMClient(api_key=api_key)
    user_prompt = USER_PROMPT_TEMPLATE.format(facts_markdown=facts_markdown)
    summary = llm.generate_summary(SYSTEM_PROMPT, user_prompt)

    # 4. Audit Log
    db = SessionLocal()
    try:
        audit_entry = AuditLog(
            patient_id=patient_id,
            facts_json=facts_json,
            summary_text=summary,
            llm_model=llm.model,
            timestamp=datetime.utcnow()
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        audit_id = audit_entry.id
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")
        audit_id = None
    finally:
        db.close()

    return {
        "patient_name": name,
        "facts_markdown": facts_markdown,
        "facts_raw": facts,
        "summary": summary,
        "audit_id": str(audit_id) if audit_id else None
    }

def main():
    # Example usage
    result = run_pipeline("patient-1")
    if "error" in result:
        print(result["error"])
    else:
        print(f"Summary for {result['patient_name']}:\n")
        print(result["summary"])

if __name__ == "__main__":
    # Ensure tables exist (quick check)
    # init_db() 
    main()
