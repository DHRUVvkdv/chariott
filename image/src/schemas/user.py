from pydantic import BaseModel, EmailStr, validator, Field
from enum import Enum
from typing import Optional


class UserType(str, Enum):
    NORMAL = "normal"
    STAFF = "staff"


class StaffType(str, Enum):
    HOUSEKEEPING = "housekeeping"
    MAINTENANCE = "maintenance"
    RECEPTION = "reception"
    MANAGER = "manager"


class UserBase(BaseModel):
    user_id: str
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    user_type: UserType
    staff_type: Optional[StaffType] = None

    @validator("staff_type")
    def validate_staff_type(cls, v, values):
        if values.get("user_type") == UserType.STAFF and v is None:
            raise ValueError("staff_type is required for staff users")
        if values.get("user_type") == UserType.NORMAL and v is not None:
            raise ValueError("staff_type should not be provided for normal users")
        return v


class UserInDB(UserBase):
    user_type: UserType
    staff_type: StaffType | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str
