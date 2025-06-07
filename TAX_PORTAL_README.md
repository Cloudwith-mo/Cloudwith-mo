# TaxFlowsAI - Phase 1 Prototype

This repository contains a minimal Flask prototype for the **TaxFlowsAI** SaaS portal.
It demonstrates basic endpoints for client and admin interactions as outlined in the
phase 1 game plan.

## Features
- Client registration and login (simplified in-memory auth)
- Document upload endpoint storing files under `uploads/`
- Status tracking with in-memory store
- Admin endpoints to view clients and update status

## Running Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the app:
   ```bash
   python tax_portal/app.py
   ```

This will run the server on `http://localhost:5000` with debug mode enabled.

**Note**: This is only a minimal proof of concept. Integration with
AWS services (Cognito, S3, Textract) and a production database would
be required for a real deployment.
