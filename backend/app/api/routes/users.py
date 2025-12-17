"""
User routes
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import UserResponse, UserUpdate, CustomerProfileResponse, CustomerProfileUpdate
from app.auth.dependencies import get_current_active_user
from app.database import get_supabase

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update current user information"""
    supabase = get_supabase()

    result = supabase.table("users")\
        .update(update_data.model_dump(exclude_unset=True))\
        .eq("id", current_user["id"])\
        .execute()

    return result.data[0]

@router.get("/me/profile", response_model=CustomerProfileResponse)
async def get_user_profile(current_user: dict = Depends(get_current_active_user)):
    """Get user's customer profile"""
    supabase = get_supabase()

    result = supabase.table("customer_profiles")\
        .select("*")\
        .eq("user_id", current_user["id"])\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return result.data[0]

@router.put("/me/profile", response_model=CustomerProfileResponse)
async def update_user_profile(
    update_data: CustomerProfileUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update user's customer profile"""
    supabase = get_supabase()

    result = supabase.table("customer_profiles")\
        .update(update_data.model_dump(exclude_unset=True))\
        .eq("user_id", current_user["id"])\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return result.data[0]
