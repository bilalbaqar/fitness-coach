from fastapi import APIRouter
from datetime import date
from typing import List, Dict, Any

router = APIRouter()

@router.get("/getReadinessScore")
def get_readiness_score():
    """
    Get readiness score for the current user.
    Returns a comprehensive readiness assessment with score, status, and contributing factors.
    """
    return {
        "userId": "u12345",
        "date": "2025-08-09",
        "readinessScore": {
            "score": 78,
            "status": "moderate",
            "recommendation": "You're moderately recovered. A steady training session is fine, but avoid max-intensity efforts.",
            "factors": [
                {
                    "name": "HRV",
                    "value": 74,
                    "unit": "ms",
                    "impact": "positive"
                },
                {
                    "name": "Resting Heart Rate",
                    "value": 62,
                    "unit": "bpm",
                    "impact": "neutral"
                },
                {
                    "name": "Sleep Quality",
                    "value": 82,
                    "unit": "score",
                    "impact": "positive"
                },
                {
                    "name": "Muscle Soreness",
                    "value": "mild",
                    "impact": "negative"
                }
            ]
        },
        "notes": "Slight leg soreness from yesterday's workout."
    }
