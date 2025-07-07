import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Определяем абсолютный путь к файлу базы данных, чтобы скрипты из
# любой директории работали с одной и той же БД.
backend_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(backend_dir, "test.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Database dependency function"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()