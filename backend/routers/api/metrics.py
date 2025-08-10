from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from datetime import date, timedelta
from typing import List
from deps import get_current_user, get_session
from models import User, MetricSample
from schemas.api import MetricTimelineItem, MetricsImportRequest, MetricsImportResponse

router = APIRouter()

@router.get("/metrics/timeline", response_model=List[MetricTimelineItem], tags=["Frontend API"])
async def get_metrics_timeline(
    period: str = Query("week", description="Time period: week or month"),
    session: Session = Depends(get_session)
):
    """Get metrics timeline for the specified period (no auth required)"""
    today = date.today()
    
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
    
    if period == "week":
        start_date = today - timedelta(days=7)
    elif period == "month":
        start_date = today - timedelta(days=30)
    else:
        start_date = today - timedelta(days=7)
    
    metrics = session.exec(
        select(MetricSample)
        .where(MetricSample.user_id == user.id)
        .where(MetricSample.date >= start_date)
        .order_by(MetricSample.date)
    ).all()
    
    timeline = []
    for metric in metrics:
        timeline.append(MetricTimelineItem(
            date=metric.date.isoformat(),
            sleep=metric.sleep_h,
            stress=metric.stress,
            steps=metric.steps,
            cardio=metric.cardio,
            active=metric.active_min,
            dist=metric.distance_km,
            cal=metric.calories
        ))
    
    return timeline

@router.post("/metrics/import", response_model=MetricsImportResponse, tags=["Frontend API"])
async def import_metrics(
    request: MetricsImportRequest,
    session: Session = Depends(get_session)
):
    """Import metrics from CSV data (no auth required)"""
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
    # Parse CSV data (reusing logic from frontend)
    lines = request.csv_data.strip().split('\n')
    if len(lines) < 2:  # Need header + at least one data row
        return MetricsImportResponse(rows=0, period_detected="unknown")
    
    # Skip header, parse data rows
    data_rows = []
    for line in lines[1:]:
        if line.strip():
            parts = line.split(',')
            if len(parts) >= 8:
                try:
                    metric = MetricSample(
                        user_id=user.id,
                        date=date.fromisoformat(parts[0]),
                        sleep_h=float(parts[1]) if parts[1] else None,
                        stress=int(parts[2]) if parts[2] else None,
                        steps=int(parts[3]) if parts[3] else None,
                        cardio=int(parts[4]) if parts[4] else None,
                        active_min=int(parts[5]) if parts[5] else None,
                        distance_km=float(parts[6]) if parts[6] else None,
                        calories=int(parts[7]) if parts[7] else None
                    )
                    data_rows.append(metric)
                except (ValueError, IndexError):
                    continue
    
    # Save to database
    for metric in data_rows:
        session.add(metric)
    session.commit()
    
    # Determine period
    if len(data_rows) <= 7:
        period_detected = "week"
    else:
        period_detected = "month"
    
    return MetricsImportResponse(
        rows=len(data_rows),
        period_detected=period_detected
    )
