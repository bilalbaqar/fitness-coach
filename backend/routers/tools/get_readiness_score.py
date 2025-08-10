from fastapi import APIRouter, Depends, Header
from sqlmodel import Session, select
from datetime import date
from typing import Optional
from deps import verify_agent_token, get_session
from models import User, ReadinessSnapshot, MetricSample
from schemas.tools import GetReadinessScoreRequest, GetReadinessScoreResponse, ReadinessScore, ReadinessFactor

router = APIRouter()

@router.post("/getReadinessScore", response_model=GetReadinessScoreResponse, tags=["Agent Tools"])
async def get_readiness_score_tool(
    request: GetReadinessScoreRequest,
    session: Session = Depends(get_session),
    _: bool = Depends(verify_agent_token)
):
    """Get readiness score for a user (agent tool)"""
    # Get the first user (demo user)
    user = session.exec(select(User)).first()
    
    if not user:
        # Create demo user if none exists
        user = User(
            email="demo@example.com",
            name="Demo User",
            height_cm=175.0,
            weight_kg=70.0
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    
    # Handle date parameter (string or None)
    if request.date:
        try:
            target_date = date.fromisoformat(request.date)
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()
    
    # Check for cached readiness snapshot
    snapshot = session.exec(
        select(ReadinessSnapshot)
        .where(ReadinessSnapshot.user_id == user.id)
        .where(ReadinessSnapshot.date == target_date)
    ).first()
    
    if snapshot:
        # Return cached snapshot
        factors = []
        for factor_name, factor_data in snapshot.factors_json.items():
            if isinstance(factor_data, dict):
                factors.append(ReadinessFactor(
                    name=factor_name,
                    value=factor_data.get("value", 0),
                    unit=factor_data.get("unit"),
                    impact=factor_data.get("impact", "neutral")
                ))
            else:
                factors.append(ReadinessFactor(
                    name=factor_name,
                    value=factor_data,
                    impact="neutral"
                ))
        
        return GetReadinessScoreResponse(
            user_id=str(user.id),
            date=target_date.isoformat(),
            readiness_score=ReadinessScore(
                score=snapshot.score,
                status=snapshot.status,
                recommendation=snapshot.recommendation,
                factors=factors
            )
        )
    
    # Calculate readiness from metrics
    recent_metrics = session.exec(
        select(MetricSample)
        .where(MetricSample.user_id == user.id)
        .order_by(MetricSample.date.desc())
        .limit(7)
    ).all()
    
    if recent_metrics:
        latest = recent_metrics[0]
        
        # Calculate factors
        factors = []
        
        # Sleep quality
        if latest.sleep_h:
            sleep_score = int(latest.sleep_h * 10)
            factors.append(ReadinessFactor(
                name="Sleep Quality",
                value=sleep_score,
                unit="score",
                impact="positive" if sleep_score > 80 else "neutral" if sleep_score > 70 else "negative"
            ))
        
        # Resting heart rate
        if latest.stress:  # Using stress as proxy for HR
            hr_rest = latest.stress
            factors.append(ReadinessFactor(
                name="Resting Heart Rate",
                value=hr_rest,
                unit="bpm",
                impact="positive" if hr_rest < 60 else "neutral" if hr_rest < 70 else "negative"
            ))
        
        # HRV (calculated)
        if latest.sleep_h:
            hrv = 70 + (int(latest.sleep_h * 10) - 75) // 2
            factors.append(ReadinessFactor(
                name="HRV",
                value=hrv,
                unit="ms",
                impact="positive" if hrv > 75 else "neutral" if hrv > 65 else "negative"
            ))
        
        # Overall score calculation
        positive_factors = sum(1 for f in factors if f.impact == "positive")
        negative_factors = sum(1 for f in factors if f.impact == "negative")
        
        if positive_factors > negative_factors:
            score = 85
            status = "good"
            recommendation = "You're well recovered. Ready for high-intensity training."
        elif negative_factors > positive_factors:
            score = 45
            status = "poor"
            recommendation = "You need recovery. Focus on light activity or rest today."
        else:
            score = 65
            status = "moderate"
            recommendation = "You're moderately recovered. A steady training session is fine, but avoid max-intensity efforts."
    else:
        # Default values
        score = 50
        status = "unknown"
        recommendation = "No recent data available. Consider logging your metrics for better insights."
        factors = []
    
    return GetReadinessScoreResponse(
        user_id=str(user.id),
        date=target_date.isoformat(),
        readiness_score=ReadinessScore(
            score=score,
            status=status,
            recommendation=recommendation,
            factors=factors
        ),
        notes="Calculated from recent metrics" if recent_metrics else "No metrics available"
    )
