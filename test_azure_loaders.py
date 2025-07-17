"""
Tests for Azure Blob Storage Loaders with Entra ID

These tests verify that the loaders can be instantiated and have the correct interface.
For full integration testing, you need valid Azure credentials and storage account.
"""

import pytest
import os
from unittest.mock import Mock, patch
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from azure_blob_entra_container_loader import AzureBlobStorageContainerEntraLoader, load_azure_blob_documents
from azure_blob_entra_loader import AzureBlobStorageEntraLoader


class TestAzureBlobStorageContainerEntraLoader:
    """Test the container loader class"""
    
    def test_init_with_defaults(self):
        """Test loader initialization with default parameters"""
        loader = AzureBlobStorageContainerEntraLoader(
            storage_account_name="testaccount",
            container="testcontainer"
        )
        
        assert loader.storage_account_name == "testaccount"
        assert loader.container == "testcontainer"
        assert loader.prefix is None
        assert loader.file_pattern is None
        assert isinstance(loader.credential, DefaultAzureCredential)
        assert loader.account_url == "https://testaccount.blob.core.windows.net"
    
    def test_init_with_custom_parameters(self):
        """Test loader initialization with custom parameters"""
        import re
        
        credential = Mock()
        file_pattern = re.compile(r"\.pdf$")
        
        loader = AzureBlobStorageContainerEntraLoader(
            storage_account_name="testaccount",
            container="testcontainer",
            prefix="documents/",
            credential=credential,
            file_pattern=file_pattern
        )
        
        assert loader.storage_account_name == "testaccount"
        assert loader.container == "testcontainer"
        assert loader.prefix == "documents/"
        assert loader.file_pattern == file_pattern
        assert loader.credential == credential
    
    def test_load_method_exists(self):
        """Test that load method exists and returns list"""
        loader = AzureBlobStorageContainerEntraLoader(
            storage_account_name="testaccount",
            container="testcontainer"
        )
        
        # Mock the Azure client to avoid actual API calls
        with patch.object(loader, 'credential'), \
             patch('azure_blob_entra_container_loader.BlobServiceClient') as mock_client:
            
            # Mock the blob service client chain
            mock_container_client = Mock()
            mock_client.return_value.get_container_client.return_value = mock_container_client
            mock_container_client.list_blobs.return_value = []
            
            result = loader.load()
            assert isinstance(result, list)
            assert len(result) == 0


class TestAzureBlobStorageEntraLoader:
    """Test the file loader class"""
    
    def test_init_with_defaults(self):
        """Test loader initialization with default parameters"""
        loader = AzureBlobStorageEntraLoader(
            storage_account_name="testaccount",
            container_name="testcontainer"
        )
        
        assert loader.storage_account_name == "testaccount"
        assert loader.container_name == "testcontainer"
        assert loader.blob_name is None
        assert isinstance(loader.credential, DefaultAzureCredential)
        assert loader.account_url == "https://testaccount.blob.core.windows.net"
    
    def test_init_with_blob_name(self):
        """Test loader initialization with specific blob name"""
        loader = AzureBlobStorageEntraLoader(
            storage_account_name="testaccount",
            container_name="testcontainer",
            blob_name="test.pdf"
        )
        
        assert loader.storage_account_name == "testaccount"
        assert loader.container_name == "testcontainer"
        assert loader.blob_name == "test.pdf"
    
    def test_load_method_exists(self):
        """Test that load method exists and returns list"""
        loader = AzureBlobStorageEntraLoader(
            storage_account_name="testaccount",
            container_name="testcontainer"
        )
        
        # Mock the Azure client to avoid actual API calls
        with patch.object(loader, 'credential'), \
             patch('azure_blob_entra_loader.BlobServiceClient') as mock_client:
            
            # Mock the blob service client chain
            mock_container_client = Mock()
            mock_client.return_value.get_container_client.return_value = mock_container_client
            mock_container_client.list_blobs.return_value = []
            
            result = loader.load()
            assert isinstance(result, list)
            assert len(result) == 0


class TestConvenienceFunction:
    """Test the convenience function"""
    
    def test_load_azure_blob_documents_function(self):
        """Test the convenience function creates loader correctly"""
        with patch('azure_blob_entra_container_loader.AzureBlobStorageContainerEntraLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader.load.return_value = []
            mock_loader_class.return_value = mock_loader
            
            result = load_azure_blob_documents(
                storage_account_name="testaccount",
                container="testcontainer"
            )
            
            # Verify the loader was created with correct parameters
            mock_loader_class.assert_called_once_with(
                storage_account_name="testaccount",
                container="testcontainer",
                prefix=None,
                file_pattern=None,
                credential=None
            )
            
            # Verify load was called
            mock_loader.load.assert_called_once()
            assert result == []


class TestIntegrationWithEnvironment:
    """Integration tests that require environment variables"""
    
    def test_with_env_vars_if_available(self):
        """Test loaders work with environment variables if available"""
        # Only run this test if we have Azure credentials
        if not all([
            os.getenv('AZURE_CLIENT_ID'),
            os.getenv('AZURE_TENANT_ID'),
            os.getenv('AZURE_CLIENT_SECRET')
        ]):
            pytest.skip("Azure credentials not available in environment")
        
        # Test that we can at least create the credential
        loader = AzureBlobStorageContainerEntraLoader(
            storage_account_name="testaccount",
            container="testcontainer"
        )
        
        assert isinstance(loader.credential, DefaultAzureCredential)
    
    def test_default_values_from_env(self):
        """Test that default values work"""
        # This test just verifies the defaults are reasonable
        loader = AzureBlobStorageContainerEntraLoader(
            storage_account_name="testaccount",
            container="testcontainer"
        )
        
        # Should have reasonable defaults
        assert loader.storage_account_name == "testaccount"
        assert loader.container == "testcontainer"
        assert loader.account_url == "https://testaccount.blob.core.windows.net"


class TestErrorHandling:
    """Test error handling in loaders"""
    
    def test_container_loader_handles_missing_container(self):
        """Test that container loader handles missing container gracefully"""
        loader = AzureBlobStorageContainerEntraLoader(
            storage_account_name="testaccount",
            container="nonexistent"
        )
        
        # Mock Azure client to simulate container not found
        with patch('azure_blob_entra_container_loader.BlobServiceClient') as mock_client:
            mock_container_client = Mock()
            mock_client.return_value.get_container_client.return_value = mock_container_client
            
            # Simulate an exception when listing blobs
            mock_container_client.list_blobs.side_effect = Exception("Container not found")
            
            # The loader should handle this by raising the exception (current behavior)
            with pytest.raises(Exception, match="Container not found"):
                loader.load()
    
    def test_file_loader_handles_missing_blob(self):
        """Test that file loader handles missing blob gracefully"""
        loader = AzureBlobStorageEntraLoader(
            storage_account_name="testaccount",
            container_name="testcontainer",
            blob_name="nonexistent.pdf"
        )
        
        # Mock Azure client to simulate blob not found
        with patch('azure_blob_entra_loader.BlobServiceClient') as mock_client:
            mock_container_client = Mock()
            mock_client.return_value.get_container_client.return_value = mock_container_client
            
            # Simulate an exception when getting blob
            mock_container_client.get_blob_client.side_effect = Exception("Blob not found")
            
            # The loader should handle this gracefully
            result = loader.load()
            assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])