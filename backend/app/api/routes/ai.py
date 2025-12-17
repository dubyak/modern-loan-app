"""
AI/Chat routes
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import ChatRequest, ChatResponse, ThreadResponse
from app.auth.dependencies import get_current_active_user
from app.services.ai_assistant import ai_assistant
from app.database import get_supabase

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Send a message to the AI loan officer (Lucy)"""
    try:
        # Get or create thread
        if request.thread_id:
            thread_id = request.thread_id
        else:
            thread_id = await ai_assistant.get_or_create_thread(current_user["id"])

        # Send message and get response
        response = await ai_assistant.send_message(
            thread_id=thread_id,
            message=request.message,
            user_id=current_user["id"]
        )

        if not response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get response from AI"
            )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )

@router.get("/thread", response_model=ThreadResponse)
async def get_or_create_thread(current_user: dict = Depends(get_current_active_user)):
    """Get or create conversation thread for user"""
    supabase = get_supabase()

    # Get existing thread
    result = supabase.table("conversation_threads")\
        .select("*")\
        .eq("user_id", current_user["id"])\
        .eq("status", "active")\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()

    if result.data:
        return result.data[0]

    # Create new thread
    thread_data = await ai_assistant.create_thread(current_user["id"])
    return thread_data

@router.get("/thread/history")
async def get_thread_history(current_user: dict = Depends(get_current_active_user)):
    """Get conversation history for user's active thread"""
    supabase = get_supabase()

    # Get thread
    thread_result = supabase.table("conversation_threads")\
        .select("id")\
        .eq("user_id", current_user["id"])\
        .eq("status", "active")\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()

    if not thread_result.data:
        return {"messages": []}

    thread_id = thread_result.data[0]["id"]

    # Get messages
    messages = supabase.table("messages")\
        .select("*")\
        .eq("thread_id", thread_id)\
        .order("created_at", asc=True)\
        .execute()

    return {"messages": messages.data}
