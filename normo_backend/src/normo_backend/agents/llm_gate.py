from __future__ import annotations

import json
from typing import Dict, Any

from normo_backend.utils.llm_inference import get_default_chat_model


class LLMGate:
    """Simple LLM gate to determine if a query requires the full agentic workflow."""
    
    def __init__(self):
        self.llm = get_default_chat_model()
        self.system_prompt = """
You are a gatekeeper for an Austrian architectural legal document analysis system. 
Your job is to determine if a user query requires the full agentic workflow or can be answered with a simple LLM response.

The system has access to:
- Austrian building codes and regulations
- OIB guidelines (fire protection, accessibility, etc.)
- ÖNORM standards
- Federal and state laws
- PDF documents with specific calculations and requirements

Use the FULL AGENTIC WORKFLOW for queries about:
- Building requirements, codes, regulations
- Architectural planning, calculations, measurements
- Fire safety, accessibility, energy efficiency
- Legal compliance, permits, standards
- Specific technical questions about construction
- Questions requiring document retrieval and analysis
- Any query that might need to search through legal documents

Use SIMPLE LLM RESPONSE for:
- General greetings ("Hello", "How are you", "Hi")
- System status questions ("What can you do", "Help")
- General explanations about the system
- Non-technical questions
- Questions not related to architecture, building, or legal documents
- Simple clarifications or confirmations

Respond with a JSON object containing:
- "use_agent": true/false
- "reason": brief explanation of your decision

Examples:

Query: "How are you?"
Response: {"use_agent": false, "reason": "General greeting, no architectural content"}

Query: "What are the building height requirements in Austria?"
Response: {"use_agent": true, "reason": "Requires specific legal document analysis"}

Query: "Can you help me with building codes?"
Response: {"use_agent": true, "reason": "Architectural legal question requiring document search"}

Query: "What can you do?"
Response: {"use_agent": false, "reason": "General system information request"}

Query: "I need to know about playground area requirements for a 5-flat building"
Response: {"use_agent": true, "reason": "Specific architectural calculation requiring legal document analysis"}

Query: "Summarize the conversation"
Response: {"use_agent": false, "reason": "General conversation summary request"}

Query: "What is the minimum room height for living spaces?"
Response: {"use_agent": true, "reason": "Specific building requirement needing legal document search"}
"""

    def should_use_agent(self, user_query: str, conversation_history: list = None) -> Dict[str, Any]:
        """
        Determine if the query requires the full agentic workflow.
        
        Args:
            user_query: The user's question
            conversation_history: Previous conversation context
            
        Returns:
            Dict with 'use_agent' boolean and 'reason' string
        """
        try:
            # Build context for the gate
            context = f"User Query: {user_query}\n"
            
            if conversation_history:
                context += f"Conversation History: {conversation_history}\n"
            
            # Create the prompt
            prompt = f"{self.system_prompt}\n\n{context}\n\nRespond with JSON only:"
            
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            # Parse JSON response
            try:
                result = json.loads(response.content.strip())
                return {
                    "use_agent": result.get("use_agent", True),  # Default to agent for safety
                    "reason": result.get("reason", "Default to agent workflow")
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, default to agent workflow
                return {
                    "use_agent": True,
                    "reason": "Failed to parse gate response, defaulting to agent workflow"
                }
                
        except Exception as e:
            # If any error occurs, default to agent workflow for safety
            return {
                "use_agent": True,
                "reason": f"Gate error: {str(e)}, defaulting to agent workflow"
            }

    def get_simple_response(self, user_query: str, conversation_history: list = None) -> str:
        """
        Generate a simple LLM response for non-architectural queries.
        
        Args:
            user_query: The user's question
            conversation_history: Previous conversation context
            
        Returns:
            Simple response string
        """
        system_prompt = """
You are a helpful assistant for the Normo architectural legal document analysis system. 
You can answer general questions about the system and provide basic information, but for specific 
architectural, building code, or legal document questions, users should ask those directly.

Keep responses concise and helpful. If the user asks about architectural topics, gently guide them 
to ask specific questions that the system can help with.
"""

        context = f"User Query: {user_query}\n"
        
        if conversation_history:
            context += f"Conversation History: {conversation_history}\n"
        
        prompt = f"{system_prompt}\n\n{context}"
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Please try again or ask a specific question about Austrian building codes and regulations."


# Global gate instance
llm_gate = LLMGate()
