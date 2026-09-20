"""Эндпоинты маршрутизации."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.router import RouteResult, describe_departments, route_query

router = APIRouter()


class RouteRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


@router.get("/departments")
async def departments() -> dict:
    return {"departments": describe_departments()}


@router.post("/route", response_model=RouteResult)
async def route(
    request: RouteRequest,
    settings: Settings = Depends(get_settings),
) -> RouteResult:
    try:
        return route_query(request.text, settings.escalate_below)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
