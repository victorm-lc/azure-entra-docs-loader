# Azure Blob Storage Loaders with Entra ID

> **TL;DR:** These are drop-in replacements for LangChain's Azure blob loaders that properly support service principal authentication via Entra ID.

This repository provides two custom LangChain document loaders that solve authentication issues with Azure Blob Storage when using service principals:

- `AzureBlobStorageContainerEntraLoader` - Loads all documents from a container
- `AzureBlobStorageEntraLoader` - Loads specific files or all files from a container

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
pip install -r requirements.txt
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

### 2. Test the Setup

```bash
# Activate UV environment
uv run python azure_blob_entra_container_loader.py

# Or with traditional Python
python azure_blob_entra_container_loader.py
```

## Usage Examples

### Container Loader (Multiple Files)

```python
from azure_blob_entra_container_loader import AzureBlobStorageContainerEntraLoader
import re

# Load all documents
loader = AzureBlobStorageContainerEntraLoader(
    storage_account_name="yourstorageaccount",
    container="documents"
)
documents = loader.load()

# Load with filters
loader = AzureBlobStorageContainerEntraLoader(
    storage_account_name="yourstorageaccount",
    container="documents",
    prefix="reports/",  # Only files in reports/ folder
    file_pattern=re.compile(r"\.(pdf|docx)$", re.IGNORECASE)  # Only PDF and DOCX
)
documents = loader.load()

# Convenience function
from azure_blob_entra_container_loader import load_azure_blob_documents

docs = load_azure_blob_documents(
    storage_account_name="yourstorageaccount",
    container="documents",
    prefix="reports/",
    file_pattern=re.compile(r"\.pdf$", re.IGNORECASE)
)
```

### File Loader (Single Files)

```python
from azure_blob_entra_loader import AzureBlobStorageEntraLoader

# Load specific file
loader = AzureBlobStorageEntraLoader(
    storage_account_name="yourstorageaccount",
    container_name="documents",
    blob_name="important-report.pdf"
)
documents = loader.load()

# Load all files in container (same as container loader)
loader = AzureBlobStorageEntraLoader(
    storage_account_name="yourstorageaccount",
    container_name="documents"
)
documents = loader.load()
```

## Document Metadata

Both loaders enhance documents with rich metadata:

```python
{
    "source": "https://yourstorageaccount.blob.core.windows.net/documents/report.pdf",
    "blob_name": "report.pdf",
    "container": "documents",
    "storage_account": "yourstorageaccount",
    "file_size": 1024576,
    "last_modified": "2024-01-15T10:30:00Z",
    "content_type": "application/pdf"
}
```

## Comparison with LangChain Built-ins

| Feature | LangChain Built-in | These Custom Loaders |
|---------|-------------------|---------------------|
| Service Principal Auth | ❌ Problematic | ✅ Works perfectly |
| Connection String | ✅ Supported | ✅ Supported |
| DefaultAzureCredential | ⚠️ Inconsistent | ✅ Reliable |
| Metadata | ✅ Basic | ✅ Enhanced |
| Error Handling | ⚠️ Basic | ✅ Robust |

## Migration from LangChain Built-ins

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

## Troubleshooting

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

### Verify Service Principal Setup

```bash
# Check if service principal can access Azure
az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID

# List storage accounts you have access to
az storage account list --query "[].name" -o table
```

## Microsoft Azure Configuration Summary

To get this working in Microsoft Azure:

1. **Azure Active Directory**: Create App Registration (Service Principal)
2. **Storage Account**: Assign "Storage Blob Data Reader" role to Service Principal
3. **Networking**: Ensure storage account allows access from your location
4. **Environment**: Set `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

## Dependencies

```
azure-identity>=1.15.0
azure-storage-blob>=12.19.0
langchain-core>=0.1.0
langchain-community>=0.0.20
langchain-unstructured>=0.1.0
unstructured[pdf]>=0.12.0
python-dotenv>=1.0.0
```

## Development

This project uses UV for dependency management:

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run ruff format

# Lint code
uv run ruff check
```

## License

MIT License