import asyncio
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from app.models.esg_sustainability import (
    CarbonFootprint, ESGScore, SustainabilityDashboard,
    WasteImpact, GreenCertification, CarbonCredit
)
from app.schemas.esg_sustainability import (
    CarbonFootprintCreate, CarbonFootprintResponse,
    ESGScoreCreate, ESGScoreResponse,
    SustainabilityDashboardCreate, SustainabilityDashboardResponse
)
from app.core.security import get_current_user

router = APIRouter()

Session = Any


def get_db() -> None:
    return None


def _run(coro):
    return asyncio.run(coro)


@router.post("/carbon-footprint", response_model=CarbonFootprintResponse)
def create_carbon_footprint(
    footprint: CarbonFootprintCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Record carbon footprint data"""
    db_footprint = CarbonFootprint(**footprint.dict())
    _run(db_footprint.insert())
    return db_footprint


@router.get("/carbon-footprint/{factory_id}", response_model=List[CarbonFootprintResponse])
def get_carbon_footprints(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get carbon footprint data for a factory"""
    footprints = _run(CarbonFootprint.find(CarbonFootprint.factory_id == factory_id).sort(-CarbonFootprint.period_start).to_list())
    return footprints


@router.post("/esg-score", response_model=ESGScoreResponse)
def create_esg_score(
    score: ESGScoreCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create ESG score assessment"""
    db_score = ESGScore(**score.dict())
    _run(db_score.insert())
    return db_score


@router.get("/esg-score/{factory_id}", response_model=ESGScoreResponse)
def get_esg_score(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get latest ESG score for a factory"""
    score = _run(ESGScore.find(ESGScore.factory_id == factory_id).sort(-ESGScore.assessment_date).first_or_none())
    if not score:
        raise HTTPException(status_code=404, detail="ESG score not found")
    return score


@router.post("/sustainability-dashboard", response_model=SustainabilityDashboardResponse)
def create_sustainability_dashboard(
    dashboard: SustainabilityDashboardCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create sustainability dashboard data"""
    db_dashboard = SustainabilityDashboard(**dashboard.dict())
    _run(db_dashboard.insert())
    return db_dashboard


@router.get("/sustainability-dashboard/{factory_id}", response_model=SustainabilityDashboardResponse)
def get_sustainability_dashboard(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get sustainability dashboard for a factory"""
    dashboard = _run(SustainabilityDashboard.find(SustainabilityDashboard.factory_id == factory_id).sort(-SustainabilityDashboard.period_end).first_or_none())
    if not dashboard:
        raise HTTPException(status_code=404, detail="Sustainability dashboard not found")
    return dashboard


@router.get("/waste-impact/{material_id}")
def get_waste_impact(
    material_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get waste impact analysis for a material"""
    impact = _run(WasteImpact.find_one(WasteImpact.material_id == material_id))
    if not impact:
        raise HTTPException(status_code=404, detail="Waste impact data not found")
    return impact


@router.get("/green-certifications/{factory_id}")
def get_green_certifications(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get green certifications for a factory"""
    certifications = _run(GreenCertification.find(GreenCertification.factory_id == factory_id).to_list())
    return certifications


@router.get("/carbon-credits/{factory_id}")
def get_carbon_credits(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get carbon credits for a factory"""
    credits = _run(CarbonCredit.find(CarbonCredit.factory_id == factory_id).to_list())
    return credits
