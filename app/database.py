from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Linking to the local SQLite file named as zorvyn.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./zorvyn.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
) # 'check_same_thread=False' is strictly required for SQLite to work with FastAPI's async routing

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This is the dependency injection. It gives our routers a database session & safely closes it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
