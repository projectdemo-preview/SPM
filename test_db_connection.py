from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URI = 'postgresql://postgres:python@localhost:5432/planner_db'

try:
    engine = create_engine(DATABASE_URI)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful!")
except SQLAlchemyError as e:
    print(f"Database connection failed: {str(e)}")
