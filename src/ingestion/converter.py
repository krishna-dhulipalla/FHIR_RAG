from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import Fact, FactType
from .normalization import normalize_unit

def parse_fhir_date(date_str: str) -> datetime:
    """Parses FHIR date strings which can be YYYY, YYYY-MM, or YYYY-MM-DDTHH:MM:SS."""
    if not date_str:
        return datetime.min
    try:
        # Simplistic parsing for now, can be robustified
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min

def flatten_observation(resource: Dict[str, Any]) -> Fact:
    patient_ref = resource.get("subject", {}).get("reference", "")
    patient_id = patient_ref.split("/")[-1] if "/" in patient_ref else patient_ref
    
    # Determine type (Lab vs Vital)
    categories = resource.get("category", [])
    fact_type = FactType.OTHER
    for cat in categories:
        for coding in cat.get("coding", []):
            code = coding.get("code", "")
            if code == "laboratory":
                fact_type = FactType.LAB
            elif code == "vital-signs":
                fact_type = FactType.VITAL

    # Get Name
    code_text = resource.get("code", {}).get("text")
    if not code_text:
        # Try finding a display name in codings
        codings = resource.get("code", {}).get("coding", [])
        if codings:
            code_text = codings[0].get("display", "Unknown Observation")
        else:
            code_text = "Unknown Observation"

    # Get Value
    value = "N/A"
    unit = None
    if "valueQuantity" in resource:
        vq = resource["valueQuantity"]
        raw_val = str(vq.get("value"))
        raw_unit = vq.get("unit") or vq.get("code")
        # Normalize
        value, unit = normalize_unit(raw_val, raw_unit)
    elif "valueString" in resource:
        value = resource["valueString"]

    timestamp = parse_fhir_date(resource.get("effectiveDateTime"))
    
    return Fact(
        patient_id=patient_id,
        timestamp=timestamp,
        type=fact_type,
        name=code_text,
        value=value,
        unit=unit,
        status=resource.get("status"),
        source_id=f"Observation/{resource.get('id')}"
    )

def flatten_medication_request(resource: Dict[str, Any]) -> Fact:
    patient_ref = resource.get("subject", {}).get("reference", "")
    patient_id = patient_ref.split("/")[-1] if "/" in patient_ref else patient_ref
    
    # Get Med Name
    med_name = "Unknown Medication"
    if "medicationCodeableConcept" in resource:
        codings = resource["medicationCodeableConcept"].get("coding", [])
        if codings:
            med_name = codings[0].get("display", "Unknown Medication")
        else:
            med_name = resource["medicationCodeableConcept"].get("text", "Unknown Medication")
            
    timestamp = parse_fhir_date(resource.get("authoredOn"))
    
    return Fact(
        patient_id=patient_id,
        timestamp=timestamp,
        type=FactType.MED_ORDER,
        name=med_name,
        value="Ordered", # Dosage instructions could be parsed here
        status=resource.get("status"),
        source_id=f"MedicationRequest/{resource.get('id')}"
    )

def flatten_encounter(resource: Dict[str, Any]) -> Fact:
    patient_ref = resource.get("subject", {}).get("reference", "")
    patient_id = patient_ref.split("/")[-1] if "/" in patient_ref else patient_ref
    
    timestamp = parse_fhir_date(resource.get("period", {}).get("start"))
    
    # Class/Type
    enc_class = resource.get("class", {})
    name = enc_class.get("display") or enc_class.get("code") or "Encounter"
    
    return Fact(
        patient_id=patient_id,
        timestamp=timestamp,
        type=FactType.ENCOUNTER,
        name=name,
        value="Admit",
        status=resource.get("status"),
        source_id=f"Encounter/{resource.get('id')}"
    )

def entry_to_facts(entry: Dict[str, Any]) -> List[Fact]:
    resource = entry.get("resource", {})
    r_type = resource.get("resourceType")
    
    if r_type == "Observation":
        return [flatten_observation(resource)]
    elif r_type == "MedicationRequest":
        return [flatten_medication_request(resource)]
    elif r_type == "Encounter":
        return [flatten_encounter(resource)]
    
    return []
