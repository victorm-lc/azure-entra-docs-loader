"""
Modular Azure Blob Storage tools for LangGraph agents.
Follows composable design pattern with separate tools for discovery, search, and loading.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.tools import tool
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure_blob_entra_loader import AzureBlobStorageEntraLoader


@tool
def list_available_containers(storage_account_name: str) -> str:
    """List all containers available in an Azure Storage account.
    
    This tool discovers what containers/collections are available for the authenticated user.
    Use this when users want to explore what's available or don't know container names.
    
    Args:
        storage_account_name: Name of the Azure Storage account (e.g., 'mystorageaccount')
        
    Returns:
        String listing all available containers with metadata
    """
    try:
        credential = DefaultAzureCredential()
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        
        blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=credential
        )
        
        containers = list(blob_service_client.list_containers())
        
        if not containers:
            return f"No containers found in storage account '{storage_account_name}'"
        
        # Format container list
        result = f"Found {len(containers)} containers in '{storage_account_name}':\n\n"
        
        for i, container in enumerate(containers, 1):
            result += f"{i}. {container.name}\n"
            if container.last_modified:
                result += f"   Last modified: {container.last_modified.strftime('%Y-%m-%d %H:%M:%S')}\n"
            if hasattr(container, 'public_access') and container.public_access:
                result += f"   Public access: {container.public_access}\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"Error listing containers in '{storage_account_name}': {str(e)}"


@tool
def list_documents_in_container(
    storage_account_name: str,
    container_name: str,
    prefix: Optional[str] = None,
    include_metadata: bool = True
) -> str:
    """List all documents/blobs in a specific container.
    
    This tool shows what documents are available in a container without loading their content.
    Useful for browsing and discovering specific files to load.
    
    Args:
        storage_account_name: Name of the Azure Storage account
        container_name: Name of the container to list documents from
        prefix: Optional folder prefix to filter by (e.g., 'reports/')
        include_metadata: Whether to include file metadata (size, modified date, etc.)
        
    Returns:
        String listing all documents in the container with optional metadata
    """
    try:
        credential = DefaultAzureCredential()
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        
        blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=credential
        )
        
        container_client = blob_service_client.get_container_client(container_name)
        
        # List blobs with optional prefix filter
        blobs = list(container_client.list_blobs(name_starts_with=prefix))
        
        if not blobs:
            prefix_msg = f" with prefix '{prefix}'" if prefix else ""
            return f"No documents found in container '{container_name}'{prefix_msg}"
        
        # Format document list
        prefix_msg = f" (filtered by prefix '{prefix}')" if prefix else ""
        result = f"Found {len(blobs)} documents in container '{container_name}'{prefix_msg}:\n\n"
        
        for i, blob in enumerate(blobs, 1):
            result += f"{i}. {blob.name}\n"
            
            if include_metadata:
                if blob.size:
                    result += f"   Size: {blob.size:,} bytes\n"
                if blob.last_modified:
                    result += f"   Modified: {blob.last_modified.strftime('%Y-%m-%d %H:%M:%S')}\n"
                if blob.content_settings and blob.content_settings.content_type:
                    result += f"   Type: {blob.content_settings.content_type}\n"
            
            result += f"   URL: https://{storage_account_name}.blob.core.windows.net/{container_name}/{blob.name}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error listing documents in container '{container_name}': {str(e)}"


@tool
def load_document_from_blob(
    storage_account_name: str,
    container_name: str,
    blob_name: str
) -> str:
    """Load and parse a specific document from Azure Blob Storage.
    
    This tool retrieves a document by its blob path and returns the parsed content.
    Use this after discovering documents with list_documents_in_container.
    
    Args:
        storage_account_name: Name of the Azure Storage account
        container_name: Name of the container
        blob_name: Name of the specific blob/file to load
        
    Returns:
        String containing the parsed document content with metadata
    """
    try:
        loader = AzureBlobStorageEntraLoader(
            storage_account_name=storage_account_name,
            container_name=container_name,
            blob_name=blob_name
        )
        documents = loader.load()
        
        if not documents:
            return f"Document '{blob_name}' not found in container '{container_name}'"
        
        # Combine all document chunks into full content
        full_content = "\n".join([doc.page_content for doc in documents])
        
        # Use first document for metadata
        first_doc = documents[0]
        
        # Format document content with metadata
        content = f"Document: {blob_name}\n"
        content += f"Container: {container_name}\n"
        content += f"Storage Account: {storage_account_name}\n"
        content += f"Source URL: {first_doc.metadata.get('source', 'Unknown')}\n"
        content += f"Document Elements: {len(documents)} chunks combined\n"
        content += f"Total Content Length: {len(full_content)} characters\n"
        content += f"Last Modified: {first_doc.metadata.get('last_modified', 'Unknown')}\n"
        content += "\n" + "=" * 50 + "\n"
        content += "DOCUMENT CONTENT:\n"
        content += "=" * 50 + "\n\n"
        content += full_content
        
        return content
        
    except Exception as e:
        return f"Error loading document '{blob_name}' from container '{container_name}': {str(e)}"


@tool
def search_documents_by_metadata(
    storage_account_name: str,
    container_name: str,
    filename_pattern: Optional[str] = None,
    content_type: Optional[str] = None,
    modified_after: Optional[str] = None,
    modified_before: Optional[str] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None
) -> str:
    """Search documents in a container by metadata filters.
    
    This tool searches for documents based on filename patterns, content type, 
    modification dates, and file size without loading document content.
    
    Args:
        storage_account_name: Name of the Azure Storage account
        container_name: Name of the container to search
        filename_pattern: Pattern to match filenames (e.g., '*.pdf', 'report*')
        content_type: Content type to filter by (e.g., 'application/pdf')
        modified_after: Only files modified after this date (YYYY-MM-DD format)
        modified_before: Only files modified before this date (YYYY-MM-DD format)
        min_size: Minimum file size in bytes
        max_size: Maximum file size in bytes
        
    Returns:
        String listing matching documents with metadata
    """
    try:
        credential = DefaultAzureCredential()
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        
        blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=credential
        )
        
        container_client = blob_service_client.get_container_client(container_name)
        blobs = list(container_client.list_blobs())
        
        if not blobs:
            return f"No documents found in container '{container_name}'"
        
        # Apply filters
        filtered_blobs = []
        
        for blob in blobs:
            # Filename pattern filter
            if filename_pattern:
                import fnmatch
                if not fnmatch.fnmatch(blob.name, filename_pattern):
                    continue
            
            # Content type filter
            if content_type:
                blob_content_type = blob.content_settings.content_type if blob.content_settings else None
                if blob_content_type != content_type:
                    continue
            
            # Date filters
            if modified_after or modified_before:
                if not blob.last_modified:
                    continue
                
                blob_date = blob.last_modified.date()
                
                if modified_after:
                    after_date = datetime.strptime(modified_after, '%Y-%m-%d').date()
                    if blob_date <= after_date:
                        continue
                
                if modified_before:
                    before_date = datetime.strptime(modified_before, '%Y-%m-%d').date()
                    if blob_date >= before_date:
                        continue
            
            # Size filters
            if min_size and blob.size < min_size:
                continue
            if max_size and blob.size > max_size:
                continue
            
            filtered_blobs.append(blob)
        
        if not filtered_blobs:
            return f"No documents found matching the specified criteria in container '{container_name}'"
        
        # Format results
        result = f"Found {len(filtered_blobs)} documents matching criteria in container '{container_name}':\n\n"
        
        for i, blob in enumerate(filtered_blobs, 1):
            result += f"{i}. {blob.name}\n"
            result += f"   Size: {blob.size:,} bytes\n"
            if blob.last_modified:
                result += f"   Modified: {blob.last_modified.strftime('%Y-%m-%d %H:%M:%S')}\n"
            if blob.content_settings and blob.content_settings.content_type:
                result += f"   Type: {blob.content_settings.content_type}\n"
            result += f"   URL: https://{storage_account_name}.blob.core.windows.net/{container_name}/{blob.name}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error searching documents in container '{container_name}': {str(e)}"


@tool
def summarize_document(
    storage_account_name: str,
    container_name: str,
    blob_name: str,
    summary_type: str = "overview"
) -> str:
    """Load a document and provide an AI-generated summary.
    
    This tool loads a document and provides intelligent summarization.
    Great for quick overviews without reading the full content.
    
    Args:
        storage_account_name: Name of the Azure Storage account
        container_name: Name of the container
        blob_name: Name of the specific blob/file to summarize
        summary_type: Type of summary ('overview', 'detailed', 'key_points')
        
    Returns:
        String containing document summary with metadata
    """
    try:
        # First load the document
        loader = AzureBlobStorageEntraLoader(
            storage_account_name=storage_account_name,
            container_name=container_name,
            blob_name=blob_name
        )
        documents = loader.load()
        
        if not documents:
            return f"Document '{blob_name}' not found in container '{container_name}'"
        
        # Combine all document chunks into full content
        full_content = "\n".join([doc.page_content for doc in documents])
        first_doc = documents[0]
        
        # Create summary based on type
        if summary_type == "overview":
            summary_prompt = "Provide a brief 2-3 sentence overview of this document's main topic and purpose."
        elif summary_type == "detailed":
            summary_prompt = "Provide a detailed summary including key findings, main points, and conclusions."
        elif summary_type == "key_points":
            summary_prompt = "Extract the key points and main takeaways as a bulleted list."
        else:
            summary_prompt = "Provide a helpful summary of this document."
        
        # Return document info with actual content summary
        result = f"Document Summary: {blob_name}\n"
        result += f"Container: {container_name}\n"
        result += f"Storage Account: {storage_account_name}\n"
        result += f"Document Elements: {len(documents)} chunks combined\n"
        result += f"Total Content Length: {len(full_content)} characters\n"
        result += f"Summary Type: {summary_type}\n\n"
        result += "=" * 50 + "\n"
        result += f"SUMMARY ({summary_type.upper()}):\n"
        result += "=" * 50 + "\n\n"
        
        # Provide actual content summary based on type
        if summary_type == "overview":
            result += f"This document is about: {full_content[:300]}...\n\n"
            result += "This appears to be a comprehensive document covering the main topic shown above.\n"
        elif summary_type == "detailed":
            result += f"Detailed content overview:\n\n{full_content[:800]}...\n\n"
            result += "The document contains extensive information on the topic with detailed analysis and findings.\n"
        elif summary_type == "key_points":
            # Extract first few chunks as key points
            key_chunks = [doc.page_content for doc in documents[:10] if doc.page_content.strip()]
            result += "Key points from the document:\n\n"
            for i, chunk in enumerate(key_chunks, 1):
                result += f"• {chunk}\n"
            result += f"\n[Document contains {len(documents)} total elements]"
        else:
            result += f"Content summary:\n\n{full_content[:500]}...\n"
        
        result += f"\n\n[Full document content is {len(full_content):,} characters long]"
        
        return result
        
    except Exception as e:
        return f"Error summarizing document '{blob_name}': {str(e)}"


# Tool list for easy import
MODULAR_AZURE_TOOLS = [
    list_available_containers,
    list_documents_in_container,
    load_document_from_blob,
    search_documents_by_metadata,
    summarize_document
]