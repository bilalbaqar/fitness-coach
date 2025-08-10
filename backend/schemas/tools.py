from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# Base tool response
class ToolResponse(BaseModel):
    ok: bool
    error: Optional[str] = None
    hint: Optional[str] = None

# Get Current Metrics
class GetCurrentMetricsRequest(BaseModel):
    user_id: Optional[str] = None  # Optional for demo user

class MetricFactor(BaseModel):
    name: str
    value: float
    unit: str
    impact: str  # "positive" | "neutral" | "negative"
    description: str

class GetCurrentMetricsResponse(BaseModel):
    userId: str
    date: str
    currentMetrics: Dict[str, float]
    readinessScore: int
    readinessStatus: str
    recommendation: str
    factors: List[MetricFactor]
    notes: str

# Get Readiness Score
class GetReadinessScoreRequest(BaseModel):
    user_id: Optional[str] = None  # Optional for demo user
    date: Optional[str] = None  # Accept string date or None

class ReadinessFactor(BaseModel):
    name: str
    value: Any
    unit: Optional[str] = None
    impact: str  # "positive" | "neutral" | "negative"

class ReadinessScore(BaseModel):
    score: int
    status: str
    recommendation: str
    factors: List[ReadinessFactor]

class GetReadinessScoreResponse(BaseModel):
    user_id: str
    date: str
    readiness_score: ReadinessScore
    notes: Optional[str] = None

# Get Workout History
class GetWorkoutHistoryRequest(BaseModel):
    user_id: str
    range: str  # "7d" | "30d"

class WorkoutHistoryItem(BaseModel):
    date: str
    activity: str
    duration_min: Optional[int] = None
    intensity: Optional[str] = None
    notes: Optional[str] = None

class GetWorkoutHistoryResponse(BaseModel):
    workouts: List[WorkoutHistoryItem]

# Get Workout Plan
class GetWorkoutPlanRequest(BaseModel):
    user_id: str
    week_start: Optional[date] = None

class Exercise(BaseModel):
    name: str
    sets: int
    reps: int
    rest_seconds: int

class WorkoutPlanDay(BaseModel):
    day: str
    exercises: List[Exercise]
    notes: Optional[str] = None

class GetWorkoutPlanResponse(BaseModel):
    plan: List[WorkoutPlanDay]

# Update Workout Plan
class UpdateWorkoutPlanRequest(BaseModel):
    user_id: str
    changes: Dict[str, Any]
    reason: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

class UpdateWorkoutPlanResponse(BaseModel):
    ok: bool
    plan_id: str

# Log Workout Session
class WorkoutSet(BaseModel):
    name: str
    load_kg: Optional[float] = None
    reps: Optional[int] = None
    duration_s: Optional[int] = None
    rpe: Optional[int] = None

class WorkoutSessionData(BaseModel):
    date: date
    activity: str
    sets: List[WorkoutSet]
    notes: Optional[str] = None

class LogWorkoutSessionRequest(BaseModel):
    user_id: str
    session: WorkoutSessionData
    session_id: Optional[str] = None
    request_id: Optional[str] = None

class LogWorkoutSessionResponse(BaseModel):
    ok: bool
    session_id: str

# Log Daily Note
class LogDailyNoteRequest(BaseModel):
    user_id: str
    date: date
    type: str  # "training" | "eating" | "sleep" | "recovery"
    text: str

class LogDailyNoteResponse(BaseModel):
    ok: bool
    note_id: str

# Analyze Pose
class AnalyzePoseRequest(BaseModel):
    user_id: str
    snapshot_base64: Optional[str] = None
    keypoints: Optional[List[Dict[str, Any]]] = None

class AnalyzePoseResponse(BaseModel):
    flags: List[str]
    cues: List[str]

# Finalize Session
class FinalizeSessionRequest(BaseModel):
    user_id: str
    session_id: str
    summary: str
    actions: List[str]

class FinalizeSessionResponse(BaseModel):
    ok: bool
    recap_id: str
