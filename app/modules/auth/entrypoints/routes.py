from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.application.login import (
    InactiveUserError,
    InvalidCredentialsError,
    LoginUser,
    LoginUserCommand,
)
from app.modules.auth.application.register import (
    RegisterUser,
    RegisterUserCommand,
    UsernameAlreadyExistsError,
)
from app.modules.auth.entrypoints.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)
from app.modules.auth.wiring import get_current_user, get_login_user, get_register_user
from app.modules.users.domain.user import User


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    register_user: RegisterUser = Depends(get_register_user),
) -> UserResponse:
    try:
        user = register_user.execute(
            RegisterUserCommand(
                username=request.username,
                password=request.password,
            )
        )
    except UsernameAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    return UserResponse.from_public_user(user)


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    login_user: LoginUser = Depends(get_login_user),
) -> LoginResponse:
    try:
        result = login_user.execute(
            LoginUserCommand(
                username=request.username,
                password=request.password,
            )
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InactiveUserError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return LoginResponse.from_result(result)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.from_domain(current_user)
