from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from datetime import date, timedelta
from typing import List, Optional
from deps import get_current_user, get_session
from models import User, DiaryEntry
from schemas.api import DiaryCreateRequest, DiaryEntryResponse

router = APIRouter()

@router.get("/diary", response_model=List[DiaryEntryResponse], tags=["Frontend API"])
async def get_diary(
    from_date: Optional[date] = Query(None, description="Start date"),
    to_date: Optional[date] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get diary entries for the specified date range"""
    query = select(DiaryEntry).where(DiaryEntry.user_id == current_user.id)
    
    if from_date:
        query = query.where(DiaryEntry.date >= from_date)
    if to_date:
        query = query.where(DiaryEntry.date <= to_date)
    
    # Default to last 7 days if no dates specified
    if not from_date and not to_date:
        default_from = date.today() - timedelta(days=7)
        query = query.where(DiaryEntry.date >= default_from)
    
    entries = session.exec(query.order_by(DiaryEntry.date.desc())).all()
    
    return [
        DiaryEntryResponse(
            id=entry.id,
            date=entry.date.isoformat(),
            type=entry.type,
            text=entry.text
        )
        for entry in entries
    ]

@router.post("/diary", response_model=DiaryEntryResponse, tags=["Frontend API"])
async def create_diary_entry(
    request: DiaryCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new diary entry"""
    entry_date = request.date or date.today()
    
    entry = DiaryEntry(
        user_id=current_user.id,
        date=entry_date,
        type=request.type,
        text=request.text
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    
    return DiaryEntryResponse(
        id=entry.id,
        date=entry.date.isoformat(),
        type=entry.type,
        text=entry.text
    )
