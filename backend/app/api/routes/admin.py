"""
Admin routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from app.models.schemas import (
    AdminUserListResponse,
    AdminLoanListResponse,
    UserResponse,
    CustomerProfileResponse
)
from app.auth.dependencies import require_admin, require_agent_or_admin
from app.database import get_supabase

router = APIRouter()

@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    page: int = 1,
    page_size: int = 50,
    role: Optional[str] = None,
    current_user: dict = Depends(require_agent_or_admin)
):
    """List all users (admin/agent only)"""
    supabase = get_supabase()

    query = supabase.table("users").select("*", count="exact")

    if role:
        query = query.eq("role", role)

    # Pagination
    offset = (page - 1) * page_size
    result = query.order("created_at", desc=True)\
        .range(offset, offset + page_size - 1)\
        .execute()

    return {
        "users": result.data,
        "total": result.count,
        "page": page,
        "page_size": page_size
    }

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(require_agent_or_admin)
):
    """Get specific user (admin/agent only)"""
    supabase = get_supabase()

    result = supabase.table("users")\
        .select("*")\
        .eq("id", user_id)\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return result.data[0]

@router.get("/users/{user_id}/profile", response_model=CustomerProfileResponse)
async def get_user_profile(
    user_id: str,
    current_user: dict = Depends(require_agent_or_admin)
):
    """Get user's profile (admin/agent only)"""
    supabase = get_supabase()

    result = supabase.table("customer_profiles")\
        .select("*")\
        .eq("user_id", user_id)\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return result.data[0]

@router.get("/loans", response_model=AdminLoanListResponse)
async def list_loans(
    page: int = 1,
    page_size: int = 50,
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: dict = Depends(require_agent_or_admin)
):
    """List all loans (admin/agent only)"""
    supabase = get_supabase()

    query = supabase.table("loans").select("*", count="exact")

    if status:
        query = query.eq("status", status)

    if user_id:
        query = query.eq("user_id", user_id)

    # Pagination
    offset = (page - 1) * page_size
    result = query.order("created_at", desc=True)\
        .range(offset, offset + page_size - 1)\
        .execute()

    return {
        "loans": result.data,
        "total": result.count,
        "page": page,
        "page_size": page_size
    }

@router.get("/stats")
async def get_stats(current_user: dict = Depends(require_admin)):
    """Get platform statistics (admin only)"""
    supabase = get_supabase()

    # Count users
    users_result = supabase.table("users").select("*", count="exact", head=True).execute()
    total_users = users_result.count

    # Count loans by status
    loans_result = supabase.table("loans").select("status", count="exact").execute()

    loans_by_status = {}
    for loan in loans_result.data:
        status = loan["status"]
        loans_by_status[status] = loans_by_status.get(status, 0) + 1

    # Calculate total disbursed
    disbursed_result = supabase.table("loans")\
        .select("amount")\
        .in_("status", ["approved", "active", "completed"])\
        .execute()

    total_disbursed = sum(loan["amount"] for loan in disbursed_result.data)

    # Count active loans
    active_loans = supabase.table("loans")\
        .select("*", count="exact", head=True)\
        .eq("status", "active")\
        .execute()

    return {
        "total_users": total_users,
        "total_loans": loans_result.count,
        "loans_by_status": loans_by_status,
        "total_disbursed": total_disbursed,
        "active_loans": active_loans.count
    }

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status: str,
    current_user: dict = Depends(require_admin)
):
    """Update user status (admin only)"""
    supabase = get_supabase()

    if status not in ["active", "inactive", "suspended"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )

    result = supabase.table("users")\
        .update({"status": status})\
        .eq("id", user_id)\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": "User status updated", "user": result.data[0]}
