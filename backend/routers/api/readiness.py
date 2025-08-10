from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from datetime import date
from deps import get_current_user, get_session
from models import User, ReadinessSnapshot, MetricSample
from schemas.api import ReadinessTodayResponse
from readiness import get_readiness_score

router = APIRouter()

@router.get("/readiness/today", response_model=ReadinessTodayResponse, tags=["Frontend API"])
async def get_readiness_today(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get today's readiness score for current user"""
    today = date.today()
    
    # Check if we have a cached readiness snapshot for today
    snapshot = session.exec(
        select(ReadinessSnapshot)
        .where(ReadinessSnapshot.user_id == current_user.id)
        .where(ReadinessSnapshot.date == today)
    ).first()
    
    if snapshot:
        # Return cached snapshot
        return ReadinessTodayResponse(
            sleep_score=snapshot.factors_json.get("sleep_score"),
            hr_rest=snapshot.factors_json.get("hr_rest"),
            hrv=snapshot.factors_json.get("hrv"),
            fatigue=snapshot.factors_json.get("fatigue"),
            recommendation=snapshot.recommendation
        )
    
    # Get recent metrics for readiness calculation
    recent_metrics = session.exec(
        select(MetricSample)
        .where(MetricSample.user_id == current_user.id)
        .order_by(MetricSample.date.desc())
        .limit(7)
    ).all()
    
    # Calculate readiness score (simplified logic)
    if recent_metrics:
        latest = recent_metrics[0]
        sleep_score = int(latest.sleep_h * 10) if latest.sleep_h else 75
        hr_rest = latest.stress if latest.stress else 60
        hrv = 70 + (sleep_score - 75) // 2  # Simple HRV calculation
        fatigue = "low" if sleep_score > 80 else "moderate" if sleep_score > 70 else "high"
        
        recommendation = "You're well recovered. Ready for high-intensity training."
        if fatigue == "moderate":
            recommendation = "You're moderately recovered. A steady training session is fine, but avoid max-intensity efforts."
        elif fatigue == "high":
            recommendation = "You need recovery. Focus on light activity or rest today."
    else:
        # Default values if no metrics
        sleep_score = 75
        hr_rest = 60
        hrv = 70
        fatigue = "moderate"
        recommendation = "No recent data. Consider logging your metrics for better insights."
    
    return ReadinessTodayResponse(
        sleep_score=sleep_score,
        hr_rest=hr_rest,
        hrv=hrv,
        fatigue=fatigue,
        recommendation=recommendation
    )
