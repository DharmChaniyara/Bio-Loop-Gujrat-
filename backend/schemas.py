"""
Pydantic v2 schemas for API requests, evaluations, and village-level responses.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


# District
class DistrictOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    region: str
    lat: float
    lng: float


# Village
class VillageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    taluka: str
    district_id: str
    lat: float
    lng: float
    coord_precision: str
    primary_crops_json: Optional[str] = None
    primary_crops: Optional[List[str]] = None
    source: str
    limitations: str
    record_status: str


# Biomass Types
class BiomassTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    typical_moisture_min: float
    typical_moisture_max: float
    harvest_months: List[str]
    properties_json: Optional[str] = None
    source: str
    limitations: str
    record_status: str


# Pathway
class PathwayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    compatible_biomass_ids: List[str]
    max_moisture: float
    min_quantity_tpm: float
    processing_requirements: str
    capex_level: str
    ease_level: str
    source: str
    limitations: str
    record_status: str


# Offtakers, Hubs, and Farmer Groups
class OfftakerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: str
    village_id: str
    village_name: Optional[str] = None
    district_name: Optional[str] = None
    lat: float
    lng: float
    accepts_biomass_ids: List[str]
    pathway_ids: List[str]
    capacity_tpm: float
    listing_status: str
    source: str
    limitations: str
    record_status: str
    distance_km: Optional[float] = None
    est_trip_time_mins: Optional[int] = None


class LogisticsHubOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    village_id: str
    village_name: Optional[str] = None
    district_name: Optional[str] = None
    lat: float
    lng: float
    hub_type: str
    listing_status: str
    source: str
    limitations: str
    record_status: str
    distance_km: Optional[float] = None
    est_trip_time_mins: Optional[int] = None


class FarmerGroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    village_id: str
    village_name: Optional[str] = None
    district_name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    biomass_ids: List[str]
    est_supply_tpm: float
    season_months: List[str]
    source: str
    limitations: str
    record_status: str
    distance_km: Optional[float] = None


# Weights
class WeightItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: float = Field(..., ge=0.0, le=1.0)
    description: str
    source: str
    limitations: str
    record_status: str


class WeightsUpdateRequest(BaseModel):
    weights: Dict[str, float]

    @field_validator("weights")
    @classmethod
    def validate_weights(cls, v: Dict[str, float]) -> Dict[str, float]:
        required = {"w1_material_fit", "w2_processing_fit", "w3_logistics", "w4_market_fit", "w5_ease"}
        if not required.issubset(v.keys()):
            missing = required - set(v.keys())
            raise ValueError(f"Missing required weight keys: {list(missing)}")
        total = sum(v.values())
        if abs(total - 1.0) > 0.005:
            raise ValueError(f"Weights must sum to 1.0 (got {total:.3f})")
        return v


# Evaluation Request & Output
class EvaluateRequest(BaseModel):
    biomass_type: str = Field(..., description="Biomass ID e.g. groundnut_shell")
    district_id: Optional[str] = Field(None, description="Gujarat district ID or name")
    village_id: str = Field(..., description="Selected village ID as origin")
    quantity: float = Field(..., gt=0, description="Quantity in tonnes per month")
    moisture_content: Optional[float] = Field(None, ge=0.0, le=100.0, description="Moisture percentage")
    seasonality_notes: Optional[str] = Field(None, max_length=500, description="Optional seasonality notes")
    max_radius_km: Optional[float] = Field(100.0, ge=10.0, le=500.0, description="Catchment radius filter in km")


class FactorBreakdownItem(BaseModel):
    factor_name: str
    raw_score: float  # 0 to 100
    weight: float     # e.g. 0.30
    weighted_score: float
    status: str       # "Verified" | "Illustrative" | "Requires verification"
    explanation: str


class RankedPathway(BaseModel):
    pathway_id: str
    pathway_name: str
    score: float           # 0 to 100
    rank: int
    eligible: bool
    status_reason: str     # Short reason line
    capex_level: str
    ease_level: str
    logistics_level: str
    market_fit_level: str
    data_confidence: str   # "High" | "Moderate" | "Low"
    factors: List[FactorBreakdownItem]
    ineligibility_reasons: List[str] = []
    verification_steps: List[str] = []
    source: str
    limitations: str
    record_status: str


class EvaluationResponse(BaseModel):
    input_summary: Dict[str, Any]
    ranked_pathways: List[RankedPathway]
    eligible_count: int
    ineligible_count: int
    nearby_offtakers: List[OfftakerOut]
    nearby_hubs: List[LogisticsHubOut]
    nearby_farmer_groups: List[FarmerGroupOut]
    missing_info: List[str]
    catchment_radius_km: float
    disclaimer: str
