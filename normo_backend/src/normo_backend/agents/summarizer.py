from normo_backend.models import AgentState
from normo_backend.prompts import SUMMARIZER_SYSTEM_PROMPT
from normo_backend.utils import get_default_chat_model
from normo_backend.utils.trimer import extract_json

llm = get_default_chat_model(model="gpt-4o-mini", temperature=0.2)


def summarizer_agent(state: AgentState) -> AgentState:
    # Format conversation history for the prompt
    conversation_history_str = ""
    if state.conversation_history:
        for msg in state.conversation_history:
            conversation_history_str += f"Role: {msg['role']}, Content: {msg['content']}\n"
            if msg.get('pdf_names'):
                conversation_history_str += f"  PDFs: {', '.join(msg['pdf_names'])}\n"
    
    prompt = SUMMARIZER_SYSTEM_PROMPT.format(
        user_query=state.user_query,
        conversation_history=conversation_history_str or "No previous conversation",
        is_follow_up=state.is_follow_up,
        memory=state.memory
    )
    response = llm.invoke(prompt)
    try:
        state.summary = extract_json(response.content)["summary"]
    except (KeyError, TypeError):
        # Fallback if JSON extraction fails
        state.summary = response.content
    
    state.memory.append(
        {
            "role": "summarizer_agent",
            "content": state.summary,
        }
    )
    return state
