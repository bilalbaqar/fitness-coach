from datetime import date, timedelta
from sqlmodel import Session, select
from db import engine
from models import User, MetricSample, Goal, DiaryEntry, WorkoutPlan, ReadinessSnapshot

def seed_database():
    """Seed the database with demo data"""
    with Session(engine) as session:
        # Check if demo user exists
        demo_user = session.exec(select(User).where(User.email == "demo@example.com")).first()
        
        if not demo_user:
            # Create demo user
            demo_user = User(
                email="demo@example.com",
                name="Demo User",
                height_cm=175.0,
                weight_kg=70.0
            )
            session.add(demo_user)
            session.commit()
            session.refresh(demo_user)
            print(f"Created demo user: {demo_user.name}")
        
        # Seed metrics for the last 30 days
        today = date.today()
        for i in range(30):
            metric_date = today - timedelta(days=i)
            
            # Check if metric already exists
            existing = session.exec(
                select(MetricSample)
                .where(MetricSample.user_id == demo_user.id)
                .where(MetricSample.date == metric_date)
            ).first()
            
            if not existing:
                # Generate realistic metrics
                base_sleep = 7.5 + (i % 3 - 1) * 0.5  # Vary sleep between 7-8 hours
                base_stress = 30 + (i % 5) * 5  # Vary stress between 30-55
                base_steps = 8000 + (i % 7) * 500  # Vary steps between 8000-11000
                
                metric = MetricSample(
                    user_id=demo_user.id,
                    date=metric_date,
                    sleep_h=base_sleep,
                    stress=base_stress,
                    steps=base_steps,
                    cardio=45 + (i % 3) * 5,
                    active_min=35 + (i % 4) * 5,
                    distance_km=6.0 + (i % 3) * 0.5,
                    calories=2200 + (i % 5) * 50
                )
                session.add(metric)
        
        # Seed goals
        goals_data = [
            ("speed", "Hit 31 km/h top speed"),
            ("passing", "Reach 88% pass accuracy"),
            ("endurance", "Complete 10km run under 45 minutes"),
            ("strength", "Bench press 100kg for 5 reps")
        ]
        
        for category, text in goals_data:
            existing_goal = session.exec(
                select(Goal)
                .where(Goal.user_id == demo_user.id)
                .where(Goal.category == category)
                .where(Goal.text == text)
            ).first()
            
            if not existing_goal:
                goal = Goal(
                    user_id=demo_user.id,
                    category=category,
                    text=text
                )
                session.add(goal)
        
        # Seed diary entries
        diary_data = [
            ("training", "5v5 small-sided, good pop"),
            ("eating", "Carb load pre-session"),
            ("recovery", "Ice bath after intense workout"),
            ("sleep", "Slept well, feeling refreshed"),
            ("training", "Speed drills and agility work")
        ]
        
        for i, (entry_type, text) in enumerate(diary_data):
            entry_date = today - timedelta(days=i+1)
            
            existing_entry = session.exec(
                select(DiaryEntry)
                .where(DiaryEntry.user_id == demo_user.id)
                .where(DiaryEntry.date == entry_date)
                .where(DiaryEntry.type == entry_type)
            ).first()
            
            if not existing_entry:
                entry = DiaryEntry(
                    user_id=demo_user.id,
                    date=entry_date,
                    type=entry_type,
                    text=text
                )
                session.add(entry)
        
        # Seed workout plan
        week_start = today - timedelta(days=today.weekday())
        existing_plan = session.exec(
            select(WorkoutPlan)
            .where(WorkoutPlan.user_id == demo_user.id)
            .where(WorkoutPlan.week_start == week_start)
        ).first()
        
        if not existing_plan:
            plan_data = {
                "plan": [
                    {
                        "day": "Monday",
                        "focus": "speed",
                        "volume": 1.0,
                        "exercises": [
                            {"name": "Sprint intervals", "sets": 6, "reps": 30, "rest_seconds": 90},
                            {"name": "Agility ladder", "sets": 3, "reps": 5, "rest_seconds": 60}
                        ]
                    },
                    {
                        "day": "Wednesday",
                        "focus": "passing",
                        "volume": 0.9,
                        "exercises": [
                            {"name": "Rondo 6v2", "sets": 4, "reps": 3, "rest_seconds": 120},
                            {"name": "Passing patterns", "sets": 3, "reps": 8, "rest_seconds": 90}
                        ]
                    },
                    {
                        "day": "Friday",
                        "focus": "conditioning",
                        "volume": 0.8,
                        "exercises": [
                            {"name": "HIIT intervals", "sets": 8, "reps": 45, "rest_seconds": 60},
                            {"name": "Small-sided games", "sets": 3, "reps": 6, "rest_seconds": 180}
                        ]
                    }
                ]
            }
            
            plan = WorkoutPlan(
                user_id=demo_user.id,
                week_start=week_start,
                plan_json=plan_data
            )
            session.add(plan)
        
        # Seed readiness snapshot for today
        existing_snapshot = session.exec(
            select(ReadinessSnapshot)
            .where(ReadinessSnapshot.user_id == demo_user.id)
            .where(ReadinessSnapshot.date == today)
        ).first()
        
        if not existing_snapshot:
            snapshot = ReadinessSnapshot(
                user_id=demo_user.id,
                date=today,
                score=78,
                status="moderate",
                factors_json={
                    "HRV": {"value": 74, "unit": "ms", "impact": "positive"},
                    "Resting Heart Rate": {"value": 62, "unit": "bpm", "impact": "neutral"},
                    "Sleep Quality": {"value": 82, "unit": "score", "impact": "positive"},
                    "Muscle Soreness": {"value": "mild", "impact": "negative"}
                },
                recommendation="You're moderately recovered. A steady training session is fine, but avoid max-intensity efforts."
            )
            session.add(snapshot)
        
        session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
