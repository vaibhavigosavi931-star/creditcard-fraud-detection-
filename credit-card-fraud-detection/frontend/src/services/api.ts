const API = "http://127.0.0.1:8000/api";
const TOKEN_KEY = "fraudshield_access_token";

export type AuthUser = { id: number; username: string; email: string; role: "analyst" | "admin" };

export type TransactionInput = {
  amount: number; hour: number; distance_from_home: number; merchant_risk: number;
  device_trust: number; international: number; velocity_24h: number; account_age_days: number;
};
export type Prediction = {
  fraud_probability: number; prediction: "FRAUD" | "LEGITIMATE";
  anomaly_score: number; reasons: string[];
};

type AuthResponse = { access_token: string; token_type: string };

function getToken() { return sessionStorage.getItem(TOKEN_KEY); }
export function clearToken() { sessionStorage.removeItem(TOKEN_KEY); }

async function request<T>(path: string, options: RequestInit = {}, authenticated = true): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (authenticated) {
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${API}${path}`, { ...options, headers });
  if (response.status === 401) { clearToken(); throw Error("Authentication required"); }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw Error(body?.detail || "Request failed");
  }
  return response.json();
}

export function getStoredToken() { return getToken(); }

export async function login(loginValue: string, password: string) {
  const result = await request<AuthResponse>("/auth/login", {
    method: "POST", body: JSON.stringify({ login: loginValue, password })
  }, false);
  sessionStorage.setItem(TOKEN_KEY, result.access_token);
  return getMe();
}

export async function register(username: string, email: string, password: string) {
  return request<AuthUser>("/auth/register", {
    method: "POST", body: JSON.stringify({ username, email, password })
  }, false);
}

export function getMe() { return request<AuthUser>("/auth/me"); }
export function getDashboard() { return request<any>("/dashboard"); }
export function getTransactions() { return request<any[]>("/transactions"); }
export function predictTransaction(input: TransactionInput) { return request<Prediction>("/predict", { method: "POST", body: JSON.stringify(input) }); }
