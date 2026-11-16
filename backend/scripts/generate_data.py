"""Deterministic synthetic HR compensation dataset generator. No real employee data."""
import argparse, random, csv, json, hashlib
from pathlib import Path
from datetime import date
import numpy as np
SEED=20261022
ROLE_NAMES=[('Software Engineer','Engineering'),('Data Analyst','Analytics'),('HR Specialist','People'),('QA Engineer','Engineering'),('Operations Analyst','Operations'),('Embedded Engineer','Engineering'),('Security Analyst','Security'),('Product Manager','Product'),('Sales Executive','Sales'),('Support Engineer','Support'),('Cloud Engineer','Engineering'),('DevOps Engineer','Engineering'),('UX Designer','Design'),('Financial Analyst','Finance'),('Recruiter','People'),('Business Analyst','Business'),('Network Engineer','IT'),('Technical Writer','Content'),('Project Manager','Product'),('Customer Success','Support')]
ROLES=[(f'ROLE-{i:02d}',name,family) for i,(name,family) in enumerate(ROLE_NAMES,1)]
LEVEL_NAMES=['Trainee','Junior','Associate I','Associate II','Mid I','Mid II','Senior I','Senior II','Lead','Principal']
LEVELS=[(f'L{i:02d}',name,i) for i,name in enumerate(LEVEL_NAMES,1)]
LOCS=[('LOC-BLR','Bengaluru','IN','INR',1.0),('LOC-HYD','Hyderabad','IN','INR',1.0),('LOC-PUN','Pune','IN','INR',1.0),('LOC-LON','London','UK','GBP',105.0),('LOC-NYC','New York','US','USD',83.0)]
def write_csv(path,rows):
 if not rows: return
 with open(path,'w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def generate(n,out,seed):
 rng=random.Random(seed); np.random.seed(seed); out=Path(out); out.mkdir(parents=True,exist_ok=True)
 roles=[dict(id=a,name=b,family=c) for a,b,c in ROLES]; levels=[dict(id=a,name=b,rank=c) for a,b,c in LEVELS]; locs=[dict(id=a,name=b,country=c,currency=d,fx_to_inr=e) for a,b,c,d,e in LOCS]
 bands=[]
 for role in roles:
  for lev in levels:
   for loc in locs:
    mid=(450000+levels[[x['id'] for x in levels].index(lev['id'])]['rank']*145000)
    bands.append(dict(id=f"BAND-{role['id']}-{lev['id']}-{loc['id']}-2026",role_id=role['id'],level_id=lev['id'],location_id=loc['id'],currency=loc['currency'],minimum=round(mid*.8,2),midpoint=round(mid,2),maximum=round(mid*1.2,2),effective_from='2024-01-01',effective_to='2026-12-31'))
 employees=[]; salaries=[]; performance=[]; tenures=[]; promotions=[]; truth=[]; proposals=[]
 for i in range(1,n+1):
  emp=f'EMP-{i:06d}'; role=rng.choice(roles); lev=rng.choice(levels); loc=rng.choice(locs); hire_year=rng.randint(2017,2023); hire=date(hire_year,rng.randint(1,12),rng.randint(1,27)); fte=rng.choice([1.0,1.0,1.0,.8,.5]); employees.append(dict(id=emp,name=f'Synthetic Employee {i:05d}',role_id=role['id'],level_id=lev['id'],location_id=loc['id'],hire_date=hire.isoformat(),employment_status='ACTIVE',fte=fte))
  band=next(b for b in bands if b['role_id']==role['id'] and b['level_id']==lev['id'] and b['location_id']==loc['id']); midpoint=band['midpoint']; start=max(2024,hire_year)
  base=(midpoint/loc['fx_to_inr'])*rng.uniform(.78,1.16)
  for yr in range(start,2027):
   eff=f'{yr}-01-01'; salary=base*(1.04**(yr-start)); fte_year=fte if not (yr==2025 and i%41==0) else .8
   if yr==2025 and i%53==0: salary*=1.12
   currency=loc['currency']; fx=loc['fx_to_inr']; record_salary=salary
   if yr==2025 and i%67==0:
    currency='USD'; record_salary=salary*fx/83.0; fx=83.0
   annualized=record_salary*fx/fte_year
   issue=''
   if i%997==0 and yr==2026: annualized*=.62; issue='UNEXPLAINED_OUTLIER'
   if i%991==0 and yr==2026: annualized=record_salary*fx; issue='FTE_IGNORED'
   sid=f'SAL-{emp}-{yr}-01'
   reason='CURRENCY_CHANGE' if yr==2025 and i%67==0 else ('PART_TIME_CHANGE' if yr==2025 and i%41==0 else ('ANNUAL_REVIEW' if yr>start else 'INITIAL'))
   salaries.append(dict(id=sid,employee_id=emp,effective_date=eff,base_salary=round(record_salary,2),currency=currency,fte=fte_year,annualized_inr=round(annualized,2),band_id=band['id'],change_reason=reason,issue_type=issue))
   if issue: truth.append(dict(record_id=sid,employee_id=emp,issue_type=issue,expected_decision='FLAG_FOR_HUMAN_REVIEW',reason='Synthetic salary deliberately placed materially below comparable baseline'))
  years=max(0,(date(2026,1,1)-hire).days/365.25); tenures.append(dict(id=f'TEN-{emp}-2026',employee_id=emp,as_of_date='2026-01-01',years=round(years,2)))
  performance.append(dict(id=f'PERF-{emp}-2025',employee_id=emp,period_start='2025-01-01',period_end='2025-12-31',rating=rng.choice([2.5,3,3.5,4,4.5,5]),evidence_note='Synthetic annual performance evidence'))
  if i%19==0 and lev['rank']<5:
   nxt=levels[lev['rank']]; promotions.append(dict(id=f'PROM-{emp}-2025',employee_id=emp,from_level_id=lev['id'],to_level_id=nxt['id'],effective_date='2025-07-01',approved_by='SYNTHETIC-MANAGER'))
 # Five deliberate labelled exception classes; keep them explicit and isolated in exception fixtures.
 exceptions=[dict(case_id='EX-001',issue_type='EXPIRED_BAND',description='Salary effective date is after band expiry',expected='Do not use expired band; flag missing effective band'),dict(case_id='EX-002',issue_type='FTE_IGNORED',description='Raw salary is compared without annualizing for FTE',expected='Normalize salary to 1.0 FTE before comparison'),dict(case_id='EX-003',issue_type='FX_MISSING',description='Foreign currency salary lacks a valid FX rate',expected='Quarantine comparison; do not assume INR parity'),dict(case_id='EX-004',issue_type='UNAPPROVED_ADJUSTMENT',description='Adjustment is marked applied without approval',expected='Flag lifecycle violation; require approval trail'),dict(case_id='EX-005',issue_type='INCOMPARABLE_GROUP',description='Different role families are grouped without rationale',expected='Reject group or require documented comparability rationale')]
 # Isolated negative fixtures use real generated parent IDs but are not loaded as normal feature rows.
 fixtures=[]
 e0,e1,e2,e3,e4=employees[:5]
 fixtures.append(dict(case_id='EX-001',entity_type='SalaryRecord',record_id='FIX-SAL-EXPIRED-001',employee_id=e0['id'],issue_type='EXPIRED_BAND',payload_json=json.dumps({'effective_date':'2026-06-01','band_id':'FIX-BAND-EXPIRED-001','band_effective_from':'2023-01-01','band_effective_to':'2024-12-31'}),expected_decision='Reject expired band; flag for current effective band lookup'))
 fixtures.append(dict(case_id='EX-002',entity_type='SalaryRecord',record_id='FIX-SAL-FTE-001',employee_id=e1['id'],issue_type='FTE_IGNORED',payload_json=json.dumps({'base_salary':500000,'currency':'INR','fte':0.5,'annualized_inr_incorrect':500000,'annualized_inr_expected':1000000}),expected_decision='Flag normalization reconciliation failure'))
 fixtures.append(dict(case_id='EX-003',entity_type='SalaryRecord',record_id='FIX-SAL-FX-001',employee_id=e2['id'],issue_type='CURRENCY_CONVERSION_MISSING',payload_json=json.dumps({'base_salary':40000,'currency':'XXX','fte':1.0,'annualized_inr':None}),expected_decision='Quarantine comparison; do not assume an FX rate'))
 fixtures.append(dict(case_id='EX-004',entity_type='AdjustmentProposal',record_id='FIX-ADJ-UNAPPROVED-001',employee_id=e3['id'],issue_type='UNAPPROVED_ADJUSTMENT',payload_json=json.dumps({'status':'APPLIED','manager_approved_by':None,'hr_approved_by':None}),expected_decision='Flag illegal lifecycle transition; require approval evidence'))
 fixtures.append(dict(case_id='EX-005',entity_type='ComparableGroup',record_id='FIX-GROUP-INCOMPARABLE-001',employee_id=e4['id'],issue_type='INCOMPARABLE_GROUP',payload_json=json.dumps({'member_role_id_a':e4['role_id'],'member_role_id_b':e0['role_id'],'rationale':''}),expected_decision='Reject grouping or require documented job-related rationale'))
 truth.extend([dict(record_id=x['record_id'],employee_id=x['employee_id'],issue_type=x['issue_type'],expected_decision=x['expected_decision'],reason=x['payload_json']) for x in fixtures])
 tables={'edge_case_fixtures':fixtures,'roles':roles,'levels':levels,'locations':locs,'compensation_bands':bands,'employees':employees,'salary_records':salaries,'performance_evidence':performance,'tenure':tenures,'promotions':promotions,'ground_truth':truth,'negative_scenarios':exceptions}
 for name,rows in tables.items(): write_csv(out/f'{name}.csv',rows); (out/f'{name}.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
 manifest={'seed':seed,'employees':n,'salary_history_years':3,'synthetic_only':True,'files':{}}
 for p in sorted(out.glob('*.csv')): manifest['files'][p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':sum(1 for _ in open(p,encoding='utf-8'))-1}
 (out/'source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 print(json.dumps(manifest,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--employees',type=int,default=5000); p.add_argument('--out',default='../data/generated'); p.add_argument('--seed',type=int,default=SEED); a=p.parse_args(); generate(a.employees,a.out,a.seed)
