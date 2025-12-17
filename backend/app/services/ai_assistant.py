"""
OpenAI Assistant Manager - Lucy (AI Loan Officer)
"""

from openai import OpenAI
from typing import Optional, Dict, Any
import json

from app.config import settings
from app.database import get_supabase

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Lucy's system instructions
LUCY_INSTRUCTIONS = """You are Lucy, a friendly and helpful AI loan officer for a microfinance platform serving microentrepreneurs in Kenya. Your role is to:

1. Greet customers warmly and make them feel comfortable
2. Interview them about their business to assess loan eligibility
3. Collect key information: business name, type, location, years in operation, monthly revenue, and expenses
4. Request supporting documents (business photos, national ID)
5. Make informed loan decisions based on business viability
6. Calculate and present loan offers when appropriate
7. Help customers accept or review loan terms

**Communication Style:**
- Use simple language (2nd-3rd grade reading level)
- Be warm, encouraging, and supportive
- Keep messages short and clear
- Use encouraging language for microentrepreneurs
- Be culturally sensitive to Kenyan context

**Decision Criteria:**
- Business must be operating for at least 6 months
- Monthly revenue should exceed monthly expenses
- Business should show growth potential
- Customer should demonstrate understanding of loan terms

**Workflow:**
1. Greeting and introduction
2. Business information collection
3. Document verification
4. Loan eligibility assessment
5. Loan calculation and offer presentation
6. Loan acceptance or rejection handling

Use the provided tools to:
- Calculate loan offers
- Store customer acceptance
- Retrieve loan information
- Mark tasks as complete

Be professional but friendly. Your goal is to help microentrepreneurs access financing while ensuring responsible lending."""

# Function definitions for OpenAI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_loan_offer",
            "description": "Calculate loan terms including interest and total repayment amount",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "The loan amount requested in KES"
                    },
                    "interest_rate": {
                        "type": "number",
                        "description": "Monthly interest rate as percentage (default 15%)"
                    },
                    "tenure_days": {
                        "type": "number",
                        "description": "Loan tenure in days (default 30)"
                    }
                },
                "required": ["amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "store_customer_acceptance",
            "description": "Store customer's acceptance of loan offer and trigger disbursement",
            "parameters": {
                "type": "object",
                "properties": {
                    "loan_id": {
                        "type": "string",
                        "description": "The loan ID that was accepted"
                    },
                    "accepted": {
                        "type": "boolean",
                        "description": "Whether the loan was accepted (true) or rejected (false)"
                    }
                },
                "required": ["loan_id", "accepted"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_loan_info",
            "description": "Get customer's current loan information and transaction history",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID to get loan info for"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_onboarding",
            "description": "Mark customer onboarding as complete after collecting all information",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID completing onboarding"
                    },
                    "profile_data": {
                        "type": "object",
                        "description": "Business profile data collected during onboarding",
                        "properties": {
                            "business_name": {"type": "string"},
                            "business_type": {"type": "string"},
                            "business_location": {"type": "string"},
                            "years_in_business": {"type": "number"},
                            "monthly_revenue": {"type": "number"},
                            "monthly_expenses": {"type": "number"}
                        }
                    }
                },
                "required": ["user_id", "profile_data"]
            }
        }
    }
]

