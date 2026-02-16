import sys
import os
sys.path.append(os.path.abspath("src"))

from db.database import SessionLocal, init_db
from db.models import AuditLog
from db.feedback import submit_feedback
import uuid
from datetime import datetime

def test_feedback_submission():
    # Ensure tables exist
    init_db()
    
    db = SessionLocal()
    try:
        # 1. Create a dummy log
        log_id = uuid.uuid4()
        entry = AuditLog(
            id=log_id,
            patient_id="test-feedback-patient",
            facts_json=[],
            summary_text="Summary for feedback",
            llm_model="test-model",
            timestamp=datetime.utcnow()
        )
        db.add(entry)
        db.commit()
        
        # 2. Submit Feedback
        success = submit_feedback(str(log_id), 0, "Missed important fact")
        assert success is True
        
        # 3. Verify
        updated_log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
        assert updated_log.feedback_score == 0
        assert updated_log.feedback_text == "Missed important fact"
        
        print("Feedback Test Passed!")
    except Exception as e:
        print(f"Feedback Test Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_feedback_submission()
