#!/usr/bin/env python3
"""
Startup script for Railway deployment
Initializes database and seeds with demo data
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from db import create_db_and_tables
from models import User, MetricSample, Goal, DiaryEntry, WorkoutPlan, ReadinessSnapshot, ToolLog
from sqlmodel import Session, select
from datetime import date, timedelta
import json

def seed_database():
    """Seed the database with demo data"""
    from db import engine
    
    with Session(engine) as session:
        # Check if demo user already exists
        demo_user = session.exec(select(User).where(User.email == "demo@example.com")).first()
        
        if not demo_user:
            print("Creating demo user...")
            demo_user = User(
                email="demo@example.com",
                name="Demo User",
                height_cm=175.0,
                weight_kg=70.0
            )
            session.add(demo_user)
            session.commit()
            session.refresh(demo_user)
            print(f"Demo user created with ID: {demo_user.id}")
        else:
            print(f"Demo user already exists with ID: {demo_user.id}")
        
        # Add sample metrics if none exist
        existing_metrics = session.exec(select(MetricSample).where(MetricSample.user_id == demo_user.id)).first()
        if not existing_metrics:
            print("Adding sample metrics...")
            # Add 7 days of sample metrics
            for i in range(7):
                metric_date = date.today() - timedelta(days=i)
                metric = MetricSample(
                    user_id=demo_user.id,
                    date=metric_date,
                    sleep_h=7.5 + (i * 0.2),
                    stress=30 + (i * 2),
                    steps=8000 + (i * 200),
                    cardio=50 + (i * 1),
                    active_min=35 + (i * 1),
                    distance_km=6.2 + (i * 0.1),
                    calories=2200 + (i * 10)
                )
                session.add(metric)
            
            # Add sample goals
            goals_data = [
                {"category": "fitness", "text": "Run a 5K in under 25 minutes"},
                {"category": "strength", "text": "Bench press 100kg"},
                {"category": "health", "text": "Get 8 hours of sleep consistently"}
            ]
            
            for goal_data in goals_data:
                goal = Goal(
                    user_id=demo_user.id,
                    category=goal_data["category"],
                    text=goal_data["text"]
                )
                session.add(goal)
            
            # Add sample diary entries
            diary_entries = [
                {"type": "workout", "text": "Great strength training session today. Felt strong on squats."},
                {"type": "nutrition", "text": "Ate well today - lots of protein and vegetables."},
                {"type": "recovery", "text": "Good sleep last night, feeling refreshed."}
            ]
            
            for i, entry_data in enumerate(diary_entries):
                entry = DiaryEntry(
                    user_id=demo_user.id,
                    date=date.today() - timedelta(days=i),
                    type=entry_data["type"],
                    text=entry_data["text"]
                )
                session.add(entry)
            
            session.commit()
            print("Sample data added successfully!")
        else:
            print("Sample data already exists")

def main():
    """Main startup function"""
    print("🚀 Starting AI Sports Coach Backend...")
    
    # Create database tables
    print("📊 Creating database tables...")
    create_db_and_tables()
    print("✅ Database tables created")
    
    # Seed with demo data
    print("🌱 Seeding database with demo data...")
    seed_database()
    print("✅ Database seeded")
    
    print("🎉 Startup complete! Ready to serve requests.")

if __name__ == "__main__":
    main()
