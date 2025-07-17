# Accessing Azure Blob Storage through Azure AI Foundry

This repository demonstrates how to access Azure Blob Storage through Azure AI Foundry connections, providing a solution for scenarios where LangChain's Azure blob loaders don't support your authentication method (e.g., service principal credentials).

## Problem Statement

LangChain's Azure blob storage loaders (`AzureBlobStorageContainerLoader` and `AzureBlobStorageFileLoader`) require either:
- A connection string (with account key)
- Account URL with DefaultAzureCredential

However, they don't directly support service principal authentication with client credentials. If your organization uses service principals for authentication, you need an alternative approach.

## Solution: Use Azure AI Foundry as a Bridge

Azure AI Foundry allows you to configure storage connections with various authentication methods. By accessing your storage through AI Foundry's connection management, you can:

1. Use service principal authentication to connect to AI Foundry
2. Retrieve storage account credentials from AI Foundry connections
3. Use these credentials with LangChain loaders

## Prerequisites

- Azure subscription with AI Foundry project
- Service principal with appropriate permissions
- Python 3.8+
- Storage account connected to your AI Foundry project

## Setup

### 1. Install Dependencies

```bash
pip install azure-ai-projects azure-identity langchain-community azure-storage-blob python-dotenv
```

For PDF processing:
```bash
pip install unstructured unstructured[pdf]
```

### 2. Environment Variables

Create a `.env` file with your credentials:

```env
# Azure AI Foundry endpoint (with project ID)
AZURE_AI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/api/projects/your-project-id

# Service Principal credentials
AZURE_CLIENT_ID=your-service-principal-client-id
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_CLIENT_SECRET=your-service-principal-secret

# Optional: Specific storage container
STORAGE_CONTAINER_NAME=your-container-name
```

### 3. Service Principal Permissions

Your service principal needs:
- `Microsoft.CognitiveServices/accounts/AIServices/connections/read` permission on the AI Foundry resource
- Appropriate access to the AI Foundry project

## Key Challenges & Solutions

### 1. SDK Migration
The newer `azure.ai.projects` SDK has different attributes than the older `azure.ai.resources`:
- Old: `ai_client.data`
- New: `ai_client.connections`

### 2. Authentication Requirements
The AI Foundry connections API requires `DefaultAzureCredential` or similar Azure Identity credentials:
```python
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()  # Uses env vars automatically
```

### 3. Endpoint Format
The endpoint must include the project ID:
```
https://your-resource.cognitiveservices.azure.com/api/projects/your-project-id
```

### 4. Extracting Credentials
Connection objects don't directly expose credentials. Use the `as_dict()` method:
```python
conn_details = ai_client.connections.get(
    name=connection_name,
    include_credentials=True
)
conn_dict = conn_details.as_dict()
account_key = conn_dict['credentials']['key']
```

### 5. Container Names
Container names in Azure are case-sensitive. Verify the exact name using Azure Portal or Storage Explorer.

## Usage

### Basic Example

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from langchain_community.document_loaders import AzureBlobStorageContainerLoader
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to AI Foundry
ai_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.getenv("AZURE_AI_ENDPOINT")
)

# Find storage connection
storage_conn_name = None
for conn in ai_client.connections.list():
    if 'storage' in conn.name.lower():
        storage_conn_name = conn.name
        break

# Get connection details with credentials
conn_details = ai_client.connections.get(
    name=storage_conn_name,
    include_credentials=True
)

# Extract credentials
conn_dict = conn_details.as_dict()
account_name = conn_dict['account_name']
account_key = conn_dict['credentials']['key']

# Create connection string
conn_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"

# Use with LangChain loader
loader = AzureBlobStorageContainerLoader(
    conn_str=conn_string,
    container=os.getenv("STORAGE_CONTAINER_NAME")
)

# Load documents
documents = loader.load()
```

### Complete Working Example

See `test.py` for a complete implementation with error handling and debugging output.

### Service Principal Setup Helper

Run `setup_service_principal_auth.py` to verify your service principal configuration and test authentication methods.

## Troubleshooting

### Permission Denied Error
If you get "PermissionDenied" when accessing connections:
1. Verify service principal has the required permission: `Microsoft.CognitiveServices/accounts/AIServices/connections/read`
2. Check that the service principal has access to the specific AI Foundry project

### No Storage Connections Found
1. Verify storage account is connected in AI Foundry portal
2. Check connection type is `AzureBlob` or `AzureDataLakeGen2`

### Authentication Failures
1. Ensure all environment variables are set correctly
2. Test with `az login` to verify credentials work
3. Use `DefaultAzureCredential()` which automatically uses env vars

## Security Notes

- Never commit `.env` files or credentials to version control
- Use Azure Key Vault for production environments
- Rotate service principal secrets regularly
- Apply principle of least privilege to service principal permissions

## Additional Resources

- [Azure AI Foundry Documentation](https://docs.microsoft.com/azure/ai-services/)
- [LangChain Azure Integration](https://python.langchain.com/docs/integrations/document_loaders/azure_blob_storage)
- [Azure Identity Library](https://docs.microsoft.com/python/api/azure-identity/)

## License

This project is licensed under the MIT License.