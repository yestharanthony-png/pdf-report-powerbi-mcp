import os
from azure.storage.blob import BlobServiceClient

class BlobStorageService:
    def __init__(self):
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("AZURE_CONTAINER_NAME")

        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        self.container_client = self.blob_service_client.get_container_client(
            container_name
        )

    def upload_pdf(self, file_path: str) -> str:
        blob_name = os.path.basename(file_path)

        blob_client = self.container_client.get_blob_client(blob_name)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        return blob_client.url