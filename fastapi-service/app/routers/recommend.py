from fastapi import APIRouter, HTTPException

from ..schemas.recommend import GraduateProfile, RecommendationResponse
from ..services.recommendation import RecommendationService

router = APIRouter(tags=["Recommendations"])


@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(profile: GraduateProfile):
    if not profile.skills:
        raise HTTPException(status_code=400, detail="يجب تقديم قائمة مهارات واحدة على الأقل.")
    try:
        recommendations, data_source = RecommendationService.get_recommendations(profile)
        return RecommendationResponse(
            recommendations=recommendations,
            total_found=len(recommendations),
            data_source=data_source,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"حدث خطأ أثناء معالجة التوصيات: {str(exc)}",
        ) from exc
