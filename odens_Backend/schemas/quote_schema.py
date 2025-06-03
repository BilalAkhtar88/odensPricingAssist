from pydantic import BaseModel, Field

class QuoteML(BaseModel):
    weight_kg_m: float = Field(..., description="Material weight per meter")
    length_m: float = Field(..., description="Profile length in meters")
    quantity: int = Field(..., description="Number of items quoted")
    raw_material_price_eur_kg: float = Field(..., description="Raw material price in EUR/kg")
    surface_treatment: str = Field(..., description="Surface treatment applied to profile")
    alloy: str = Field(..., description="Alloy type used in profile")
    profile_ref: str = Field(..., description="Reference to profile shape")

class QuoteWithTarget(QuoteML):
    quoted_price_sek: float = Field(..., description="Actual quoted price in SEK")