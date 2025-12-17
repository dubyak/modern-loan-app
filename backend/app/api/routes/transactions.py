"""
Transaction routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.models.schemas import TransactionResponse
from app.auth.dependencies import get_current_active_user
from app.database import get_supabase

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
async def get_user_transactions(
    current_user: dict = Depends(get_current_active_user),
    loan_id: Optional[str] = None,
    limit: int = 50
):
    """Get transactions for current user"""
    supabase = get_supabase()

    query = supabase.table("transactions")\
        .select("*")\
        .eq("user_id", current_user["id"])

    if loan_id:
        query = query.eq("loan_id", loan_id)

    result = query.order("created_at", desc=True).limit(limit).execute()

    return result.data

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get specific transaction"""
    supabase = get_supabase()

    result = supabase.table("transactions")\
        .select("*")\
        .eq("id", transaction_id)\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    transaction = result.data[0]

    # Check permission
    if transaction["user_id"] != current_user["id"] and current_user["role"] not in ["admin", "agent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this transaction"
        )

    return transaction
