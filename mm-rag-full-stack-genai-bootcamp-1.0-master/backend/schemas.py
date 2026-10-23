from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    id: str
    email: str
    tenant_id: str
    role: str


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse