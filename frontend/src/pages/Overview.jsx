import {useEffect,useMemo,useState} from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  BriefcaseBusiness,
  Check,
  CheckCircle2,
  ClipboardCheck,
  FileSpreadsheet,
  LoaderCircle,
  Play,
  Scale,
  Users,
} from 'lucide-react';
import {api} from '../services/api';

const metrics=[
  {key:'employees',label:'Employees',Icon:Users},
  {key:'salary_records',label:'Salary records',Icon:FileSpreadsheet},
  {key:'proposals_pending',label:'Pending reviews',Icon:ClipboardCheck},
  {key:'role_level_combinations',label:'Role/level combinations',Icon:BriefcaseBusiness},
];

const stages=[
  {key:'data_quality',label:'Data quality validation'},
  {key:'normalization',label:'Currency and FTE normalization'},
  {key:'band_compliance',label:'Effective-dated band compliance'},
  {key:'comparability',label:'Comparable-group construction'},
  {key:'disparity',label:'Pay disparity and anomaly detection'},
  {key:'recommendation',label:'Evidence-backed adjustment proposals'},
];

const numberFormat=new Intl.NumberFormat('en-US');
const currencyFormat=new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0});

function formatNumber(value){
  return value!==null&&value!==undefined&&value!==''&&Number.isFinite(Number(value))?numberFormat.format(Number(value)):'—';
}

function formatCurrency(value){
  return value!==null&&value!==undefined&&value!==''&&Number.isFinite(Number(value))?currencyFormat.format(Number(value)):'—';
}

function formatPercent(count,total){
  if(!total||!count)return '0%';
  const percentage=count/total*100;
  return percentage<1?'<1%':`${Math.round(percentage)}%`;
}

function sampleLabel(agent,sample){
  if(agent==='data_quality')return `${sample.employee_id} · ${sample.issue}`;
  if(agent==='normalization')return `${sample.employee_id} · ${formatCurrency(sample.normalized_salary_inr)} normalized`;
  if(agent==='band_compliance'){
    if(sample.issue)return `${sample.employee_id} · ${sample.issue}`;
    return `${sample.employee_id} · compa-ratio ${sample.compa_ratio??'—'} · band position ${sample.band_position??'—'}`;
  }
  if(agent==='comparability')return `${sample.role_id} / ${sample.level_id} / ${sample.location_id} / ${sample.year} · ${formatNumber(sample.record_count)} records`;
  if(agent==='disparity')return `${sample.employee_id} · ${sample.gap_pct??'—'}% below group median`;
  return `${sample.employee_id} · proposed ${formatCurrency(sample.proposed_amount_inr)}`;
}

function ActivityItem({item}){
  const date=item.created_at?new Date(item.created_at):null;
  const stamp=date&&!Number.isNaN(date.getTime())?date.toLocaleString():'';
  return <div className="overview-activity-item">
    <span className="overview-activity-icon">{item.event_type==='CREATED'?<Check size={17}/>:<Activity size={17}/>}</span>
    <div><strong>{item.event_type.replaceAll('_',' ')}</strong><p>{item.details||item.entity_id}</p></div>
    {stamp&&<time>{stamp}</time>}
  </div>;
}

