# Architecture & Data Flow

## High-Level Pipeline

1.  **Retrieval Layer (FHIR Client)**
    - Queries HAPI FHIR for patient resources (Patient, Encounter, Observation, MedicationRequest).
    - Filters by time window (last 24-48 hours).

2.  **Ingestion & Normalization Engine**
    - **Flattening**: Converts nested FHIR JSON into flat "Fact" objects.
    - **Normalization**: Standardizes units (e.g., mg/dL vs g/L) and timestamps.
    - **Missing Data Detection**: Flags orders without administrations, etc.
    - **Output**: A canonical `FactTable` (List of Events).

3.  **PHI Redaction Middleware**
    - Intercepts text/data before it hits the LLM.
    - Detects sensitive entities (Names, Dates, IDs).
    - Replaces with tokens (e.g., `[PATIENT_NAME]`).

4.  **Summarization Engine (LLM)**
    - Input: `FactTable` (JSON/Markdown representation).
    - System Prompt: strict instruction to use _only_ provided facts and cite IDs.
    - Output: Summarized text with `[citation_id]` tags.

5.  **User Interface**
    - Displays the generated summary.
    - Renders citations as clickable links.
    - Clicking a citation opens the "Evidence Panel" showing the raw FHIR JSON for that fact.
    - "Mark Incorrect" button for HITL feedback.

6.  **Observability & Persistence**
    - **Postgres**: Stores audit logs (Query, Fact Hash, Prompt, Response, User Feedback).
    - **Eval Pipeline**: Offline script runs "LLM-as-a-Judge" to verify groundedness of logs.

## Directory Structure (Proposed)

```
/
├── docker/                 # HAPI FHIR, Postgres compose files
├── docs/                   # Documentation (Architecture, Epics, Setup)
├── src/
│   ├── api/                # FastAPI app
│   ├── db/                 # Postgres connection & models
│   ├── fhir/               # FHIR client & retrieval logic
│   ├── ingestion/          # Fact extraction & normalization logic
│   ├── llm/                # Prompts & LLM integration
│   ├── redaction/          # PHI removal middleware
│   └── ui/                 # Frontend code
├── tests/                  # Unit & Integration tests
├── scripts/                # Eval & Utility scripts
├── data/                   # Seed data / Synthea bundles
└── requirements.txt
```
