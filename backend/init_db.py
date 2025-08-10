from db import create_db_and_tables
from models import User, MetricSample, Goal, DiaryEntry, WorkoutPlan, ReadinessSnapshot, ToolLog

def init_database():
    """Initialize the database by creating all tables"""
    print("Creating database tables...")
    create_db_and_tables()
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
