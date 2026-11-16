import {useEffect,useState} from 'react';
import {LayoutDashboard,Users,Scale,AlertTriangle,ClipboardCheck,Sun,Moon,ChevronLeft,CalendarDays} from 'lucide-react';
import Assistant from './Assistant';
import {api} from '../services/api';

const items=[['Overview',LayoutDashboard],['Employees',Users],['Comparisons',Scale],['Anomalies',AlertTriangle],['Approvals',ClipboardCheck]];
export default function Layout({page,setPage,children,overviewPeriod}){
  const [collapsed,setCollapsed]=useState(false);
  const [dark,setDark]=useState(true);
  const [connection,setConnection]=useState('Checking…');

  useEffect(()=>{
    let active=true;
    const check=()=>api.health()
      .then(result=>{if(active)setConnection(result.status==='ok'?'Connected':'Unavailable')})
      .catch(()=>{if(active)setConnection('Unavailable')});
    check();
    const timer=setInterval(check,30000);
    return ()=>{active=false;clearInterval(timer)};
  },[]);

  return <div className={`${dark?'app dark':'app'} ${page==='Overview'?'app-overview':''}`}>
    <aside className={collapsed?'sidebar collapsed':'sidebar'}>
      <div className="brand">
        <div className="brand-mark">CE</div>
        {!collapsed&&<div><b>EquityIQ</b><small>COMPENSATION INTELLIGENCE</small></div>}
      </div>
      <button className="collapse" onClick={()=>setCollapsed(!collapsed)} aria-label={collapsed?'Expand navigation':'Collapse navigation'}><ChevronLeft size={17}/></button>
      <nav>{items.map(([label,Icon])=><button key={label} className={page===label?'nav-item active':'nav-item'} onClick={()=>setPage(label)} title={label}><Icon size={18}/>{!collapsed&&label}</button>)}</nav>
      <div className="side-bottom">
        <button className="nav-item" onClick={()=>setDark(!dark)}>{dark?<Sun size={18}/>:<Moon size={18}/>} {!collapsed&&(dark?'Light theme':'Dark theme')}</button>
        <div className="user"><div className="avatar">HR</div>{!collapsed&&<div><b>HR Workspace</b><small>Administrator</small></div>}</div>
      </div>
    </aside>
    <main className="main">
      <header className={`topbar ${page==='Overview'?'topbar-overview':''}`}>
        <div><span className="eyebrow">PEOPLE ANALYTICS / {page.toUpperCase()}</span><h1>{page}</h1>{page==='Overview'&&<p className="topbar-subtitle">Compensation equity insights for a fairer workplace</p>}</div>
        <div className="top-actions">
          {page==='Overview'&&overviewPeriod?.start&&overviewPeriod?.end&&<span className="overview-period"><CalendarDays size={14}/>{overviewPeriod.start.slice(0,4)}–{overviewPeriod.end.slice(0,4)}</span>}
          <span className={connection==='Connected'?'live-dot':'live-dot offline'}>● {connection}</span>
        </div>
      </header>
      <section className={`content ${page==='Overview'?'content-overview':''}`}>{children}</section>
      <Assistant/>
    </main>
  </div>;
}
