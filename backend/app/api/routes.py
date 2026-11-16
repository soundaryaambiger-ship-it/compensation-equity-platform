from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_,func
from app.db.session import get_db
from app.models.entities import Employee,Role,Level,Location,SalaryRecord,CompensationBand,AdjustmentProposal,AuditEvent
from app.schemas.assistant import AssistantChatRequest
from app.services.assistant import answer_question
from app.services.analysis import run_analysis
import json
router=APIRouter()

def _agent_outputs(result):
 normalized=result.get('normalized_records',[])
 groups=result.get('comparable_groups',{})
 quality=sorted(result.get('quality_issues',[]),key=lambda item:(item.get('employee_id',''),item.get('issue','')))
 bands=sorted(result.get('band_findings',[]),key=lambda item:(item.get('employee_id',''),item.get('issue','')))
 disparities=sorted(result.get('disparity_findings',[]),key=lambda item:(item.get('employee_id',''),item.get('issue','')))
 proposals=sorted(result.get('review_proposals',[]),key=lambda item:item.get('employee_id',''))
 sorted_groups=sorted(groups.items(),key=lambda item:tuple(str(value) for value in item[0]))
 missing_currency=sum(1 for item in normalized if item.get('normalized_salary_inr') is None)
 return [
  {'agent':'data_quality','output_count':len(quality),'summary':f'{len(quality):,} quality exceptions found.','sample':quality[:5]},
  {'agent':'normalization','output_count':len(normalized),'summary':f'{len(normalized):,} salary records processed; {missing_currency:,} lack a normalized INR value.','sample':[{'employee_id':item['employee_id'],'date':str(item['date']),'normalized_salary_inr':item.get('normalized_salary_inr')} for item in sorted(normalized,key=lambda item:(item.get('employee_id',''),str(item.get('date',''))))[:5]]},
  {'agent':'band_compliance','output_count':len(bands),'summary':f'{len(bands):,} band findings produced.','sample':bands[:5]},
  {'agent':'comparability','output_count':len(groups),'summary':f'{len(groups):,} comparable groups formed from {sum(len(rows) for rows in groups.values()):,} records.','sample':[{'role_id':key[0],'level_id':key[1],'location_id':key[2],'year':key[3],'record_count':len(rows)} for key,rows in sorted_groups[:5]]},
  {'agent':'disparity','output_count':len(disparities),'summary':f'{len(disparities):,} potential disparity findings produced.','sample':disparities[:5]},
  {'agent':'recommendation','output_count':len(proposals),'summary':f'{len(proposals):,} evidence-backed review proposals produced.','sample':proposals[:5]},
 ]

def _dashboard_compensation_summary(db):
 latest_salary=db.query(
  SalaryRecord.employee_id.label('employee_id'),
  func.max(SalaryRecord.effective_date).label('effective_date')
 ).group_by(SalaryRecord.employee_id).subquery()
 rows=db.query(Employee,SalaryRecord,Role.family).join(
  SalaryRecord,SalaryRecord.employee_id==Employee.id
 ).join(
  latest_salary,and_(
   latest_salary.c.employee_id==SalaryRecord.employee_id,
   latest_salary.c.effective_date==SalaryRecord.effective_date
  )
 ).join(Role,Role.id==Employee.role_id).all()
 bands_by_key={}
 for band in db.query(CompensationBand).all():
  key=(band.role_id,band.level_id,band.location_id)
  bands_by_key.setdefault(key,[]).append(band)
 distribution={'below':0,'within':0,'above':0,'without_effective_band':0,'without_conversion':0,'total':0}
 family_totals={}
 as_of=None
 for employee,salary,family in rows:
  if as_of is None or salary.effective_date>as_of: as_of=salary.effective_date
  amount=salary.annualized_inr
  if amount is None:
   distribution['without_conversion']+=1
   continue
  family_totals.setdefault(family,[]).append(amount)
  candidates=[
   band for band in bands_by_key.get((employee.role_id,employee.level_id,employee.location_id),[])
   if band.effective_from<=salary.effective_date and (band.effective_to is None or band.effective_to>=salary.effective_date)
  ]
  if not candidates:
   distribution['without_effective_band']+=1
   continue
  band=max(candidates,key=lambda item:item.effective_from)
  if band.maximum<=band.minimum:
   distribution['without_effective_band']+=1
   continue
  position=(amount-band.minimum)/(band.maximum-band.minimum)
  distribution['total']+=1
  if position<0: distribution['below']+=1
  elif position>1: distribution['above']+=1
  else: distribution['within']+=1
 families=[
  {'family':family,'average_salary_inr':round(sum(values)/len(values),2),'employee_count':len(values)}
  for family,values in sorted(family_totals.items())
 ]
 history=db.query(func.min(SalaryRecord.effective_date),func.max(SalaryRecord.effective_date)).one()
 recent_activity=[
  {'event_type':event.event_type,'entity_id':event.entity_id,'actor':event.actor,'created_at':event.created_at.isoformat() if event.created_at else None,'details':event.details}
  for event in db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(4).all()
 ]
 return {
  'latest_salary_distribution':distribution,
  'compensation_by_role_family':families,
  'salary_history_start':history[0].isoformat() if history[0] else None,
  'salary_history_end':history[1].isoformat() if history[1] else None,
  'latest_salary_as_of':as_of.isoformat() if as_of else None,
  'recent_activity':recent_activity
 }

