"""
Robust Azure Blob Storage Loader using Entra ID
This custom loader combines the simplicity of Entra ID auth with proper document parsing
"""

import os
import tempfile
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader
from langchain_unstructured import UnstructuredLoader
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient


class AzureBlobStorageEntraLoader(BaseLoader):
    """Load documents from Azure Blob Storage using Entra ID authentication."""
    
    def __init__(
        self, 
        storage_account_name: str, 
        container_name: str,
        blob_name: Optional[str] = None,
        credential=None
    ):
        """
        Initialize the loader.
        
        Args:
            storage_account_name: Name of the Azure Storage account
            container_name: Name of the container
            blob_name: Optional specific blob name. If None, loads all blobs in container
            credential: Azure credential (defaults to DefaultAzureCredential)
        """
        self.storage_account_name = storage_account_name
        self.container_name = container_name
        self.blob_name = blob_name
        self.credential = credential or ClientSecretCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET")
        )
        self.account_url = f"https://{storage_account_name}.blob.core.windows.net"
        
    def load(self) -> List[Document]:
        """Load documents from blob storage."""
        blob_service_client = BlobServiceClient(
            account_url=self.account_url,
            credential=self.credential
        )
        
        container_client = blob_service_client.get_container_client(self.container_name)
        documents = []
        
        # Get list of blobs to process
        if self.blob_name:
            # Load specific blob
            blobs = [self.blob_name]
        else:
            # Load all blobs in container
            blobs = [blob.name for blob in container_client.list_blobs()]
        
        # Process each blob
        for blob_name in blobs:
            try:
                blob_client = container_client.get_blob_client(blob_name)
                
                # Download and parse blob using temporary file
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Create file path maintaining blob structure
                    file_path = os.path.join(temp_dir, self.container_name, blob_name)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # Download blob to temp file
                    with open(file_path, "wb") as file:
                        blob_data = blob_client.download_blob()
                        blob_data.readinto(file)
                    
                    # Parse document using UnstructuredLoader
                    loader = UnstructuredLoader(file_path)
                    docs = loader.load()
                    
                    # Enhance metadata with Azure blob info
                    for doc in docs:
                        doc.metadata.update({
                            "source": f"{self.account_url}/{self.container_name}/{blob_name}",
                            "blob_name": blob_name,
                            "container": self.container_name,
                            "storage_account": self.storage_account_name
                        })
                    
                    documents.extend(docs)
                    
            except Exception as e:
                print(f"Error processing blob {blob_name}: {e}")
                continue
        
        return documents


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Get config from environment
    storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "langchaintesting1")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER", "docs")
    
    print("🔐 Using robust Entra ID blob loader...")
    print(f"   Storage Account: {storage_account_name}")
    print(f"   Container: {container_name}")
    
    # Create loader - can load all blobs or specific blob
    # Option 1: Load all blobs in container
    loader = AzureBlobStorageEntraLoader(
        storage_account_name=storage_account_name,
        container_name=container_name
    )
    
    # Option 2: Load specific blob
    # loader = AzureBlobStorageEntraLoader(
    #     storage_account_name=storage_account_name,
    #     container_name=container_name,
    #     blob_name="example_study.pdf"
    # )
    
    try:
        # Load documents
        print("\n📄 Loading documents...")
        documents = loader.load()
        
        print(f"\n✅ Loaded {len(documents)} documents")
        
        if documents:
            print(f"\nFirst document:")
            print(f"  Source: {documents[0].metadata.get('source')}")
            print(f"  Blob: {documents[0].metadata.get('blob_name')}")
            print(f"  Content preview: {documents[0].page_content[:200]}...")
            
            print("\n🎉 SUCCESS! Documents are properly parsed and ready for:")
            print("  - Text splitting")
            print("  - Embedding generation")
            print("  - Vector store indexing")
            print("  - RAG applications")
        else:
            print("\n⚠️  No documents found")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure your Entra ID identity has 'Storage Blob Data Reader' role") 