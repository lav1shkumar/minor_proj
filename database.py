from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

import models  # Register table definitions before create_all() runs.

# Keep the database beside this file, regardless of where the app is started.
DATABASE_PATH = Path(__file__).with_name("database.db")

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
