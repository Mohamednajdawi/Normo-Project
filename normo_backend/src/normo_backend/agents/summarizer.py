from normo_backend.models import AgentState
from normo_backend.prompts import SUMMARIZER_SYSTEM_PROMPT
from normo_backend.utils import get_default_chat_model
from normo_backend.utils.trimer import extract_json

llm = get_default_chat_model(model="gpt-4.1-2025-04-14", temperature=0.1)


def summarizer_agent(state: AgentState) -> AgentState:
    # Format conversation history for the prompt
    conversation_history_str = ""
    if state.conversation_history:
        for msg in state.conversation_history:
            conversation_history_str += f"Role: {msg['role']}, Content: {msg['content']}\n"
            if msg.get('pdf_names'):
                conversation_history_str += f"  PDFs: {', '.join(msg['pdf_names'])}\n"
    
    # Format memory content for better calculation extraction
    memory_str = ""
    if state.memory:
        for mem_item in state.memory:
            role = mem_item.get('role', 'unknown')
            content = mem_item.get('content', '')
            if isinstance(content, dict):
                # Format dictionary content more readably
                if 'retrieved_info' in content:
                    memory_str += f"[{role}]: Retrieved Information:\n{content.get('retrieved_info', '')}\n\n"
                    if 'source_citations' in content:
                        memory_str += "Source Citations:\n"
                        for citation in content.get('source_citations', [])[:5]:  # Limit to top 5
                            if isinstance(citation, dict):
                                memory_str += f"  - {citation.get('pdf_name', 'Unknown')} (Page {citation.get('page', 'N/A')})\n"
                                if citation.get('calculations'):
                                    memory_str += f"    Calculations found: {citation.get('calculations')}\n"
                                if citation.get('area_measurements'):
                                    memory_str += f"    Area measurements: {citation.get('area_measurements')}\n"
                else:
                    memory_str += f"[{role}]: {str(content)}\n\n"
            else:
                memory_str += f"[{role}]: {str(content)}\n\n"
    
    prompt = SUMMARIZER_SYSTEM_PROMPT.format(
        user_query=state.user_query,
        conversation_history=conversation_history_str or "No previous conversation",
        is_follow_up=state.is_follow_up,
        memory=memory_str or "No previous processing steps"
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
