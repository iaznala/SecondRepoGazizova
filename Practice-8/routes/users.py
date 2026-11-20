from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from models.users import User, UserSignIn

user_router = APIRouter()


class UserCreate(BaseModel):
    email: EmailStr
    password: str


@user_router.post("/signup")
async def sign_new_user(data: UserCreate):
    existing_user = await User.find_one(User.email == data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with supplied username exists"
        )

    new_user = User(
        email=data.email,
        password=data.password,
        events=[]
    )

    await new_user.create()

    return {"message": "User successfully registered!"}


@user_router.post("/signin")
async def sign_user_in(user: UserSignIn):
    existing_user = await User.find_one(User.email == user.email)

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist"
        )

    if existing_user.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong credentials passed"
        )

    return {"message": "User signed in successfully"}