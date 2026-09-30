from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, params
from sqlmodel import Session, text
from database import create_db_and_tables, get_session
from routes import auth
from fastapi.middleware.cors import CORSMiddleware




@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI and uv!"}


@app.get("/db-check")
def check_database(session: Session = Depends(get_session)):

    session.exec(
        text("""INSERT INTO user (username, password, verified) VALUES (:username, :password, :verified)"""),
        params={"username": "john_doe", "password": "secret123","verified": False},
    )
    session.commit()

    result = session.exec(text("SELECT * FROM user")).mappings().all()


    print("Database check result:", result)
    return {"connected": result}
