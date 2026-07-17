import asyncio
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.endpoints.auth import get_current_user
from app.models.match import Match
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.match import MatchCreate, MatchOut

router = APIRouter()

Session = Any


def get_db() -> None:
    return None


def _run(coro):
    return asyncio.run(coro)


@router.get("", response_model=SuccessResponse)
def list_matches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    matches = _run(Match.find_all().to_list())
    return {"success": True, "message": "Operation successful", "data": {"matches": [MatchOut.model_validate(match).model_dump() for match in matches]}}


@router.post("/generate", response_model=SuccessResponse)
def generate_match(match_in: MatchCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    match = Match(id=str(uuid4()), **match_in.model_dump())
    _run(match.insert())
    return {"success": True, "message": "Operation successful", "data": {"match": MatchOut.model_validate(match).model_dump()}}


@router.get("/{match_id}", response_model=SuccessResponse)
def get_match(match_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    match = _run(Match.find_one(Match.id == match_id))
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"success": True, "message": "Operation successful", "data": {"match": MatchOut.model_validate(match).model_dump()}}
