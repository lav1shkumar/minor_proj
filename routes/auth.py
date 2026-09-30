from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pwdlib import PasswordHash
import jwt
from sqlmodel import Session, text
from database import get_session
from dotenv import load_dotenv
import os
import time



load_dotenv()  # Load environment variables from .env file


router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hasher.verify(password, hashed_password)

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="User is not logged in")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp", "sub", "user_id"]})
        
        return {"user_id": payload["user_id"], "username": payload["sub"]}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


class LoginRequest(BaseModel):
    username: str
    password: str

@router.get("/login", status_code=200)
def login(body: LoginRequest,response:Response, session: Session = Depends(get_session)):
    username = body.username
    password = body.password

    result = session.exec(
        text("""Select * from user where username = :username"""),
        params={"username": username},
    ).mappings().all()
    
    if len(result) == 0:
        return JSONResponse(status_code=400, content={"message": "Invalid username or password"})

    user = result[0]
    if not verify_password(password, user["password"]):
        return JSONResponse(status_code=400, content={"message": "Invalid username or password"})


    jwt_payload = {
        "sub": user["username"],
        "user_id": user["id"],
        "exp": time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

    jwt_token = jwt.encode(jwt_payload, SECRET_KEY, algorithm=ALGORITHM)


    response.set_cookie(
        key="access_token",
        value=jwt_token,
        secure=True,  # Set to True in production with HTTPS
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        path="/"
    )
    return {"message": "Login Successful"}


class RegisterRequest(BaseModel):
    username: str
    password: str

@router.post("/register", status_code=201)
def register(body: RegisterRequest, session: Session = Depends(get_session)):

    username = body.username
    password = body.password

    result = session.exec(
        text("""Select * from user where username = :username"""),
        params={"username": username},
    ).mappings().all()

    if(len(result) > 0):
        return JSONResponse(status_code=400, content={"message": "Username already exists"})

    hashed_password = hash_password(password)
    session.exec(
        text("""INSERT INTO user (username, password, verified) VALUES (:username, :password, :verified)"""),
        params={"username": username, "password": hashed_password, "verified": False},
    )
    session.commit()

    return {"message": "Successfully registered user", "username": username}


@router.delete("/logout")
def logout(request: Request, response: Response):
    if(request.cookies.get("access_token") is None):
        return JSONResponse(status_code=400, content={"message": "User is not logged in"})

    response.delete_cookie(key="access_token", path="/")
    return {"message": "Successfully logged out"}
