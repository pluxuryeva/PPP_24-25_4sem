from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.cruds.user import get_user_by_email, create_user, authenticate_user, create_access_token
from app.schemas.schemas import UserCreate, UserResponse, UserLogin
from app.services.auth import get_current_user
from app.models.models import User

router = APIRouter()


@router.post("/sign-up/", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    db_user = create_user(db=db, user=user)
    token = create_access_token(data={"sub": db_user.email})
    
    return {"id": db_user.id, "email": db_user.email, "token": token}


@router.post("/login/", response_model=UserResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token(data={"sub": db_user.email})
    return {"id": db_user.id, "email": db_user.email, "token": token}


@router.get("/users/me/", response_model=UserResponse)
def get_users_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email} 