export default function Overview({onHistoryRangeChange}){
  const [dashboard,setDashboard]=useState(null);
  const [dashboardError,setDashboardError]=useState('');
  const [analysis,setAnalysis]=useState(null);
  const [analysisError,setAnalysisError]=useState('');
  const [running,setRunning]=useState(false);
  const [selectedAgent,setSelectedAgent]=useState(null);
  const [showAllFamilies,setShowAllFamilies]=useState(false);

  const refreshDashboard=async()=>{
    try{
      const data=await api.dashboard();
      setDashboard(data);
      onHistoryRangeChange?.({start:data.salary_history_start,end:data.salary_history_end});
      setDashboardError('');
    }catch(error){
      setDashboardError(error.message);
    }
  };

  useEffect(()=>{refreshDashboard()},[]);

  const runAnalysis=async()=>{
    setRunning(true);
    setAnalysisError('');
    try{
      const result=await api.analysis();
      setAnalysis(result);
      setSelectedAgent('data_quality');
      setRunning(false);
      await refreshDashboard();
    }catch(error){
      setAnalysisError(error.message);
    }finally{
      setRunning(false);
    }
  };

  const distribution=dashboard?.latest_salary_distribution;
  const categories=[
    {key:'below',label:'Below band',color:'#f18b74'},
    {key:'within',label:'Within band',color:'#8a49f5'},
    {key:'above',label:'Above band',color:'#15b9c9'},
  ];
  const distributionTotal=distribution?.total||0;
  const distributionStyle=distributionTotal?{
    background:`conic-gradient(${categories.map((category,index)=>{
      const start=categories.slice(0,index).reduce((sum,item)=>sum+(distribution[item.key]||0),0)/distributionTotal*100;
      const end=(start*distributionTotal/100+(distribution[category.key]||0))/distributionTotal*100;
      return `${category.color} ${start}% ${end}%`;
    }).join(', ')})`,
  }:undefined;
  const roleFamilies=dashboard?.compensation_by_role_family||[];
  const maxFamilySalary=Math.max(...roleFamilies.map(item=>item.average_salary_inr||0),0);
  const visibleRoleFamilies=showAllFamilies
    ?roleFamilies
    :[...roleFamilies].sort((a,b)=>b.employee_count-a.employee_count).slice(0,4);
  const outputsByAgent=Object.fromEntries((analysis?.agent_outputs||[]).map(output=>[output.agent,output]));
  const selectedOutput=selectedAgent?outputsByAgent[selectedAgent]:null;
  const selectedStage=stages.find(stage=>stage.key===selectedAgent);

  const insights=useMemo(()=>{
    if(!analysis)return [];
    const gaps=(analysis.disparity_findings||[]).map(item=>item.gap_pct).filter(Number.isFinite).sort((a,b)=>a-b);
    const medianGap=gaps.length?gaps[Math.floor(gaps.length/2)]:0;
    const roleIds=new Set((analysis.disparity_findings||[]).map(item=>item.group?.[0]).filter(Boolean));
    const outside=(distribution?.below||0)+(distribution?.above||0);
    return [
      {label:'Median flagged pay gap',value:`${medianGap.toFixed(1)}%`,Icon:Activity},
      {label:'Latest salaries outside band',value:formatNumber(outside),Icon:AlertTriangle},
      {label:'Roles with disparity findings',value:formatNumber(roleIds.size),Icon:Scale},
    ];
  },[analysis,distribution]);

  return <div className="overview-page">
    <section className="overview-hero">
      <div className="overview-hero-icon"><Scale size={43}/></div>
      <div className="overview-hero-copy">
        <h2>Compensation, with context.</h2>
        <p>Understand pay positioning, identify exceptions and ensure pay equity.</p>
      </div>
      <button className="overview-run-button" onClick={runAnalysis} disabled={running}>
        {running?<LoaderCircle className="overview-spinner" size={17}/>:<Play size={17}/>}
        {running?'Running…':'Run Analysis'}
      </button>
    </section>

    {dashboardError&&<div className="error">Dashboard data could not be loaded: {dashboardError}</div>}
    {analysisError&&<div className="error">Compensation analysis failed: {analysisError}</div>}

    <section className="overview-metrics" aria-label="Live dashboard metrics">
      {metrics.map(({key,label,Icon})=><article className="overview-metric" key={key}>
        <div className={`overview-metric-icon overview-metric-${key}`}><Icon size={20}/></div>
        <span>{label}</span>
        <strong>{dashboard?formatNumber(dashboard[key]):'—'}</strong>
        {key==='role_level_combinations'&&dashboard&&<small>{formatNumber(dashboard.roles)} roles · {formatNumber(dashboard.levels)} levels</small>}
      </article>)}
    </section>

    <section className="overview-dashboard-grid">
      <article className="overview-panel overview-distribution">
        <div className="overview-panel-heading">
          <div><h3>Salary Distribution</h3><p>Latest salary compared with effective bands</p></div>
          <Scale size={18}/>
        </div>
        {distributionTotal>0?<div className="overview-donut-layout">
          <div className="overview-donut" style={distributionStyle}>
            <div><strong>{formatNumber(distributionTotal)}</strong><span>Employees</span></div>
          </div>
          <div className="overview-legend">
            {categories.map(category=><div className="overview-legend-row" key={category.key}>
              <i style={{'--legend-color':category.color}}/>
              <span>{category.label}</span>
              <strong>{formatNumber(distribution[category.key])}</strong>
              <small>{formatPercent(distribution[category.key]||0,distributionTotal)}</small>
            </div>)}
          </div>
        </div>:<div className="overview-empty">{dashboard?'No latest salaries have a valid effective band.':'Loading salary band data…'}</div>}
        {distribution?.without_effective_band>0&&<small className="overview-panel-note">{formatNumber(distribution.without_effective_band)} without an effective band · {formatNumber(distribution.without_conversion)} without currency conversion</small>}
      </article>

      <article className="overview-panel overview-family-panel">
        <div className="overview-panel-heading">
          <div><h3>Compensation by Role Family</h3><p>Average normalized pay for latest salary records</p></div>
          {roleFamilies.length>4
            ?<button className="overview-link-button" onClick={()=>setShowAllFamilies(!showAllFamilies)}>{showAllFamilies?'Top 4':'View all'} <ArrowUpRight size={12}/></button>
            :<BriefcaseBusiness size={18}/>}
        </div>
        {visibleRoleFamilies.length?<div className={`overview-family-chart ${showAllFamilies?'is-expanded':''}`}>
          {visibleRoleFamilies.map(item=><div className="overview-family-column" key={item.family} title={`${item.family}: ${formatCurrency(item.average_salary_inr)} across ${formatNumber(item.employee_count)} employees`}>
            <strong>₹{(item.average_salary_inr/100000).toFixed(1)}L</strong>
            <div className="overview-family-bar" style={{height:`${Math.max(8,(item.average_salary_inr/maxFamilySalary)*100)}%`}}/>
            <span>{item.family}</span>
          </div>)}
        </div>:<div className="overview-empty">{dashboard?'No normalized salary records are available.':'Loading role-family compensation…'}</div>}
      </article>

      <article className="overview-panel overview-workflow">
        <div className="overview-panel-heading">
          <div><h3>Analysis Workflow</h3><p>Six specialized agents, one auditable decision path</p></div>
          <span className={`overview-workflow-status ${analysis?'is-complete':''}`}>{running?'Running':analysis?'Completed':dashboardError?'Unavailable':dashboard?'System ready':'Connecting'}</span>
        </div>
        <div className="overview-stage-list">
          {stages.map((stage,index)=>{
            const output=outputsByAgent[stage.key];
            const active=selectedAgent===stage.key;
            return <button className={`overview-stage-row ${active?'is-selected':''}`} key={stage.key} onClick={()=>output&&setSelectedAgent(stage.key)} disabled={!output}>
              <span className={`overview-stage-number ${output?'is-complete':''}`}>{output?<Check size={12}/>:index+1}</span>
              <span className="overview-stage-name">{stage.label}</span>
              <span className="overview-stage-result">{output?`${formatNumber(output.output_count)} outputs`:analysis?'Completed':dashboard?'Ready':'—'}</span>
              {output&&<CheckCircle2 size={15} className="overview-stage-check"/>}
            </button>;
          })}
        </div>
        <button className="overview-run-workflow" onClick={runAnalysis} disabled={running}>
          {running?<LoaderCircle className="overview-spinner" size={15}/>:<Play size={15}/>}
          {running?'Running…':'Run Compensation Analysis'}
        </button>
      </article>
    </section>

    <section className="overview-bottom-grid">
      <article className="overview-panel overview-key-insights">
        <div className="overview-panel-heading">
          <div><h3>Key Insights</h3><p>{analysis?'Derived from the latest agent run':'Run the analysis to calculate findings'}</p></div>
          {analysis&&<span className="overview-link-label">LATEST RUN <ArrowUpRight size={13}/></span>}
        </div>
        {analysis?<div className="overview-insight-grid">
          {insights.map(({label,value,Icon})=><div className="overview-insight-card" key={label}>
            <Icon size={17}/><strong>{value}</strong><span>{label}</span>
          </div>)}
        </div>:<div className="overview-empty overview-insight-empty">Analysis insights appear here after the pipeline runs.</div>}
      </article>

      <article className="overview-panel overview-activity-panel">
        <div className="overview-panel-heading">
          <div><h3>Recent Activity</h3><p>Recorded proposal and review events</p></div>
          <Activity size={18}/>
        </div>
        {dashboard?.recent_activity?.length?<div className="overview-activity-list">
          {dashboard.recent_activity.slice(0,2).map(item=><ActivityItem key={`${item.entity_id}-${item.event_type}`} item={item}/>)}
        </div>:<div className="overview-empty overview-activity-empty">{dashboard?'No review activity has been recorded yet.':'Loading activity…'}</div>}
      </article>
    </section>

    {analysis&&selectedOutput&&<section className="overview-panel overview-agent-output">
      <div className="overview-panel-heading">
        <div><h3>Agent Output</h3><p>Select an agent to inspect its latest results.</p></div>
        <span className="overview-workflow-status is-complete">{formatNumber(analysis.agent_outputs?.length)} AGENTS COMPLETED</span>
      </div>
      <div className="overview-agent-tabs">
        {stages.map(stage=><button className={selectedAgent===stage.key?'is-selected':''} key={stage.key} onClick={()=>setSelectedAgent(stage.key)}>{stage.label}</button>)}
      </div>
      <div className="overview-agent-output-summary">
        <div><strong>{selectedStage?.label}</strong><span>{formatNumber(selectedOutput.output_count)} outputs</span></div>
        <p>{selectedOutput.summary}</p>
        {selectedOutput.sample?.length>0&&<ul>{selectedOutput.sample.map((sample,index)=><li key={`${selectedAgent}-${sample.employee_id||sample.role_id||index}-${index}`}>{sampleLabel(selectedAgent,sample)}</li>)}</ul>}
        {selectedOutput.output_count>selectedOutput.sample?.length&&<small>Showing {selectedOutput.sample?.length||0} sample outputs.</small>}
      </div>
    </section>}

    {analysis&&<p className="overview-review-note">A flagged difference is a prompt for investigation, not proof of unfair treatment. Review contextual evidence and human approvals before acting.</p>}
  </div>;
}
