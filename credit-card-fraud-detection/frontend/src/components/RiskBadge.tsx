export default function RiskBadge({prediction}:{prediction:string}){
 const fraud=prediction==="FRAUD";
 return <span className={`risk-badge ${fraud?"fraud":"legit"}`}><span className="badge-dot"/>{fraud?"Fraud":"Legitimate"}</span>;
}
