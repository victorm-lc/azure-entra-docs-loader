# Azure Blob Storage Tools with Entra ID

> **TL;DR:** Custom Azure Blob Storage loaders + composable LangGraph tools that properly support service principal authentication via Entra ID.

This repository provides:

1. **Custom LangChain Document Loaders** - Drop-in replacements for LangChain's Azure blob loaders
2. **Modular LangGraph Tools** - Composable tools for discovery, search, and document loading
3. **Demo Agent** - Interactive example showing enterprise-ready Azure document management

## 🔧 Components

### Document Loaders
- `AzureBlobStorageContainerEntraLoader` - Loads all documents from a container
- `AzureBlobStorageEntraLoader` - Loads specific files or all files from a container

### LangGraph Tools (Modular & Composable)
- `list_available_containers` - Discover available containers
- `list_documents_in_container` - Browse documents without loading content
- `search_documents_by_metadata` - Filter by filename, type, date, size
- `load_document_from_blob` - Load and parse specific documents
- `summarize_document` - AI-powered document summarization

## Why These Loaders?

LangChain's built-in Azure blob loaders (`AzureBlobStorageContainerLoader` and `AzureBlobStorageFileLoader`) have issues with service principal authentication. These custom loaders:

- ✅ **Properly support service principal authentication**
- ✅ **Use DefaultAzureCredential for seamless auth**
- ✅ **Drop-in replacements with same interface**
- ✅ **Enhanced metadata with blob properties**
- ✅ **Robust error handling**

## Prerequisites

Before using these loaders, you need:
1. **Azure Storage Account** with blob containers
2. **Service Principal** with appropriate permissions
3. **Python 3.8+** with UV package manager

## Installation

