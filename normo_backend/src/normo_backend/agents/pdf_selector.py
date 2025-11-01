from normo_backend.models import AgentState
from normo_backend.prompts import APPENDIX_A, PDF_SELECTOR_SYSTEM_PROMPT
from normo_backend.utils import get_default_chat_model
from normo_backend.utils.pdf_processor import get_available_pdfs
from normo_backend.utils.trimer import extract_json

llm = get_default_chat_model(model="gpt-4.1-2025-04-14", temperature=0.3)


def pdf_selector_agent(state: AgentState) -> AgentState:
    # Get available PDFs from the arch_pdfs folder
    available_pdfs = get_available_pdfs("arch_pdfs")
    
    # Format the available PDFs list
    if available_pdfs:
        available_pdfs_text = "\n".join([f"- {pdf}" for pdf in available_pdfs])
    else:
        available_pdfs_text = "No PDFs found in arch_pdfs folder"
    
    # Format the appendix with available PDFs
    formatted_appendix = APPENDIX_A.format(available_pdfs=available_pdfs_text)
    
    prompt = PDF_SELECTOR_SYSTEM_PROMPT.format(user_query=state.user_query, appendex_a=formatted_appendix)
    response = llm.invoke(prompt)
    try:
        state.pdf_names = extract_json(response.content)["pdf_names"]
    except (KeyError, TypeError):
        # Fallback: if no specific PDFs can be identified, suggest the most general ones
        if available_pdfs:
            # Pick the first few available PDFs as fallback
            state.pdf_names = available_pdfs[:3]
        else:
            state.pdf_names = []
    
    state.memory.append(
        {
            "role": "pdf_selector_agent",
            "content": state.pdf_names,
        }
    )
    return state
