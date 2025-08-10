from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from deps import get_current_user, get_session
from models import User, Goal
from schemas.api import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse, tags=["Frontend API"])
async def get_me(
    session: Session = Depends(get_session)
):
    """Get current user profile with goals summary (no auth required)"""
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
    
    # Get user's goals for summary
    goals = session.exec(
        select(Goal).where(Goal.user_id == user.id)
    ).all()
    
    goals_summary = [f"{goal.category}: {goal.text}" for goal in goals]
    
    return UserResponse(
        id=user.id,
        name=user.name,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        goals_summary=goals_summary
    )
