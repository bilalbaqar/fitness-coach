from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date, timedelta
from typing import List, Optional
from deps import verify_agent_token, get_session
from models import User, MetricSample
from schemas.tools import GetCurrentMetricsRequest, GetCurrentMetricsResponse, MetricFactor

router = APIRouter()

@router.post("/getCurrentMetrics", response_model=GetCurrentMetricsResponse, tags=["Agent Tools"])
async def get_current_metrics(
    request: GetCurrentMetricsRequest,
    session: Session = Depends(get_session),
    _: bool = Depends(verify_agent_token)
):
    """
    Get current health metrics for the user.
    Returns the most recent metrics data with readiness insights.
    """
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
    
    # Get the most recent metrics (last 7 days)
    today = date.today()
    start_date = today - timedelta(days=7)
    
    recent_metrics = session.exec(
        select(MetricSample)
        .where(MetricSample.user_id == user.id)
        .where(MetricSample.date >= start_date)
        .order_by(MetricSample.date.desc())
    ).all()
    
    if not recent_metrics:
        # Return default metrics if no data exists
        return GetCurrentMetricsResponse(
            userId=str(user.id),
            date=today.isoformat(),
            currentMetrics={
                "sleep": 7.5,
                "stress": 30,
                "steps": 8000,
                "cardio": 50,
                "active": 35,
                "distance": 6.2,
                "calories": 2200
            },
            readinessScore=75,
            readinessStatus="moderate",
            recommendation="No recent data available. Consider logging your daily metrics for better insights.",
            factors=[
                MetricFactor(
                    name="Sleep",
                    value=7.5,
                    unit="hours",
                    impact="neutral",
                    description="Default sleep value"
                ),
                MetricFactor(
                    name="Stress",
                    value=30,
                    unit="score",
                    impact="positive",
                    description="Default stress level"
                ),
                MetricFactor(
                    name="Activity",
                    value=8000,
                    unit="steps",
                    impact="neutral",
                    description="Default step count"
                )
            ],
            notes="Using default metrics as no recent data is available."
        )
    
    # Get the most recent metric
    latest_metric = recent_metrics[0]
    
    # Calculate readiness score based on metrics
    sleep_score = int(latest_metric.sleep_h * 10) if latest_metric.sleep_h else 75
    stress_score = 100 - (latest_metric.stress or 30)  # Lower stress = higher score
    activity_score = min(100, (latest_metric.steps or 8000) // 100)  # 10k steps = 100 score
    
    # Calculate overall readiness score
    readiness_score = (sleep_score + stress_score + activity_score) // 3
    
    # Determine readiness status
    if readiness_score >= 80:
        readiness_status = "high"
        recommendation = "You're well recovered and ready for high-intensity training."
    elif readiness_score >= 60:
        readiness_status = "moderate"
        recommendation = "You're moderately recovered. A steady training session is fine, but avoid max-intensity efforts."
    else:
        readiness_status = "low"
        recommendation = "You need recovery. Focus on light activity or rest today."
    
    # Create factors list
    factors = []
    
    if latest_metric.sleep_h:
        sleep_impact = "positive" if latest_metric.sleep_h >= 7 else "negative" if latest_metric.sleep_h < 6 else "neutral"
        factors.append(MetricFactor(
            name="Sleep",
            value=latest_metric.sleep_h,
            unit="hours",
            impact=sleep_impact,
            description=f"Last night's sleep duration"
        ))
    
    if latest_metric.stress is not None:
        stress_impact = "positive" if latest_metric.stress <= 30 else "negative" if latest_metric.stress >= 70 else "neutral"
        factors.append(MetricFactor(
            name="Stress",
            value=latest_metric.stress,
            unit="score",
            impact=stress_impact,
            description="Current stress level (lower is better)"
        ))
    
    if latest_metric.steps:
        activity_impact = "positive" if latest_metric.steps >= 10000 else "neutral" if latest_metric.steps >= 6000 else "negative"
        factors.append(MetricFactor(
            name="Activity",
            value=latest_metric.steps,
            unit="steps",
            impact=activity_impact,
            description="Daily step count"
        ))
    
    if latest_metric.cardio is not None:
        cardio_impact = "positive" if latest_metric.cardio >= 60 else "neutral" if latest_metric.cardio >= 40 else "negative"
        factors.append(MetricFactor(
            name="Cardio",
            value=latest_metric.cardio,
            unit="minutes",
            impact=cardio_impact,
            description="Cardio exercise duration"
        ))
    
    if latest_metric.active_min:
        active_impact = "positive" if latest_metric.active_min >= 45 else "neutral" if latest_metric.active_min >= 30 else "negative"
        factors.append(MetricFactor(
            name="Active Minutes",
            value=latest_metric.active_min,
            unit="minutes",
            impact=active_impact,
            description="Active exercise minutes"
        ))
    
    # Generate notes based on metrics
    notes_parts = []
    if latest_metric.sleep_h and latest_metric.sleep_h < 7:
        notes_parts.append("Sleep duration is below recommended 7-9 hours.")
    if latest_metric.stress and latest_metric.stress > 50:
        notes_parts.append("Stress levels are elevated.")
    if latest_metric.steps and latest_metric.steps < 8000:
        notes_parts.append("Daily activity is below target.")
    
    notes = " ".join(notes_parts) if notes_parts else "Metrics look good overall."
    
    return GetCurrentMetricsResponse(
        userId=str(user.id),
        date=latest_metric.date.isoformat(),
        currentMetrics={
            "sleep": latest_metric.sleep_h or 7.5,
            "stress": latest_metric.stress or 30,
            "steps": latest_metric.steps or 8000,
            "cardio": latest_metric.cardio or 50,
            "active": latest_metric.active_min or 35,
            "distance": latest_metric.distance_km or 6.2,
            "calories": latest_metric.calories or 2200
        },
        readinessScore=readiness_score,
        readinessStatus=readiness_status,
        recommendation=recommendation,
        factors=factors,
        notes=notes
    )
