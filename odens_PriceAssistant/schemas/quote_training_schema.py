from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union
from datetime import date

class Quote(BaseModel):
    # --- Tenant Info ---
    user_id: str = Field(..., description="Anonymized identifier for the company/user")
    
    # --- Core Metadata ---
    quote_id: str = Field(..., description="Unique quote identifier per user")
    quote_date: date = Field(..., description="Date of quote creation")
    source_file: Optional[str] = Field(None, description="Original PDF or upload file")

    # --- Customer (No PII) ---
    customer_id: Optional[str] = Field(None, description="Anonymized customer reference ID")
    customer_segment: Optional[str] = Field(None, description="Optional customer segment")

    # --- Product Specs ---
    profile_ref: str = Field(..., description="Shape/profile reference (e.g., Glaskil, Dekorlist)")
    weight_kg_m: float = Field(..., description="Weight in kg per meter")
    length_m: float = Field(..., description="Length in meters")

    # --- Manufacturing ---
    quantity: int = Field(..., description="Order quantity / Expected Annual Volume")
    surface_treatment: Optional[str] = Field(None, description="Surface treatment like anodizing")

    # --- Material & Standards ---
    alloy: str = Field(..., description="Material or alloy type")
    finish: Optional[str] = Field(None, description="Finish or coating (e.g., Raw, Matte)")
    standard: Optional[str] = Field(None, description="Applicable standard (e.g., EN-AW-6063)")

    # --- Contextual Factors ---
    lead_time_weeks: Optional[str] = Field(None, description="Delivery time range (e.g., 5–6 weeks)")
    validity_date: Optional[date] = Field(None, description="Quote valid until date")
    raw_material_price_eur_kg: Optional[float] = Field(None, description="Material base price at quote time")

    # --- Pricing ---
    quoted_price_sek: float = Field(..., description="Final quoted unit price in SEK")
    currency: Optional[str] = Field("SEK", description="Currency of the quoted price")
    tool_cost_sek: Optional[float] = Field(None, description="One-time tooling fee")

    # --- Derived or Engineered (Optional) ---
    is_outlier: Optional[bool] = Field(None, description="Mark if this entry was flagged during preprocessing")
    
    # Following may be added in later versions
    # profile_complexity_score: Optional[float] = Field(None, description="Numeric representation of profile complexity")

    # --- System Flags ---
    schema_version: Optional[str] = Field("v1.0", description="Version of the schema used for this quote")
    is_valid: Optional[bool] = Field(True, description="Validation flag after processing")

    # --- Validators ---
    @field_validator('quoted_price_sek', 'weight_kg_m', 'length_m', 'quantity')
    @classmethod
    def check_positive(cls, value: Union[int, float], info) -> Union[int, float]:
        if value <= 0:
            raise ValueError(f"{info.field_name} must be greater than zero")
        return value

    @field_validator('tool_cost_sek')
    @classmethod
    def check_non_negative(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and value < 0:
            raise ValueError("tool_cost_sek must be non-negative")
        return value
    

# ================================================================
# Feature Selection and Schema Definition for ML model Training
# ----------------------------------------------------------------
# Based on previous analysis, the following features are used
# to train the pricing model:
#
# - weight_kg_m                (float): Core material weight per meter
# - length_m                   (float): Profile length in meters
# - quantity                   (int): Quoted volume, affects discount
# - raw_material_price_eur_kg  (float): LME-influenced material cost
# - surface_treatment          (str): Processing step impacting cost
# - alloy                      (str): Material type affecting cost
# - profile_ref                (str): Used for encoding. Unknowns handled.
#
# Dropped:
# - quote_date: Excluded for now (could add temporal modeling later)
# - currency: Constant in dataset
# 
# 🎯 Target Variable:
# quoted_price_sek: This is what we want to predict.
#
# NOTE:
# profile_ref may introduce unseen values during prediction. Use:
# - Category encoding with fallback for "unknown"
# - Or treat with target encoding / embeddings
# ================================================================

class QuoteML(BaseModel):
    weight_kg_m: float = Field(..., description="Material weight per meter")
    length_m: float = Field(..., description="Profile length in meters")
    quantity: int = Field(..., description="Number of items quoted")
    raw_material_price_eur_kg: float = Field(..., description="Raw material price in EUR/kg")
    surface_treatment: str = Field(..., description="Surface treatment applied to profile")
    alloy: str = Field(..., description="Alloy type used in profile")
    profile_ref: str = Field(..., description="Reference to profile shape")
    quoted_price_sek: float = Field(..., description="Quoted price in SEK (target variable)")