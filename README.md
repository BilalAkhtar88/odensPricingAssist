# 🧠 Odens Pricing Assistant – Development Summary

Odens Pricing Assistant is a prototype for a user-personalized, intelligent pricing engine designed to predict quote prices for aluminum profiles. It consists of two modular components: a secure backend API and a local training pipeline. The architecture supports extensibility, user isolation, and retraining over time.

---

## 📁 Project Architecture

Monorepo with two main components:

### `odens_PriceAssistant/`
> **Purpose**: Data ingestion, augmentation, feature engineering, and training of a personalized ML model.

- Designed to run locally as a manual or scheduled cron job.
- Users must store real-world quote data, run the training pipeline, and **manually copy** the trained model to the backend folder.
- Currently a standalone script-based pipeline that will later be automated and integrated.

### `odens_Backend/`
> **Purpose**: Secure FastAPI application for predictions, user authentication, and quote logging.

- All APIs are authenticated via JWT tokens.
- Each user has an isolated model and data directory.
- Structured for future extension into a full microservice with a persistent database.
- Currently supports a single test user (`bilal` with model in `ml_models/bilal_yahoo/`).

---

## 🔄 Step-by-Step Development Summary

### ✅ Step 1: Quote Data Ingestion

- 50 historical quote PDFs placed under:  
  `odens_PriceAssistant/data/user_alpha/original_quotes/`

- Extracted using `pdfplumber` and regex logic.

- Parsed shared metadata (e.g. weight, alloy) and product line items.

- Validated against `Quote` schema and saved as structured JSON.

### 🔁 Step 2: Data Augmentation

- Analyzed trends in real quotes by profile type, alloy, and treatment.

- Generated 1500+ synthetic quotes using:
  - Profile-based pricing multipliers
  - Volume discount rules
  - Controlled Gaussian noise
  - LME price correlations

- Output saved as:  
  `data/user_alpha/quotes_augmented.json`

### 🛠️ Step 3: Feature Engineering

- Input features:
  - Numerical: `weight_kg_m`, `length_m`, `quantity`, `raw_material_price_eur_kg`
  - Categorical: `profile_ref`, `surface_treatment`, `alloy`

- Target: `quoted_price_sek`

- Used `pandas.get_dummies` with `handle_unknown='ignore'`

- Final dataset stored as:  
  `data/user_alpha/quotes_features.csv`

### 🤖 Step 4: Model Training

- Algorithm: **XGBoostRegressor**
  - Chosen for speed, accuracy, and native support for mixed feature types.
  - Alternatives (e.g., Linear Regression, Random Forest) were considered but underperformed.

- Hyperparameters:
  - Manually tuned and optionally optimized with **Optuna**
  - Learning rate (`eta`) tuning had the largest performance impact

- Regularization:
  - `reg_alpha`, `reg_lambda` for generalization

- Evaluation:
  - KFold (5 splits)
  - Metrics: `MAPE`, `RMSE`, `R²`
  - Model trained primarily to **minimize MAPE**

- Output files:
  - Model: `ml_models/user_alpha/xgboost_model.json`
  - Metadata: `ml_models/user_alpha/model_metadata.json`

### 📊 Step 5: Evaluation on Real Data

- Model tested on real quotes
- Metrics:
  - **R² was negative** → indicates distribution shift or small sample size
  - **MAPE** showed strong generalization and was prioritized

---

## 🔐 Backend API (FastAPI)

### 📌 Endpoints

| Method | Path                 | Purpose                                |
|--------|----------------------|----------------------------------------|
| POST   | `/auth/signup`       | Register a user and receive token      |
| POST   | `/auth/login`        | Login and receive token                |
| GET    | `/user/me`           | Get user info using token              |
| POST   | `/predict/model_latest` | Predict quote price using model    |
| POST   | `/predict/save_quote`   | Save the quoted feature + result    |

### ⚙️ Security

