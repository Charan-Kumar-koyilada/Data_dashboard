from sqlmodel import SQLModel, create_engine, Session
import os

# Database URL (creates SQLite file in project folder)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dataviz.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args={"check_same_thread": False}  # required for SQLite
)

# Function to create all tables
def init_db():
    SQLModel.metadata.create_all(engine)

# Function to get DB session
def get_session():
    with Session(engine) as session:
        yield session
