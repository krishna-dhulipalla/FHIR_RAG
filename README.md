# 🏥 Pre-Rounding Assistant

**A Grounded, Evidence-Based Clinical Summarization Tool powered by FHIR and LLMs.**

The **Pre-Rounding Assistant** helps clinicians quickly review patient data by generating concise, accurate summaries from FHIR records. Unlike generic chatbots, this system is **grounded**: every claim in the summary is cited with a link back to the original clinical fact (Lab, Vital, Medication). **This means: zero hallucination, full audit trail, and trust in clinical accuracy.**

![Status](https://img.shields.io/badge/Status-Prototype-blue)
![Tech](https://img.shields.io/badge/Built%20With-Python%20|%20Streamlit%20|%20PostgreSQL%20|%20FHIR%20|%20OpenAI-green)

---

## 💡 Use Case Example

**Scenario**: Dr. Smith needs to pre-round on 15 patients in 30 minutes.

**Without this tool**: She manually clicks through each patient's EHR, reviewing 20+ tabs per patient (Labs, Vitals, Meds, Notes). Takes 2-3 minutes per patient.

**With this tool**:

1. Opens the assistant
2. Selects patient ID
3. Gets a 200-word summary: "Since yesterday, creatinine rose from 1.2→1.8 [[Lab/456]], BP stable at 120/80 [[Vital/789]], added Lisinopril 10mg [[Med/234]]"
4. Reviews summary in 15 seconds, clicks citations if needed

**Time saved**: 2.5 minutes per patient × 15 patients = **37 minutes saved** every morning.

## ✨ Key Features

- **Grounded Summaries**: Uses a deterministic "Fact Table" approach to ensure LLM outputs are faithful to the data.
- **Strict Citations**: Every sentence includes a click-to-verify citation (e.g., `[[Observation/123]]`).
- **Privacy First (PHI Redaction)**: Built-in `Redactor` middleware scrubs names and dates _before_ sending data to the LLM.
- **Audit Logging**: Every request, fact table, and summary is logged to PostgreSQL for compliance.
- **Human-in-the-Loop Feedback**: Clinicians can rate summaries ("Good" vs "Incorrect") directly in the UI.
- **Automated Evaluation**: Includes an "LLM-as-a-Judge" script to score groundedness and hallucination rates.

## 🎯 Why This Matters

In clinical settings, **accuracy is non-negotiable**. Generic LLM chatbots can hallucinate medication names, misreport lab values, or fabricate patient history—all potentially dangerous.

This assistant solves that by:

- ✅ Using a **deterministic fact table** that captures only what's in the FHIR records
- ✅ Forcing the LLM to **cite every claim** with a verifiable source
- ✅ **Logging everything** for compliance and audit trails
- ✅ Implementing **PHI redaction** to protect patient privacy

**Result**: Summaries that are fast, accurate, and safe enough for real clinical consideration.

## 🏗️ Architecture

1.  **Ingestion**: Fetches raw JSON resources (Encounters, Observations, Meds) from a **HAPI FHIR** server.
2.  **Processing**: Flattens resources into a temporal `FactTable`, normalizing units and detecting data gaps.
3.  **Redaction**: Regex-based middleware replaces PHI (names, dates, MRNs) with deterministic tokens before LLM processing, ensuring no sensitive data leaves the system boundary.
4.  **Inference**: Sends the redacted fact table to **OpenAI GPT-4o** with a strict system prompt.
5.  **UI**: A **Streamlit** dashboard displays the summary alongside a searchable "Evidence Explorer".

---

## 🚀 Getting Started

### Prerequisites

- **Docker & Docker Compose** (for FHIR Server & Postgres)
- **Python 3.9+**
- **OpenAI API Key**

### 1. Installation

Clone the repository:

```bash
git clone https://github.com/krishna-dhulipalla/Clinical-pre-rounding-ai.git
cd Clinical-pre-rounding-ai
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 2. Infrastructure Setup

Start the local FHIR server (HAPI) and Database (Postgres):

```bash
docker-compose up -d
```

_Wait ~30 seconds for the containers to initialize._

### 3. Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API Key:

```ini
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=postgresql://admin:admin@localhost:5432/fhir_rag_audit
FHIR_BASE_URL=http://localhost:8080/fhir
```

### 4. Load Synthetic Data

Since the local FHIR server is empty, load the sample Synthea data:

```bash
python scripts/load_synthea.py
```

_This script uploads a sample patient bundle (`data/patient_bundle_1.json`) to the FHIR server._

---

## 🖥️ Usage

Run the User Interface:

```bash
streamlit run src/ui/app.py
```

Open your browser to `http://localhost:8501`.

1.  **Select Patient**: Choose a patient from the dropdown (defaults to the synthetic patient).
2.  **Generate Summary**: Click the red button.
3.  **Review**:
    - **Summary Tab**: Read the clinical narrative. Hover over citations `[[...]]`.
    - **Triage Board**: See critical/high priority labs instantly.
    - **Evidence Explorer**: Filter and search the raw facts used to generate the summary.
4.  **Feedback**: Rate the summary in the "Audit and Feedback" tab.

---

## 🛠️ Developer Tools

### Run Automated Evaluation

Score the quality of your recent summaries using the LLM-as-a-Judge:

```bash
python scripts/run_eval.py
```

### Run Unit Tests

Verify the Redaction and Logic components:

```bash
pytest tests/
# or specific tests
python tests/test_redaction.py
python tests/test_audit_log.py
```

---

## 📂 Project Structure

```text
├── data/                 # Synthetic FHIR bundles
├── docs/                 # Documentation (Architecture, Epics)
├── scripts/
│   ├── load_synthea.py   # Data loader
│   └── run_eval.py       # Offline evaluation script
├── src/
│   ├── db/               # Database models & Feedback logic
│   ├── eval/             # LLM Judge logic
│   ├── fhir/             # FHIR API Client
│   ├── ingestion/        # Fact Table Engine & Normalization
│   ├── llm/              # Prompts & OpenAI Client
│   ├── redaction/        # Privacy Middleware
│   ├── ui/               # Streamlit App
│   └── main.py           # Core pipeline orchestration
├── tests/                # Unit tests
├── docker-compose.yml    # Infrastructure
└── requirements.txt      # Python dependencies
```

## 🔒 Security Note

This project is a **prototype**.

- **PHI**: The `Redactor` is regex-based. For production, integrate a specialized NLP tool like Microsoft Presidio.
- **Auth**: The local FHIR server is open. See `docs/smart_on_fhir_setup.md` for production OAuth2 integration.

---

**License**: MIT
