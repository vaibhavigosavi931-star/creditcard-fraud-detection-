import { useEffect, useState } from "react";
import { Bell, Menu, ShieldCheck } from "lucide-react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Analyze from "./pages/Analyze";
import Transactions from "./pages/Transactions";
import Evaluation from "./pages/Evaluation";
import Login from "./pages/Login";
import { AuthUser, clearToken, getMe, getStoredToken } from "./services/api";

export default function App() {
    const [page, setPage] = useState("dashboard"); const [mobile, setMobile] = useState(false);
    const [user, setUser] = useState<AuthUser | null>(null); const [checking, setChecking] = useState(true);
    useEffect(() => { if (!getStoredToken()) { setChecking(false); return; } getMe().then(setUser).catch(() => clearToken()).finally(() => setChecking(false)); }, []);
    if (checking) return <div className="loading">Loading secure workspace…</div>;
    if (!user) return <Login onAuthenticated={setUser} />;
    const content = { dashboard: <Dashboard />, analyze: <Analyze />, transactions: <Transactions />, evaluation: <Evaluation /> }[page];
    const change = (p: string) => { setPage(p); setMobile(false) };
    const logout = () => { clearToken(); setUser(null) };
    return <div className="app-shell">
        <button className="mobile-menu" onClick={() => setMobile(!mobile)}><Menu /></button>
        <div className={mobile ? "mobile-sidebar open" : "mobile-sidebar"}><Sidebar active={page} onChange={change} user={user} onLogout={logout} /></div>
        <div className="desktop-sidebar"><Sidebar active={page} onChange={change} user={user} onLogout={logout} /></div>
        <main className="main"><header className="topbar"><div className="topbar-brand"><ShieldCheck size={18} /> CREDIT RISK LAB</div><div className="top-actions"><span className="api-status"><i /> API connected</span><Bell size={18} /></div></header><div className="page-content">{content}</div></main>
    </div>;
}
