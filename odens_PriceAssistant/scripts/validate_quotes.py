# from datetime import date
from pprint import pprint

def run_validation(QuoteModel):
    # Step 1: Define a list of 10 example quote dictionaries
    
    sample_quotes = [
        {
            "user_id": "company_alpha",
            "quote_id": "Q-2025-001",
            "quote_date": "2025-04-30",
            "source_file": "quote_01.pdf",
            "customer_id": "MM",
            "profile_ref": "Glaskil",
            "weight_kg_m": 1.055,
            "length_m": 20.2,
            "quantity": 68000,
            "alloy": "Raw",
            "quoted_price_sek": 2.42
        },
        {
            "user_id": "company_alpha",
            "quote_id": "Q-2025-002",
            "quote_date": "2025-03-15",
            "source_file": "quote_02.pdf",
            "customer_id": "JJ",
            "profile_ref": "Dekorlist",
            "weight_kg_m": 1.12,
            "length_m": 23.5,
            "quantity": 50000,
            "alloy": 7890,
            "quoted_price_sek": -0.9
        },
        # Add 8 more varied examples below
    ]

    # Step 2: Validate and print results
    print("✅ Starting validation of sample quote entries...\n")
    for i, quote_dict in enumerate(sample_quotes, start=1):
        print(f"--- Validating Quote #{i} ---")
        try:
            quote = QuoteModel(**quote_dict)
            print("✔️ Validated successfully:")
            pprint(quote.model_dump())
        except Exception as e:
            print("❌ Validation error:")
            print(str(e))
        print("\n")
