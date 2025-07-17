from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from langchain_community.document_loaders import AzureBlobStorageContainerLoader
from azure.ai.projects.models import ConnectionType
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Connect to Azure AI Foundry
print("🔐 Connecting to Azure AI Foundry...")
ai_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.getenv("AZURE_AI_ENDPOINT")
)

print(f"✅ Connected to Azure AI Project")

# Find storage connection
print("\n🔍 Looking for storage connections...")
storage_connection = None

for conn in ai_client.connections.list():
    print(f"  Found: {conn.name} (Type: {conn.type})")
    if conn.type == ConnectionType.AZURE_STORAGE_ACCOUNT:
        storage_connection = conn
        print(f"  ✅ Using this storage connection!")
        break

if not storage_connection:
    print("❌ No storage connection found")
    exit(1)

# Get the connection with credentials
print(f"\n📦 Getting credentials for: {storage_connection.name}")
try:
    detailed_conn = ai_client.connections.get(
        name=storage_connection.name,
        include_credentials=True
    )
    
    # Use as_dict() to get the full connection data
    conn_dict = detailed_conn.as_dict()
    
    # Extract account name from target
    account_name = None
    target = conn_dict.get('target', '')
    match = re.search(r'https://([^\.]+)\.blob\.core\.windows\.net', target)
    if match:
        account_name = match.group(1)
        print(f"  Account name: {account_name}")
    
    # Extract account key from credentials
    account_key = None
    credentials = conn_dict.get('credentials', {})
    if credentials.get('type') == 'AccountKey':
        account_key = credentials.get('key')
        if account_key:
            print(f"  ✅ Found account key!")
    
    # Build connection string
    if account_name and account_key:
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={account_name};"
            f"AccountKey={account_key};"
            f"EndpointSuffix=core.windows.net"
        )
        print("  ✅ Successfully built connection string")
    else:
        print("\n❌ Could not extract credentials")
        exit(1)
    
    # Load documents
    container_name = os.getenv("AZURE_STORAGE_CONTAINER", "docs")  # Changed default to 'docs'
    print(f"\n📄 Loading documents from container '{container_name}'...")
    
    loader = AzureBlobStorageContainerLoader(
        conn_str=connection_string,
        container=container_name
    )
    
    docs = loader.load()
    print(f"✅ Loaded {len(docs)} documents")
    
    if docs:
        print(f"\nFirst document:")
        print(f"  Source: {docs[0].metadata.get('source')}")
        print(f"  Content: {docs[0].page_content[:200]}...")
        print("\n🎉 SUCCESS! You can now use these documents with LangChain!")
        print("\nNext steps:")
        print("  1. Split documents with RecursiveCharacterTextSplitter")
        print("  2. Create embeddings with Azure OpenAI")
        print("  3. Store in a vector database")
        print("  4. Build RAG applications")
    else:
        print("\n⚠️  No documents found in the container")
        print("  Make sure:")
        print(f"  1. The container '{container_name}' exists")
        print("  2. The container has documents in it")
        print("  3. Your service principal has 'Storage Blob Data Reader' role")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    
    # Provide specific troubleshooting based on the error
    error_str = str(e)
    if "container" in error_str.lower() and "not found" in error_str.lower():
        print("\nThe container doesn't exist. Check your AZURE_STORAGE_CONTAINER in .env")
    elif "403" in error_str or "forbidden" in error_str.lower():
        print("\nAccess denied. Make sure your connection has the right permissions")
    elif "404" in error_str:
        print("\nResource not found. Check the container name and storage account")
    else:
        print("\nGeneral troubleshooting:")
        print("1. Verify the container name in your .env file")
        print("2. Check the storage connection in AI Foundry has valid credentials")
        print("3. Ensure the storage account exists and is accessible")