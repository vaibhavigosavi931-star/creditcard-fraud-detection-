import re
import sqlite3

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .auth import create_access_token, get_current_user, hash_password, require_roles, verify_password
from .database import (
    average_probability,
    count_fraud,
    count_transactions,
    create_user,
    get_user_by_login,
    init_db,
    insert_transaction,
    list_transactions,
)
from .ml import train, predict, metrics
from .schemas import (
    DashboardResponse,
    LoginRequest,
    PredictionResponse,
    RegisterRequest,
    TokenResponse,
    TransactionInput,
    UserResponse,
)

app = FastAPI(title="Credit Card Fraud Detection API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    train()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/dashboard", response_model=DashboardResponse)
def dashboard(current_user=Depends(require_roles("analyst", "admin"))):
    total = count_transactions()
    fraud = count_fraud()
    m = metrics()
    return {
        "total_transactions": total,
        "fraud_transactions": fraud,
        "fraud_rate": (fraud / total * 100) if total else 0,
        "avg_fraud_probability": average_probability(),
        **m,
    }

@app.post("/api/predict", response_model=PredictionResponse)
def score(transaction: TransactionInput, current_user=Depends(require_roles("analyst", "admin"))):
    result = predict(transaction.model_dump())
    insert_transaction({**transaction.model_dump(), **result}, user_id=current_user["id"])
    return result

@app.get("/api/transactions")
def transactions(current_user=Depends(require_roles("analyst", "admin"))):
    return list_transactions()


@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest):
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", request.email):
        raise HTTPException(status_code=422, detail="Invalid email address")
    try:
        user_id = create_user(
            request.username,
            request.email,
            hash_password(request.password),
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Username or email already exists") from exc
    return {"id": user_id, "username": request.username, "email": request.email, "role": "analyst"}


@app.post("/api/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    user = get_user_by_login(request.login)
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user["id"], user["role"]), "token_type": "bearer"}


@app.get("/api/auth/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    return current_user


@app.get("/api/admin/model", response_model=DashboardResponse)
def admin_model(current_user=Depends(require_roles("admin"))):
    total = count_transactions()
    fraud = count_fraud()
    return {
        "total_transactions": total,
        "fraud_transactions": fraud,
        "fraud_rate": (fraud / total * 100) if total else 0,
        "avg_fraud_probability": average_probability(),
        **metrics(),
    }
