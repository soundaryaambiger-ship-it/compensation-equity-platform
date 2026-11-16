# Compensation Equity Intelligence Platform

A full-stack, synthetic-data reference implementation for effective-dated compensation comparison, disparity triage and human-reviewed adjustment proposals. It uses FastAPI, PostgreSQL, SQLAlchemy and React/Vite. All generated people and compensation data are synthetic; do not load confidential HR records into this demo.

## What it does
- Stores employees, roles, levels, locations, compensation bands, salary history, performance evidence, tenure, promotions, proposals, comparable groups and audit events.
- Generates deterministic synthetic master and transaction data (5,000 employees by default; 20 roles x 10 levels, 5 locations and 3 salary records per employee for 2024–2026).
- Normalizes salaries to INR and 1.0 FTE before comparing; uses role + level + location as the default comparison cohort.
- Computes compa-ratio (`normalized annual salary / band midpoint`) and band position (`(salary - min) / (max - min)`). Values outside [0,1] are below/above band.
- Runs six deterministic agents and produces potential review proposals. It never directly changes salary.
- Records approval decisions as status transitions and audit events.
- Serves live data to the React dashboard through REST endpoints; the dashboard contains no embedded employee counts or sample employee rows.

## Architecture
See `docs/architecture.png` and `docs/architecture.pdf`.

## Frontend screenshots
Save frontend screenshots in `docs/screenshots/` using PNG or JPEG files. For example, save the Overview capture as `docs/screenshots/overview.png`, then embed it in this README with:

```markdown
![Compensation equity Overview](docs/screenshots/overview.png)
```

Only use synthetic/demo data in screenshots; do not publish real employee names, IDs, or compensation.

## Requirements
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ or Docker Desktop with Docker Compose

## Run locally (Windows PowerShell)
1. Start PostgreSQL using **one** of these options:

   **Local PostgreSQL:** Install PostgreSQL for Windows and remember the password set for the `postgres` user. Create the project database (adjust `16` in the path if you installed another version; skip this if the database already exists):
   ```powershell
   & 'C:\Program Files\PostgreSQL\16\bin\psql.exe' -U postgres -h 127.0.0.1 -p 5432 -d postgres -c "CREATE DATABASE comp_equity;"
   ```
   If `psql.exe` is not at that path, find the `bin\psql.exe` under your PostgreSQL installation. You do not need to add it to `PATH` when using the full path above.

   **Docker Desktop:** Install and start Docker Desktop, then open a new PowerShell terminal and verify `docker --version` and `docker compose version` work. From the project root, run:
   ```powershell
   docker compose up -d postgres
   ```
   Compose creates the `comp_equity` database. To open a PostgreSQL prompt inside the container, run `docker compose exec postgres psql -U postgres -d comp_equity`.

2. Ensure `backend\.env` has a `DATABASE_URL` matching your local PostgreSQL username, password and port. The default is `postgresql+psycopg://postgres:postgres@localhost:5432/comp_equity`; update the password if you chose a different one during installation. The Compose database uses the default credentials. Copy `backend\.env.example` if needed.
3. In PowerShell, run the backend setup from the project root:
   ```powershell
   Set-Location .\backend
   py -3.12 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m scripts.generate_data --employees 5000 --seed 20261022 --out ..\data\generated
   .\.venv\Scripts\python.exe -m scripts.validate_data ..\data\generated
   .\.venv\Scripts\python.exe -m scripts.init_db
   .\.venv\Scripts\python.exe -m scripts.seed_db ..\data\generated
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
   ```
4. In a second PowerShell terminal, run the frontend from the project root:
   ```powershell
   Set-Location .\frontend
   npm install
   npm run dev
   ```
5. Open http://localhost:5173. API documentation is at http://localhost:8000/docs.

