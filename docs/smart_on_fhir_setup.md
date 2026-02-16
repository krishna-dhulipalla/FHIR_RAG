# SMART on FHIR Setup Guide

This document outlines how to transition the **Pre-Rounding Assistant** from a local HAPI FHIR server to a production EHR environment using SMART on FHIR.

## Overview

SMART on FHIR allows apps to run inside an EHR (like Epic or Cerner) using OAuth2 for authentication and authorization.

## Configuration Steps

### 1. Register the App

- Go to the EHR Developer Portal (e.g., [Epic App Orchard](https://apporchard.epic.com/)).
- Register "Pre-Rounding Assistant".
- **Redirect URI**: `https://your-app.com/callback` (or `http://localhost:8501` for testing).
- **Scopes**: `patient/Observation.read`, `patient/Encounter.read`, `launch`.

### 2. Update `src/fhir/client.py`

Modify `FHIRClient` to handle the OAuth2 handshake.

```python
class SmartFHIRClient(FHIRClient):
    def __init__(self, base_url, token):
        self.headers = {"Authorization": f"Bearer {token}"}
        # ...
```

### 3. Launch Flow

The app will be launched from the EHR with a `launch` token.

1. **Launch Request**: EHR redirects to valid `launch_url`.
2. **Auth Request**: App redirects to EHR Auth Server.
3. **Token Exchange**: App exchanges authorization code for `access_token`.
4. **Context**: The token response includes the `patient` ID in context.

## Local Testing

For local development without an EHR, we continue to use the Open/No-Auth HAPI FHIR server as configured in `docker-compose.yml`.
