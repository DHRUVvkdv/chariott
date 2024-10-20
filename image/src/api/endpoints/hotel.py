from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.hotel import HotelCreate, Hotel, HotelUpdate
from services.hotel_service import HotelService

router = APIRouter()


@router.post("/hotels", response_model=Hotel)
async def create_hotel(hotel: HotelCreate):
    return await HotelService.create_hotel(hotel)


@router.get("/hotels/{hotel_id}", response_model=Hotel)
async def get_hotel(hotel_id: str):
    return await HotelService.get_hotel(hotel_id)


@router.get("/hotels", response_model=List[Hotel])
async def get_all_hotels():
    return await HotelService.get_all_hotels()


@router.put("/hotels/{hotel_id}", response_model=Hotel)
async def update_hotel(hotel_id: str, hotel_update: HotelUpdate):
    return await HotelService.update_hotel(hotel_id, hotel_update)


@router.delete("/hotels/{hotel_id}")
async def delete_hotel(hotel_id: str):
    return await HotelService.delete_hotel(hotel_id)
