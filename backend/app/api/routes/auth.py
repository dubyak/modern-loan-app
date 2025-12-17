"""
Authentication routes
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta

from app.models.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    OTPRequest,
    OTPVerify,
    UserResponse
)
from app.auth.utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    generate_otp,
    get_otp_expiry
)
from app.database import get_supabase
from app.config import settings

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """Register a new user"""
    supabase = get_supabase()

    # Check if phone already exists
    existing = supabase.table("users").select("*").eq("phone", request.phone).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    # Create user in Supabase Auth
    try:
        auth_response = supabase.auth.sign_up({
            "phone": request.phone,
            "password": request.password
        })

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )

        # Create user record
        user_data = {
            "id": auth_response.user.id,
            "phone": request.phone,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "role": "customer",
            "status": "active"
        }

        user = supabase.table("users").insert(user_data).execute()

        # Create empty customer profile
        supabase.table("customer_profiles").insert({
            "user_id": auth_response.user.id
        }).execute()

        # Create JWT token
        access_token = create_access_token(
            data={"sub": auth_response.user.id}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.data[0]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login user"""
    supabase = get_supabase()

    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "phone": request.phone,
            "password": request.password
        })

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Get user data
        user = supabase.table("users").select("*").eq("id", auth_response.user.id).execute()

        if not user.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if user is active
        if user.data[0]["status"] != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )

        # Create JWT token
        access_token = create_access_token(
            data={"sub": auth_response.user.id}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.post("/send-otp")
async def send_otp(request: OTPRequest):
    """Send OTP to phone number"""
    supabase = get_supabase()

    # Generate OTP
    code = generate_otp()
    expires_at = get_otp_expiry()

    # Store OTP in database
    supabase.table("otp_verifications").insert({
        "phone": request.phone,
        "code": code,
        "expires_at": expires_at.isoformat()
    }).execute()

    # TODO: Send OTP via SMS provider (Twilio, Africa's Talking, etc.)
    # For now, return the code in development mode only
    response = {"message": "OTP sent successfully"}

    if settings.DEBUG:
        response["code"] = code  # Only in development!

    return response

@router.post("/verify-otp")
async def verify_otp(request: OTPVerify):
    """Verify OTP code"""
    supabase = get_supabase()

    # Get OTP from database
    result = supabase.table("otp_verifications")\
        .select("*")\
        .eq("phone", request.phone)\
        .eq("code", request.code)\
        .eq("verified", False)\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    otp = result.data[0]

    # Check if expired
    from datetime import datetime
    if datetime.fromisoformat(otp["expires_at"].replace("Z", "+00:00")) < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired"
        )

    # Mark as verified
    supabase.table("otp_verifications")\
        .update({"verified": True})\
        .eq("id", otp["id"])\
        .execute()

    return {"message": "OTP verified successfully", "verified": True}
