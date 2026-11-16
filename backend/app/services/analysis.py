from sqlalchemy.orm import Session
from app.models.entities import Employee,SalaryRecord,CompensationBand,PerformanceEvidence,Tenure,Promotion
from app.agents.orchestrator import CompensationOrchestrator
from datetime import date

def run_analysis(db:Session):
 rows=db.query(Employee,SalaryRecord).join(SalaryRecord,SalaryRecord.employee_id==Employee.id).all()
 bands=db.query(CompensationBand).all()
 band_index={}
 for band in bands: band_index.setdefault((band.role_id,band.level_id,band.location_id),[]).append(band)
 performance=db.query(PerformanceEvidence).all(); perf_index={}
 for item in performance: perf_index[item.employee_id]=item.rating
 tenure=db.query(Tenure).all(); tenure_index={item.employee_id:item.years for item in tenure}
 promotions=db.query(Promotion).all(); promotion_index={}
 for item in promotions: promotion_index.setdefault(item.employee_id,[]).append(str(item.effective_date))
 records=[]
 for e,s in rows:
  candidates=[x for x in band_index.get((e.role_id,e.level_id,e.location_id),[]) if x.effective_from<=s.effective_date and (x.effective_to is None or x.effective_to>=s.effective_date)]
  b=sorted(candidates,key=lambda x:x.effective_from,reverse=True)[0] if candidates else None
  fx_missing=s.annualized_inr is None
  fx=(s.annualized_inr/s.base_salary*s.fte) if (s.annualized_inr is not None and s.base_salary) else 1.0
  records.append({'employee_id':e.id,'role_id':e.role_id,'level_id':e.level_id,'location_id':e.location_id,'salary':s.base_salary,'fx':fx,'fte':s.fte,'issue_type':s.issue_type,'performance_rating':perf_index.get(e.id),'tenure_years':tenure_index.get(e.id),'promotion_dates':promotion_index.get(e.id,[]),'date':s.effective_date,'fx_missing':fx_missing,'band':({'min':b.minimum,'midpoint':b.midpoint,'max':b.maximum,'from':b.effective_from,'to':b.effective_to} if b else None)})
 return CompensationOrchestrator().run(records)
