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
    """Create an enhanced retrieval tool optimized for architectural calculations with priority system."""
    
    def get_document_priority(doc):
        """Get priority level based on document filename prefix."""
        source = doc.metadata.get('source', '')
        if source.startswith('1_') or source.startswith('2_'):
            return 1  # Highest priority - Laws and Regulations
        elif source.startswith('3_'):
            return 2  # Second priority - OIB Guidelines
        elif source.startswith('4_'):
            return 3  # Lowest priority - ÖNORM Standards
        else:
            return 4  # Unknown priority
    
    @tool
    def retrieve_documents(query: str) -> str:
        """Retrieve relevant documents with focus on architectural requirements and calculations, prioritizing by document type."""
        # Enhanced search for architectural calculations
        search_queries = [
            query,
            # Add specific architectural terms
            # f"{query} Kinderspielplatz playground area calculation",
            # f"{query} Spielplatz Fläche Berechnung square meters",
            # f"{query} Wohnbau residential building requirements",
            # "playground area calculation formula square meters apartment building"
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
        
        # Sort by priority first, then by relevance
        all_docs.sort(key=lambda doc: (get_document_priority(doc), -len(doc.page_content)))
        
        # Limit to top 8 unique documents, prioritizing higher-priority documents
        all_docs = all_docs[:8]
        
        # Enhanced formatting with calculation detection and source citations
        result = "Retrieved architectural requirements (prioritized by document type):\n\n"
        source_citations = []
        
        for i, doc in enumerate(all_docs, 1):
            content = doc.page_content
            metadata = doc.metadata
            
            source = metadata.get('source', 'unknown')
            page = metadata.get('page', 'N/A')
            paragraph = metadata.get('paragraph', 'N/A')
            chunk_id = metadata.get('chunk_id', f'chunk_{i}')
            
            # Get priority information
            priority = get_document_priority(doc)
            priority_text = {
                1: "LAW/REGULATION (1_/2_) - HIGHEST PRIORITY",
                2: "OIB GUIDELINE (3_) - SECOND PRIORITY", 
                3: "ÖNORM STANDARD (4_) - LOWEST PRIORITY",
                4: "UNKNOWN PRIORITY"
            }.get(priority, "UNKNOWN PRIORITY")
            
            result += f"{i}. Source: {source} (Page {page}, Section {paragraph})\n"
            result += f"   Priority: {priority_text}\n"
            result += f"   Content: {content}\n"
            
            # Collect citation info
            citation_info = {
                "pdf_name": source,
                "page": page,
                "paragraph": paragraph,
                "chunk_id": chunk_id,
                "priority": priority,
                "priority_text": priority_text,
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
        result += "\n📚 SOURCE CITATIONS (PRIORITIZED):\n"
        for i, citation in enumerate(source_citations, 1):
            result += f"{i}. {citation['pdf_name']} - Page {citation['page']}, Section {citation['paragraph']}\n"
            result += f"   Priority: {citation['priority_text']}\n"
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
        llm = get_default_chat_model(model="gpt-4.1-2025-04-14", temperature=0.3)
        agent = create_react_agent(llm, tools=[retrieve_tool])
        
        # Create an architect-focused query for retrieval with priority system
        # Extract jurisdiction from user query
        jurisdiction_hint = ""
        user_query_lower = state.user_query.lower()
        if any(keyword in user_query_lower for keyword in ["linz", "oberösterreich", "upper austria", "oö", "oo"]):
            jurisdiction_hint = "\n\n## CRITICAL JURISDICTION FILTER:\n- The query mentions LINZ or UPPER AUSTRIA - ONLY use documents from '04. OBERÖSTERREICH' folder\n- DO NOT use Vienna (01.Wien) or federal documents if Upper Austria-specific documents exist\n- Upper Austria has its own Building Code and Building Technology Law that override general regulations"
        elif any(keyword in user_query_lower for keyword in ["wien", "vienna"]):
            jurisdiction_hint = "\n\n## CRITICAL JURISDICTION FILTER:\n- The query mentions VIENNA (WIEN) - ONLY use documents from '01.Wien' folder\n- DO NOT use Upper Austria or other state documents if Vienna-specific documents exist"
        
        retrieval_query = f"""
        You are an assistant for architects and urban planners working with Austrian building regulations.
        
        User Query: "{state.user_query}"
        {jurisdiction_hint}
        
        Search through the Austrian legal documents to find EXACT requirements, calculations, and formulas that architects need.
        
        ## CRITICAL DOCUMENT PRIORITY SYSTEM - FOLLOW THIS EXACT ORDER:
        
        **HIGHEST PRIORITY (1st Choice):** Documents starting with "1_" or "2_"
        - These are LAWS and REGULATIONS (Bundesgesetze, Landesgesetze, Verordnungen)
        - These contain the most authoritative and legally binding requirements
        - ALWAYS prioritize information from these documents
        - If these documents contain the required information, use ONLY these sources
        
        **SECOND PRIORITY (2nd Choice):** Documents starting with "3_"
        - These are OIB GUIDELINES (OIB-Richtlinien)
        - Use these ONLY if 1_/2_ documents don't contain sufficient information
        - These provide technical guidance and interpretation
        
        **LOWEST PRIORITY (3rd Choice):** Documents starting with "4_"
        - These are AUSTRIAN STANDARDS (ÖNORM)
        - Use these ONLY if 1_/2_/3_ documents don't contain sufficient information
        - These provide technical specifications and standards
        
        ## RETRIEVAL STRATEGY:
        
        1. **FIRST**: Search for and prioritize information from documents starting with "1_" or "2_"
        2. **SECOND**: If no sufficient information from 1_/2_ documents, search for "3_" documents
        3. **THIRD**: If no sufficient information from 1_/2_/3_ documents, search for "4_" documents
        4. **NEVER** use 3_ or 4_ documents if 1_/2_ documents contain the required information
        
        Focus specifically on:
        - Numerical requirements (square meters, dimensions)
        - Calculation formulas with specific numbers (e.g., "100 m² + 10 m² per apartment", "100 + 5 × 10 = 150")
        - Mathematical formulas that use variables (e.g., "base area + X per unit")
        - Specific legal standards and minimums
        - Precise measurements and technical specifications
        
        IMPORTANT: When searching, ALWAYS respect jurisdiction filters above. If the query mentions a specific location (e.g., "Linz", "Vienna"), prioritize documents from that jurisdiction's folder over other jurisdictions or general federal documents.
        
        **CRITICAL FOR CALCULATION QUERIES:**
        If the user is asking for a calculation (e.g., "how many square meters", "calculate", "required area"), you MUST:
        1. Search for documents containing calculation formulas with specific numbers
        2. Look for phrases like "100 m²", "10 m² per", "je Wohnung", "pro Wohnung", "zuzüglich"
        3. Find the exact formula text from the regulations
        4. Extract ALL numerical components of the formula
        5. If you find conflicting information (some saying "no fixed formula" and others with formulas), prioritize the formula with specific numbers
        
        Use the retrieve_documents tool multiple times with different search terms to ensure you find all relevant calculations:
        - Search for: "Spielplatz" OR "playground" AND "Berechnung" OR "calculation" OR "Formel" OR "formula"
        - Search for: "100 m²" OR "10 m²" AND "Wohnung" OR "apartment"
        - Search for: Section numbers mentioned (e.g., "§ 11", "Section 11")
        Make sure to search specifically for jurisdiction-appropriate documents first.
        
        Provide exact numbers, formulas, and legal requirements as written in the documents.
        If you find calculation formulas, include them exactly as they appear.
        
        When presenting your findings:
        - ALWAYS mention the document priority level (1_/2_ = Law/Regulation, 3_ = OIB Guideline, 4_ = ÖNORM Standard)
        - If using 3_ or 4_ documents, explain why 1_/2_ documents were insufficient
        - Prioritize information from higher-priority documents in your response
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
                # Get priority information
                source = metadata.get('source', 'unknown')
                priority = 1 if source.startswith(('1_', '2_')) else (2 if source.startswith('3_') else (3 if source.startswith('4_') else 4))
                priority_text = {
                    1: "LAW/REGULATION (1_/2_) - HIGHEST PRIORITY",
                    2: "OIB GUIDELINE (3_) - SECOND PRIORITY", 
                    3: "ÖNORM STANDARD (4_) - LOWEST PRIORITY",
                    4: "UNKNOWN PRIORITY"
                }.get(priority, "UNKNOWN PRIORITY")
                
                citation = {
                    "pdf_name": source,
                    "page": metadata.get('page', 'N/A'),
                    "paragraph": metadata.get('paragraph', 'N/A'),
                    "chunk_id": metadata.get('chunk_id', ''),
                    "file_path": metadata.get('file_path', ''),
                    "priority": priority,
                    "priority_text": priority_text,
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
