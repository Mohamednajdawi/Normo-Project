"""PDF processing utilities for loading and chunking PDF documents."""

import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re


def parse_document_metadata(pdf_name: str, pdf_path: Path) -> dict:
    """Parse document metadata from filename and folder structure.
    
    Args:
        pdf_name: Relative path to PDF file
        pdf_path: Full path to PDF file
        
    Returns:
        Dictionary with parsed metadata
    """
    metadata = {
        "source": pdf_name,
        "file_path": str(pdf_path),
        "document_type": "unknown",
        "jurisdiction": "unknown",
        "category": "unknown",
        "year": "unknown",
        "title": "unknown"
    }
    
    # Parse filename pattern: {level}_{country}_{state}_{type}_{category}_{title}_{year}.pdf
    filename = Path(pdf_name).name
    
    # Try different patterns to handle various filename formats
    patterns = [
        r'(\d+)_AT_([^_]+)_(\d+)_([^_]+)_(.+?)_(\d{4})\.pdf',  # Standard pattern
        r'(\d+)_AT_([^_]+)_(\d+)_([^_]+)_(.+?)\.pdf',  # Without year
        r'(\d+)_AT_([^_]+)_([^_]+)_(.+?)_(\d{4})\.pdf',  # Without type code
        r'(\d+)_AT_([^_]+)_([^_]+)_(.+?)\.pdf',  # Without type code and year
    ]
    
    match = None
    for pattern in patterns:
        match = re.match(pattern, filename)
        if match:
            break
    
    if match:
        groups = match.groups()
        
        # Map level to document type
        level_map = {
            "1": "law",
            "2": "regulation", 
            "3": "guideline",
            "4": "standard"
        }
        
        # Map state to jurisdiction
        state_map = {
            "0": "federal",
            "W": "vienna",
            "OOE": "upper_austria"
        }
        
        # Map category
        category_map = {
            "GE": "law",
            "VE": "regulation",
            "OIB": "guideline",
            "OEN": "standard"
        }
        
        # Handle different pattern matches
        if len(groups) == 6:  # Standard pattern with all fields
            level, state, type_code, category, title, year = groups
            metadata.update({
                "document_type": level_map.get(level, "unknown"),
                "jurisdiction": state_map.get(state, "unknown"),
                "category": category_map.get(category, "unknown"),
                "year": year,
                "title": title.replace("_", " "),
                "level": level,
                "state_code": state,
                "type_code": type_code
            })
        elif len(groups) == 5:  # Without year
            level, state, type_code, category, title = groups
            metadata.update({
                "document_type": level_map.get(level, "unknown"),
                "jurisdiction": state_map.get(state, "unknown"),
                "category": category_map.get(category, "unknown"),
                "title": title.replace("_", " "),
                "level": level,
                "state_code": state,
                "type_code": type_code
            })
        elif len(groups) == 4:  # Without type code
            level, state, category, title = groups
            metadata.update({
                "document_type": level_map.get(level, "unknown"),
                "jurisdiction": state_map.get(state, "unknown"),
                "category": category_map.get(category, "unknown"),
                "title": title.replace("_", " "),
                "level": level,
                "state_code": state
            })
    
    # Parse folder structure for additional context
    path_parts = Path(pdf_name).parts
    
    if len(path_parts) >= 2:
        main_folder = path_parts[0]
        sub_folder = path_parts[1] if len(path_parts) > 1 else ""
        
        # Map main folder to document category
        folder_map = {
            "00_Bundesgesetze": "federal_laws",
            "01-02_Bundesländer- Gesetze und Verordnungen": "state_laws",
            "03_OIB Richtlinien": "oib_guidelines",
            "04_ÖNORM": "austrian_standards"
        }
        
        metadata["folder_category"] = folder_map.get(main_folder, "unknown")
        
        # Extract state from subfolder
        if "Wien" in sub_folder:
            metadata["jurisdiction"] = "vienna"
        elif "OBERÖSTERREICH" in sub_folder:
            metadata["jurisdiction"] = "upper_austria"
        elif "Bundesgesetze" in main_folder:
            metadata["jurisdiction"] = "federal"
    
    # Extract OIB guideline number if applicable
    if "OIB" in filename:
        oib_match = re.search(r'OIB-RL\s*(\d+(?:\.\d+)?)', filename)
        if oib_match:
            metadata["oib_guideline_number"] = oib_match.group(1)
    
    return metadata


