from datetime import datetime
from pydantic import BaseModel, EmailStr, constr


class UserBaseSchema(BaseModel):
    name: str
    email: str
    password: str

    otp_enabled: bool = False
    otp_verified: bool = False

    otp_base32: str | None = None
    otp_auth_url: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserRequestSchema(BaseModel):
    user_id: str
    token: str | None = None
