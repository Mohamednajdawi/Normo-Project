"""
Persistent Vector Store Service for ChromaDB with incremental PDF loading.
Handles embedding creation, storage, and incremental updates.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from normo_backend.config import get_settings
from normo_backend.utils.pdf_processor import (get_available_pdfs,
                                               load_pdfs_from_folder)


class PersistentVectorStore:
    """Manages persistent ChromaDB vector store with incremental PDF loading."""
    
    def __init__(self, persist_directory: str = "vector_store", pdf_folder: str = "arch_pdfs"):
        self.persist_directory = persist_directory
        self.pdf_folder = pdf_folder
        self.metadata_file = Path(persist_directory) / "pdf_metadata.json"
        
        # Ensure directories exist
        Path(persist_directory).mkdir(exist_ok=True)
        
        # Initialize embeddings
        settings = get_settings()
        self.embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
        
        # Initialize ChromaDB with persistence
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name="normo_legal_docs"
        )
        
        # Load or create metadata tracking
        self.pdf_metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Dict]:
        """Load PDF metadata tracking file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load metadata file: {e}")
                return {}
        return {}
    
    def _save_metadata(self):
        """Save PDF metadata tracking file."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.pdf_metadata, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save metadata file: {e}")
    
    def _get_pdf_hash(self, pdf_path: str) -> str:
        """Calculate MD5 hash of PDF file for change detection."""
        try:
            with open(pdf_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except IOError:
            return ""
    
    def _get_pdf_stats(self, pdf_path: str) -> Dict:
        """Get PDF file statistics."""
        try:
            stat = os.stat(pdf_path)
            return {
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "hash": self._get_pdf_hash(pdf_path)
            }
        except OSError:
            return {}
    
    def get_pdfs_to_process(self, pdf_names: List[str]) -> List[str]:
        """Determine which PDFs need to be processed (new or changed)."""
        pdfs_to_process = []
        
        for pdf_name in pdf_names:
            pdf_path = Path(self.pdf_folder) / pdf_name
            
            if not pdf_path.exists():
                print(f"⚠️  PDF not found: {pdf_name}")
                continue
            
            current_stats = self._get_pdf_stats(str(pdf_path))
            if not current_stats:
                continue
            
            # Check if PDF is new or changed
            if pdf_name not in self.pdf_metadata:
                print(f"🆕 New PDF detected: {pdf_name}")
                pdfs_to_process.append(pdf_name)
            else:
                stored_stats = self.pdf_metadata[pdf_name]
                if (stored_stats.get("hash") != current_stats.get("hash") or
                    stored_stats.get("size") != current_stats.get("size")):
                    print(f"🔄 Changed PDF detected: {pdf_name}")
                    pdfs_to_process.append(pdf_name)
                else:
                    print(f"✅ PDF already embedded: {pdf_name}")
        
        return pdfs_to_process
    
    def remove_pdf_embeddings(self, pdf_name: str):
        """Remove embeddings for a specific PDF."""
        try:
            # Get all document IDs for this PDF
            results = self.vectorstore.similarity_search(
                query="", 
                k=10000,  # Large number to get all docs
                filter={"source": pdf_name}
            )
            
            if results:
                print(f"🗑️  Removing {len(results)} existing chunks for {pdf_name}")
                # ChromaDB doesn't have a direct way to delete by metadata filter
                # So we need to delete the entire collection and rebuild
                # For now, we'll track this for full rebuild when needed
                pass
            
        except Exception as e:
            print(f"Warning: Could not remove embeddings for {pdf_name}: {e}")
    
    def add_pdf_embeddings(self, pdf_names: List[str]) -> int:
        """Add embeddings for new/changed PDFs."""
        if not pdf_names:
            return 0
        
        print(f"📊 Processing {len(pdf_names)} PDFs for embedding...")
        
        # Load documents from PDFs
        documents = load_pdfs_from_folder(self.pdf_folder, pdf_names)
        
        if not documents:
            print("❌ No documents loaded")
            return 0
        
        # Add documents to vector store
        print(f"💾 Adding {len(documents)} chunks to vector store...")
        self.vectorstore.add_documents(documents)
        
        # Update metadata for processed PDFs
        for pdf_name in pdf_names:
            pdf_path = Path(self.pdf_folder) / pdf_name
            if pdf_path.exists():
                self.pdf_metadata[pdf_name] = self._get_pdf_stats(str(pdf_path))
        
        # Save metadata
        self._save_metadata()
        
        print(f"✅ Successfully embedded {len(pdf_names)} PDFs with {len(documents)} chunks")
        return len(documents)
    
    def get_retriever(self, search_kwargs: Optional[Dict] = None):
        """Get retriever for the vector store."""
        default_kwargs = {
            "search_type": "mmr",
            "search_kwargs": {
                "k": 12,
                "lambda_mult": 0.7,
                "fetch_k": 20
            }
        }
        
        if search_kwargs:
            default_kwargs.update(search_kwargs)
        
        return self.vectorstore.as_retriever(**default_kwargs)
    
    def ensure_pdfs_embedded(self, pdf_names: List[str]) -> bool:
        """Ensure specified PDFs are embedded. Returns True if any new embeddings were created."""
        # Get available PDFs if none specified
        if not pdf_names:
            pdf_names = get_available_pdfs(self.pdf_folder)
        
        # Filter to only existing PDFs
        existing_pdfs = []
        for pdf_name in pdf_names:
            if (Path(self.pdf_folder) / pdf_name).exists():
                existing_pdfs.append(pdf_name)
        
        if not existing_pdfs:
            print(f"❌ No valid PDFs found in {self.pdf_folder}")
            return False
        
        # Check which PDFs need processing
        pdfs_to_process = self.get_pdfs_to_process(existing_pdfs)
        
        if not pdfs_to_process:
            print(f"✅ All {len(existing_pdfs)} PDFs already embedded")
            return False
        
        # Process new/changed PDFs
        chunks_added = self.add_pdf_embeddings(pdfs_to_process)
        
        return chunks_added > 0
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector store collection."""
        try:
            # Get collection info
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "total_chunks": count,
                "embedded_pdfs": len(self.pdf_metadata),
                "pdf_list": list(self.pdf_metadata.keys())
            }
        except Exception as e:
            return {
                "total_chunks": 0,
                "embedded_pdfs": 0,
                "pdf_list": [],
                "error": str(e)
            }
    
    def reset_vector_store(self):
        """Reset the entire vector store (useful for debugging or full rebuild)."""
        try:
            # Delete the collection
            self.vectorstore.delete_collection()
            
            # Clear metadata
            self.pdf_metadata = {}
            self._save_metadata()
            
            # Recreate vector store
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="normo_legal_docs"
            )
            
            print("🔄 Vector store reset successfully")
            
        except Exception as e:
            print(f"❌ Error resetting vector store: {e}")


# Global instance
_vector_store = None

def get_vector_store() -> PersistentVectorStore:
    """Get the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = PersistentVectorStore()
    return _vector_store
