# ⚖️ EquityIQ — Compensation Equity Intelligence

**A full-stack compensation equity analytics and intelligence platform**

EquityIQ is a demonstration project for comparing compensation against role, level, location, effective-dated salary bands, and other documented factors. It identifies potential exceptions and disparity cases, then creates evidence-backed proposals for human review.

The application combines a React/Vite dashboard, a Python/FastAPI backend, PostgreSQL, and six deterministic Python agents. All employee and compensation records in the included dataset are synthetic. The analysis is a decision-support demo, not a legal finding or production compensation policy.

**Repository:** [soundaryaambiger-ship-it/compensation-equity-platform](https://github.com/soundaryaambiger-ship-it/compensation-equity-platform)

---

## 📸 Frontend screenshots

These screenshots show the application using synthetic demonstration data.

### Overview dashboard

![EquityIQ Overview dashboard](docs/screenshots/overview.png)

### Overview with the EquiQ assistant

![Overview with EquiQ assistant open](docs/screenshots/overview-assistant.png)

### Agent output after running compensation analysis

![Overview showing the six agents' results](docs/screenshots/overview-agent-results.png)

### Employee directory

![Synthetic employee directory](docs/screenshots/employees.png)

### Compensation comparisons

![Band positioning and compa-ratio results](docs/screenshots/comparisons-results.png)

![Comparisons page while analysis is running](docs/screenshots/comparisons-running.png)

### Approval queue

![Adjustment proposal approval queue](docs/screenshots/approvals.png)

To add or replace a screenshot, save a PNG in `docs/screenshots/`, add a Markdown image link here (for example, `![Overview](docs/screenshots/overview.png)`), then commit and push the image and README.

---

## 🛠️ Technology stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Analysis engine | Six deterministic, rule-based Python agents |
| API documentation | FastAPI / Swagger UI |
| Synthetic data | Python, CSV, JSON |

---

## ✨ What the application does

- Generates or loads synthetic employees, roles, levels, locations, compensation bands, and salary histories.
- Normalizes salary values to INR and full-time equivalent (FTE) before comparison.
- Uses effective-dated bands to calculate compa-ratio and band position.
- Groups records by role, level, location, and salary year for comparison.
- Flags potential pay disparity and data-quality exceptions for review.
- Creates proposed adjustments with evidence and a pending human-review status.
- Records proposal decisions as audit events; approving a proposal does **not** change an employee salary record.
- Provides a local, rule-based EquiQ assistant for supported project questions and synthetic database lookups. No external AI API key is required.

---

## 📂 Project structure

```text
compensation-equity-platform/
├── backend/
│   ├── app/
│   │   ├── agents/       # Six analysis agents and orchestrator
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Application configuration
│   │   ├── db/           # SQLAlchemy database setup
│   │   ├── models/       # Database entities
│   │   ├── schemas/      # Request schemas
│   │   └── services/     # Analysis and assistant services
│   ├── scripts/          # Generate, validate, initialize, and seed data
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── data/
│   └── generated/        # Synthetic CSV/JSON seed data and evaluation files
├── docs/
│   ├── screenshots/
│   ├── architecture.png
│   ├── architecture.pdf
│   └── data_dictionary.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── .env.example
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 📊 Synthetic dataset

The repository includes reproducible synthetic seed data. The generator can recreate it with the same seed.

| Dataset measure | Volume |
|---|---:|
| Employees | 5,000 |
| Roles | 20 |
| Levels | 10 |
| Role/level combinations | 200 |
| Locations | 5 |
| Compensation bands | 1,000 |
| Salary records | 15,000 |
| Salary history | 3 years (2024–2026) |
| Default random seed | `20261022` |

Generated artifacts include CSV and JSON files, a separate `ground_truth` dataset, isolated edge-case fixtures, and a SHA-256 source manifest. Ground-truth labels are not used as analysis input features.

---

## 💻 Run locally (Windows PowerShell)

### Prerequisites

- Python 3.11 or newer (the commands below use Python 3.12)
- Node.js 20 or newer and npm
- PostgreSQL 15 or newer, or Docker Desktop with Docker Compose
- Git

### 1. Clone the repository

```powershell
git clone https://github.com/soundaryaambiger-ship-it/compensation-equity-platform.git
Set-Location .\compensation-equity-platform
```

### 2. Create the database

Start your local PostgreSQL service, then create the database if it does not already exist. Update the PostgreSQL installation version in the path if needed:

```powershell
& 'C:\Program Files\PostgreSQL\16\bin\psql.exe' -U postgres -h 127.0.0.1 -p 5432 -d postgres -c "CREATE DATABASE comp_equity;"
```

Alternatively, start the Compose PostgreSQL service from the project root:

```powershell
docker compose up -d postgres
```

### 3. Set up and start the backend

From the project root:

```powershell
Set-Location .\backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend\.env` and set `DATABASE_URL` to match your local PostgreSQL username and password. For example:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/comp_equity
```

The checked-in generated dataset can be validated and loaded as follows:

```powershell
python -m scripts.validate_data ..\data\generated
python -m scripts.init_db
python -m scripts.seed_db ..\data\generated
python -m uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`; interactive API documentation is at `http://localhost:8000/docs`.

To regenerate the synthetic data before validation and seeding:

```powershell
python -m scripts.generate_data --employees 5000 --seed 20261022 --out ..\data\generated
```

### 4. Set up and start the frontend

Open a second PowerShell terminal at the project root:

```powershell
Set-Location .\frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open `http://localhost:5173`. The frontend API URL defaults to `http://localhost:8000/api/v1`; change `VITE_API_URL` in `frontend\.env` only if your backend uses a different address.

---

## 🤖 Six-agent analysis workflow

Select **Run Compensation Analysis** on the Overview page to execute the pipeline. The dashboard displays each agent's output count and sample results.

| Agent | Responsibility |
|---|---|
| **Data quality** | Flags invalid FTE, marked FTE exceptions, and missing currency conversions. |
| **Normalization** | Converts salary to INR and normalizes to 1.0 FTE. |
| **Band compliance** | Selects the effective band for a salary date and calculates compa-ratio and band position. |
| **Comparability** | Groups records by role, level, location, and salary year. |
| **Disparity detection** | Flags salaries below 80% of the group median when the comparison group has at least three records. |
| **Recommendation** | Produces a pending human-review proposal with supporting evidence. |

The agents are deterministic Python rules, not autonomous LLM agents. The pipeline does not directly change salary records.

### Compensation calculations

```text
Compa-ratio = Normalized annual salary / Compensation band midpoint

Band position = (Normalized salary - Band minimum) / (Band maximum - Band minimum)
```

Band positions below `0` are below band; values above `1` are above band. The 20% disparity threshold is a demonstration rule only, not an approved policy or legal conclusion.

---

## 🧭 Application modules

| Module | Purpose |
|---|---|
| **Overview** | Live database metrics, latest-salary positioning, role-family summaries, workflow, and agent results |
| **Employees** | Browse synthetic employee records |
| **Comparisons** | Inspect band positioning and compa-ratio results |
| **Anomalies** | Inspect potential pay disparity findings |
| **Approvals** | Review proposals and record approve/reject decisions |
| **EquiQ assistant** | Answer supported project and synthetic database questions locally |

---

## 🔌 API endpoints

All endpoints are under `/api/v1`.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Backend health check |
| `GET` | `/dashboard` | Live counts, latest-salary summaries, role-family data, and recent audit events |
| `GET` | `/employees` | Retrieve synthetic employee records |
| `GET` | `/analysis` | Run the agent pipeline, return findings, and create pending proposals |
| `GET` | `/proposals` | Retrieve adjustment proposals |
| `POST` | `/proposals/{proposal_id}/decision` | Approve or reject a pending proposal |
| `POST` | `/assistant/chat` | Ask the local EquiQ assistant a supported question |

---

## ✅ Validation and tests

Run these commands from `backend` with the virtual environment active:

```powershell
python -m scripts.validate_data ..\data\generated
python -m scripts.reproducibility_check
python -m unittest discover -s tests -v
```

The validator checks generated records and relationships. The reproducibility check compares fixed-seed outputs and checksums.

---

## ⚠️ Scope and limitations

- All included employee and compensation data is synthetic. Do not load confidential or real HR information into this demo.
- Performance, tenure, promotion history, and FTE are supplied as contextual evidence; they are not currently statistical adjustment factors.
- Isolated edge-case fixtures are generated but are not loaded into the baseline database or exercised by the baseline analysis.
- Automated precision, recall, and F1 evaluation against ground truth is not currently implemented.
- The disparity threshold is a hard-coded demonstration rule and needs HR/legal approval before any production use.
- The approval API is not authenticated. A production system would require authentication, role-based access, approval segregation, secure audit retention, encryption, and privacy/fairness validation.

---

## 📚 Documentation

- [Data dictionary](docs/data_dictionary.md)
- [Acceptance criteria](docs/acceptance_criteria.md)
- [File guide](docs/file_guide.md)
- [Architecture diagram](docs/architecture.png)
- [Architecture document](docs/architecture.pdf)
- [Screenshot files](docs/screenshots/)

---

**EquityIQ — making compensation analysis more transparent, traceable, and evidence-driven.**
