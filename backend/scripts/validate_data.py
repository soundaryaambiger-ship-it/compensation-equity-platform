"""CSV validation for primary keys, foreign keys, enum/range rules and arithmetic."""
import csv,sys
from pathlib import Path
p=Path(sys.argv[1] if len(sys.argv)>1 else '../data/generated')
def load(n):
 with open(p/f'{n}.csv',encoding='utf-8') as f:return list(csv.DictReader(f))
def unique(rows,key): return len(rows)==len({r[key] for r in rows})
roles,levels,locs,bands,emps,sals=map(load,['roles','levels','locations','compensation_bands','employees','salary_records'])
checks={}
checks['role_pk_unique']=unique(roles,'id');checks['level_pk_unique']=unique(levels,'id');checks['location_pk_unique']=unique(locs,'id');checks['band_pk_unique']=unique(bands,'id');checks['employee_pk_unique']=unique(emps,'id');checks['salary_pk_unique']=unique(sals,'id')
checks['employee_role_fk']=all(r['role_id'] in {x['id'] for x in roles} for r in emps)
checks['employee_level_fk']=all(r['level_id'] in {x['id'] for x in levels} for r in emps)
checks['employee_location_fk']=all(r['location_id'] in {x['id'] for x in locs} for r in emps)
checks['salary_employee_fk']=all(r['employee_id'] in {x['id'] for x in emps} for r in sals)
checks['salary_band_fk']=all(r['band_id'] in {x['id'] for x in bands} for r in sals)
checks['band_math']=all(float(b['minimum'])<=float(b['midpoint'])<=float(b['maximum']) for b in bands)
checks['fte_range']=all(0<float(r['fte'])<=1 for r in emps+sals)
checks['salary_nonnegative']=all(float(r['base_salary'])>=0 for r in sals)
checks['three_salary_records_per_employee']=all(sum(1 for s in sals if s['employee_id']==e['id'])==3 for e in emps)
checks['ground_truth_separate']=(p/'ground_truth.csv').exists()
print({'checks':checks,'passed':sum(checks.values()),'total':len(checks)})
if not all(checks.values()): raise SystemExit(1)
