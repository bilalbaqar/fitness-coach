from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from deps import get_current_user, get_session
from models import User, Goal
from schemas.api import GoalCreateRequest, GoalResponse

router = APIRouter()

@router.get("/goals", response_model=List[GoalResponse], tags=["Frontend API"])
async def get_goals(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all goals for current user"""
    goals = session.exec(
        select(Goal).where(Goal.user_id == current_user.id).order_by(Goal.created_at.desc())
    ).all()
    
    return [
        GoalResponse(
            id=goal.id,
            category=goal.category,
            text=goal.text,
            created=goal.created_at.isoformat()
        )
        for goal in goals
    ]

@router.post("/goals", response_model=GoalResponse, tags=["Frontend API"])
async def create_goal(
    request: GoalCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new goal"""
    goal = Goal(
        user_id=current_user.id,
        category=request.category,
        text=request.text
    )
    session.add(goal)
    session.commit()
    session.refresh(goal)
    
    return GoalResponse(
        id=goal.id,
        category=goal.category,
        text=goal.text,
        created=goal.created_at.isoformat()
    )

@router.delete("/goals/{goal_id}", tags=["Frontend API"])
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a goal"""
    goal = session.exec(
        select(Goal)
        .where(Goal.id == goal_id)
        .where(Goal.user_id == current_user.id)
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    session.delete(goal)
    session.commit()
    
    return {"ok": True}
