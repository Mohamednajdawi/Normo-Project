"""
Command-line interface for managing the Normo backend.
"""

import argparse
import sys
from pathlib import Path

from normo_backend.services.vector_store import get_vector_store
from normo_backend.utils.pdf_processor import get_available_pdfs


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Normo Backend CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Vector store commands
    vs_parser = subparsers.add_parser("vectorstore", help="Vector store management")
    vs_subparsers = vs_parser.add_subparsers(dest="vs_command")
    
    # Status command
    vs_subparsers.add_parser("status", help="Show vector store status")
    
    # Embed command
    embed_parser = vs_subparsers.add_parser("embed", help="Embed PDFs")
    embed_parser.add_argument("--all", action="store_true", help="Embed all available PDFs")
    embed_parser.add_argument("--force", action="store_true", help="Force re-embedding")
    embed_parser.add_argument("pdfs", nargs="*", help="Specific PDFs to embed")
    
    # Reset command
    vs_subparsers.add_parser("reset", help="Reset vector store (delete all embeddings)")
    
    # List command
    vs_subparsers.add_parser("list", help="List available PDFs")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "vectorstore":
        handle_vectorstore_command(args)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


def handle_vectorstore_command(args):
    """Handle vector store commands."""
    if not args.vs_command:
        print("Vector store command required. Use --help for options.")
        return
    
    vector_store = get_vector_store()
    
    if args.vs_command == "status":
        print("📊 Vector Store Status")
        print("=" * 40)
        
        stats = vector_store.get_collection_stats()
        print(f"Total chunks: {stats['total_chunks']}")
        print(f"Embedded PDFs: {stats['embedded_pdfs']}")
        
        if stats['pdf_list']:
            print("\nEmbedded PDFs:")
            for pdf in stats['pdf_list']:
                print(f"  ✅ {pdf}")
        
        available_pdfs = get_available_pdfs("arch_pdfs")
        embedded_pdfs = set(stats['pdf_list'])
        missing_pdfs = set(available_pdfs) - embedded_pdfs
        
        if missing_pdfs:
            print(f"\nAvailable but not embedded ({len(missing_pdfs)}):")
            for pdf in missing_pdfs:
                print(f"  ⏳ {pdf}")
    
    elif args.vs_command == "embed":
        if args.all:
            available_pdfs = get_available_pdfs("arch_pdfs")
            if args.force:
                vector_store.reset_vector_store()
            result = vector_store.ensure_pdfs_embedded(available_pdfs)
            if result:
                print("✅ Embedding completed")
            else:
                print("ℹ️  All PDFs already embedded")
        elif args.pdfs:
            if args.force:
                # For specific PDFs, we would need to implement selective reset
                print("⚠️  Force flag not supported for specific PDFs yet")
            result = vector_store.ensure_pdfs_embedded(args.pdfs)
            if result:
                print("✅ Embedding completed")
            else:
                print("ℹ️  Specified PDFs already embedded")
        else:
            print("❌ No PDFs specified. Use --all or provide specific PDF names.")
    
    elif args.vs_command == "reset":
        confirmation = input("⚠️  This will delete all embeddings. Are you sure? (y/N): ")
        if confirmation.lower() in ['y', 'yes']:
            vector_store.reset_vector_store()
            print("✅ Vector store reset completed")
        else:
            print("❌ Reset cancelled")
    
    elif args.vs_command == "list":
        available_pdfs = get_available_pdfs("arch_pdfs")
        stats = vector_store.get_collection_stats()
        embedded_pdfs = set(stats['pdf_list'])
        
        print("📚 Available PDFs")
        print("=" * 40)
        
        for pdf in available_pdfs:
            status = "✅ Embedded" if pdf in embedded_pdfs else "⏳ Not embedded"
            print(f"{status:<15} {pdf}")
        
        print(f"\nTotal: {len(available_pdfs)} PDFs, {len(embedded_pdfs)} embedded")


if __name__ == "__main__":
    main()
