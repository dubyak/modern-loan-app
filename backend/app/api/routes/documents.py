"""
Document upload routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List
import uuid

from app.models.schemas import DocumentUploadResponse, DocumentType
from app.auth.dependencies import get_current_active_user
from app.database import get_supabase
from app.config import settings

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    current_user: dict = Depends(get_current_active_user)
):
    """Upload a document"""
    supabase = get_supabase()

    # Validate file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}"
        )

    # Validate file size
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum of {settings.MAX_FILE_SIZE_MB}MB"
        )

    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    storage_path = f"{current_user['id']}/{document_type.value}/{unique_filename}"

    try:
        # Upload to Supabase Storage
        storage = supabase.storage.from_("documents")
        upload_response = storage.upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": file.content_type}
        )

        # Get public URL (or create signed URL for private buckets)
        file_url = storage.get_public_url(storage_path)

        # Store document record in database
        document_data = {
            "user_id": current_user["id"],
            "type": document_type.value,
            "file_name": file.filename,
            "file_url": file_url,
            "storage_path": storage_path,
            "file_size": file_size,
            "mime_type": file.content_type
        }

        result = supabase.table("documents").insert(document_data).execute()

        return result.data[0]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )

@router.get("/", response_model=List[DocumentUploadResponse])
async def get_user_documents(
    current_user: dict = Depends(get_current_active_user),
    document_type: DocumentType = None
):
    """Get user's documents"""
    supabase = get_supabase()

    query = supabase.table("documents")\
        .select("*")\
        .eq("user_id", current_user["id"])

    if document_type:
        query = query.eq("type", document_type.value)

    result = query.order("created_at", desc=True).execute()

    return result.data

@router.get("/{document_id}", response_model=DocumentUploadResponse)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get specific document"""
    supabase = get_supabase()

    result = supabase.table("documents")\
        .select("*")\
        .eq("id", document_id)\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    document = result.data[0]

    # Check permission
    if document["user_id"] != current_user["id"] and current_user["role"] not in ["admin", "agent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this document"
        )

    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete a document"""
    supabase = get_supabase()

    # Get document
    doc_result = supabase.table("documents")\
        .select("*")\
        .eq("id", document_id)\
        .execute()

    if not doc_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    document = doc_result.data[0]

    # Check permission
    if document["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this document"
        )

    # Delete from storage
    try:
        storage = supabase.storage.from_("documents")
        storage.remove([document["storage_path"]])
    except Exception as e:
        print(f"Failed to delete from storage: {e}")

    # Delete from database
    supabase.table("documents").delete().eq("id", document_id).execute()

    return {"message": "Document deleted successfully"}
