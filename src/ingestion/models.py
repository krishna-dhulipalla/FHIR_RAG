from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional

class FactType(Enum):
    LAB = "LAB"
    VITAL = "VITAL"
    MED_ORDER = "MED_ORDER"
    MED_ADMIN = "MED_ADMIN"
    ENCOUNTER = "ENCOUNTER"
    OTHER = "OTHER"

@dataclass
class Fact:
    patient_id: str
    timestamp: datetime
    type: FactType
    name: str
    value: str
    unit: Optional[str] = None
    status: Optional[str] = None
    source_id: str = ""  # The FHIR Resource ID (e.g., "Observation/123")
    
    def to_markdown(self) -> str:
        """Returns a string representation suitable for LLM injection."""
        base = f"- [{self.timestamp.strftime('%Y-%m-%d %H:%M')}] **{self.type.value}** - {self.name}: {self.value}"
        if self.unit:
            base += f" {self.unit}"
        if self.status:
            base += f" ({self.status})"
        base += f" [[{self.source_id}]]"
        return base
