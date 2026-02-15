import requests
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class FHIRClient:
    def __init__(self, base_url: str = "http://localhost:8080/fhir"):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Content-Type": "application/fhir+json"}

    def _get(self, resource_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Helper to perform GET requests."""
        url = f"{self.base_url}/{resource_type}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"FHIR Request failed: {e}")
            return {"entry": []}

    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific Patient resource by ID."""
        url = f"{self.base_url}/Patient/{patient_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch Patient/{patient_id}: {e}")
            return None

    def search_encounters(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Fetch Encounters for a patient.
        """
        params = {
            "subject": f"Patient/{patient_id}",
            "_sort": "-date",
            "_count": 50
        }
        bundle = self._get("Encounter", params)
        return [entry["resource"] for entry in bundle.get("entry", [])]

    def search_observations(self, patient_id: str, category: str = None) -> List[Dict[str, Any]]:
        """
        Fetch Observations (Labs, Vitals) for a patient.
        """
        params = {
            "subject": f"Patient/{patient_id}",
            "_sort": "-date",
            "_count": 100
        }
        if category:
            params["category"] = category
            
        bundle = self._get("Observation", params)
        return [entry["resource"] for entry in bundle.get("entry", [])]

    def search_medication_requests(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Fetch MedicationRequests for a patient.
        """
        params = {
            "subject": f"Patient/{patient_id}",
            "_sort": "-authoredon",
            "_count": 50
        }
        bundle = self._get("MedicationRequest", params)
        return [entry["resource"] for entry in bundle.get("entry", [])]
