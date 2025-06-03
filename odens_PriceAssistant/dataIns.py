import json
import pandas as pd
from pathlib import Path

# Load your extracted quote data
with open("data/user_alpha/quotes_extracted.json", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)
df["quote_date"] = pd.to_datetime(df["quote_date"])

# Convert numerical fields to numeric dtype
for col in ["weight_kg_m", "length_m", "quantity", "quoted_price_sek", "raw_material_price_eur_kg", "tool_cost_sek"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Quantity binning to analyze volume effect
df["quantity_bin"] = pd.cut(df["quantity"], bins=[0, 50000, 100000, 200000, 500000], right=True)

# Group statistics
print("\n--- Price by Profile ---")
print(df.groupby("profile_ref")["quoted_price_sek"].agg(["mean", "std", "count"]))

print("\n--- Price by Alloy ---")
print(df.groupby("alloy")["quoted_price_sek"].agg(["mean", "std", "count"]))

print("\n--- Price by Surface Treatment ---")
print(df.groupby("surface_treatment")["quoted_price_sek"].agg(["mean", "std", "count"]))

print("\n--- Price by Quantity Bin ---")
print(df.groupby("quantity_bin")["quoted_price_sek"].agg(["mean", "std", "count"]))
