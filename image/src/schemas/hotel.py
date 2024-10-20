from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional, Union


class Location(BaseModel):
    city: str
    state: str
    country: str


class CommunityProject(BaseModel):
    image_url: Union[HttpUrl, str]
    title: str
    description: str

    @validator("image_url", pre=True)
    def parse_image_url(cls, v):
        if isinstance(v, str):
            return HttpUrl(v)
        return v


class Amenities(BaseModel):
    breakfast: bool
    bar: bool
    room_service: bool
    pet_friendly: bool
    front_desk_24_7: bool
    parking: bool


class HotelBase(BaseModel):
    chain_id: Optional[str] = None
    name: str
    eco_rating: int = Field(..., ge=0, le=10)
    location: Location
    local_community_projects: List[CommunityProject] = []
    amenities: Amenities


class HotelCreate(HotelBase):
    pass


class Hotel(HotelBase):
    hotel_id: str

    class Config:
        from_attributes = True


class HotelUpdate(BaseModel):
    chain_id: Optional[str] = None
    name: Optional[str] = None
    eco_rating: Optional[int] = Field(None, ge=0, le=10)
    location: Optional[Location] = None
    local_community_projects: Optional[List[CommunityProject]] = None
    amenities: Optional[Amenities] = None


class HotelInDB(Hotel):
    pass
