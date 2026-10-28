import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


def get_database_url() -> str:
    host = os.getenv("FSTR_DB_HOST", "localhost")
    port = os.getenv("FSTR_DB_PORT", "5432")
    login = os.getenv("FSTR_LOGIN", "postgres")
    password = os.getenv("FSTR_PASS", "postgres")
    database = os.getenv("FSTR_DB_NAME", "pereval")
    return f"postgresql+psycopg://{login}:{password}@{host}:{port}/{database}"


engine = create_engine(get_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
