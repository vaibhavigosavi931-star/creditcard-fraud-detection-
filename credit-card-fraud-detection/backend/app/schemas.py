from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    login: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class TransactionInput(BaseModel):
    amount: float = Field(gt=0)
    hour: int = Field(ge=0, le=23)
    distance_from_home: float = Field(ge=0)
    merchant_risk: float = Field(ge=0, le=1)
    device_trust: float = Field(ge=0, le=1)
    international: int = Field(ge=0, le=1)
    velocity_24h: int = Field(ge=0)
    account_age_days: int = Field(ge=0)

class PredictionResponse(BaseModel):
    fraud_probability: float
    prediction: str
    anomaly_score: float
    reasons: list[str]

class DashboardResponse(BaseModel):
    total_transactions: int
    fraud_transactions: int
    fraud_rate: float
    avg_fraud_probability: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