def load_pdfs_from_folder(pdf_folder: str, pdf_names: List[str]) -> List[Document]:
    """Load and process PDF documents from a hierarchical folder structure.
    
    Args:
        pdf_folder: Path to the folder containing PDF files
        pdf_names: List of PDF filenames to load (can include relative paths)
        
    Returns:
        List of Document objects with text content and metadata
    """
    documents = []
    pdf_folder_path = Path(pdf_folder)
    
    # Initialize text splitter optimized for legal/technical documents
    # Smaller chunks with more overlap to preserve calculation context
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,  # Smaller chunks for better precision
        chunk_overlap=300,  # More overlap to preserve context around calculations
        length_function=len,
        add_start_index=True,
        separators=["\n\n", "\n", ".", "!", "?", ";", ",", " ", ""],  # Better sentence preservation
    )
    
    for pdf_name in pdf_names:
        # Handle both simple filenames and relative paths
        pdf_path = pdf_folder_path / pdf_name
        
        if not pdf_path.exists():
            print(f"Warning: PDF file {pdf_name} not found in {pdf_folder}")
            continue
            
        try:
            # Load PDF using PyPDFLoader
            loader = PyPDFLoader(str(pdf_path))
            pdf_documents = loader.load()
            
            print(f"📚 Loading {pdf_name}: {len(pdf_documents)} pages found")
            
            # Split documents into chunks with correct page tracking
            for doc_idx, doc in enumerate(pdf_documents):
                # PyPDFLoader provides 0-based page numbers, convert to 1-based for user display
                zero_based_page = doc.metadata.get("page", doc_idx)
                page_label = doc.metadata.get("page_label")
                
                # Use page_label if available (usually better), otherwise convert 0-based to 1-based
                if page_label and page_label.isdigit():
                    page_num = int(page_label)
                else:
                    page_num = zero_based_page + 1
                
                # Parse enhanced metadata from filename and folder structure
                enhanced_metadata = parse_document_metadata(pdf_name, pdf_path)
                
                # Add enhanced source metadata
                doc.metadata.update({
                    "source": pdf_name,
                    "file_path": str(pdf_path),
                    "page": page_num,
                    "original_page_index": zero_based_page,  # Keep original for debugging
                    **enhanced_metadata  # Add all parsed metadata
                })
                
                # Split this page's content into chunks
                chunks = text_splitter.split_documents([doc])
                
                # Add paragraph/chunk information to each chunk from this page
                for chunk_idx, chunk in enumerate(chunks):
                    # Each chunk represents a paragraph/section on this specific page
                    chunk.metadata.update({
                        "paragraph": chunk_idx + 1,  # Paragraph number within this page
                        "total_chunks_on_page": len(chunks),
                        "chunk_id": f"{pdf_name}_p{page_num}_c{chunk_idx + 1}",
                        "page": page_num  # Ensure correct page number is preserved
                    })
                    
                documents.extend(chunks)
                
        except Exception as e:
            print(f"Error loading PDF {pdf_name}: {str(e)}")
            continue
    
    return documents


def get_available_pdfs(pdf_folder: str) -> List[str]:
    """Get list of available PDF files in the hierarchical folder structure.
    
    Args:
        pdf_folder: Path to the folder containing PDF files
        
    Returns:
        List of PDF filenames found in the folder (with relative paths)
    """
    pdf_folder_path = Path(pdf_folder)
    
    if not pdf_folder_path.exists():
        return []
    
    pdf_files = []
    
    # Search recursively through the hierarchical structure
    for file_path in pdf_folder_path.rglob("*.pdf"):
        # Get relative path from the pdf_folder
        relative_path = file_path.relative_to(pdf_folder_path)
        pdf_files.append(str(relative_path))
    
    return sorted(pdf_files)


def create_fallback_documents(pdf_names: List[str], user_query: str) -> List[Document]:
    """Create fallback when PDFs cannot be loaded.
    
    Returns an error document indicating the issue.
    """
    return [
        Document(
            page_content=f"Error: Could not load PDF documents. Requested PDFs: {', '.join(pdf_names)}. Please ensure the PDF files exist in the arch_pdfs folder and are readable.",
            metadata={"source": "error", "user_query": user_query, "type": "error"}
        )
    ]
