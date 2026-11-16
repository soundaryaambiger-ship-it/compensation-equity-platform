from app.agents.agents import DataQualityAgent,NormalizationAgent,BandComplianceAgent,ComparabilityAgent,DisparityAgent,RecommendationAgent
class CompensationOrchestrator:
 def __init__(self): self.agents=[DataQualityAgent(),NormalizationAgent(),BandComplianceAgent(),ComparabilityAgent(),DisparityAgent(),RecommendationAgent()]
 def run(self, records):
  context={'records':records}; trace=[]
  for agent in self.agents:
   result=agent.run(context); context.update(result); trace.append({'agent':agent.name,'output_count':sum(len(v) for v in result.values() if isinstance(v,(list,dict)))})
  context['trace']=trace
  return context
