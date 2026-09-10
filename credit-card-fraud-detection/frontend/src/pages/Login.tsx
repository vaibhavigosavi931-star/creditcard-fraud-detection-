import { FormEvent, useState } from "react";
import { LockKeyhole, LogIn, ShieldCheck, UserPlus } from "lucide-react";
import { AuthUser, login, register } from "../services/api";

export default function Login({ onAuthenticated }: { onAuthenticated: (user: AuthUser) => void }) {
    const [mode, setMode] = useState<"login" | "register">("login");
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loginValue, setLoginValue] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    async function submit(event: FormEvent) {
        event.preventDefault(); setError(""); setLoading(true);
        try {
            if (mode === "register") await register(username, email, password);
            const user = await login(mode === "register" ? email : loginValue, password);
            onAuthenticated(user);
        } catch (reason) {
            setError(reason instanceof Error ? reason.message : "Authentication failed");
        } finally { setLoading(false); }
    }

    return <main className="auth-shell"><section className="auth-panel">
        <div className="auth-brand"><div className="brand-icon"><ShieldCheck size={23} /></div><div><h1>FraudShield</h1><span>ML Detection System</span></div></div>
        <div className="eyebrow">SECURE ACCESS</div><h2>{mode === "login" ? "Sign in to your workspace" : "Create an analyst account"}</h2>
        <p className="auth-copy">Access transaction analysis and model insights with your authorized account.</p>
        <form onSubmit={submit} className="auth-form">
            {mode === "register" && <><label className="field"><span>Username</span><input required value={username} onChange={e => setUsername(e.target.value)} autoComplete="username" /></label><label className="field"><span>Email</span><input required type="email" value={email} onChange={e => setEmail(e.target.value)} autoComplete="email" /></label></>}
            {mode === "login" && <label className="field"><span>Username or email</span><input required value={loginValue} onChange={e => setLoginValue(e.target.value)} autoComplete="username" /></label>}
            <label className="field"><span>Password</span><input required minLength={8} type="password" value={password} onChange={e => setPassword(e.target.value)} autoComplete={mode === "login" ? "current-password" : "new-password"} /></label>
            {error && <div className="auth-error">{error}</div>}
            <button className="primary-btn" disabled={loading}>{mode === "login" ? <LogIn size={18} /> : <UserPlus size={18} />} {loading ? "Please wait…" : mode === "login" ? "Sign in" : "Register"}</button>
        </form>
        <button className="auth-switch" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError("") }}>{mode === "login" ? "Create an analyst account" : "Already have an account? Sign in"}</button>
        <div className="auth-note"><LockKeyhole size={15} /> Passwords are securely hashed and never exposed.</div>
    </section></main>;
}