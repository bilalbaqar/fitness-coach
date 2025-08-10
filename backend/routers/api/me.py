from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from deps import get_current_user, get_session
from models import User, Goal
from schemas.api import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse, tags=["Frontend API"])
async def get_me(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get current user profile with goals summary"""
    # Get user's goals for summary
    goals = session.exec(
        select(Goal).where(Goal.user_id == current_user.id)
    ).all()
    
    goals_summary = [f"{goal.category}: {goal.text}" for goal in goals]
    
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        height_cm=current_user.height_cm,
        weight_kg=current_user.weight_kg,
        goals_summary=goals_summary
    )
