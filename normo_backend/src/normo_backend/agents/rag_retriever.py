from __future__ import annotations

import os
import re
from typing import Any, Dict, List

from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from normo_backend.config import get_settings
from normo_backend.models import AgentState
from normo_backend.services.vector_store import get_vector_store
from normo_backend.utils import get_default_chat_model
from normo_backend.utils.pdf_processor import create_fallback_documents

# Note: Document loading is now handled by the persistent vector store service


def create_retrieve_tool(retriever):
    """Create an enhanced retrieval tool optimized for architectural calculations."""
    
    @tool
    def retrieve_documents(query: str) -> str:
        """Retrieve relevant documents with focus on architectural requirements and calculations."""
        # Enhanced search for architectural calculations
        search_queries = [
            query,
            # Add specific architectural terms
            f"{query} Kinderspielplatz playground area calculation",
            f"{query} Spielplatz Fläche Berechnung square meters",
            f"{query} Wohnbau residential building requirements",
            "playground area calculation formula square meters apartment building"
        ]
        
        all_docs = []
        seen_content = set()
        
        # Search with multiple queries to catch different phrasings
        for search_query in search_queries:
            docs = retriever.invoke(search_query)
            for doc in docs:
                # Avoid duplicates
                if doc.page_content not in seen_content:
                    seen_content.add(doc.page_content)
                    all_docs.append(doc)
        
        # Sort by relevance and limit
        all_docs = all_docs[:8]  # Top 8 unique documents
        
        # Enhanced formatting with calculation detection and source citations
        result = "Retrieved architectural requirements:\n\n"
        source_citations = []
        
        for i, doc in enumerate(all_docs, 1):
            content = doc.page_content
            metadata = doc.metadata
            
            source = metadata.get('source', 'unknown')
            page = metadata.get('page', 'N/A')
            paragraph = metadata.get('paragraph', 'N/A')
            chunk_id = metadata.get('chunk_id', f'chunk_{i}')
            
            result += f"{i}. Source: {source} (Page {page}, Section {paragraph})\n"
            result += f"   Content: {content}\n"
            
            # Collect citation info
            citation_info = {
                "pdf_name": source,
                "page": page,
                "paragraph": paragraph,
                "chunk_id": chunk_id,
                "relevant_content": content[:200] + "..." if len(content) > 200 else content
            }
            source_citations.append(citation_info)
            
            # Highlight potential calculations and measurements
            import re

            # Look for calculations, formulas, and measurements
            calculations = re.findall(r'\d+(?:\s*[+\-×x*]\s*\d+)+(?:\s*=\s*\d+)?', content)
            area_mentions = re.findall(r'\d+(?:\.\d+)?\s*(?:m²|qm|Quadratmeter|square\s*meter)', content, re.IGNORECASE)
            
            if calculations:
                result += f"   → Calculations found: {', '.join(calculations)}\n"
                citation_info["calculations"] = calculations
            if area_mentions:
                result += f"   → Area measurements: {', '.join(area_mentions)}\n"
                citation_info["area_measurements"] = area_mentions
            
            result += "\n"
        
        # Add source citations summary
        result += "\n📚 SOURCE CITATIONS:\n"
        for i, citation in enumerate(source_citations, 1):
            result += f"{i}. {citation['pdf_name']} - Page {citation['page']}, Section {citation['paragraph']}\n"
            if "calculations" in citation:
                result += f"   Contains calculations: {', '.join(citation['calculations'])}\n"
        
        return result
    
    return retrieve_documents


