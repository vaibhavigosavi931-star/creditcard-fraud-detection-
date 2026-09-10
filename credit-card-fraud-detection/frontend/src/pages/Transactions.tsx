import { useEffect, useState } from "react";
import { RefreshCw, History } from "lucide-react";
import { getTransactions } from "../services/api";
import { Heading, TransactionTable } from "./Dashboard";

export default function Transactions() {
    const [rows, setRows] = useState<any[]>([]);
    const load = (): void => {
        void getTransactions().then(setRows).catch(console.error);
    };
    useEffect(() => { load(); }, []);
    return <div><Heading eyebrow="DATABASE" title="Transaction History" text="Review transactions that have been scored by the fraud model." />
        <section className="panel table-panel"><div className="panel-header"><div><h2>Scored transactions</h2><p>{rows.length} recent records</p></div><button className="secondary-btn" onClick={load}><RefreshCw size={16} /> Refresh</button></div><TransactionTable rows={rows} /></section></div>;
}
