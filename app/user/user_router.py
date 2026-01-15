from fastapi import APIRouter, HTTPException, Depends, status
from app.user.user_schema import User, UserLogin, UserUpdate, UserDeleteRequest
from app.user.user_service import UserService
from app.dependencies import get_user_service
from app.responses.base_response import BaseResponse

user = APIRouter(prefix="/api/user")


@user.post("/login", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def login_user(user_login: UserLogin, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """
    /api/user/login Endpoint
    1. 유저 로그인
    2. 성공 시 BaseResponse[User] 반환
    3. 실패 시 HTTPException 반환 (400 Bad Request)
    """
    try:
        user = service.login(user_login)
        return BaseResponse(status="success", data=user, message="Login Success.") 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user.post("/register", response_model=BaseResponse[User], status_code=status.HTTP_201_CREATED)
def register_user(user: User, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """
    /api/user/register Endpoint
    1. 유저 회원가입
    2. 성공 시 BaseResponse[User] 반환
    3. 실패 시 HTTPException 반환 (400 Bad Request)
    """
    try:
        user = service.register_user(user)
        return BaseResponse(status="success", data=user, message="User registration success.") 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user.delete("/delete", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def delete_user(user_delete_request: UserDeleteRequest, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """
    /api/user/delete Endpoint
    1. 유저 회원탈퇴
    2. 성공 시 BaseResponse[User] 반환
    3. 실패 시 HTTPException 반환 (404 Not Found)
    """
    try:
        user = service.delete_user(user_delete_request.email)
        return BaseResponse(status="success", data=user, message="User Deletion Success.") 
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@user.put("/update-password", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def update_user_password(user_update: UserUpdate, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """
    /api/user/update-password Endpoint
    1. 유저 비밀번호 변경
    2. 성공 시 BaseResponse[User] 반환
    3. 실패 시 HTTPException 반환 (404 Not Found)
    """
    try:
        user = service.update_user_pwd(user_update)
        return BaseResponse(status="success", data=user, message="User password update success.") 
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