## Use the workflow
1. **Overview** shows live database counts. Select **Run Compensation Analysis** to execute the six-agent pipeline and display data-derived findings, positioning metrics and sample outputs for each agent. **Employees** lists seeded synthetic employees.
2. Open **Comparisons** or **Anomalies** to inspect detailed band or disparity findings. Analysis also creates pending review proposals in the database.
3. Open **Approvals** to inspect proposal evidence and approve or reject a pending review. Decisions are recorded as status changes and audit events; approval does not change a salary record.

To check the generated-data validations, run `.\.venv\Scripts\python.exe -m scripts.validate_data ..\data\generated` from `backend`. To verify fixed-seed reproducibility, run `.\.venv\Scripts\python.exe -m scripts.reproducibility_check` from `backend`.
Run backend tests from `backend` with `python -m unittest discover -s tests`.
EquiQ runs entirely locally without API keys or external AI services. It answers project reference questions and supported queries against the synthetic database, including employee ID lookups by name.

## Run with Docker
Install and start Docker Desktop before running these commands. From the project root:

```bash
docker compose up --build -d
docker compose exec api python -m scripts.generate_data --employees 5000 --seed 20261022 --out /tmp/generated
docker compose exec api python -m scripts.validate_data /tmp/generated
docker compose exec api python -m scripts.seed_db /tmp/generated
```
The API container creates the database tables on startup. These commands generate and validate the synthetic records inside the API container, then seed PostgreSQL. In a separate PowerShell terminal, start the frontend as described above.

## API
- `GET /api/v1/health`
- `GET /api/v1/dashboard`
- `GET /api/v1/employees?skip=0&limit=100`
- `GET /api/v1/analysis` — runs the six-agent pipeline, returns findings and per-agent output summaries, and persists pending review proposals.
- `GET /api/v1/proposals`
- `POST /api/v1/assistant/chat` — answers reference questions and supported local database queries; no external AI service is called.
- `POST /api/v1/proposals/{proposal_id}/decision?decision=APPROVED` (or REJECTED)

## Six agents
1. **DataQualityAgent** — checks FTE validity and missing currency conversion.
2. **NormalizationAgent** — converts to INR and 1.0 FTE.
3. **BandComplianceAgent** — checks band effective dates and computes compa-ratio/band position.
4. **ComparabilityAgent** — groups by role, level and location.
5. **DisparityAgent** — flags materially low salaries against the comparable-group median (initial demo threshold: 20%).
6. **RecommendationAgent** — creates a proposed review amount and evidence summary. Human review remains mandatory.

The 20% threshold is a hard-coded demo rule, not a legal finding or compensation policy. Before production use, HR/legal must approve the policy, add documented job-related explanatory factors to the model, secure endpoints, add role-based access, and perform fairness/privacy validation.

## Important implementation notes / limitations
- The included synthetic generator exports master/transaction CSV and JSON, `ground_truth`, negative scenario descriptions, isolated `edge_case_fixtures.csv/json`, and a SHA-256 source manifest. The edge-case fixtures are deliberately not loaded into the baseline database. It is deterministic for a fixed seed.
- `ground_truth` and negative scenarios are separate evaluation artefacts; do not load them as model input features.
- The baseline analysis compares role + level + location + salary year. Performance rating, tenure, promotions and FTE are included as contextual evidence, not used as statistical adjustment factors. The isolated negative fixtures are not exercised by the baseline analysis, and the project does not currently calculate precision/recall against `ground_truth`.
- The floating EquiQ assistant uses local rules and synthetic database queries; it does not call an external AI service. The six analysis agents remain deterministic Python rules, not autonomous LLM agents.
- The demo approval endpoint is not authenticated. Add SSO/RBAC, CSRF protection, audit retention, encryption and approval segregation before production.
- The generated data generator includes synthetic annual salary history, performance, tenure and promotions. Review `data_dictionary.md` for units and semantics.

## Reproducibility
Run the generator twice to separate output directories with the same seed and compare `source_manifest.json` SHA-256 values. The manifest excludes itself. Example:
```bash
python -m scripts.generate_data --employees 5000 --seed 20261022 --out ..\data\run_a
python -m scripts.generate_data --employees 5000 --seed 20261022 --out ..\data\run_b
```
