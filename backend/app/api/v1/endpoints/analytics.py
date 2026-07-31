import asyncio
from inspect import isawaitable
from typing import Any
from fastapi import APIRouter, Depends

from app.api.v1.endpoints.auth import get_current_user
from app.models.analytics import Analytics
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.analytics import AnalyticsOut

router = APIRouter()

Session = Any


def get_db() -> None:
    return None


async def _run(coro):
    if isawaitable(coro):
        return await coro
    return coro


@router.get("/dashboard", response_model=SuccessResponse)
async def dashboard_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    analytics = await _run(Analytics.find_all().sort(-Analytics.created_at).first_or_none())
    if not analytics:
        analytics = Analytics(
            id="analytics-1",
            revenue_generated=245000,
            co2_avoided=1240,
            landfill_diversion=3820,
            active_matches=42,
        )
        await _run(analytics.insert())
    return {"success": True, "message": "Operation successful", "data": {"analytics": AnalyticsOut.model_validate(analytics).model_dump()}}
