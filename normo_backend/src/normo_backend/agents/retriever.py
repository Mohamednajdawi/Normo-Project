from normo_backend.models import AgentState
from normo_backend.prompts import RETRIEVER_SYSTEM_PROMPT
from normo_backend.utils import get_default_chat_model
from normo_backend.utils.trimer import extract_json


def retriever_agent(state: AgentState) -> AgentState:
    prompt = RETRIEVER_SYSTEM_PROMPT.format(user_query=state.user_query)
    response = get_default_chat_model(model="gpt-4o-mini", temperature=0.2).invoke(
        prompt
    )
    state.retrieved_documents = extract_json(response.content)["retrieved_documents"]
    state.memory.append(
        {
            "role": "retriever_agent",
            "content": state.retrieved_documents,
        }
    )
    return state