This project uses [UV](https://docs.astral.sh/uv/) as the package manager for fast, reliable dependency management.

### Install UV (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install Dependencies

```bash
# Install all dependencies
uv sync

# Or install manually
uv add azure-identity azure-storage-blob langchain-core langchain-community langchain-unstructured unstructured python-dotenv
```

### Alternative: Traditional pip install

```bash
# Install from pyproject.toml (recommended)
pip install -e .

# Or install specific dependencies
pip install azure-identity azure-storage-blob langchain-community langchain-core langchain-unstructured "unstructured[pdf]"
```

## Azure Setup

### Step 1: Create Service Principal

1. **Go to Azure Portal** → **Azure Active Directory** → **App registrations**
2. **Click "New registration"**
3. **Enter a name** (e.g., "LangChain Blob Loader")
4. **Click "Register"**
5. **Copy the Application (client) ID** and **Directory (tenant) ID**
6. **Go to "Certificates & secrets"** → **"New client secret"**
7. **Copy the client secret value** (save it immediately!)

### Step 2: Assign Storage Permissions

1. **Go to your Storage Account** → **Access Control (IAM)**
2. **Click "Add role assignment"**
3. **Select "Storage Blob Data Reader"** role
4. **Select your service principal** from Step 1
5. **Click "Review + assign"**

### Step 3: Set Environment Variables

Create a `.env` file in your project root:

```bash
# Service Principal credentials
AZURE_CLIENT_ID=your-application-client-id
AZURE_TENANT_ID=your-directory-tenant-id
AZURE_CLIENT_SECRET=your-client-secret

# Storage configuration (optional, has working defaults)
AZURE_STORAGE_ACCOUNT_NAME=yourstorageaccount
AZURE_STORAGE_CONTAINER=yourcontainer
```

## Quick Start

### 1. Basic Usage

```python
from azure_blob_entra_container_loader import AzureBlobStorageContainerEntraLoader
from azure_blob_entra_loader import AzureBlobStorageEntraLoader

# Load all documents from container
loader = AzureBlobStorageContainerEntraLoader(
    storage_account_name="yourstorageaccount",
    container="documents"
)
documents = loader.load()

# Load specific file
file_loader = AzureBlobStorageEntraLoader(
    storage_account_name="yourstorageaccount",
    container_name="documents",
    blob_name="report.pdf"
)
document = file_loader.load()
```

### 2. Test the Basic Loaders

```bash
# Test the container loader
python azure_blob_entra_container_loader.py

# Test individual file loader
python azure_blob_entra_loader.py
```

## 🚀 LangGraph Tools Demo

The main demo showcases enterprise-ready, composable Azure document management tools:

```bash
# Run the interactive demo
python modular_agent_example.py

# Choose mode:
# 1. Interactive chat - Chat with the agent
# 2. Demo workflow - Automated demo of all tools
```

### Demo Workflow
1. **Discovery** - Find available containers
2. **Browse** - List documents without loading content  
3. **Search** - Filter by metadata (filename, type, date, size)
4. **Summarize** - AI-powered document summaries
5. **Load** - Full document content when needed

### Example Interactions
- *"What containers are available?"*
- *"Show me documents in the docs container"*
- *"Find all PDF files from last month"*
- *"Summarize the quarterly-report.pdf document"*
- *"Load the full content of research-paper.pdf"*

## 🏢 Enterprise Deployment

For production deployment on **LangGraph Platform**, store Azure credentials in the `MinimalUserDict` for custom authentication:

```python
# For LangGraph Platform deployment
# Store these in MinimalUserDict instead of environment variables
azure_config = {
    "AZURE_CLIENT_ID": "your-application-client-id",
    "AZURE_TENANT_ID": "your-directory-tenant-id", 
    "AZURE_CLIENT_SECRET": "your-client-secret"
}
```

This demo uses environment variables for simplicity, but enterprise deployments should use proper credential management.

## 🎯 Key Benefits

### Modular Design
- **Composable tools** - Each tool has a single responsibility
- **Scalable** - Easy to add new search/filter capabilities  
- **Efficient** - Only loads content when needed
- **Extensible** - Ready for semantic search, chunking, embeddings

### Enterprise Ready
- **Proper authentication** - Service principal support that actually works
- **Robust error handling** - Graceful failures and helpful error messages
- **Rich metadata** - Enhanced document properties and context
- **Production patterns** - Follows best practices for Azure integration

## 📋 Document Metadata

The loaders provide rich metadata for each document:

```python
{
    "source": "https://yourstorageaccount.blob.core.windows.net/documents/report.pdf",
    "blob_name": "report.pdf", 
    "container": "documents",
    "storage_account": "yourstorageaccount",
    "file_size": 1024576,
    "last_modified": "2024-01-15T10:30:00Z",
    "content_type": "application/pdf",
    "element_id": "unique-element-identifier",
    "page_number": 1,
    "category": "Header"  # or "Paragraph", "Table", etc.
}
```

## 📁 Project Structure

```
├── azure_blob_entra_container_loader.py  # Container loader + test script
├── azure_blob_entra_loader.py           # Individual file loader + test script
├── modular_azure_tools.py               # LangGraph tools (main demo)
├── modular_agent_example.py             # Interactive agent demo
├── requirements.txt                     # Dependencies
├── pyproject.toml                       # Project configuration
└── README.md                           # This file
```

## 🔄 Migration from LangChain Built-ins

### Before (LangChain built-in)
```python
from langchain_community.document_loaders import AzureBlobStorageContainerLoader

# Often fails with service principals
loader = AzureBlobStorageContainerLoader(
    account_url="https://yourstorageaccount.blob.core.windows.net",
    container="documents"
)
```

### After (Custom loader)
```python
from azure_blob_entra_container_loader import AzureBlobStorageContainerEntraLoader

# Works reliably with service principals
loader = AzureBlobStorageContainerEntraLoader(
    storage_account_name="yourstorageaccount",
    container="documents"
)
```

### Enterprise (LangGraph Tools)
```python
from modular_azure_tools import MODULAR_AZURE_TOOLS
from langgraph.prebuilt import create_react_agent

# Composable, enterprise-ready tools
agent = create_react_agent(llm, tools=MODULAR_AZURE_TOOLS)
```

## 🔧 Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure service principal has Storage Blob Data Reader role
2. **Container Not Found**: Verify container name is correct (case-sensitive)
3. **No Documents**: Check if container has files and file patterns match
4. **Environment Variables**: Make sure `.env` file is in the correct location

### Debug Steps

```python
# Test Azure credentials
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

credential = DefaultAzureCredential()
client = BlobServiceClient(
    account_url="https://yourstorageaccount.blob.core.windows.net",
    credential=credential
)

# List containers
for container in client.list_containers():
    print(f"Container: {container.name}")
```

## 📄 License

MIT License

