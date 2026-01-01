import os
from pathlib import Path
from sqlmodel import create_engine
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:makikotori@localhost:5432/optcg")

# Ensure the connection string uses the correct driver format
# Replace postgresql:// with postgresql+psycopg2:// if not already specified
if DATABASE_URL.startswith("postgresql://") and "+" not in DATABASE_URL.split("://")[0]:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(str(DATABASE_URL))
