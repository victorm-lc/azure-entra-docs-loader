"""
Azure Blob Storage Container Loader with Entra ID

Drop-in replacement for LangChain's AzureBlobStorageContainerLoader that properly
supports service principal authentication via Entra ID.
"""

import os
import tempfile
from typing import List, Optional, Pattern
from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader
from langchain_unstructured import UnstructuredLoader
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


class AzureBlobStorageContainerEntraLoader(BaseLoader):
    """
    Load documents from an Azure Blob Storage container using Entra ID authentication.
    
    This loader properly supports service principal authentication, which LangChain's
    built-in AzureBlobStorageContainerLoader doesn't handle well. It uses
    DefaultAzureCredential and provides the same interface as the original.
    
    Example:
        loader = AzureBlobStorageContainerEntraLoader(
            storage_account_name="mystorageaccount",
            container="documents"
        )
        documents = loader.load()
    """
    
    def __init__(
        self,
        storage_account_name: str,
        container: str,
        prefix: Optional[str] = None,
        credential=None,
        file_pattern: Optional[Pattern[str]] = None,
    ):
        """
        Initialize the loader.
        
        Args:
            storage_account_name: Name of the Azure Storage account (e.g., 'mystorageaccount')
            container: Name of the container (e.g., 'documents')
            prefix: Optional prefix to filter blobs (e.g., 'reports/' for files in reports folder)
            credential: Azure credential. If None, uses DefaultAzureCredential which 
                       automatically detects service principal credentials from environment
            file_pattern: Optional regex pattern to filter files by name
        """
        self.storage_account_name = storage_account_name
        self.container = container
        self.prefix = prefix
        self.credential = credential or DefaultAzureCredential()
        self.file_pattern = file_pattern
        self.account_url = f"https://{storage_account_name}.blob.core.windows.net"
        
    def load(self) -> List[Document]:
        """Load documents from the container."""
        blob_service_client = BlobServiceClient(
            account_url=self.account_url,
            credential=self.credential
        )
        
        container_client = blob_service_client.get_container_client(self.container)
        documents = []
        
        # List blobs with optional prefix
        blobs = container_client.list_blobs(name_starts_with=self.prefix)
        
        for blob in blobs:
            # Skip if file pattern doesn't match
            if self.file_pattern and not self.file_pattern.match(blob.name):
                continue
                
            try:
                blob_client = container_client.get_blob_client(blob.name)
                
                # Use temporary directory for processing
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Create file path maintaining blob structure
                    file_path = os.path.join(temp_dir, self.container, blob.name)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # Download blob to temp file
                    with open(file_path, "wb") as file:
                        blob_data = blob_client.download_blob()
                        blob_data.readinto(file)
                    
                    # Use UnstructuredLoader to parse the document
                    loader = UnstructuredLoader(file_path)
                    docs = loader.load()
                    
                    # Add Azure blob metadata to documents
                    for doc in docs:
                        doc.metadata.update({
                            "source": f"{self.account_url}/{self.container}/{blob.name}",
                            "blob_name": blob.name,
                            "container": self.container,
                            "storage_account": self.storage_account_name,
                            "file_size": blob.size,
                            "last_modified": blob.last_modified.isoformat() if blob.last_modified else None,
                            "content_type": blob.content_settings.content_type if blob.content_settings else None,
                        })
                    
                    documents.extend(docs)
                    
            except Exception as e:
                print(f"Warning: Failed to process blob {blob.name}: {e}")
                continue
        
        return documents


def load_azure_blob_documents(
    storage_account_name: str,
    container: str,
    prefix: Optional[str] = None,
    file_pattern: Optional[Pattern[str]] = None,
    credential=None
) -> List[Document]:
    """
    Convenience function to quickly load documents from Azure Blob Storage.
    
    This is a one-line alternative to creating the loader class manually.
    
    Args:
        storage_account_name: Name of the Azure Storage account
        container: Name of the container
        prefix: Optional prefix to filter blobs (e.g., 'reports/')
        file_pattern: Optional regex pattern to filter files by name
        credential: Azure credential (defaults to DefaultAzureCredential)
        
    Returns:
        List of LangChain Document objects
        
    Example:
        import re
        docs = load_azure_blob_documents(
            storage_account_name="mystorageaccount",
            container="documents",
            prefix="reports/",
            file_pattern=re.compile(r"\.(pdf|docx)$", re.IGNORECASE)
        )
    """
    loader = AzureBlobStorageContainerEntraLoader(
        storage_account_name=storage_account_name,
        container=container,
        prefix=prefix,
        file_pattern=file_pattern,
        credential=credential
    )
    return loader.load()


if __name__ == "__main__":
    import re
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Configuration
    storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "langchaintesting1")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER", "docs")
    
    print(f"Testing Azure Blob Container Loader with Entra ID")
    print(f"Storage Account: {storage_account_name}")
    print(f"Container: {container_name}")
    
    try:
        # Example 1: Load all documents
        print("\n1. Loading all documents...")
        loader = AzureBlobStorageContainerEntraLoader(
            storage_account_name=storage_account_name,
            container=container_name
        )
        documents = loader.load()
        print(f"   Loaded {len(documents)} documents")
        
        # Example 2: Load only PDFs
        print("\n2. Loading only PDF files...")
        pdf_pattern = re.compile(r"\.pdf$", re.IGNORECASE)
        pdf_docs = load_azure_blob_documents(
            storage_account_name=storage_account_name,
            container=container_name,
            file_pattern=pdf_pattern
        )
        print(f"   Loaded {len(pdf_docs)} PDF documents")
        
        # Example 3: Load from specific folder
        print("\n3. Loading from 'reports/' folder...")
        folder_docs = load_azure_blob_documents(
            storage_account_name=storage_account_name,
            container=container_name,
            prefix="reports/"
        )
        print(f"   Loaded {len(folder_docs)} documents from reports/")
        
        # Show sample document
        if documents:
            print("\nSample document:")
            doc = documents[0]
            print(f"  Source: {doc.metadata.get('source')}")
            print(f"  Blob: {doc.metadata.get('blob_name')}")
            print(f"  Size: {doc.metadata.get('file_size')} bytes")
            print(f"  Content: {doc.page_content[:100]}...")
            
        print("\n✅ Success! Ready for LangChain processing.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("- Check your Azure credentials (service principal env vars)")
        print("- Ensure your identity has 'Storage Blob Data Reader' role")
        print("- Verify storage account name and container name are correct") 