- JWT-based authentication
- User's email (e.g. `bilal@yahoo.com`) is used to isolate model and data
- Folder names are sanitized: `@` → `_`, `.com` → removed → `bilal_yahoo`

---

## 🛡️ Data & Model Security

- Each user has:
  - `ml_models/{user_dir}/xgboost_model.json`
  - `data/{user_dir}/quotes_features.csv`

- Token validation protects access to all endpoints

- No sensitive data is stored in tokens

- Admin access or encryption features can be added in future

---

## 🔁 Continuous Learning Plan

- Every prediction gets stored to:
  - `data/{user_dir}/quotes_features.csv`

- These accumulate and are used to retrain models with the cron job pipeline

- Retraining is manual for now but will become automated via cron jobs

---

## 📦 Folder Structure Overview

### `odens_PriceAssistant/`

- data/
- └── user_alpha/
-     ├── original_quotes/ # Raw PDFs
-     ├── quotes_augmented.json # Augmented data
-     └── quotes_features.csv # Final features
- models/
- └── user_alpha/ # Trained XGBoost model + metadata
- scripts/ # All preprocessing and training scripts
- schemas/ # Quote & QuoteML schemas
- main.py # Pipeline orchestrator

### `odens_Backend/`

- auth/
- └── auth_utils.py # JWT, password hashing
- database/
- └── users.py # In-memory user db
- ml_models/
- └── bilal/ # User-specific model and metadata
- routes/
- ├── auth.py
- ├── user.py
- ├── predict.py
- schemas/
- └── quote_schema.py # Pydantic input validation
- main.py # FastAPI app
- data/
- └── bilal_yahoo/quotes_features.csv


---

## 🚀 Setup & Run Instructions

### 🛠 Pre-Requisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv): Fast Python environment manager

---

### 🔧 Step 1: Create Separate Environments

For each project (`odens_Backend` and `odens_PriceAssistant`):

```bash
cd odens_Backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

cd ../odens_PriceAssistant
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 🔄 Step 2: Train the ML Model
In odens_PriceAssistant/:

```bash
Copy
Edit
python main.py
```

This:

Ingests & augments data

Trains model

Saves model to: models/user_alpha/xgboost_model.json

Then manually copy:

```bash
Copy
Edit
cp models/user_alpha/* ../odens_Backend/ml_models/bilal_yahoo/
```

### ▶️ Step 3: Start the Backend
In odens_Backend/:

```bash
Copy
Edit
uvicorn main:app --reload
Swagger UI:
http://localhost:8000/docs
```

#### 🧪 API Testing Guide
Register User
POST /auth/signup
Form data:

```bash
Copy
Edit
username: bilal@yahoo.com
password: abcd
```

#### Login
POST /auth/login
Returns JWT token

#### Predict Quote
POST /predict/model_latest
Include Bearer token
JSON body:

json
Copy
Edit
{
  "weight_kg_m": 20,
  "length_m": 40,
  "quantity": 40000,
  "raw_material_price_eur_kg": 3,
  "surface_treatment": "Ra",
  "alloy": "Ra",
  "profile_ref": "Hornvinkel"
}

#### 📊 Accuracy Calculation & Metrics
Primary metric: MAPE (Mean Absolute Percentage Error)

Supplementary: RMSE, R²

R² occasionally negative due to small test sample size

MAPE used as key indicator of real-world generalization

#### 🔮 Future Enhancements
Quantile Regression for uncertainty estimation

Database integration and multitenancy

Role-based access and admin dashboard

Event-driven retraining with cron + background job queue

Full frontend integration (optional)

#### 🧪 Testability Notes
All functionality is testable via Swagger UI

Local training pipeline produces artifacts for API consumption

No external DB or cloud dependencies

Only known limitation: single-user setup

#### 📌 Maintainer Notes
To support new users:

Add their trained model to: ml_models/{user_dir}

Ensure quotes_features.csv is updated after predictions

Folder structure uses username for routing
