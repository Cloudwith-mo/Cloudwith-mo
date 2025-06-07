# TaxFlowsAI Portal

This portal is a simple prototype that demonstrates how to capture income and deduction data from users. The goal is to explore AI techniques that can provide automated tax insights. It is not intended for production use and should only be run locally for experimentation.

## Requirements
* Python 3.11+
* `virtualenv` or your preferred environment manager

## Quick Start

1. Clone the repository.
```bash
git clone https://github.com/your-user-name/Cloudwith-mo.git
cd Cloudwith-mo
```
2. Create a virtual environment and install dependencies.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3. Run the prototype server.
```bash
python taxflowsai.py
```
4. Open your browser to `http://localhost:8000` to see the portal.

## Features

* Add income or deduction entries
* View a basic summary of your tax situation
* Experiment with AI-driven suggestions (placeholder)

This portal is for experimentation only. Do not upload real financial data.
=======
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
