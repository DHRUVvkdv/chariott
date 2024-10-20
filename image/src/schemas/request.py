from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional
from uuid import uuid4


class Department(str, Enum):
    RECEPTION = "reception"
    HOUSEKEEPING = "housekeeping"
    MAINTENANCE = "maintenance"


class RequestStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Request(BaseModel):
    request_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the request",
    )
    user_id: str = Field(..., description="ID of the user who created the request")
    hotel_id: str = Field(..., description="ID of the hotel where the request was made")
    department: Department = Field(
        ..., description="Department responsible for the request"
    )
    task: str = Field(..., description="Description of the task to be performed")
    time_issued: datetime = Field(
        default_factory=datetime.now, description="Time when the request was issued"
    )
    time_completed: Optional[datetime] = Field(
        None, description="Time when the request was completed"
    )
    status: RequestStatus = Field(
        default=RequestStatus.PENDING, description="Current status of the request"
    )


class RequestCreate(BaseModel):
    user_id: str
    hotel_id: str
    department: Department
    task: str


class RequestUpdate(BaseModel):
    status: RequestStatus
    time_completed: Optional[datetime] = None


class RequestResponse(Request):
    pass
