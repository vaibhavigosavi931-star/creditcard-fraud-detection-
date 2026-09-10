import { FormEvent, useState } from "react";
import { AlertTriangle, CheckCircle2, Search, Sparkles } from "lucide-react";
import { predictTransaction, Prediction, TransactionInput } from "../services/api";
import { Heading } from "./Dashboard";

const initial: TransactionInput = { amount: 250, hour: 14, distance_from_home: 12, merchant_risk: .25, device_trust: .85, international: 0, velocity_24h: 2, account_age_days: 600 };

export default function Analyze() {
    const [form, setForm] = useState(initial); const [result, setResult] = useState<Prediction | null>(null); const [loading, setLoading] = useState(false);
    const update = (k: keyof TransactionInput, v: string) => setForm(p => ({ ...p, [k]: Number(v) }));
    async function submit(e: FormEvent) { e.preventDefault(); setLoading(true); try { setResult(await predictTransaction(form)) } finally { setLoading(false) } }
    return <div><Heading eyebrow="TRANSACTION ANALYSIS" title="Analyze a Transaction" text="Enter transaction features and get an ML-powered fraud probability." />
        <div className="analyze-grid">
            <form className="panel form-panel" onSubmit={submit}><div className="panel-header"><div><h2>Transaction details</h2><p>All fields are used by the model.</p></div><Search size={20} /></div>
                <div className="form-grid">
                    <Field label="Transaction amount ($)" value={form.amount} set={(v: string) => update("amount", v)} step=".01" />
                    <Field label="Transaction hour" value={form.hour} set={(v: string) => update("hour", v)} min="0" max="23" />
                    <Field label="Distance from home (km)" value={form.distance_from_home} set={(v: string) => update("distance_from_home", v)} step=".1" />
                    <Field label="Merchant risk (0–1)" value={form.merchant_risk} set={(v: string) => update("merchant_risk", v)} step=".01" min="0" max="1" />
                    <Field label="Device trust (0–1)" value={form.device_trust} set={(v: string) => update("device_trust", v)} step=".01" min="0" max="1" />
                    <Field label="Transactions in 24h" value={form.velocity_24h} set={(v: string) => update("velocity_24h", v)} min="0" />
                    <Field label="Account age (days)" value={form.account_age_days} set={(v: string) => update("account_age_days", v)} min="0" />
                    <label className="field"><span>International transaction</span><select value={form.international} onChange={e => update("international", e.target.value)}><option value="0">No</option><option value="1">Yes</option></select></label>
                </div>
                <button className="primary-btn" disabled={loading}><Sparkles size={18} />{loading ? "Analyzing…" : "Run fraud analysis"}</button>
            </form>
            <section className={`panel result-panel ${result ? "has-result" : ""}`}>
                {!result ? <div className="empty-result"><div className="empty-icon">✓</div><h2>Awaiting analysis</h2><p>Submit a transaction to see its fraud probability, anomaly score and risk signals.</p></div> :
                    <><div className="result-top"><div><div className="eyebrow">MODEL DECISION</div><h2>{result.prediction === "FRAUD" ? "Potential fraud detected" : "Transaction looks legitimate"}</h2></div>{result.prediction === "FRAUD" ? <AlertTriangle size={30} /> : <CheckCircle2 size={30} />}</div>
                        <div className="probability"><span>Fraud probability</span><strong>{(result.fraud_probability * 100).toFixed(1)}%</strong></div>
                        <div className="big-progress"><i style={{ width: `${result.fraud_probability * 100}%` }} /></div>
                        <div className="score-box"><span>Anomaly score</span><strong>{result.anomaly_score.toFixed(3)}</strong></div>
                        <h3>Risk signals</h3><ul className="reason-list">{result.reasons.map(x => <li key={x}>{x}</li>)}</ul>
                    </>}
            </section>
        </div></div>;
}
type FieldProps = {
    label: string;
    value: number;
    set: (value: string) => void;
};

function Field({ label, value, set, ...props }: FieldProps & React.InputHTMLAttributes<HTMLInputElement>) {
    return <label className="field"><span>{label}</span><input type="number" value={value} onChange={e => set(e.target.value)} {...props} /></label>;
}
