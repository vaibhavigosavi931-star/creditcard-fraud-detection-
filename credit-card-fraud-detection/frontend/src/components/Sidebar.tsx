import { ShieldCheck, LayoutDashboard, ScanSearch, History, BarChart3, Database, LogOut } from "lucide-react";
import { AuthUser } from "../services/api";
type Props = { active: string; onChange: (page: string) => void; user: AuthUser; onLogout: () => void };
const items = [["dashboard", "Dashboard", LayoutDashboard], ["analyze", "Analyze Transaction", ScanSearch], ["transactions", "Transactions", History], ["evaluation", "Model Evaluation", BarChart3]] as const;

export default function Sidebar({ active, onChange, user, onLogout }: Props) {
    return <aside className="sidebar">
        <div className="brand"><div className="brand-icon"><ShieldCheck size={23} /></div><div><div className="brand-name">FraudShield</div><div className="brand-sub">ML Detection System</div></div></div>
        <nav><div className="nav-label">MONITORING</div>
            {items.map(([id, label, Icon]) => <button key={id} className={`nav-item ${active === id ? "active" : ""}`} onClick={() => onChange(id)}><Icon size={18} /><span>{label}</span></button>)}
            <div className="nav-label data-label">DATA</div><div className="data-status"><Database size={16} /><span>SQLite connected</span><span className="status-dot" /></div>
        </nav>
        <div className="sidebar-footer"><div className="model-pill"><span className="pulse" /> Model online</div><small>Random Forest + Isolation Forest</small><div className="user-row"><div><strong>{user.username}</strong><span>{user.role}</span></div><button className="logout-btn" onClick={onLogout} title="Log out"><LogOut size={16} /></button></div></div>
    </aside>;
}
