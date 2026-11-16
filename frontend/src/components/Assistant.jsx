import {useEffect,useRef,useState} from 'react';
import {Bot,Send} from 'lucide-react';
import {api} from '../services/api';

const faqs=[
  {
    question:'What does each agent do?',
    answer:'The six agents are deterministic Python rules, not LLMs: Data Quality flags invalid FTE and missing FX; Normalization converts pay to INR and 1.0 FTE; Band Compliance checks effective bands and calculates compa-ratio and band position; Comparability groups by role, level, location and year; Disparity flags salaries below 80% of a group median (groups need at least 3 records); Recommendation creates a pending review proposal. The rules are explicit so findings can be traced.'
  },
  {
    question:'How is a potential disparity flagged?',
    answer:'The current demo groups records by role, level, location and salary year. For groups with at least 3 salaries, it flags a normalized salary below 80% of that group’s median. A flag is a prompt for human review, not proof of unfair treatment.'
  },
  {
    question:'How are currency and FTE normalized?',
    answer:'The generator derives annualized INR from the salary record’s currency conversion and FTE. Analysis compares pay at 1.0 FTE and flags records whose annualized INR is missing instead of assuming a conversion. Demo FX rates are synthetic and static by location; production use would need governed, effective-dated FX data.'
  },
  {
    question:'What are compa-ratio and band position?',
    answer:'Compa-ratio is normalized annual salary divided by the effective band midpoint. Band position is (salary − band minimum) ÷ (band maximum − band minimum). A value below 0 or above 1 is outside the band.'
  },
  {
    question:'What happens to adjustment proposals?',
    answer:'Analysis creates a pending proposal with its evidence. An HR reviewer can approve or reject it; the decision is recorded as an audit event. This demo does not apply the proposed amount to a salary record.'
  },
  {
    question:'Are the edge-case fixtures analyzed?',
    answer:'No. The five labelled negative fixtures and ground-truth labels are exported separately and are not loaded into baseline analysis. The project currently validates data integrity and reproducibility but does not calculate precision or recall against ground truth.'
  },
  {
    question:'Why are there 200 role/level combinations?',
    answer:'The generator defines 20 distinct roles and 10 levels. Their Cartesian product is 20 × 10 = 200 role/level combinations; the dashboard reports combinations, not 200 distinct roles.'
  },
  {
    question:'Is this a live AI chatbot?',
    answer:'No external AI service is used. EquiQ answers reference questions with local rules and can query the synthetic database for supported counts and employee IDs.'
  }
];

const welcome='Hi, I’m EquiQ. I answer project questions and can look up supported information in the local synthetic database. No API key or external AI service is used.';

function findFaqAnswer(question){
  const normalize=value=>value.toLowerCase().replace(/[^\w\s]/g,'').trim();
  return faqs.find(item=>normalize(item.question)===normalize(question))?.answer;
}

export default function Assistant(){
  const [open,setOpen]=useState(false);
  const [question,setQuestion]=useState('');
  const [messages,setMessages]=useState([{id:1,role:'assistant',text:welcome}]);
  const [loading,setLoading]=useState(false);
  const messagesEndRef=useRef(null);
  const nextMessageId=useRef(2);

  useEffect(()=>{
    if(open)messagesEndRef.current?.scrollIntoView({block:'end',behavior:'smooth'});
  },[messages,open]);

  const ask=async(text)=>{
    const value=text.trim();
    if(!value||loading)return;
    const userMessageId=nextMessageId.current++;
    const answerMessageId=nextMessageId.current++;
    const localAnswer=findFaqAnswer(value);
    setMessages(current=>[
      ...current,
      {id:userMessageId,role:'user',text:value},
      {id:answerMessageId,role:'assistant',text:localAnswer||'EquiQ is thinking…',pending:!localAnswer}
    ]);
    setQuestion('');
    if(localAnswer)return;

    setLoading(true);
    try{
      const result=await api.assistantChat(value);
      setMessages(current=>current.map(message=>message.id===answerMessageId?{...message,text:result.answer,pending:false}:message));
    }catch(error){
      const message=`EquiQ could not reach the local assistant. ${error.message}`;
      setMessages(current=>current.map(item=>item.id===answerMessageId?{...item,text:message,pending:false}:item));
    }finally{
      setLoading(false);
    }
  };

  const submit=(event)=>{
    event.preventDefault();
    ask(question);
  };

  return <>
    {open&&<section id="equityiq-assistant" className="assistant-panel" role="dialog" aria-label="EquiQ FAQ assistant">
      <header className="assistant-panel-header">
          <div className="assistant-heading">
          <span className="assistant-avatar"><Bot size={19}/></span>
          <div><strong>EquiQ</strong><small>Offline FAQ + database helper</small></div>
        </div>
      </header>
      <div className="assistant-messages" aria-live="polite">
        {messages.map(message=><div className={`assistant-message ${message.role==='assistant'?'bot':'user'}`} key={message.id}>{message.text}</div>)}
        <div ref={messagesEndRef}/>
      </div>
      {messages.length===1&&<div className="assistant-faqs">
        <span>Quick questions</span>
        {faqs.map(faq=><button type="button" className="assistant-faq" key={faq.question} onClick={()=>ask(faq.question)}>{faq.question}</button>)}
      </div>}
      <form className="assistant-form" onSubmit={submit}>
        <input value={question} onChange={event=>setQuestion(event.target.value)} placeholder="Ask about the project..." aria-label="Ask EquiQ" maxLength={2000} disabled={loading}/>
        <button type="submit" aria-label="Send question" disabled={!question.trim()||loading}><Send size={17}/></button>
      </form>
      <p className="assistant-disclaimer">Runs locally using synthetic project data. No API key or external AI is used.</p>
    </section>}
    <button className="assistant-launcher" type="button" onClick={()=>setOpen(value=>!value)} aria-label={open?'EquiQ assistant, click to hide':'Open EquiQ assistant'} aria-expanded={open} aria-controls="equityiq-assistant">
      <Bot size={22}/><span>EquiQ</span>
    </button>
  </>;
}
