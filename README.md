# TrustFabric 🛡️
### **Adaptive Multi-Channel Banking Trust Layer**
*Developed for Bank of Baroda × IIT Gandhinagar Hackathon*

TrustFabric is a **shared trust infrastructure** that sits between every banking channel (mobile app, net banking, UPI, IVR, branch teller, ATM, internal admin tools) and the services they call. Instead of each channel re-implementing its own authentication and risk scoring, they consume short-lived, **cryptographically signed Trust Tokens (RS256 JWT)**. Downstream APIs consume these tokens to decide whether to allow, step-up, or block requests.

---

## 💎 The Four Differentiating Pillars

| Innovation Pillar | Technical Stack | Hackathon Differentiator |
| :--- | :--- | :--- |
| **Trust Token Backbone** | `PyJWT` + `cryptography` (RS256) | Modelled on W3C Verifiable Credentials. Downstream APIs verify signed claims independently without database lookup overhead. |
| **Explainable Transaction AI** | `LightGBM` + `SHAP` Explainer | Trained on the 680MB IEEE-CIS dataset using the **"UID trick"** (pseudo-identity tracking). Explains exact feature impacts on transaction decisions in real-time. |
| **Cross-Channel Trust Graph** | `NetworkX` + `python-louvain` | Builds a real-time network of customers, devices, and IPs. Runs Louvain community detection to detect and propagate risk across coordinated fraud rings. |
| **Synthetic Identity Recycling** | `SentenceTransformer` (`all-MiniLM-L6-v2`) | Normalizes soft-PII details into a dense vector, calculating cosine similarity against historical data. Catches fraudsters altering 1-2 characters in fake KYC forms. |

---

## ⚡ Quick Start

