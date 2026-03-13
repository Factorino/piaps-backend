from fastapi import APIRouter


router = APIRouter(tags=["Root"])


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "API is running", "version": "1.0.0"}
