"""
Loan routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timedelta

from app.models.schemas import (
    LoanCalculateRequest,
    LoanCalculateResponse,
    LoanCreateRequest,
    LoanResponse,
    LoanUpdateStatus
)
from app.auth.dependencies import get_current_active_user, require_agent_or_admin
from app.database import get_supabase
from app.config import settings

router = APIRouter()

@router.post("/calculate", response_model=LoanCalculateResponse)
async def calculate_loan(request: LoanCalculateRequest):
    """Calculate loan offer without authentication"""
    amount = request.amount
    interest_rate = request.interest_rate or settings.DEFAULT_INTEREST_RATE
    tenure_days = request.tenure_days or settings.DEFAULT_LOAN_TENURE_DAYS

    # Validate amount
    if amount < settings.MIN_LOAN_AMOUNT or amount > settings.MAX_LOAN_AMOUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Loan amount must be between {settings.MIN_LOAN_AMOUNT} and {settings.MAX_LOAN_AMOUNT}"
        )

    # Calculate interest
    interest_amount = (amount * interest_rate / 100) * (tenure_days / 30)
    total_repayment = amount + interest_amount
    daily_interest = interest_amount / tenure_days

    return {
        "amount": amount,
        "interest_rate": interest_rate,
        "tenure_days": tenure_days,
        "interest_amount": round(interest_amount, 2),
        "total_repayment": round(total_repayment, 2),
        "daily_interest": round(daily_interest, 2)
    }

@router.post("/", response_model=LoanResponse)
async def create_loan(
    request: LoanCreateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new loan application"""
    supabase = get_supabase()

    # Calculate loan details
    calc_result = await calculate_loan(LoanCalculateRequest(
        amount=request.amount,
        interest_rate=request.interest_rate,
        tenure_days=request.tenure_days
    ))

    # Create loan
    loan_data = {
        "user_id": current_user["id"],
        "amount": request.amount,
        "interest_rate": calc_result.interest_rate,
        "tenure_days": calc_result.tenure_days,
        "total_repayment": calc_result.total_repayment,
        "status": "pending",
        "ai_decision": request.ai_decision,
        "ai_confidence": request.ai_confidence,
        "due_date": (datetime.utcnow() + timedelta(days=calc_result.tenure_days)).isoformat()
    }

    result = supabase.table("loans").insert(loan_data).execute()

    return result.data[0]

@router.get("/", response_model=List[LoanResponse])
async def get_user_loans(current_user: dict = Depends(get_current_active_user)):
    """Get all loans for current user"""
    supabase = get_supabase()

    result = supabase.table("loans")\
        .select("*")\
        .eq("user_id", current_user["id"])\
        .order("created_at", desc=True)\
        .execute()

    return result.data

@router.get("/{loan_id}", response_model=LoanResponse)
async def get_loan(
    loan_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get specific loan details"""
    supabase = get_supabase()

    result = supabase.table("loans")\
        .select("*")\
        .eq("id", loan_id)\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )

    loan = result.data[0]

    # Check permission
    if loan["user_id"] != current_user["id"] and current_user["role"] not in ["admin", "agent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this loan"
        )

    return loan

@router.put("/{loan_id}/status", response_model=LoanResponse)
async def update_loan_status(
    loan_id: str,
    status_update: LoanUpdateStatus,
    current_user: dict = Depends(require_agent_or_admin)
):
    """Update loan status (admin/agent only)"""
    supabase = get_supabase()

    update_data = {
        "status": status_update.status.value,
        "ai_decision": status_update.ai_decision,
        "ai_confidence": status_update.ai_confidence
    }

    if status_update.status.value == "approved":
        update_data["approved_by"] = current_user["id"]
        update_data["approved_at"] = datetime.utcnow().isoformat()

    result = supabase.table("loans")\
        .update(update_data)\
        .eq("id", loan_id)\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )

    return result.data[0]

@router.post("/{loan_id}/accept", response_model=LoanResponse)
async def accept_loan(
    loan_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Accept a loan offer"""
    supabase = get_supabase()

    # Get loan
    loan_result = supabase.table("loans")\
        .select("*")\
        .eq("id", loan_id)\
        .eq("user_id", current_user["id"])\
        .execute()

    if not loan_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )

    loan = loan_result.data[0]

    if loan["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Loan cannot be accepted in current status"
        )

    # Update loan status
    updated_loan = supabase.table("loans")\
        .update({
            "status": "approved",
            "approved_at": datetime.utcnow().isoformat()
        })\
        .eq("id", loan_id)\
        .execute()

    # Create disbursement transaction
    supabase.table("transactions").insert({
        "loan_id": loan_id,
        "user_id": current_user["id"],
        "type": "disbursement",
        "amount": loan["amount"],
        "balance_after": loan["total_repayment"],
        "notes": "Loan disbursement"
    }).execute()

    return updated_loan.data[0]
