"""
Odens Pricing Assistant - AI Quoting System Prototype
-----------------------------------------------------

This is the main entry point of the project.
It follows a modular, schema-driven architecture designed for scalability,
data privacy, and machine learning readiness.

The system is built step-by-step, starting with schema validation and evolving into
a full pricing engine. This file currently runs Step 2: Quote Data Validation.

Project Structure ( ---> Initially Planned <--- ):
    Step 1 - Define the data schema using Pydantic (done)
    Step 2 - Validate sample quote entries against the schema (this step)
    Step 3 - Extract real quotes from PDFs into structured data
    Step 4 - Preprocess and engineer features
    Step 5 - Train a price prediction model
    Step 6 - Build user-facing prediction interface (e.g., Streamlit, API)
    Step 7 - Add multi-user support, uncertainty quantification, and feedback loop

"""

import json

# --- STEP 1: Import schema (already defined in schema/quote_training_schema.py)
from schemas.quote_training_schema import Quote  # <- This is your core data model

# --- STEP 2: Import the validation logic
# We're passing Quote into this module to avoid hard dependencies or circular imports
from scripts.validate_quotes import run_validation
from scripts.extract_pdf_quotes import run_pdf_extraction
from scripts.analyze_50_quotes_data import analyze_data
from scripts.augment_quotes import run_quote_augmentation
from scripts.extract_features import run_feature_extraction
from scripts.ml_model_training import run_model_training
from scripts.predict_real_quotes import run_prediction_and_evaluation
    
def main():
    print("🚀 Starting Odens Pricing Assistant Prototype\n")
    # # In step 1 we define the schemas.

    print("🔍 Running Step 2: Validating sample quote entries using Pydantic schema...\n")
    # # This function validates hard-coded sample quote dictionaries.
    # # It's designed to simulate structured entries from PDF-extracted quotes.
    run_validation(Quote)

    print("✅ Validation complete. Ready for Step 3: PDF data ingestion.\n")
    run_pdf_extraction(Quote)
    print("\n✅ Done Step 3. PDF data has been extracted and validated.")

    # # 🔍 Step 4: Data Analysis before Augmentation
    # # The results from this sectiona re used as a prompt for more realistic data augmentation
    print("Data Analysis before Augmentation:\n")
    with open("data/user_alpha/quotes_extracted.json", encoding="utf-8") as f:
        quotes = json.load(f)
    analyze_data(quotes)

    # Step 5: Augment extracted data with synthetic variations
    print("🔄 Running Step 5: Data augmentation from real quotes...\n")
    run_quote_augmentation(Quote,1500)
    print("✅ Step 5 complete: Augmented dataset created.\n")

    # 🔹 Step 6: Feature extraction from augmented dataset adhering to QuoteML schema
    print("\n📊 Running Step 6: Feature extraction for ML training...")
    df_features = run_feature_extraction()
    print(df_features.head())

    # Step 7: Model Training with XGBoost and Optuna
    print("\n🤖 Running Step 7: ML Model Training (XGBoost with Hyperparameter Tuning)")
    run_model_training()
    print("\n✅ Done. Model is trained and saved with metadata.")

    # Step 8 - Evaluate model on real quote data
    print("\n🤖 Running Step 8: Evaluate Model on Real Quote Data...")
    real_metrics = run_prediction_and_evaluation()

    # IMPORTANT NOTE:
    # 🔍 Understanding Evaluation Metrics for the Pricing Model
    # 
    # ✅ Why MAPE is a strong signal in this example?
    # - MAPE (Mean Absolute Percentage Error) is a key metric for pricing applications.
    # - It's easy for stakeholders to understand.
    # - It is scale-invariant — so it handles both low and high price ranges fairly.
    # - A MAPE below 10% typically indicates excellent performance for real-world pricing.

    # ❗ About R² (Getting Negative Value)
    # - In this case, the augmented training data (~1500 examples) covers a wide variety of profiles and quantities,
    #   while the real quote set is small (just 50) and potentially skewed.
    #   The R² calculation compares model predictions against the mean of just these 50 quotes, which limits its reliability.
    # - So a negative R² often indicates:
    #   1. Distribution shift between train and test data.
    #   2. Small or noisy test set.
    #   3. Unmodeled effects in the test set (e.g., rare profiles, missing cost fields like tool cost).
    # 
    # ➡️ Takeaway:
    # - R² is sensitive to the data distribution and test set size.
    # - It's useful only when train and test data come from similar distributions.
    # 
    # ✅ Conclusion
    # - We focus on MAPE as our main model evaluation metric for pricing.
    # - Use RMSE to understand average absolute error in SEK.
    # - Use R² only as a diagnostic signal, not a deciding factor, especially with small test sets.
    # """  

if __name__ == "__main__":
    main()