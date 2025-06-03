# app/api/routes_health.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="Health check")
def health_check():
    return {"status": "ok", "message": "Backend is running"}
