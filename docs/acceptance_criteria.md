# Evaluation and acceptance checklist

| Area | Check | Evidence |
|---|---|---|
| Data quality | PK uniqueness and FK integrity | `python scripts/validate_data.py ../data/generated` |
| Effective dates | Band is selected only when effective for the salary date | BandComplianceAgent; missing/expired band is an exception |
| Normalization | Convert local currency to INR and annualize to 1.0 FTE | `annualized_inr` field and NormalizationAgent |
| Comparable groups | Role, level and location are the default cohort dimensions | ComparabilityAgent |
| Explainability | Every potential gap includes group median, employee normalized salary and gap % | disparity finding evidence JSON |
| Human control | Proposals remain pending until explicit decision | Approval endpoint + AuditEvent |
| Traceability | Proposal create and decision events are recorded | `audit_events` table |
| Reproducibility | Fixed seed generates stable CSV checksums | `source_manifest.json` |
| Evaluation labels | Ground truth is stored separately | `ground_truth.csv/json` |

Suggested metrics for a formal evaluation: precision/recall/F1 against labelled anomaly cases; false-positive rate across normal cohorts; percent of salary records with valid effective bands; percent with FX/FTE normalization; proposal evidence completeness; approval turnaround time; and reproducibility checksum match. Do not claim model accuracy until measured against an independently reviewed labelled test set.

The generator also emits `edge_case_fixtures.csv/json`: five isolated, labelled negative fixtures with real generated parent employee IDs and explicit malformed/exception payloads. They are intentionally not loaded by `seed_db.py` or included in analysis features. This keeps deliberate test anomalies from silently contaminating the valid baseline. Use these fixtures in negative-path tests or import them into a dedicated test schema.