The project is pre-configured and already running on your machine:
*   **Vite Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
*   **FastAPI Backend Server**: [http://localhost:8000](http://localhost:8000)
*   **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

*(Manual setup instructions are listed at the bottom of this document).*

---

## 🎯 Step-by-Step Demo Walkthrough Script (For Judges)

Open [http://localhost:3000](http://localhost:3000) in your browser and follow this sequence to experience the full end-to-end security pipeline:

### **Step 1: The Adaptive Trust Gate (Biometrics & OTP Step-Up)**
1. Navigate to the **Login** page.
2. Enter any username (e.g. `cust_001`).
3. In the Password field, try typing **arbitrary keys** or copy-pasting. Click **Authenticate**.
   * *Result*: The system analyzes your typing cadence (down-down, up-down, hold intervals). A timing mismatch is detected. The trust score degrades, and the gate triggers an **OTP step-up verification modal**.
4. Enter the mock 6-digit OTP `123456` in the modal and submit.
5. Now logout and try again. This time, type the exact password **`.tie5Roanl`** carefully at a natural pace.
   * *Result*: The keystroke timing matched the enrolled CMU password benchmark profile. The gate issues a **HIGH** trust token and logs you in instantly with no step-up modal required!

### **Step 2: Interactive SHAP explainability (Transfer Page)**
1. Navigate to the **Transfer** page.
2. Drag the **Transfer Amount** slider to a high value (e.g., above INR 150,000) or change email domains to high-risk choices like `temp-mail.org`.
3. Click **Evaluate Transaction**.
   * *Result*: The LightGBM classifier scores the transaction risk in real-time.
   * *SHAP explainability*: A live horizontal bar chart (using Recharts) appears, showing the **SHAP tree explanation waterfall**. Judges can see exactly which factors pushed the transaction towards a flag (e.g., amount too high, unfamiliar card series, or mismatching email domains).

### **Step 3: Identity Recycling Checker (Admin Dashboard)**
1. Navigate to the **Admin** page.
2. Look at the **KYC Onboarding Checker** form on the right.
3. Submit the default details for applicant **"Priya Sharma"**.
   * *Result*: The SentenceTransformer embedder registers her soft-PII details. Status is **CLEAR**.
4. Now, change the name slightly to **"Priya Sharma2"** or swap some digits in the Date of Birth and submit again.
   * *Result*: The embedder calculates cosine similarity against previous entries. The system detects a **similarity match of ~88%** against Priya Sharma.
   * *Alerts Feed*: The risk status turns to **REVIEW** (Recycled Identity Risk), and a high-severity alert is instantly dispatched to the **SOC Alerts Feed** on the left.

### **Step 4: Cross-Channel Trust Graph Visualizer (Graph View)**
1. Navigate to the **Graph** page.
2. Observe the **Identity Trust Graph** rendered using D3.js.
   * *Visualizing Fraud Rings*: The graph shows a coordinates network connecting customers, devices, and IPs.
   * *Louvain Risk Propagation*: The node `cust_fraud_001` (Rajan Kumar) is a confirmed fraudster (colored Red). Because he shares the device `dev_mule_shared` with other accounts, Louvain community detection group them together. Risk is automatically propagated, coloring the connected device and co-community accounts orange/red as suspicious mules.

### **Step 5: Red-Team Simulator (Adversarial Demo)**
1. Navigate to the **Adversarial** page.
2. Click **Boiling Frog ATO** scenario and click **Launch Simulation**.
   * *Result*: Simulates an adversary gradually drifting typing cadences and IP footprints over 15 sessions. The Recharts LineChart displays the gradual decay of the session trust score, showing exactly at which session the adaptive engine triggered MFA gates.
3. Try **Spoofed Biometrics** and **Graph Evasion** simulations to observe how multi-channel detection flags sophisticated evasion attempts.

---

## 🛠️ Repository File Structure & Setup (Ref.)

```
trustfabric/
├── .env                             ← Local configuration paths and thresholds
├── README.md                        ← This file
├── docker-compose.yml               ← Multi-container orchestration (DB, Redis, API, UI)
├── keys/                            
│   ├── private.pem                  ← RSA Private Key (issues signed W3C Trust Tokens)
│   └── public.pem                   ← RSA Public Key (public key verified by gateways)
│
├── backend/                         ← FastAPI Python Service
│   ├── main.py                      ← Startup loading and lifespans
│   ├── config.py                    ← Configuration reader
│   ├── requirements.txt             ← Python dependencies
│   ├── models/                      ← Pydantic schemas (Session, Onboarding, Transaction)
│   ├── routers/                     ← Route controllers (Auth, Graph, Onboarding, Passport)
│   ├── services/                    ← Business Logic (Trust Engine, Token service)
│   └── ml/                          
│       ├── artifacts/               ← Trained LightGBM and Keystroke anomaly weights
│       ├── lgbm_model.py            ← LightGBM & SHAP explanation models
│       ├── keystroke_model.py       ← Manhattan distance timing models
│       └── identity_embedder.py     ← SentenceTransformer soft-PII encoder (SHA-256 fallback)
│
├── frontend/                        ← Vite React + TypeScript Frontend
│   ├── package.json                 ← Node package list (react-router-dom, d3, recharts, zustand)
│   ├── tsconfig.json                ← Typescript compilation options
│   ├── vite.config.ts               ← Dev server port 3000 & /api reverse-proxy to backend
│   └── src/                         
│       ├── components/              ← Reusable UI (TrustMeter, GraphViewer, ShapWaterfall)
│       └── pages/                   ← Router pages (LoginPage, TransferPage, AdversarialDemo)
│
├── notebooks/                       ← Jupyter Notebook analyses
│   ├── 01_ieee_cis_eda.ipynb        ← IEEE-CIS exploratory data analysis
│   ├── 02_lgbm_training.ipynb       ← LightGBM transaction model training
│   ├── 03_keystroke_detector.ipynb  ← CMU keystroke dynamics performance evaluation
│   └── 04_graph_community_detection.ipynb ← NetworkX Louvain community detection
│
└── scripts/                         ← Setup scripts
    ├── train_lgbm.py                ← Trains and pickles LightGBM classifier
    ├── train_keystroke.py           ← Traing Scaled Manhattan profile scaler
    └── build_synthetic_graph.py     ← Builds networkx device sharing graph
```

---

## 🔧 Manual Setup & Training Commands

If you need to re-train the models or run the backend/frontend servers in a clean environment manually:

1. **Requirements & Key Pairs**:
   ```bash
   # Install dependencies
   pip install -r backend/requirements.txt
   
   # Generate RSA keys for signed JWTs
   mkdir -p keys
   openssl genrsa -out keys/private.pem 2048
   openssl rsa -in keys/private.pem -pubout -out keys/public.pem
   ```

2. **Model Training**:
   *   **Keystroke timing profile**: Download `DSL-StrongPassword.csv` to `data/raw/` and run `python scripts/train_keystroke.py`.
   *   **Transaction LightGBM model**: Download Kaggle `train_transaction.csv` to `data/raw/ieee_cis/` and run `python scripts/train_lgbm.py`.

3. **Starting Servers (Host-mode)**:
   ```bash
   # Start Backend (FastAPI)
   python scripts/start_backend.py
   
   # Start Frontend (React Dev Server)
   cd frontend
   npm run dev
   ```
