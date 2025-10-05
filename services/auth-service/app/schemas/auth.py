from pydantic import BaseModel, EmailStr



class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LogInRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str