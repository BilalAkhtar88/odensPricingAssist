# scripts/predict_real_quotes.py

import json
import pandas as pd
import xgboost as xgb
from pathlib import Path
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import root_mean_squared_error, mean_absolute_percentage_error, r2_score
from schemas.quote_training_schema import QuoteML

# Paths
REAL_QUOTES_PATH = Path("data/user_alpha/quotes_extracted.json")
MODEL_PATH = Path("models/user_alpha/xgboost_model.json")
METADATA_PATH = Path("models/user_alpha/model_metadata.json")

def load_valid_quotes(path: Path) -> pd.DataFrame:
    with open(path, encoding="utf-8") as f:
        raw_quotes = json.load(f)

    valid = []
    for q in raw_quotes:
        try:
            obj = QuoteML(**q)
            valid.append(obj.model_dump())
        except Exception as e:
            print(f"Skipping invalid quote: {e}")
    return pd.DataFrame(valid)

def prepare_features(df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    df = df.dropna(subset=["quoted_price_sek"])
    y_true = df["quoted_price_sek"].values
    X = df.drop(columns=["quoted_price_sek"])

    cat_cols = ["profile_ref", "surface_treatment", "alloy"]
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    encoder.fit(pd.DataFrame([{col: val} for col in cat_cols for val in metadata["features_used"] if col in val]))

    encoded = encoder.transform(X[cat_cols])
    encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(cat_cols))

    X = X.drop(columns=cat_cols).reset_index(drop=True)
    df_features = pd.concat([X, encoded_df], axis=1)

    # Ensure all training features exist
    for col in metadata["features_used"]:
        if col not in df_features.columns:
            df_features[col] = 0.0

    df_features = df_features[metadata["features_used"]]  # align order
    return df_features, y_true

def run_prediction_and_evaluation():
    print("📥 Loading real quotes...")
    df_real = load_valid_quotes(REAL_QUOTES_PATH)

    print("🧠 Loading trained model...")
    model = xgb.XGBRegressor()
    model.load_model(str(MODEL_PATH))

    with open(METADATA_PATH, encoding="utf-8") as f:
        metadata = json.load(f)

    print("🧪 Preparing features...")
    X_real, y_true = prepare_features(df_real.copy(), metadata)

    print("📈 Predicting...")
    y_pred = model.predict(X_real)

    print("📊 Evaluating predictions on real quotes...")
    rmse = root_mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)

    print("✅ Evaluation Results on Real Quotes:")
    print(f"   RMSE : {rmse:.4f}")
    print(f"   R2   : {r2:.4f}")
    print(f"   MAPE : {mape:.4f}")

    return {
        "RMSE": rmse,
        "R2": r2,
        "MAPE": mape
    }
