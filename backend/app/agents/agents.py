from app.agents.base import Agent
class DataQualityAgent(Agent):
 name='data_quality'
 def run(self,c):
  issues=[]
  for r in c['records']:
   if r['fte']<=0 or r['fte']>1: issues.append({'employee_id':r['employee_id'],'issue':'INVALID_FTE'})
   if r.get('issue_type')=='FTE_IGNORED': issues.append({'employee_id':r['employee_id'],'issue':'FTE_IGNORED'})
   if r.get('fx_missing'): issues.append({'employee_id':r['employee_id'],'issue':'CURRENCY_CONVERSION_MISSING'})
  return {'quality_issues':issues}
class NormalizationAgent(Agent):
 name='normalization'
 def run(self,c):
  out=[]
  for r in c['records']:
   x=dict(r); x['normalized_salary_inr']=None if x.get('fx_missing') else x['salary']*x['fx']/(x['fte'] or 1)
   out.append(x)
  return {'normalized_records':out}
class BandComplianceAgent(Agent):
 name='band_compliance'
 def run(self,c):
  findings=[]
  for r in c['normalized_records']:
   b=r.get('band')
   if not b: findings.append({'employee_id':r['employee_id'],'issue':'NO_EFFECTIVE_BAND','effective_date':str(r['date'])})
   elif b and (r['date']<b['from'] or (b.get('to') and r['date']>b['to'])): findings.append({'employee_id':r['employee_id'],'issue':'EXPIRED_BAND'})
   elif b and r.get('normalized_salary_inr') is not None:
    s=r['normalized_salary_inr']; findings.append({'employee_id':r['employee_id'],'compa_ratio':round(s/b['midpoint'],3),'band_position':round((s-b['min'])/(b['max']-b['min']),3) if b['max']>b['min'] else None})
  return {'band_findings':findings}
class ComparabilityAgent(Agent):
 name='comparability'
 def run(self,c):
  groups={}
  for r in c['normalized_records']:
   key=(r['role_id'],r['level_id'],r['location_id'],str(r['date'])[:4]); groups.setdefault(key,[]).append(r)
  return {'comparable_groups':groups}
class DisparityAgent(Agent):
 name='disparity'
 def run(self,c):
  findings=[]
  for key,rows in c['comparable_groups'].items():
   vals=[r['normalized_salary_inr'] for r in rows if r.get('normalized_salary_inr') is not None]
   if len(vals)<3: continue
   median=sorted(vals)[len(vals)//2]
   for r in rows:
    s=r.get('normalized_salary_inr')
    if s is not None and median and s<median*.80: findings.append({'employee_id':r['employee_id'],'issue':'POTENTIAL_UNEXPLAINED_GAP','group':key,'group_median_inr':round(median,2),'salary_inr':round(s,2),'gap_pct':round((median-s)/median*100,1),'contextual_factors':{'performance_rating':r.get('performance_rating'),'tenure_years':r.get('tenure_years'),'promotion_dates':r.get('promotion_dates',[]),'fte':r.get('fte'),'effective_date':str(r.get('date'))}})
  return {'disparity_findings':findings}
class RecommendationAgent(Agent):
 name='recommendation'
 def run(self,c):
  proposals=[]
  for f in c['disparity_findings']:
   proposals.append({'employee_id':f['employee_id'],'proposed_amount_inr':round(f['group_median_inr']-f['salary_inr'],2),'reason':'Review potential gap against comparable-group median; validate documented factors before action.','evidence':f,'status':'PENDING_HUMAN_REVIEW'})
  return {'review_proposals':proposals}
