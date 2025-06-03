import pandas as pd

# Load the real data
def analyze_data(quotes):
    
    df = pd.DataFrame(quotes)

    # Basic summaries
    print("\n--- Top Profiles ---")
    print(df["profile_ref"].value_counts())

    print("\n--- Top Alloys ---")
    print(df["alloy"].value_counts())

    print("\n--- Surface Treatments ---")
    print(df["surface_treatment"].value_counts())

    print("\n--- Quantity Range ---")
    print(df["quantity"].min(), "to", df["quantity"].max())

