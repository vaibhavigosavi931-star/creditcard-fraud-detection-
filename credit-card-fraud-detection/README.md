# 💳 Credit Card Fraud Detection

> **A full-stack, real-time machine learning and analytics platform for detecting credit card fraud and evaluating risk scores.**

---

## 🛠️ Tech Stack

| Domain | Technologies |
| :--- | :--- |
| **Frontend** | React, TypeScript, Vite, CSS3 |
| **Backend** | Python, FastAPI, Uvicorn |
| **Machine Learning** | scikit-learn, Pandas, NumPy |
| **Database** | SQLite |
| **Security** | JWT Authentication (Role-Based: Analyst & Admin) |

---

## ✨ Key Features

* ⚡ **Real-Time Data Preprocessing:** Automated feature scaling and data cleaning pipeline for instant model ingestion.
* 🤖 **Dual ML Detection Engine:** Combines supervised classification models with unsupervised anomaly detection.
* 📊 **Risk & Probability Scoring:** Generates dynamic fraud probability scores for individual transactions.
* 📈 **Comprehensive Evaluation Metrics:** Displays real-time Precision, Recall, F1-Score, and ROC-AUC metrics.
* 🖥️ **Interactive Operations Dashboard:** Includes manual transaction testing, historical query logs, and visual performance metrics.
* 🔐 **Role-Based Access Control (RBAC):** Secure endpoint authorization differentiating Analyst and Admin capabilities.
* 🧪 **Synthetic Dataset Generator:** Built-in data generation utilities for local testing and development.

---

## 📁 Repository Structure

```text
credit-card-fraud-detection/
├── 📂 backend/
│   ├── 📂 app/
│   │   ├── 📂 api/
│   │   ├── 📂 core/
│   │   ├── 📂 models/
│   │   └── 📂 services/
│   ├── 📂 data/
│   ├── 📄 main.py
│   └── 📄 requirements.txt
└── 📂 frontend/
    ├── 📂 src/
    │   ├── 📂 components/
    │   ├── 📂 pages/
    │   └── 📂 services/
    ├── 📄 package.json
    └── 📄 vite.config.ts
