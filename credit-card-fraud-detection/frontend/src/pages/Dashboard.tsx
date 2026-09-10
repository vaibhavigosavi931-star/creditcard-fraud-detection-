import {useEffect,useState} from "react";
import {ShieldAlert,Activity,Gauge} from "lucide-react";
import {getDashboard,getTransactions} from "../services/api";
import StatCard from "../components/StatCard";
import RiskBadge from "../components/RiskBadge";

export default function Dashboard(){
 const [d,setD]=useState<any>(); const [rows,setRows]=useState<any[]>([]);
 useEffect(()=>{Promise.all([getDashboard(),getTransactions()]).then(([a,b])=>{setD(a);setRows(b.slice(0,6))}).catch(console.error)},[]);
 if(!d)return <div className="loading">Loading fraud monitoring system…</div>;
 return <div>
  <Heading eyebrow="REAL-TIME MONITORING" title="Fraud Detection Dashboard" text="Monitor transaction risk, model performance and recent activity." chip="LIVE"/>
  <div className="stat-grid">
   <StatCard title="Transactions" value={d.total_transactions.toLocaleString()} caption="Processed in database"/>
   <StatCard title="Fraud detected" value={d.fraud_transactions.toLocaleString()} caption={`${d.fraud_rate.toFixed(2)}% fraud rate`} tone="danger"/>
   <StatCard title="Avg. fraud probability" value={`${(d.avg_fraud_probability*100).toFixed(1)}%`} caption="Across analyzed transactions"/>
   <StatCard title="ROC-AUC" value={d.roc_auc.toFixed(3)} caption="Validation performance" tone="success"/>
  </div>
  <div className="content-grid">
   <section className="panel"><div className="panel-header"><div><h2>Model health</h2><p>Classification performance on validation data</p></div><Gauge size={20}/></div>
    <div className="metric-list">{[["Precision",d.precision],["Recall",d.recall],["F1 Score",d.f1],["ROC-AUC",d.roc_auc]].map(([n,v])=><div className="metric-row" key={n as string}><span>{n}</span><div className="metric-bar"><i style={{width:`${Number(v)*100}%`}}/></div><strong>{(Number(v)*100).toFixed(1)}%</strong></div>)}</div>
   </section>
   <section className="panel"><div className="panel-header"><div><h2>Detection pipeline</h2><p>How each transaction is analyzed</p></div><Activity size={20}/></div>
    <div className="pipeline">{[["01","Preprocessing","Normalize transaction features"],["02","Classification","Random Forest fraud probability"],["03","Anomaly detection","Isolation Forest secondary signal"],["04","Risk decision","Turn signals into a decision"]].map(([n,t,x])=><div className="pipeline-item" key={n}><div className="pipeline-num">{n}</div><div><strong>{t}</strong><span>{x}</span></div></div>)}</div>
   </section>
  </div>
  <section className="panel table-panel"><div className="panel-header"><div><h2>Recent transactions</h2><p>Latest scored activity</p></div><ShieldAlert size={20}/></div><TransactionTable rows={rows}/></section>
 </div>;
}
export function Heading({eyebrow,title,text,chip}:{eyebrow:string;title:string;text:string;chip?:string}){
 return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{text}</p></div>{chip&&<div className="live-chip"><span/>{chip}</div>}</div>;
}
export function TransactionTable({rows}:{rows:any[]}){
 return <div className="table-wrap"><table><thead><tr><th>ID</th><th>Amount</th><th>Merchant risk</th><th>Probability</th><th>Status</th></tr></thead><tbody>
 {rows.map(r=><tr key={r.id}><td>#{String(r.id).padStart(5,"0")}</td><td>${Number(r.amount).toFixed(2)}</td><td>{(Number(r.merchant_risk)*100).toFixed(0)}%</td><td>{(Number(r.fraud_probability)*100).toFixed(1)}%</td><td><RiskBadge prediction={r.prediction}/></td></tr>)}
 </tbody></table></div>;
}
