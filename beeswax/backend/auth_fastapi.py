

# fastapi version
import email
from fastapi import APIRouter
from datetime import datetime, timezone
from utils import (
    get_hashed_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    JWT_SECRET_KEY, ALGORITHM,
    get_user_id
    )
from fastapi import status, HTTPException
from classes import RegisterRequest
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer()
# function wrapped around routes to take in db

def init_auth(db):
    auth_router = APIRouter(prefix="/auth", tags=["auth"])
    users = db["users"]

    @auth_router.post("/register", status_code=201)
    async def register(payload: RegisterRequest):
        
        if not payload.email or not payload.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing fields"
            )

        if users.find_one({"email": payload.email}):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )
        hashed_password = get_hashed_password(payload.password)
        users.insert_one({
            "email": payload.email,
            "password": hashed_password,
            "trust_score": 0,
            "created_at": datetime.now(timezone.utc)
        })
        return {"message": "User created"}
    

    @auth_router.post("/login", status_code=200)
    async def login(payload: RegisterRequest):
        user = users.find_one({"email": payload.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if not verify_password(payload.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        return {
            "access_token": create_access_token(user['email']),
            "refresh_token": create_refresh_token(user['email']),
        }
    
    @auth_router.get("/me", status_code=200)
    async def get_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> str:
        token = credentials.credentials

        try:
            user_id = get_user_id(token).get("sub") 
            if user_id == 'error':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            else:
                return user_id

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        
    return auth_router