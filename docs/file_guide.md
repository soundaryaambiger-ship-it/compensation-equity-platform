# Project file guide

## Root
- `README.md` — complete prerequisites, setup, run commands, API map, agent descriptions and limitations.
- `docker-compose.yml` — local PostgreSQL + API containers.
- `docs/` — architecture exports, data dictionary, acceptance checklist and this guide.
- `data/generated/` — deterministic 5,000-employee synthetic CSV/JSON exports, isolated negative-path fixtures and source manifest.

## Backend
- `backend/requirements.txt` — Python package versions.
- `backend/Dockerfile` — container image recipe for FastAPI.
- `backend/.env.example` — database connection template; copy to `.env` and edit credentials.
- `backend/app/main.py` — FastAPI app creation, CORS and route registration.
- `backend/app/core/config.py` — environment-driven configuration.
- `backend/app/db/base.py` — SQLAlchemy declarative base.
- `backend/app/db/session.py` — PostgreSQL engine, session factory and request dependency.
- `backend/app/models/entities.py` — relational table definitions and primary/foreign keys.
- `backend/app/models/__init__.py` — imports models for metadata discovery.
- `backend/app/api/routes.py` — REST endpoints for dashboard, employees, analysis, proposals and decisions.
- `backend/app/services/analysis.py` — database extraction, effective-dated band lookup and evidence context assembly.
- `backend/app/agents/base.py` — minimal agent interface.
- `backend/app/agents/agents.py` — six focused, deterministic analysis agents.
- `backend/app/agents/orchestrator.py` — executes agents in dependency order and captures trace counts.
- `backend/scripts/init_db.py` — creates database tables from SQLAlchemy metadata.
- `backend/scripts/generate_data.py` — seeded master/transaction data generator.
- `backend/scripts/seed_db.py` — loads generated CSV data into PostgreSQL.
- `backend/scripts/validate_data.py` — validates uniqueness, foreign keys, ranges, history volume and band arithmetic.
- `backend/scripts/reproducibility_check.py` — regenerates twice and compares SHA-256 manifests.

## Frontend
- `frontend/package.json` — React, Vite, Recharts and icon dependencies plus npm scripts.
- `frontend/vite.config.js` — Vite dev server configuration.
- `frontend/index.html` — browser entry document.
- `frontend/src/main.jsx` — mounts React and imports global styles.
- `frontend/src/App.jsx` — page routing/state for the dashboard shell.
- `frontend/src/styles.css` — responsive layout, components, light/dark theme styling.
- `frontend/src/services/api.js` — centralized HTTP calls to FastAPI; all displayed data comes from API responses.
- `frontend/src/components/Layout.jsx` — sidebar, collapse control, theme toggle and assistant panel shell.
- `frontend/src/pages/Overview.jsx` — live KPI cards and workflow explanation.
- `frontend/src/pages/Employees.jsx` — backend employee directory.
- `frontend/src/pages/Analysis.jsx` — run comparisons or anomaly analysis and view agent trace.
- `frontend/src/pages/Approvals.jsx` — human review queue and approve/reject actions.

## Important
The floating assistant is intentionally a clearly labelled placeholder; it does not pretend to be an LLM. The six agents are deterministic Python agents, not LLM agents. This is appropriate for reproducible compensation rules; a governed LLM can later summarize evidence but must not make or approve employment decisions.