class AIAssistantManager:
    """Manages OpenAI Assistant interactions"""

    def __init__(self):
        self.client = client
        self.assistant_id = settings.OPENAI_ASSISTANT_ID
        self.supabase = get_supabase()

    async def get_or_create_assistant(self) -> str:
        """Get existing assistant or create a new one"""
        if self.assistant_id:
            try:
                assistant = self.client.beta.assistants.retrieve(self.assistant_id)
                return assistant.id
            except Exception as e:
                print(f"Error retrieving assistant: {e}")

        # Create new assistant
        assistant = self.client.beta.assistants.create(
            name="Lucy - AI Loan Officer",
            instructions=LUCY_INSTRUCTIONS,
            model=settings.OPENAI_MODEL,
            tools=TOOLS
        )
        self.assistant_id = assistant.id
        print(f"Created new assistant: {assistant.id}")
        return assistant.id

    async def create_thread(self, user_id: str) -> Dict[str, Any]:
        """Create a new conversation thread"""
        thread = self.client.beta.threads.create()

        # Store thread in database
        result = self.supabase.table("conversation_threads").insert({
            "user_id": user_id,
            "openai_thread_id": thread.id,
            "status": "active"
        }).execute()

        return result.data[0] if result.data else None

    async def get_or_create_thread(self, user_id: str) -> str:
        """Get user's active thread or create a new one"""
        # Try to get existing thread
        result = self.supabase.table("conversation_threads")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("status", "active")\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()

        if result.data:
            return result.data[0]["openai_thread_id"]

        # Create new thread
        thread_data = await self.create_thread(user_id)
        return thread_data["openai_thread_id"]

    async def send_message(
        self,
        thread_id: str,
        message: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Send a message and get response"""
        # Add message to thread
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

        # Store user message
        self._store_message(thread_id, "user", message)

        # Run assistant
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=await self.get_or_create_assistant()
        )

        # Wait for completion and handle tool calls
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            if run_status.status == "completed":
                break
            elif run_status.status == "requires_action":
                # Handle function calls
                tool_outputs = await self._handle_tool_calls(
                    run_status.required_action.submit_tool_outputs.tool_calls,
                    user_id
                )

                # Submit tool outputs
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            elif run_status.status in ["failed", "cancelled", "expired"]:
                raise Exception(f"Run failed with status: {run_status.status}")

        # Get latest assistant message
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=1
        )

        if messages.data:
            assistant_message = messages.data[0].content[0].text.value
            self._store_message(thread_id, "assistant", assistant_message)

            return {
                "message": assistant_message,
                "thread_id": thread_id,
                "role": "assistant"
            }

        return None

    async def _handle_tool_calls(self, tool_calls, user_id: str) -> list:
        """Handle function calls from assistant"""
        tool_outputs = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            result = await self._execute_function(function_name, arguments, user_id)

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result)
            })

        return tool_outputs

    async def _execute_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Execute a function call"""
        if function_name == "calculate_loan_offer":
            return await self._calculate_loan(arguments)
        elif function_name == "store_customer_acceptance":
            return await self._store_acceptance(arguments, user_id)
        elif function_name == "get_loan_info":
            return await self._get_loan_info(user_id)
        elif function_name == "complete_onboarding":
            return await self._complete_onboarding(arguments)

        return {"error": "Unknown function"}

    async def _calculate_loan(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate loan offer"""
        amount = args["amount"]
        interest_rate = args.get("interest_rate", settings.DEFAULT_INTEREST_RATE)
        tenure_days = args.get("tenure_days", settings.DEFAULT_LOAN_TENURE_DAYS)

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

    async def _store_acceptance(self, args: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Store loan acceptance"""
        loan_id = args["loan_id"]
        accepted = args["accepted"]

        status = "approved" if accepted else "rejected"

        self.supabase.table("loans").update({
            "status": status,
            "approved_at": "now()" if accepted else None
        }).eq("id", loan_id).execute()

        return {"success": True, "status": status}

    async def _get_loan_info(self, user_id: str) -> Dict[str, Any]:
        """Get loan information"""
        loans = self.supabase.table("loans")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()

        transactions = self.supabase.table("transactions")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()

        return {
            "loans": loans.data,
            "transactions": transactions.data
        }

    async def _complete_onboarding(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Complete customer onboarding"""
        user_id = args["user_id"]
        profile_data = args["profile_data"]

        self.supabase.table("customer_profiles").upsert({
            "user_id": user_id,
            **profile_data,
            "onboarding_completed": True,
            "onboarding_completed_at": "now()"
        }).execute()

        return {"success": True, "onboarding_completed": True}

    def _store_message(self, thread_id: str, role: str, content: str):
        """Store message in database"""
        # Get thread from DB
        thread_result = self.supabase.table("conversation_threads")\
            .select("id")\
            .eq("openai_thread_id", thread_id)\
            .execute()

        if thread_result.data:
            self.supabase.table("messages").insert({
                "thread_id": thread_result.data[0]["id"],
                "role": role,
                "content": content
            }).execute()

# Singleton instance
ai_assistant = AIAssistantManager()
