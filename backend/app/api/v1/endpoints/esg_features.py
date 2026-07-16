from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
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


@router.post("/carbon-footprint", response_model=CarbonFootprintResponse)
def create_carbon_footprint(
    footprint: CarbonFootprintCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Record carbon footprint data"""
    db_footprint = CarbonFootprint(**footprint.dict())
    db.add(db_footprint)
    db.commit()
    db.refresh(db_footprint)
    return db_footprint


@router.get("/carbon-footprint/{factory_id}", response_model=List[CarbonFootprintResponse])
def get_carbon_footprints(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get carbon footprint data for a factory"""
    footprints = db.query(CarbonFootprint).filter(
        CarbonFootprint.factory_id == factory_id
    ).order_by(CarbonFootprint.period_start.desc()).all()
    return footprints


@router.post("/esg-score", response_model=ESGScoreResponse)
def create_esg_score(
    score: ESGScoreCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create ESG score assessment"""
    db_score = ESGScore(**score.dict())
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


@router.get("/esg-score/{factory_id}", response_model=ESGScoreResponse)
def get_esg_score(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get latest ESG score for a factory"""
    score = db.query(ESGScore).filter(
        ESGScore.factory_id == factory_id
    ).order_by(ESGScore.assessment_date.desc()).first()
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
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


@router.get("/sustainability-dashboard/{factory_id}", response_model=SustainabilityDashboardResponse)
def get_sustainability_dashboard(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get sustainability dashboard for a factory"""
    dashboard = db.query(SustainabilityDashboard).filter(
        SustainabilityDashboard.factory_id == factory_id
    ).order_by(SustainabilityDashboard.period_end.desc()).first()
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
    impact = db.query(WasteImpact).filter(
        WasteImpact.material_id == material_id
    ).first()
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
    certifications = db.query(GreenCertification).filter(
        GreenCertification.factory_id == factory_id
    ).all()
    return certifications


@router.get("/carbon-credits/{factory_id}")
def get_carbon_credits(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get carbon credits for a factory"""
    credits = db.query(CarbonCredit).filter(
        CarbonCredit.factory_id == factory_id
    ).all()
    return credits
