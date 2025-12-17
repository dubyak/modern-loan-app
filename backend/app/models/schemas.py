"""
Pydantic schemas for request/response models
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ============================================
# ENUMS
# ============================================

class UserRole(str, Enum):
    CUSTOMER = "customer"
    AGENT = "agent"
    ADMIN = "admin"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class LoanStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"
    DEFAULTED = "defaulted"

class TransactionType(str, Enum):
    DISBURSEMENT = "disbursement"
    REPAYMENT = "repayment"
    FEE = "fee"
    PENALTY = "penalty"
    REFUND = "refund"

class DocumentType(str, Enum):
    NATIONAL_ID = "national_id"
    BUSINESS_PHOTO = "business_photo"
    EVIDENCE = "evidence"
    OTHER = "other"

# ============================================
# AUTH SCHEMAS
# ============================================

class OTPRequest(BaseModel):
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')

class OTPVerify(BaseModel):
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    code: str = Field(..., min_length=4, max_length=6)

class RegisterRequest(BaseModel):
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class LoginRequest(BaseModel):
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    password: str = Field(..., min_length=8)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

# ============================================
# USER SCHEMAS
# ============================================

class UserBase(BaseModel):
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserResponse(UserBase):
    id: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# ============================================
# CUSTOMER PROFILE SCHEMAS
# ============================================

class CustomerProfileBase(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    business_location: Optional[str] = None
    business_description: Optional[str] = None
    years_in_business: Optional[float] = None
    monthly_revenue: Optional[float] = None
    monthly_expenses: Optional[float] = None
    national_id: Optional[str] = None

class CustomerProfileCreate(CustomerProfileBase):
    pass

class CustomerProfileUpdate(CustomerProfileBase):
    pass

class CustomerProfileResponse(CustomerProfileBase):
    id: str
    user_id: str
    onboarding_completed: bool
    onboarding_completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================
# LOAN SCHEMAS
# ============================================

class LoanCalculateRequest(BaseModel):
    amount: float = Field(..., gt=0)
    interest_rate: Optional[float] = None
    tenure_days: Optional[int] = Field(default=30, gt=0)

class LoanCalculateResponse(BaseModel):
    amount: float
    interest_rate: float
    tenure_days: int
    interest_amount: float
    total_repayment: float
    daily_interest: float

class LoanCreateRequest(BaseModel):
    amount: float = Field(..., gt=0)
    interest_rate: Optional[float] = None
    tenure_days: Optional[int] = Field(default=30, gt=0)
    ai_decision: Optional[str] = None
    ai_confidence: Optional[float] = None

class LoanResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    interest_rate: float
    tenure_days: int
    total_repayment: float
    status: LoanStatus
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    disbursed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    ai_decision: Optional[str] = None
    ai_confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LoanUpdateStatus(BaseModel):
    status: LoanStatus
    ai_decision: Optional[str] = None
    ai_confidence: Optional[float] = None

# ============================================
# TRANSACTION SCHEMAS
# ============================================

class TransactionCreate(BaseModel):
    loan_id: str
    type: TransactionType
    amount: float = Field(..., gt=0)
    reference_id: Optional[str] = None
    notes: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    loan_id: str
    user_id: str
    type: TransactionType
    amount: float
    balance_after: Optional[float] = None
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# AI/CONVERSATION SCHEMAS
# ============================================

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    thread_id: str
    role: str = "assistant"

class ThreadCreate(BaseModel):
    user_id: str

class ThreadResponse(BaseModel):
    id: str
    user_id: str
    openai_thread_id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================
# DOCUMENT SCHEMAS
# ============================================

class DocumentUploadResponse(BaseModel):
    id: str
    user_id: str
    type: DocumentType
    file_name: str
    file_url: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# ADMIN SCHEMAS
# ============================================

class AdminUserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    page_size: int

class AdminLoanListResponse(BaseModel):
    loans: List[LoanResponse]
    total: int
    page: int
    page_size: int
