from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from auth.auth_utils import decode_access_token
from schemas.quote_schema import QuoteML, QuoteWithTarget
import pandas as pd
import xgboost as xgb
from pathlib import Path
import json
import csv
import os

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/model_latest", summary="Predict quote price using latest model")
def predict_quote(data: QuoteML, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_email = payload["sub"]
    user_dir = user_email.replace("@", "_").replace(".com", "")

    model_path = Path(f"ml_models/{user_dir}/xgboost_model.json")
    meta_path = Path(f"ml_models/{user_dir}/model_metadata.json")

    if not model_path.exists() or not meta_path.exists():
        raise HTTPException(status_code=404, detail="No model found for this user")

    model = xgb.XGBRegressor()
    model.load_model(str(model_path))

    with open(meta_path, "r") as f:
        meta = json.load(f)

    input_df = pd.DataFrame([data.dict()])
    input_df = pd.get_dummies(input_df)

    for col in meta["features_used"]:
        if col not in input_df.columns:
            input_df[col] = 0
    input_df = input_df[meta["features_used"]]

    prediction = float(model.predict(input_df)[0])
    return {"predicted_price_sek": round(prediction, 2)}


@router.post("/save_quote", summary="Save quote data for training", status_code=201)
def save_quote(data: QuoteWithTarget, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_email = payload["sub"]
    user_dir = user_email.replace("@", "_").replace(".com", "")
    data_dir = Path("data") / f"{user_dir}"
    csv_file = data_dir / "quotes_features.csv"

    os.makedirs(data_dir, exist_ok=True)

    row = data.dict()

    write_header = not csv_file.exists()
    with open(csv_file, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    return {"message": f"Quote saved for user '{user_email}'"}