@router.get('/health')
def health(): return {'status':'ok'}
@router.post('/assistant/chat')
def assistant_chat(payload:AssistantChatRequest,db:Session=Depends(get_db)):
 return {'answer':answer_question(payload.question,db)}
@router.get('/dashboard')
def dashboard(db:Session=Depends(get_db)):
 return {'employees':db.query(func.count(Employee.id)).scalar() or 0,'salary_records':db.query(func.count(SalaryRecord.id)).scalar() or 0,'proposals_pending':db.query(func.count(AdjustmentProposal.id)).filter(AdjustmentProposal.status=='PENDING').scalar() or 0,'roles':db.query(func.count(Role.id)).scalar() or 0,'levels':db.query(func.count(Level.id)).scalar() or 0,'locations':db.query(func.count(Location.id)).scalar() or 0,'role_level_combinations':db.query(CompensationBand.role_id,CompensationBand.level_id).distinct().count(),**_dashboard_compensation_summary(db)}
@router.get('/employees')
def employees(skip:int=0,limit:int=100,db:Session=Depends(get_db)):
 rows=db.query(Employee).offset(skip).limit(min(limit,500)).all()
 return [{'id':e.id,'name':e.name,'role_id':e.role_id,'level_id':e.level_id,'location_id':e.location_id,'hire_date':str(e.hire_date),'fte':e.fte,'status':e.employment_status} for e in rows]
@router.get('/analysis')
def analysis(db:Session=Depends(get_db)):
 result=run_analysis(db)
 # Persist proposals as immutable review records; avoid duplicating pending proposals on repeated analysis runs.
 existing={p.employee_id for p in db.query(AdjustmentProposal).filter(AdjustmentProposal.status=='PENDING').all()}
 seq=db.query(AdjustmentProposal).count()+1
 for item in result['review_proposals']:
  if item['employee_id'] in existing: continue
  pid=f'ADJ-2026-{seq:06d}'; seq+=1
  db.add(AdjustmentProposal(id=pid,employee_id=item['employee_id'],proposed_amount_inr=item['proposed_amount_inr'],reason=item['reason'],evidence_json=json.dumps(item['evidence']),status='PENDING'))
  existing.add(item['employee_id'])
  db.add(AuditEvent(id=f'EVT-{pid}-CREATED',entity_type='AdjustmentProposal',entity_id=pid,event_type='CREATED',actor='analysis-orchestrator',details='Created from reproducible compensation analysis'))
 db.commit()
 return {'quality_issues':result['quality_issues'],'band_findings':result['band_findings'],'disparity_findings':result['disparity_findings'],'review_proposals':result['review_proposals'],'trace':result['trace'],'agent_outputs':_agent_outputs(result)}
@router.get('/proposals')
def proposals(db:Session=Depends(get_db)):
 return [{'id':p.id,'employee_id':p.employee_id,'amount_inr':p.proposed_amount_inr,'reason':p.reason,'status':p.status,'evidence':json.loads(p.evidence_json)} for p in db.query(AdjustmentProposal).order_by(AdjustmentProposal.created_at.desc()).limit(500)]
@router.post('/proposals/{proposal_id}/decision')
def decision(proposal_id:str,decision:str,actor:str='hr-reviewer',db:Session=Depends(get_db)):
 if decision not in ['APPROVED','REJECTED']: raise HTTPException(400,'Decision must be APPROVED or REJECTED')
 p=db.get(AdjustmentProposal,proposal_id)
 if not p: raise HTTPException(404,'Proposal not found')
 if p.status!='PENDING': raise HTTPException(409,'Only pending proposals can be decided')
 p.status=decision; p.hr_approved_by=actor
 db.add(AuditEvent(id=f'EVT-{proposal_id}-{decision}',entity_type='AdjustmentProposal',entity_id=p.id,event_type=decision,actor=actor,details=f'HR decision: {decision}'))
 db.commit(); return {'id':p.id,'status':p.status}