def rag_retriever_agent(state: AgentState) -> AgentState:
    """RAG retriever agent that finds relevant information from PDFs using persistent vector store."""
    
    try:
        # Get the persistent vector store
        vector_store = get_vector_store()
        
        # Ensure PDFs are embedded (incremental - only new/changed PDFs will be processed)
        print(f"🔍 Ensuring {len(state.pdf_names)} PDFs are embedded...")
        new_embeddings_created = vector_store.ensure_pdfs_embedded(state.pdf_names)
        
        if new_embeddings_created:
            print("✅ New embeddings created")
        else:
            print("⚡ Using existing embeddings (fast!)")
        
        # Get collection statistics
        stats = vector_store.get_collection_stats()
        print(f"📊 Vector store stats: {stats['total_chunks']} chunks from {stats['embedded_pdfs']} PDFs")
        
        # Get retriever from persistent vector store
        retriever = vector_store.get_retriever()
        
        # Create retrieval tool with the persistent retriever
        retrieve_tool = create_retrieve_tool(retriever)
        
        # Create ReAct agent with retrieval tool
        llm = get_default_chat_model(model="gpt-4o-mini", temperature=0.1)
        agent = create_react_agent(llm, tools=[retrieve_tool])
        
        # Create an architect-focused query for retrieval
        retrieval_query = f"""
        You are an assistant for architects and urban planners working with Austrian building regulations.
        
        User Query: "{state.user_query}"
        
        Search through the Austrian legal documents to find EXACT requirements, calculations, and formulas that architects need.
        
        Focus specifically on:
        - Numerical requirements (square meters, dimensions)
        - Calculation formulas (e.g., 100 + 5 × 10 = 150)
        - Specific legal standards and minimums
        - Precise measurements and technical specifications
        - Mathematical formulas for area calculations
        
        Use the retrieve_documents tool multiple times with different search terms to ensure you find all relevant calculations.
        
        Provide exact numbers, formulas, and legal requirements as written in the documents.
        If you find calculation formulas, include them exactly as they appear.
        """
        
        # Run the agent
        result = agent.invoke({"messages": [("user", retrieval_query)]})
        
        # Extract the final response
        if result and "messages" in result and result["messages"]:
            final_answer = result["messages"][-1].content
        else:
            final_answer = "Unable to retrieve relevant information from the documents."
        
        # Extract source citations from the last retrieval
        # Since we're using persistent storage, we need to get citations differently
        # We'll perform a similarity search to get the documents that would be retrieved
        search_docs = retriever.invoke(state.user_query)
        
        source_citations = []
        unique_sources = {}
        
        for doc in search_docs:
            metadata = doc.metadata
            source_key = f"{metadata.get('source', 'unknown')}_p{metadata.get('page', 'N/A')}_s{metadata.get('paragraph', 'N/A')}"
            
            if source_key not in unique_sources:
                citation = {
                    "pdf_name": metadata.get('source', 'unknown'),
                    "page": metadata.get('page', 'N/A'),
                    "paragraph": metadata.get('paragraph', 'N/A'),
                    "chunk_id": metadata.get('chunk_id', ''),
                    "file_path": metadata.get('file_path', ''),
                    "relevant_content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                
                # Check if this chunk contains calculations or measurements
                calculations = re.findall(r'\d+(?:\s*[+\-×x*]\s*\d+)+(?:\s*=\s*\d+)?', doc.page_content)
                area_mentions = re.findall(r'\d+(?:\.\d+)?\s*(?:m²|qm|Quadratmeter|square\s*meter)', doc.page_content, re.IGNORECASE)
                
                if calculations:
                    citation["calculations"] = calculations
                if area_mentions:
                    citation["area_measurements"] = area_mentions
                
                unique_sources[source_key] = citation
                source_citations.append(citation)
        
        # Update state with retrieved information and source citations
        state.summary = final_answer
        state.source_citations = source_citations
        state.memory.append({
            "role": "rag_retriever_agent",
            "content": {
                "retrieved_info": final_answer,
                "documents_searched": len(search_docs),
                "pdfs_processed": state.pdf_names,
                "source_citations": source_citations,
                "vector_store_stats": stats,
                "new_embeddings_created": new_embeddings_created
            }
        })
        
    except Exception as e:
        error_msg = f"Error during RAG retrieval: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Fallback to error documents
        fallback_docs = create_fallback_documents(state.pdf_names, state.user_query)
        
        state.summary = f"Error accessing legal documents: {error_msg}. Please ensure PDFs are available and the system is properly configured."
        state.source_citations = []
        state.memory.append({
            "role": "rag_retriever_agent",
            "content": {"error": error_msg, "fallback_used": True}
        })
    
    return state
