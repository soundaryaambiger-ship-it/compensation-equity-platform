"""Load generated CSV master and transaction data into PostgreSQL."""
import csv,sys
from pathlib import Path
from datetime import date
from app.db.session import SessionLocal
from app.models.entities import Role,Level,Location,Employee,CompensationBand,SalaryRecord,PerformanceEvidence,Tenure,Promotion
DATA=Path(sys.argv[1] if len(sys.argv)>1 else '../data/generated')
def rows(name):
 with open(DATA/f'{name}.csv',encoding='utf-8') as f: return list(csv.DictReader(f))
def d(v): return date.fromisoformat(v) if v else None
db=SessionLocal()
try:
 for r in rows('roles'): db.merge(Role(**r))
 for r in rows('levels'): r['rank']=int(r['rank']); db.merge(Level(**r))
 for r in rows('locations'): r['fx_to_inr']=float(r['fx_to_inr']); db.merge(Location(**r))
 db.commit()
 for r in rows('employees'): r['hire_date']=d(r['hire_date']); r['fte']=float(r['fte']); db.merge(Employee(**r))
 for r in rows('compensation_bands'):
  for k in ['minimum','midpoint','maximum']: r[k]=float(r[k])
  r['effective_from']=d(r['effective_from']); r['effective_to']=d(r['effective_to']); db.merge(CompensationBand(**r))
 db.commit()
 for r in rows('salary_records'):
  for k in ['base_salary','fte','annualized_inr']: r[k]=float(r[k]) if r[k] not in ('',None) else None
  r['effective_date']=d(r['effective_date']); db.merge(SalaryRecord(**r))
 for r in rows('performance_evidence'):
  r['rating']=float(r['rating']); r['period_start']=d(r['period_start']); r['period_end']=d(r['period_end']); db.merge(PerformanceEvidence(**r))
 for r in rows('tenure'): r['years']=float(r['years']); r['as_of_date']=d(r['as_of_date']); db.merge(Tenure(**r))
 for r in rows('promotions'): r['effective_date']=d(r['effective_date']); db.merge(Promotion(**r))
 db.commit(); print('Seed completed.')
finally: db.close()
