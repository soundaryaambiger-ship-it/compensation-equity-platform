import {useState} from 'react';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import Employees from './pages/Employees';
import Analysis from './pages/Analysis';
import Approvals from './pages/Approvals';

export default function App(){
  const [page,setPage]=useState('Overview');
  const [overviewPeriod,setOverviewPeriod]=useState(null);
  const content=page==='Overview'
    ?<Overview onHistoryRangeChange={setOverviewPeriod}/>
    :page==='Employees'
      ?<Employees/>
      :page==='Approvals'
        ?<Approvals/>
        :<Analysis mode={page}/>;
  return <Layout page={page} setPage={setPage} overviewPeriod={overviewPeriod}>{content}</Layout>;
}
