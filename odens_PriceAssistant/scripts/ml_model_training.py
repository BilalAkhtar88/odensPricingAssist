# scripts/ml_model_training.py

import json
from pathlib import Path
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import root_mean_squared_error, r2_score, mean_absolute_percentage_error
import optuna
import time

# Paths
INPUT_FEATURES = Path("data/user_alpha/quotes_features.csv")
MODEL_OUTPUT = Path("models/user_alpha/xgboost_model.json")
METADATA_OUTPUT = Path("models/user_alpha/model_metadata.json")


def load_dataset():
    df = pd.read_csv(INPUT_FEATURES)
    X = df.drop(columns=["quoted_price_sek"])
    y = df["quoted_price_sek"]
    return X, y


def train_xgboost_with_optuna(X, y):
    def objective(trial):
        params = {
            "verbosity": 0,
            "objective": "reg:squarederror",
            "learning_rate": trial.suggest_float("learning_rate", 0.005, 1.0),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "n_estimators": trial.suggest_int("n_estimators", 50, 400),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 0.0, 10.0),  # L1 regularization
            "reg_lambda": trial.suggest_float("reg_lambda", 0.0, 10.0)  # L2 regularization
        }

        model = xgb.XGBRegressor(**params)
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        score = cross_val_score(model, X, y, scoring="neg_root_mean_squared_error", cv=cv).mean()
        return -score

    print("🔍 Running Optuna hyperparameter search (recalibrated)...")
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=50, show_progress_bar=True)

    print("✅ Best trial:", study.best_trial.params)
    best_params = study.best_trial.params

    # Final model training
    model = xgb.XGBRegressor(**best_params)
    model.fit(X, y)
    return model, best_params

def evaluate_model(model, X, y):
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    preds = []
    actuals = []

    for train_index, test_index in kf.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        preds.extend(y_pred)
        actuals.extend(y_test)

    rmse = root_mean_squared_error(actuals, preds)
    r2 = r2_score(actuals, preds)
    mape = mean_absolute_percentage_error(actuals, preds)

    return {
        "RMSE": round(rmse, 4),
        "R2": round(r2, 4),
        "MAPE": round(mape, 4)
    }


def run_model_training():
    print("📦 Loading training dataset...")
    X, y = load_dataset()

    print("🚀 Training XGBoost model with Optuna tuning...")
    model, best_params = train_xgboost_with_optuna(X, y)

    print("📊 Evaluating model with 5-fold CV...")
    metrics = evaluate_model(model, X, y)

    print("✅ Model Performance:")
    for k, v in metrics.items():
        print(f"   {k}: {v}")

    print(f"💾 Saving model to: {MODEL_OUTPUT}")
    MODEL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(MODEL_OUTPUT))

    metadata = {
        "model_type": "xgboost",
        "trained_on": time.strftime("%Y-%m-%d %H:%M"),
        "metrics": metrics,
        "features_used": list(X.columns),
        "hyperparameters": best_params,
        "user": "company_alpha",
        "version": "v1.0"
    }

    with open(METADATA_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"🧠 Model metadata saved to: {METADATA_OUTPUT}")

    return model, metadata
