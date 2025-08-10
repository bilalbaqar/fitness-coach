from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from deps import get_current_user, get_session
from models import User, Goal
from schemas.api import GoalCreateRequest, GoalResponse

router = APIRouter()

@router.get("/goals", response_model=List[GoalResponse], tags=["Frontend API"])
async def get_goals(
    session: Session = Depends(get_session)
):
    """Get all goals for current user (no auth required)"""
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
    
    goals = session.exec(
        select(Goal).where(Goal.user_id == user.id).order_by(Goal.created_at.desc())
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
    session: Session = Depends(get_session)
):
    """Create a new goal (no auth required)"""
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
    
    goal = Goal(
        user_id=user.id,
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
    session: Session = Depends(get_session)
):
    """Delete a goal (no auth required)"""
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
    
    goal = session.exec(
        select(Goal)
        .where(Goal.id == goal_id)
        .where(Goal.user_id == user.id)
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    session.delete(goal)
    session.commit()
    
    return {"ok": True}
