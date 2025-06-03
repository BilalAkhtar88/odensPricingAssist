# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models.user import TokenResponse
from auth.auth_utils import hash_password, verify_password, create_access_token
from database.users import get_user, create_user

router = APIRouter()

@router.post("/signup", response_model=TokenResponse)
def signup(form_data: OAuth2PasswordRequestForm = Depends()):
    user_email = form_data.username
    password = form_data.password

    if get_user(user_email):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(password)
    create_user(user_email, hashed)

    token = create_access_token({"sub": user_email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_email = form_data.username
    password = form_data.password

    db_user = get_user(user_email)
    if not db_user or not verify_password(password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user_email})
    return {"access_token": token, "token_type": "bearer"}
