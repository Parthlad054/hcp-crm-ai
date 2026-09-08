"""
integrations/storage_client.py — Stub for file/blob storage integration.

Placeholder for future implementation (AWS S3, GCS, Azure Blob, etc.).
Implement when file uploads (attachments, call recordings, etc.) are needed.
"""
from typing import BinaryIO


class StorageClient:
    """
    Abstract storage client stub.

    Replace the method bodies with a real cloud SDK when file storage is needed.
    """

    def upload(self, file: BinaryIO, destination: str) -> str:
        """
        Upload a file to storage and return its public/signed URL.

        Args:
            file: File-like object to upload.
            destination: Target path/key in the storage bucket.

        Returns:
            str: URL of the uploaded file.
        """
        raise NotImplementedError("StorageClient.upload is not yet implemented.")

    def delete(self, path: str) -> None:
        """
        Delete a file from storage.

        Args:
            path: Path/key of the file to delete.
        """
        raise NotImplementedError("StorageClient.delete is not yet implemented.")

    def get_signed_url(self, path: str, expires_in: int = 3600) -> str:
        """
        Generate a time-limited signed URL for a private file.

        Args:
            path: Path/key of the file.
            expires_in: URL validity in seconds (default: 1 hour).

        Returns:
            str: Signed URL.
        """
        raise NotImplementedError("StorageClient.get_signed_url is not yet implemented.")


# Singleton instance — replace with real initialisation when needed.
storage_client = StorageClient()
