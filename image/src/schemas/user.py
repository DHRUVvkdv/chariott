from pydantic import BaseModel, EmailStr, validator, Field, model_validator
from enum import Enum
from typing import Optional, List, Dict


class UserType(str, Enum):
    NORMAL = "normal"
    STAFF = "staff"


class StaffType(str, Enum):
    HOUSEKEEPING = "housekeeping"
    MAINTENANCE = "maintenance"
    RECEPTION = "reception"
    MANAGER = "manager"


class DietaryRestriction(str, Enum):
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    OTHER = "other"


class MattressType(str, Enum):
    ANY = "any"
    MEMORY_FOAM = "memory foam"
    SPRING = "spring"
    MEDIUM = "medium"
    HARD = "hard"


class PillowType(str, Enum):
    ANY = "any"
    FEATHER = "feather"
    MEMORY = "memory"
    MICROFIBER = "microfiber"
    DOWN = "down"


class RoomView(str, Enum):
    CITY = "city"
    GARDEN = "garden"
    POOL = "pool"
    ANY = "any"


class LoyaltyProgram(str, Enum):
    PLATINUM = "platinum"
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"


class Preferences(BaseModel):
    dietary_restrictions: DietaryRestriction = DietaryRestriction.OTHER
    dietary_restrictions_other: Optional[str] = None
    bedding_pillows: int = Field(default=2, ge=0, le=5)
    bedding_mattress_type: MattressType = MattressType.ANY
    bedding_pillow_type: PillowType = PillowType.ANY
    bedding_other: Optional[str] = None
    climate_control: str = "Temperature set to 75°F"
    room_view: RoomView = RoomView.ANY
    quiet_room: bool = False
    misc: Optional[str] = None
    econ_rating: int = Field(default=0, ge=0, le=10)  # Added econ_rating field


class UserBase(BaseModel):
    user_id: str
    email: EmailStr
    first_name: str
    last_name: str
    loyalty_program: LoyaltyProgram


class User(UserBase):
    user_type: UserType
    staff_type: Optional[StaffType] = None
    preferences: Preferences = Field(default_factory=Preferences)
    recommendations: List[str] = []
    interaction_counter: int = 0
    loyalty_program: LoyaltyProgram

    @model_validator(mode="after")
    def validate_staff_type(self):
        if self.user_type == UserType.STAFF and self.staff_type is None:
            raise ValueError("staff_type is required for staff users")
        if self.user_type == UserType.NORMAL:
            self.staff_type = None  # Always set staff_type to None for normal users
        return self


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    user_type: UserType = UserType.NORMAL
    staff_type: Optional[StaffType] = None
    preferences: Preferences = Field(default_factory=Preferences)
    loyalty_program: LoyaltyProgram = LoyaltyProgram.BRONZE

    @validator("staff_type")
    def validate_staff_type(cls, v, values):
        if values.get("user_type") == UserType.STAFF and v is None:
            raise ValueError("staff_type is required for staff users")
        if values.get("user_type") == UserType.NORMAL and v is not None:
            raise ValueError("staff_type should not be provided for normal users")
        return v


class UserInDB(User):
    hashed_password: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str
