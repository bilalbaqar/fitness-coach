from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, JSON, Column
from pydantic import Json

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MetricSample(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: date
    sleep_h: Optional[float] = None
    stress: Optional[int] = None
    steps: Optional[int] = None
    cardio: Optional[int] = None
    active_min: Optional[int] = None
    distance_km: Optional[float] = None
    calories: Optional[int] = None

class ReadinessSnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: date
    score: int
    status: str
    factors_json: Dict[str, Any] = Field(sa_column=Column(JSON))
    recommendation: str

class WorkoutPlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    week_start: date
    plan_json: Dict[str, Any] = Field(sa_column=Column(JSON))

class WorkoutSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: date
    activity: str
    notes: Optional[str] = None
    data_json: Dict[str, Any] = Field(sa_column=Column(JSON))

class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category: str
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DiaryEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: date
    type: str
    text: str

class ToolLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tool: str
    user_id: Optional[int] = Field(foreign_key="user.id")
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    payload_json: Dict[str, Any] = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
