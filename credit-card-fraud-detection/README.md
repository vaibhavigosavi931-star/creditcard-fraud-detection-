# Credit Card Fraud Detection — VS Code

A full-stack learning project for credit-card fraud detection.

## Stack
- Frontend: React + TypeScript + Vite
- Backend: Python + FastAPI
- ML: Pandas, NumPy, scikit-learn
- Database: SQLite
- Charts/UI: React + CSS

## Features
- Transaction preprocessing
- Fraud classification
- Anomaly detection
- Fraud probability scoring
- Precision, Recall, F1 and ROC-AUC
- SQLite transaction history
- Dashboard, manual analysis, history and model evaluation
- Secure user authentication with analyst and admin roles
- Synthetic sample dataset

## Run in VS Code

### Backend
```bash
cd backend
python -m venv .venv
```
Windows:
```bash
.venv\Scripts\activate
```
macOS/Linux:
```bash
source .venv/bin/activate
```
Then:
```bash
pip install -r requirements.txt
```

Set a JWT signing secret before starting the API. It must be at least 32 characters and must not be committed:
```powershell
$env:JWT_SECRET_KEY="replace-with-a-random-secret-at-least-32-characters"
```
macOS/Linux:
```bash
export JWT_SECRET_KEY="replace-with-a-random-secret-at-least-32-characters"
```
Optional token lifetime configuration:
```bash
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Start the API:
```bash
python -m uvicorn app.main:app --reload
```

Public users can register as analysts from the application. To create the first administrator, run this from the `backend` directory and enter the password interactively:
```bash
python -m app.create_admin --username admin --email admin@example.com
```

Passwords are stored as Argon2 hashes. The API never returns password hashes. Analysts can analyze transactions and view history; admins can also access administrative model endpoints.

### Frontend
Open a second terminal:
```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

The API runs at `http://127.0.0.1:8000`.

> The included dataset is synthetic and is for education/demo use only.

### Authenticated application

Start the backend with `JWT_SECRET_KEY` set, then start the frontend in a second terminal. Open the Vite URL, register an analyst account or sign in with an administrator account, and use the logout control in the sidebar to end the browser session. Authentication state is kept in session storage and is sent to private API routes as a Bearer token.

### Tests

From the `backend` directory, with the virtual environment active:
```bash
pytest -q
```
