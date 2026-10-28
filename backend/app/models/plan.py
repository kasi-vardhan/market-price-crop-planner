"""
Pydantic models for the Crop Planning API.

CropPlanRequest  — farmer input, includes optional budget and farmer_question
CropPlanResponse — structured response with top 3 crops, ROI, and data freshness
"""

from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional

SUPPORTED_SOILS = {"red", "loamy", "black", "sandy", "clay", "alluvial"}
SUPPORTED_WATER = {"low", "medium", "high"}
SUPPORTED_SEASONS = {"kharif", "rabi", "zaid"}


class CropPlanRequest(BaseModel):

    farmer_question: Optional[str] = Field(
        default=None,
        description="Optional farmer question or additional constraints"
    )

    location: str = Field(
        min_length=1,
        max_length=150,
        description="Farm location (mandal, district, or village name)"
    )

    soil: str = Field(
        description="Soil type: red, loamy, black, sandy, clay, alluvial"
    )

    water: str = Field(
        description="Water availability: low, medium, high"
    )

    season: str = Field(
        description="Growing season: kharif, rabi, zaid"
    )

    land_area: float = Field(
        gt=0,
        le=1000,
        description="Land area in acres (must be > 0)"
    )

    budget: Optional[float] = Field(
        default=None,
        ge=0,
        description=(
            "Available cultivation investment budget in INR. "
            "Optional. If provided, crops that exceed this budget are flagged."
        )
    )

    @field_validator("farmer_question")
    @classmethod
    def validate_question(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        if len(cleaned) > 0 and len(cleaned) < 3:
            raise ValueError("Farmer question must be at least 3 characters if provided.")
        return cleaned if cleaned else None

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Location cannot be empty.")
        return cleaned

    @field_validator("soil")
    @classmethod
    def validate_soil(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if cleaned not in SUPPORTED_SOILS:
            raise ValueError(
                f"Unsupported soil type '{v}'. Supported: {', '.join(sorted(SUPPORTED_SOILS))}."
            )
        return cleaned

    @field_validator("water")
    @classmethod
    def validate_water(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if cleaned not in SUPPORTED_WATER:
            raise ValueError(
                f"Unsupported water availability '{v}'. Supported: {', '.join(sorted(SUPPORTED_WATER))}."
            )
        return cleaned

    @field_validator("season")
    @classmethod
    def validate_season(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if cleaned not in SUPPORTED_SEASONS:
            raise ValueError(
                f"Unsupported season '{v}'. Supported: {', '.join(sorted(SUPPORTED_SEASONS))}."
            )
        return cleaned


class CropPlanResponse(BaseModel):

    question: Optional[str] = None

    location: str

    recommended_crop: Optional[str] = None

    recommendation_score: Optional[float] = None

    recommendation: Optional[str] = None

    weather: Optional[dict[str, Any]] = None

    climate: Optional[dict[str, Any]] = None

    market: list[dict[str, Any]] = []

    crop_suitability: list[dict[str, Any]] = []

    profit_analysis: list[dict[str, Any]] = []

    ranking: Optional[dict[str, Any]] = None

    knowledge: list[dict[str, Any]] = []

    sources: list[dict[str, Any]] = []

    data_status: dict[str, Any] = {}

    data_confidence: dict[str, Any] = {}

    budget: Optional[float] = None

    eligible_crop_count: Optional[int] = None

    no_eligible_crops_reason: Optional[str] = None
