import random
from datetime import datetime, timedelta
import json
from pathlib import Path
from faker import Faker
import numpy as np
from pandas.tseries.offsets import BDay

# Output path
OUTPUT_PATH = Path("data/user_alpha/quotes_augmented.json")
faker = Faker()

# --- Constants from your stats ---
PROFILE_STATS = {
    "Glaskil": 2.44,
    "Hörnvinkel": 2.82,
    "Fönsterbåge": 3.49,
    "Sidoprofil": 3.52,
    "Spröjsprofil": 2.26,
    "Tätningslist": 2.64,
    "Ytterram": 3.02,
    "F-profil": 2.74,
    "H-profil": 3.05,
    "T-profil": 2.97,
    "U-profil": 2.72,
    "L-profil": 2.60,
    "Z-profil": 2.81,
    "J-profil": 2.95,
    "Karmprofil": 3.14,
    "Stödprofil": 3.08,
    "Täckprofil": 3.19,
    "Anslagslist": 2.98,
    "Baslister": 2.52,
    "Bottenlist": 2.66,
    "Glashållare": 3.09,
    "Karmlist": 2.97,
    "Ramlist": 2.80,
    "Kopplingsprofil": 2.61,
    "Droppnäsa": 2.50
}

ALLOYS = {
    "Rå": 1.0,
    "EN-AW-6060": 1.02,
    "EN-AW-6063": 1.05,
    "EN-AW-6082": 1.08,
}

SURFACE_TREATMENTS = {
    "EN-AW-6063-T5": 1.0,
    "Anodized": 1.03,
    "Powder Coated": 1.06,
    "Brushed Finish": 1.02,
    "None": 0.98
}

LME_BASE_USD_TON = 2500  # assume average LME value
USD_TO_EUR = 0.88  # current approximate rate
EUR_PER_KG_BASE = (LME_BASE_USD_TON / 907.185) * USD_TO_EUR  # ≈ 2.43

def random_weekday_within_4_months():
    today = datetime.today()
    start_date = today - timedelta(days=120)
    days_range = (today - start_date).days

    while True:
        random_days = random.randint(0, days_range)
        quote_date = start_date + timedelta(days=random_days)
        if quote_date.weekday() < 5:  # Mon–Fri
            return quote_date.date()

def apply_volume_discount(base_price, quantity):
    if quantity <= 50000:
        return base_price * 1.08
    elif quantity <= 100000:
        return base_price * 1.03
    elif quantity <= 200000:
        return base_price * 0.98
    else:
        return base_price * 0.95

def generate_quote(profile_ref):
    base_price = PROFILE_STATS[profile_ref]
    quantity = (random.randint(20, 200)) * 1000
    # quantity = random.choice([25000, 40000, 42000, 45000, 48000, 50000, 58000, 60000, 80000, 100000, 140000, 170000, 200000])
    weight = round(np.random.normal(loc=1.2, scale=0.2), 3)
    length = round(np.random.normal(loc=24, scale=2), 2)

    alloy = random.choice(list(ALLOYS.keys()))
    surface_treatment = random.choice(list(SURFACE_TREATMENTS.keys()))
    raw_material_price_eur_kg = round(np.random.normal(EUR_PER_KG_BASE, 0.1), 2)

    adjusted_price = base_price
    adjusted_price *= ALLOYS[alloy]
    adjusted_price *= SURFACE_TREATMENTS[surface_treatment]
    adjusted_price = apply_volume_discount(adjusted_price, quantity)
    adjusted_price = round(adjusted_price + np.random.normal(0, 0.01), 2)

    return {
        "user_id": "company_alpha",
        "quote_id": faker.uuid4(),
        "quote_date": str(random_weekday_within_4_months()),
        "source_file": "augmented",
        "customer_id": None,
        "customer_segment": None,
        "profile_ref": profile_ref,
        "weight_kg_m": weight,
        "length_m": length,
        "quantity": quantity,
        "surface_treatment": surface_treatment,
        "alloy": alloy,
        "finish": None,
        "standard": None,
        "lead_time_weeks": None,
        "validity_date": None,
        "raw_material_price_eur_kg": raw_material_price_eur_kg,
        "quoted_price_sek": adjusted_price,
        "currency": "SEK",
        "tool_cost_sek": None,
        "is_outlier": None,
        "schema_version": "v1.0",
        "is_valid": True
    }

def run_quote_augmentation(QuoteModel, num_examples=1000):
    print("📈 Generating synthetic quote dataset...")
    augmented = []

    profiles = list(PROFILE_STATS.keys())

    while len(augmented) < num_examples:
        profile = random.choice(profiles)
        quote_dict = generate_quote(profile)

        try:
            quote = QuoteModel(**quote_dict)
            augmented.append(quote.model_dump(mode="json"))
        except Exception as e:
            print(f"⚠️ Validation failed for {quote_dict['quote_id']}: {e}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(augmented, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(augmented)} synthetic quotes to {OUTPUT_PATH}")