type Props={title:string;value:string;caption:string;tone?:"normal"|"danger"|"success"};
export default function StatCard({title,value,caption,tone="normal"}:Props){
 return <div className="stat-card"><div className="stat-title">{title}</div><div className={`stat-value ${tone}`}>{value}</div><div className="stat-caption">{caption}</div></div>;
}
