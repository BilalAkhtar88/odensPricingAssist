# scripts/extract_features.py

import json
import pandas as pd
from pathlib import Path
from typing import List
from sklearn.preprocessing import OneHotEncoder
from schemas.quote_training_schema import QuoteML

# Input and output paths
INPUT_PATH = Path("data/user_alpha/quotes_augmented.json")
OUTPUT_PATH = Path("data/user_alpha/quotes_features.csv")

# Selected features for ML model
ML_FEATURES = [
    "profile_ref",
    "weight_kg_m",
    "length_m",
    "quantity",
    "surface_treatment",
    "alloy",
    "raw_material_price_eur_kg",
    "quoted_price_sek"
]

def load_valid_quotes(path: Path) -> List[dict]:
    """Load and validate quotes using QuoteML schema."""
    with open(path, encoding="utf-8") as f:
        raw_quotes = json.load(f)

    valid_quotes = []
    for idx, item in enumerate(raw_quotes, start=1):
        try:
            validated = QuoteML(**item)
            valid_quotes.append(validated.model_dump())
            if idx % 200 == 0:
                print(f"✅ Validated entry number {idx} to adhere to QuoteML schema.")
        except Exception as e:
            print(f"⚠️ Skipping invalid entry: {e}")

    return valid_quotes

def encode_categoricals(df: pd.DataFrame, categorical_cols: List[str]) -> pd.DataFrame:
    """One-hot encode specified categorical columns."""
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    encoded = encoder.fit_transform(df[categorical_cols])
    encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(categorical_cols))
    df = df.drop(columns=categorical_cols).reset_index(drop=True)
    df_encoded = pd.concat([df, encoded_df], axis=1)
    return df_encoded

def run_feature_extraction() -> pd.DataFrame:
    """Main feature extraction routine."""
    print("🔍 Step 7: Loading and validating augmented quotes...")
    quotes = load_valid_quotes(INPUT_PATH)

    print(f"✅ Loaded {len(quotes)} valid quotes.")
    df = pd.DataFrame(quotes)[ML_FEATURES]
    df = df.dropna(subset=ML_FEATURES)

    print(f"📊 Encoding features from {len(df)} entries...")
    categorical_cols = ["profile_ref", "surface_treatment", "alloy"]
    df_encoded = encode_categoricals(df, categorical_cols)

    # Save to CSV
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_encoded.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Features saved to {OUTPUT_PATH}")

    return df_encoded
