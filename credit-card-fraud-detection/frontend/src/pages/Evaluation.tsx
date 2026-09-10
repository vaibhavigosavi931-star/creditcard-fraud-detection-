import {useEffect,useState} from "react";
import {BarChart3,Target,Crosshair,Layers3} from "lucide-react";
import {getDashboard} from "../services/api";
import {Heading} from "./Dashboard";

export default function Evaluation(){
 const [m,setM]=useState<any>(); useEffect(()=>{getDashboard().then(setM).catch(console.error)},[]);
 if(!m)return <div className="loading">Loading evaluation…</div>;
 const items=[["Precision",m.precision,Target,"How many flagged transactions are actually fraud."],["Recall",m.recall,Crosshair,"How much of the actual fraud the model catches."],["F1 Score",m.f1,Layers3,"Balance between precision and recall."],["ROC-AUC",m.roc_auc,BarChart3,"Overall ranking quality of the classifier."]];
 return <div><Heading eyebrow="MODEL EVALUATION" title="Model Performance" text="Metrics designed for an imbalanced fraud-classification problem."/>
 <div className="evaluation-grid">{items.map(([name,val,Icon,text])=><div className="eval-card" key={name as string}><div className="eval-icon"><Icon size={19}/></div><span>{name}</span><strong>{(Number(val)*100).toFixed(1)}%</strong><p>{text}</p><div className="metric-bar wide"><i style={{width:`${Number(val)*100}%`}}/></div></div>)}</div>
 <section className="panel explanation"><h2>Why these metrics matter</h2><p>Fraud datasets are usually highly imbalanced, so accuracy alone can be misleading. Precision measures false-positive cost, recall measures missed-fraud risk, and ROC-AUC summarizes ranking quality across thresholds.</p></section>
 </div>;
}
