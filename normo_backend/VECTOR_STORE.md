# Persistent Vector Store

The Normo backend now uses a persistent ChromaDB vector store for efficient PDF embedding and retrieval. This dramatically improves performance by avoiding re-embedding PDFs on every request.

## Key Features

### 🚀 **Performance Improvements**
- **First run**: Embeds all PDFs (~2-3 minutes for 13 PDFs with 2352 chunks)
- **Subsequent runs**: Uses existing embeddings (⚡ **instant!**)
- **Incremental updates**: Only embeds new or changed PDFs

### 🔍 **Smart Change Detection**
- Tracks file size, modification time, and MD5 hash
- Automatically detects when PDFs are added, removed, or modified
- Only processes changes, saving time and API costs

### 💾 **Persistent Storage**
- Embeddings stored in `vector_store/` directory
- Metadata tracking in `vector_store/pdf_metadata.json`
- Survives server restarts and deployments

## Usage

### Automatic (Recommended)
The system automatically handles embeddings when you run the backend:

```bash
# Start the backend - it will use existing embeddings if available
source .env && PYTHONPATH=$(pwd)/src uv run python -m normo_backend.main
```

On first run or when new PDFs are detected:
```
🔍 Ensuring 3 PDFs are embedded...
🆕 New PDF detected: new_document.pdf
✅ New embeddings created
📊 Vector store stats: 2352 chunks from 13 PDFs
```

On subsequent runs:
```
🔍 Ensuring 3 PDFs are embedded...
⚡ Using existing embeddings (fast!)
📊 Vector store stats: 2352 chunks from 13 PDFs
```

### CLI Management
Use the CLI tool for advanced vector store management:

```bash
# Check status
uv run normo-cli vectorstore status

# List all PDFs and their embedding status
uv run normo-cli vectorstore list

# Embed all PDFs manually
uv run normo-cli vectorstore embed --all

# Embed specific PDFs
uv run normo-cli vectorstore embed document1.pdf document2.pdf

# Reset vector store (delete all embeddings)
uv run normo-cli vectorstore reset
```

## File Structure

```
normo_backend/
├── vector_store/                 # Persistent ChromaDB storage
│   ├── chroma.sqlite3           # ChromaDB database
│   ├── pdf_metadata.json       # PDF tracking metadata
│   └── ...                     # ChromaDB index files
├── arch_pdfs/                  # Source PDF documents
│   ├── 1_AT_OOE_*.pdf         # Austrian legal documents
│   └── ...
└── src/normo_backend/
    ├── services/
    │   └── vector_store.py     # Persistent vector store service
    └── cli.py                  # CLI management tool
```

## Metadata Tracking

The system tracks each PDF with the following metadata:

```json
{
  "document_name.pdf": {
    "size": 1234567,
    "modified": 1703123456.789,
    "hash": "a1b2c3d4e5f6..."
  }
}
```

## Benefits

### 🎯 **For Development**
- **Faster iteration**: No waiting for re-embedding during development
- **Cost savings**: Avoid unnecessary OpenAI API calls
- **Debugging**: Consistent embeddings between runs

### 🎯 **For Production**
- **Quick startup**: Server starts immediately with existing embeddings
- **Scalability**: Handle large document collections efficiently
- **Reliability**: Persistent storage survives deployments

### 🎯 **For Content Updates**
- **Smart updates**: Only process changed documents
- **Version control**: Track document changes automatically
- **Incremental growth**: Add new documents without re-processing existing ones

## Advanced Usage

### Force Re-embedding
```bash
# Reset and re-embed everything
uv run normo-cli vectorstore reset
uv run normo-cli vectorstore embed --all
```

### Check What Changed
```bash
# See which PDFs are embedded vs available
uv run normo-cli vectorstore list
```

### Monitor Performance
The backend logs show embedding performance:
```
📊 Processing 13 PDFs for embedding...
💾 Adding 2352 chunks to vector store...
✅ Successfully embedded 13 PDFs with 2352 chunks
```

## Troubleshooting

### No PDFs Found
```
❌ No valid PDFs found in arch_pdfs
```
**Solution**: Ensure PDF files are in the `arch_pdfs/` directory.

### Permission Errors
```
Warning: Could not save metadata file: Permission denied
```
**Solution**: Ensure write permissions for the `vector_store/` directory.

### Reset if Issues
If you encounter any issues with the vector store:
```bash
uv run normo-cli vectorstore reset
uv run normo-cli vectorstore embed --all
```

This will delete all embeddings and recreate them from scratch.
