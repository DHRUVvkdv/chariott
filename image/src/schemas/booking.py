from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum
from utils.utils import parse_est_datetime, format_est_datetime


class RoomSize(str, Enum):
    KING = "king"
    QUEEN = "queen"
    SUITE = "suite"
    STANDARD = "standard"


class RoomInfo(BaseModel):
    beds: int = Field(..., ge=1)
    bathrooms: int = Field(..., ge=1)
    size: RoomSize


class BookingBase(BaseModel):
    user_id: str
    hotel_id: str
    room_number: str
    start_date: datetime
    end_date: datetime
    hotel_name: str
    room_info: RoomInfo

    @validator("start_date", "end_date", pre=True)
    def parse_datetime(cls, value):
        if isinstance(value, str):
            return parse_est_datetime(value)
        return value

    class Config:
        json_encoders = {datetime: format_est_datetime}


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    booking_id: str

    class Config:
        from_attributes = True


class BookingUpdate(BaseModel):
    room_number: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    room_info: Optional[RoomInfo] = None

    @validator("start_date", "end_date", pre=True)
    def parse_datetime(cls, value):
        if isinstance(value, str):
            return parse_est_datetime(value)
        return value


class BookingInDB(Booking):
    pass
