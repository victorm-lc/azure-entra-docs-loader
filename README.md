# Azure Blob Storage Tools with Entra ID

> **TL;DR:** Custom Azure Blob Storage loaders + composable LangGraph tools that properly support service principal authentication via Entra ID.

This repository provides:

1. **Custom LangChain Document Loaders** - Drop-in replacements for LangChain's Azure blob loaders
2. **Modular LangGraph Tools** - Composable tools for discovery, search, and document loading
3. **Demo Agent** - Interactive example showing enterprise-ready Azure document management

## 🔧 Components

### Experimental Document Loaders
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

The main demo showcases composable Azure document management tools:

```bash
# Run the automated demo workflow
python modular_agent_example.py
```

### Demo Workflow
The script demonstrates the modular approach with these steps:

1. **Discovery** - Find available containers in the storage account
2. **Browse** - List documents in a container without loading content  
3. **Search** - Filter documents by metadata (filename, type, date, size)
4. **Summarize** - AI-powered document summaries with actual content
5. **Load** - Full document content when needed (extensible for other use cases)

### Key Features Demonstrated
- **Modular tool composition** - Each tool has a single responsibility
- **Efficient workflow** - Only loads content when needed
- **Rich metadata** - Enhanced document properties and context
- **Enterprise authentication** - Service principal support with Entra ID

## 🏢 Enterprise Deployment

For production deployment on **LangGraph Platform**, authenticate the use using custom auth and store Azure credentials in the AuthContext.

Docs: https://langchain-ai.github.io/langgraph/tutorials/auth/getting_started/