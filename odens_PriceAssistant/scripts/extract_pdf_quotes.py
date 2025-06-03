# scripts/extract_pdf_quotes.py

import pdfplumber
import re
from pathlib import Path
import json

# Paths
PDF_FOLDER = Path("data/user_alpha/originial_Quotes_data")
OUTPUT_PATH = Path("data/user_alpha/quotes_extracted.json")

def extract_text_from_pdf(file_path):
    """Extract all text from a multi-page PDF."""
    print("Entered step 1")
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def parse_quote_from_text(text, source_file):
    """Extract all product lines from a single quote PDF and attach shared metadata."""
    lines = text.splitlines()

    try:
        # --- Shared metadata ---
        date_line = next(line for line in lines if "Datum:" in line)
        quote_date = date_line.split(":")[1].strip()

        alloy_line = next((line for line in lines if "Legering:" in line), "Legering: Rå")
        default_alloy = alloy_line.split(":")[1].strip()

        # Optional shared fields
        tool_cost_sek = None
        surface_treatment = None
        standard = None
        lead_time_weeks = None
        validity_date = None
        raw_material_price_eur_kg = None

        for line in lines:
            # if "Verktygskostnad:" in line:
            #     match = re.search(r"(\d+)\s*kr", line.replace(" ", ""))
            #     if match:
            #         tool_cost_sek = float(match.group(1))

            if "Ytbehandling:" in line:
                surface_treatment = line.split(":", 1)[1].strip()

            if "Råvara:" in line:
                match = re.search(r"([\d,]+)\s*Euro", line)
                if match:
                    raw_material_price_eur_kg = float(match.group(1).replace(",", "."))

        # --- Extract product lines ---
        extracted_lines = []
        pattern = re.compile(
            r"(?P<profile>[A-Za-zÅÄÖåäö\-]{3,}(?:profil)?)\s+"
            r"(?P<weight>[\d,]+)\s+"
            r"(?P<length>[\d,]+)\s+"
            r"[\d,]+\s+"
            r"(?P<quantity>\d+)\s+"
            r"(?P<price>[\d,]+)\s+"
            r"(?P<alloy>\w+)"
        )

        def clean_float(val):
            return float(val.replace(",", "."))

        for match in pattern.finditer(text):
            try:
                d = match.groupdict()

                quote_data = {
                    "user_id": "company_alpha",
                    "quote_id": f"{source_file.stem}_{match.start()}",
                    "quote_date": quote_date,
                    "source_file": source_file.name,
                    "profile_ref": d["profile"],
                    "weight_kg_m": clean_float(d["weight"]),
                    "length_m": clean_float(d["length"]),
                    "quantity": int(d["quantity"]),
                    "alloy": d.get("alloy") or default_alloy,
                    "quoted_price_sek": clean_float(d["price"]),
                    "tool_cost_sek": tool_cost_sek,
                    "surface_treatment": surface_treatment,
                    "standard": standard,
                    "lead_time_weeks": lead_time_weeks,
                    "validity_date": validity_date,
                    "raw_material_price_eur_kg": raw_material_price_eur_kg
                }

                extracted_lines.append(quote_data)

            except Exception as e:
                print(f"⚠️ Failed to extract one line in {source_file.name}: {e}")

        return extracted_lines

    except Exception as e:
        print(f"❌ Error parsing shared fields in {source_file.name}: {e}")
        return []

def run_pdf_extraction(QuoteModel):
    """Main function to extract and validate quotes from all PDFs."""
    extracted = []

    for file in sorted(PDF_FOLDER.glob("PdfNAP (*.pdf")):  # To process all 50 PDFs
        print(f"📄 Processing: {file.name}")
        text = extract_text_from_pdf(file)
        print("Extracted Text starts here\n")
        print(text)
        print("Extracted Text ends here\n")

        all_quote_lines = parse_quote_from_text(text, file)

        for quote_data in all_quote_lines:
            try:
                quote = QuoteModel(**quote_data)
                extracted.append(quote.model_dump(mode="json"))
                print(f"✅ Validated and added: {quote_data['quote_id']}")
            except Exception as e:
                print(f"❌ Validation failed for {quote_data.get('quote_id', 'unknown')}: {e}")

    # Save all valid quotes
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Extraction complete. Saved {len(extracted)} quotes to {OUTPUT_PATH}")