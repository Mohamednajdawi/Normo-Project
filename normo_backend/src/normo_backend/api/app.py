from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from normo_backend.agents.builder import graph
from normo_backend.agents.llm_gate import llm_gate
from normo_backend.models import AgentState
from normo_backend.models.schemas import ChatRequest, ChatResponse, ConversationMessage
from normo_backend.services.hybrid_storage import HybridConversationStorage
from pathlib import Path
import os

app = FastAPI(title="Normo Agentic Chatbot API")

# Initialize hybrid conversation storage (MongoDB + JSON)
mongodb_url = os.getenv("MONGODB_URL")
conversation_storage = HybridConversationStorage(mongodb_url)

# Note: PDF serving is handled by the /pdf/{pdf_path:path} endpoint

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React frontend
        "http://127.0.0.1:3000",  # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.post("/sync-conversations")
def sync_conversations():
    """Sync conversations from JSON files to MongoDB."""
    try:
        conversation_storage.sync_from_json_to_mongodb()
        return {"status": "success", "message": "Conversations synced to MongoDB"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/pdf/{pdf_path:path}")
def get_pdf(pdf_path: str):
    """Serve PDF files for viewing in browser."""
    pdf_file_path = Path("arch_pdfs") / pdf_path
    
    if not pdf_file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    if not pdf_file_path.suffix.lower() == '.pdf':
        raise HTTPException(status_code=400, detail="File is not a PDF")
    
    return FileResponse(
        path=str(pdf_file_path),
        media_type="application/pdf",
        filename=pdf_file_path.name,
        headers={"Content-Disposition": "inline"}
    )


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    """Handle chat requests with conversation context support and LLM gate."""
    
    # Get the latest user message
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    latest_message = request.messages[-1]
    user_query = latest_message.content
    
    # Determine if this is a follow-up question
    is_follow_up = request.conversation_id is not None
    
    # Get conversation history if this is a follow-up
    conversation_history = []
    if is_follow_up:
        conversation_history = conversation_storage.get_conversation_history(
            request.conversation_id, limit=5
        )
    
    # Create or get conversation ID
    conversation_id = request.conversation_id or conversation_storage.create_conversation(
        user_id=request.user_id
    )
    
    # Store the user's message first
    user_message = ConversationMessage(
        role="user",
        content=user_query
    )
    conversation_storage.add_message(conversation_id, user_message)
    
    # Use LLM gate to determine if we need the full agent workflow
    gate_decision = llm_gate.should_use_agent(user_query, conversation_history)
    
    if gate_decision["use_agent"]:
        # Use full agentic workflow for architectural/legal queries
        print(f"🚀 Using agent workflow: {gate_decision['reason']}")
        
        # Create agent state with conversation context
        agent_state = AgentState(
            user_query=user_query,
            conversation_id=conversation_id,
            conversation_history=conversation_history,
            is_follow_up=is_follow_up
        )
        
        # Run the agent workflow
        result_state = graph.invoke(agent_state)
        
        # Create conversation message for storage
        conversation_message = ConversationMessage(
            role="assistant",
            content=result_state.get("summary", ""),
            agent_steps=result_state.get("steps", []),
            pdf_names=result_state.get("pdf_names", []),
            source_citations=result_state.get("source_citations", []),
            meta_data=result_state.get("meta_data", {})
        )
        
        # Store the assistant's response
        conversation_storage.add_message(conversation_id, conversation_message)
        
        # Create response
        response_message = {
            "role": "assistant",
            "content": result_state.get("summary", ""),
            "timestamp": datetime.now()
        }
        
        return ChatResponse(
            message=response_message,
            conversation_id=conversation_id,
            source_citations=result_state.get("source_citations", [])
        )
    
    else:
        # Use simple LLM response for general queries
        print(f"💬 Using simple LLM response: {gate_decision['reason']}")
        
        # Get simple response
        simple_response = llm_gate.get_simple_response(user_query, conversation_history)
        
        # Create conversation message for storage
        conversation_message = ConversationMessage(
            role="assistant",
            content=simple_response,
            agent_steps=["llm_gate"],
            pdf_names=[],
            source_citations=[],
            meta_data={"gate_decision": gate_decision}
        )
        
        # Store the assistant's response
        conversation_storage.add_message(conversation_id, conversation_message)
        
        # Create response
        response_message = {
            "role": "assistant",
            "content": simple_response,
            "timestamp": datetime.now()
        }
        
        return ChatResponse(
            message=response_message,
            conversation_id=conversation_id,
            source_citations=[]
        )


@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    """Get a specific conversation."""
    conversation = conversation_storage.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.get("/conversations")
def list_conversations(user_id: str = None):
    """List conversations for a user."""
    return conversation_storage.list_conversations(user_id=user_id)


@app.post("/conversations")
def create_conversation(user_id: str = None):
    """Create a new conversation."""
    conversation_id = conversation_storage.create_conversation(user_id=user_id)
    return {"conversation_id": conversation_id}


# Legacy endpoint for backward compatibility
@app.post("/chat/legacy")
def chat_legacy(state: AgentState) -> AgentState:
    """Legacy chat endpoint for backward compatibility."""
    return graph.invoke(state)
