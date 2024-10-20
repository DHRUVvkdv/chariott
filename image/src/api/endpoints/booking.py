from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.booking import BookingCreate, Booking, BookingUpdate
from services.booking_service import BookingService

router = APIRouter()


@router.post("/bookings", response_model=Booking)
async def create_booking(booking: BookingCreate):
    return await BookingService.create_booking(booking)


@router.get("/bookings/{booking_id}", response_model=Booking)
async def get_booking(booking_id: str):
    return await BookingService.get_booking(booking_id)


@router.get("/bookings", response_model=List[Booking])
async def get_all_bookings():
    return await BookingService.get_all_bookings()


@router.get("/bookings/current/{user_id}", response_model=List[Booking])
async def get_current_bookings(user_id: str):
    return await BookingService.get_current_bookings(user_id)


@router.get("/bookings/past/{user_id}", response_model=List[Booking])
async def get_past_bookings(user_id: str):
    return await BookingService.get_past_bookings(user_id)


@router.get("/bookings/future/{user_id}", response_model=List[Booking])
async def get_future_bookings(user_id: str):
    return await BookingService.get_future_bookings(user_id)


@router.put("/bookings/{booking_id}", response_model=Booking)
async def update_booking(booking_id: str, booking_update: BookingUpdate):
    return await BookingService.update_booking(booking_id, booking_update)


@router.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: str):
    return await BookingService.delete_booking(booking_id)
