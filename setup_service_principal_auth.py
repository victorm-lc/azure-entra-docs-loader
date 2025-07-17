"""
Setup Service Principal Authentication for Azure AI Foundry
This mimics how your customer has configured their authentication
"""

import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import ClientSecretCredential, DefaultAzureCredential

load_dotenv()

print("🔐 Service Principal Authentication Setup\n")

# Check if service principal env vars are set
sp_vars = {
    'AZURE_CLIENT_ID': 'Service Principal Application (client) ID',
    'AZURE_TENANT_ID': 'Azure AD Tenant ID',
    'AZURE_CLIENT_SECRET': 'Service Principal Secret/Password'
}

all_set = True
for var, desc in sp_vars.items():
    if os.getenv(var):
        print(f"✅ {var} is set")
    else:
        print(f"❌ {var} not set - {desc}")
        all_set = False

if not all_set:
    print("\n📝 TO SET UP SERVICE PRINCIPAL:")
    print("-" * 60)
    print("1. Create a service principal in Azure:")
    print("   az ad sp create-for-rbac --name 'your-sp-name' --role contributor \\")
    print("     --scopes /subscriptions/YOUR_SUBSCRIPTION_ID")
    print("\n2. Add to your .env file:")
    print("   AZURE_CLIENT_ID=<appId from output>")
    print("   AZURE_TENANT_ID=<tenant from output>")
    print("   AZURE_CLIENT_SECRET=<password from output>")
    print("\n3. Grant the service principal access to your AI Foundry project")
    exit(1)

print("\n✅ Service principal credentials are configured!")

# Test authentication methods
print("\n🧪 Testing authentication methods:\n")

# Method 1: Using DefaultAzureCredential (will use SP if env vars are set)
print("1. DefaultAzureCredential (automatic):")
try:
    ai_client = AIProjectClient(
        credential=DefaultAzureCredential(),
        endpoint=os.getenv("AZURE_AI_ENDPOINT")
    )
    # Test it
    connections = list(ai_client.connections.list())
    print(f"   ✅ Success! Found {len(connections)} connections")
except Exception as e:
    print(f"   ❌ Failed: {str(e)[:100]}...")

# Method 2: Using explicit ClientSecretCredential
print("\n2. ClientSecretCredential (explicit):")
try:
    credential = ClientSecretCredential(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET")
    )
    
    ai_client = AIProjectClient(
        credential=credential,
        endpoint=os.getenv("AZURE_AI_ENDPOINT")
    )
    # Test it
    connections = list(ai_client.connections.list())
    print(f"   ✅ Success! Found {len(connections)} connections")
except Exception as e:
    print(f"   ❌ Failed: {str(e)[:100]}...")

print("\n💡 RECOMMENDATIONS:")
print("-" * 60)
print("1. DefaultAzureCredential is preferred - it automatically uses SP if env vars are set")
print("2. It also falls back to other auth methods if SP fails")
print("3. Make sure your service principal has the right permissions on the AI Foundry project") 