from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# User schemas
class UserResponse(BaseModel):
    id: int
    name: str
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goals_summary: List[str]

# Readiness schemas
class ReadinessTodayResponse(BaseModel):
    sleep_score: Optional[int] = None
    hr_rest: Optional[int] = None
    hrv: Optional[int] = None
    fatigue: Optional[str] = None
    recommendation: str

# Metrics schemas
class MetricTimelineItem(BaseModel):
    date: str
    sleep: Optional[float] = None
    stress: Optional[int] = None
    steps: Optional[int] = None
    cardio: Optional[int] = None
    active: Optional[int] = None
    dist: Optional[float] = None
    cal: Optional[int] = None

class MetricsImportRequest(BaseModel):
    csv_data: str

class MetricsImportResponse(BaseModel):
    rows: int
    period_detected: str

# Regimen schemas
class RegimenPlanItem(BaseModel):
    day: str
    focus: str
    volume: float

class RegimenWeekResponse(BaseModel):
    plan: List[RegimenPlanItem]
    drills: List[str]

class RegimenUpdateRequest(BaseModel):
    changes: Dict[str, Any]
    reason: Optional[str] = None
    idempotency_key: Optional[str] = None

class RegimenUpdateResponse(BaseModel):
    ok: bool
    plan_id: int

# Video schemas
class VideoAnalyzeRequest(BaseModel):
    location: Optional[str] = None
    weather: Optional[str] = None

class VideoAnalyzeResponse(BaseModel):
    issues: List[str]
    positives: List[str]
    alternatives: List[str]
    location: Optional[str] = None
    weather: Optional[str] = None

# Goals schemas
class GoalCreateRequest(BaseModel):
    category: str
    text: str

class GoalResponse(BaseModel):
    id: int
    category: str
    text: str
    created: str

# Diary schemas
class DiaryCreateRequest(BaseModel):
    date: Optional[date] = None
    type: str
    text: str

class DiaryEntryResponse(BaseModel):
    id: int
    date: str
    type: str
    text: str

# Voice schemas
class TTSRequest(BaseModel):
    text: str
