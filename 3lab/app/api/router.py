from fastapi import APIRouter
from app.api import bruteforce

api_router = APIRouter()

api_router.include_router(
    bruteforce.router,
    prefix="/bruteforce",
    tags=["bruteforce"]
) 