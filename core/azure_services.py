"""
Azure Services — Cosmos DB, Blob Storage, Email Communication
"""
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

try:
    from azure.cosmos import CosmosClient, PartitionKey, exceptions as cosmos_exceptions
    from azure.storage.blob import BlobServiceClient, ContentSettings
    from azure.communication.email import EmailClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.warning("Azure SDKs not installed. Running in local/mock mode.")


class CosmosDBService:
    """Manages all database operations for marketing data."""

    def __init__(self, endpoint: str, key: str, database_name: str = "marketing_db"):
        self.database_name = database_name
        self.client = None
        self.database = None

        if AZURE_AVAILABLE and endpoint and key:
            try:
                self.client = CosmosClient(endpoint, key)
                self.database = self.client.create_database_if_not_exists(id=database_name)
                self._init_containers()
                logger.info("CosmosDB connected successfully.")
            except Exception as e:
                logger.error(f"CosmosDB connection failed: {e}")
        else:
            logger.info("CosmosDB running in mock mode.")

    def _init_containers(self):
        """Create all required containers."""
        containers = [
            ("content", "/content_type"),
            ("campaigns", "/platform"),
            ("analytics", "/source"),
            ("seo_data", "/domain"),
            ("email_campaigns", "/campaign_type"),
            ("social_posts", "/platform"),
            ("ad_campaigns", "/platform"),
            ("reports", "/report_type"),
            ("keywords", "/category"),
            ("leads", "/source"),
            ("audit_log", "/action_type"),
        ]
        for name, partition_key in containers:
            try:
                self.database.create_container_if_not_exists(
                    id=name,
                    partition_key=PartitionKey(path=partition_key),
                )
            except Exception as e:
                logger.warning(f"Container '{name}' init warning: {e}")

    def save_document(self, container_name: str, document: Dict) -> Dict:
        """Save a document to a container."""
        if not document.get("id"):
            document["id"] = str(uuid.uuid4())
        document["created_at"] = datetime.now(timezone.utc).isoformat()
        document["updated_at"] = datetime.now(timezone.utc).isoformat()

        if self.database:
            container = self.database.get_container_client(container_name)
            return container.upsert_item(document)
        else:
            logger.info(f"[MOCK] Saved to {container_name}: {document.get('id')}")
            return document

    def query_documents(self, container_name: str, query: str, parameters: Optional[List] = None) -> List[Dict]:
        """Query documents from a container."""
        if self.database:
            container = self.database.get_container_client(container_name)
            items = container.query_items(
                query=query,
                parameters=parameters or [],
                enable_cross_partition_query=True,
            )
            return list(items)
        else:
            logger.info(f"[MOCK] Query on {container_name}: {query}")
            return []

    def get_document(self, container_name: str, doc_id: str, partition_key: str) -> Optional[Dict]:
        """Get a specific document by ID."""
        if self.database:
            container = self.database.get_container_client(container_name)
            try:
                return container.read_item(item=doc_id, partition_key=partition_key)
            except cosmos_exceptions.CosmosResourceNotFoundError:
                return None
        return None

    def delete_document(self, container_name: str, doc_id: str, partition_key: str) -> bool:
        """Delete a document."""
        if self.database:
            container = self.database.get_container_client(container_name)
            try:
                container.delete_item(item=doc_id, partition_key=partition_key)
                return True
            except Exception as e:
                logger.error(f"Delete failed: {e}")
                return False
        return False


class BlobStorageService:
    """Manages file storage for marketing assets (images, PDFs, reports)."""

    def __init__(self, connection_string: str):
        self.client = None

        if AZURE_AVAILABLE and connection_string:
            try:
                self.client = BlobServiceClient.from_connection_string(connection_string)
                self._init_containers()
                logger.info("Blob Storage connected successfully.")
            except Exception as e:
                logger.error(f"Blob Storage connection failed: {e}")
        else:
            logger.info("Blob Storage running in mock mode.")

    def _init_containers(self):
        """Create required blob containers."""
        containers = ["marketing-assets", "reports", "email-templates", "social-media-images", "ad-creatives"]
        for name in containers:
            try:
                self.client.create_container(name)
            except Exception:
                pass  # Container already exists

    def upload_file(self, container: str, blob_name: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload a file and return its URL."""
        if self.client:
            blob_client = self.client.get_blob_client(container=container, blob=blob_name)
            blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type),
            )
            return blob_client.url
        else:
            logger.info(f"[MOCK] Uploaded {blob_name} to {container}")
            return f"https://mock-storage.blob.core.windows.net/{container}/{blob_name}"

    def download_file(self, container: str, blob_name: str) -> Optional[bytes]:
        """Download a file."""
        if self.client:
            blob_client = self.client.get_blob_client(container=container, blob=blob_name)
            return blob_client.download_blob().readall()
        return None

    def list_files(self, container: str, prefix: str = "") -> List[str]:
        """List files in a container."""
        if self.client:
            container_client = self.client.get_container_client(container)
            return [blob.name for blob in container_client.list_blobs(name_starts_with=prefix)]
        return []


class EmailService:
    """Manages email sending via Azure Communication Services."""

    def __init__(self, connection_string: str, sender_address: str = ""):
        self.client = None
        self.sender = sender_address or "DoNotReply@your-domain.com"

        if AZURE_AVAILABLE and connection_string:
            try:
                self.client = EmailClient.from_connection_string(connection_string)
                logger.info("Email Service connected successfully.")
            except Exception as e:
                logger.error(f"Email Service connection failed: {e}")
        else:
            logger.info("Email Service running in mock mode.")

    def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        html_body: str,
        plain_text: str = "",
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> Dict:
        """Send an email."""
        recipients = {
            "to": [{"address": addr} for addr in to_addresses],
        }
        if cc:
            recipients["cc"] = [{"address": addr} for addr in cc]
        if bcc:
            recipients["bcc"] = [{"address": addr} for addr in bcc]

        message = {
            "senderAddress": self.sender,
            "recipients": recipients,
            "content": {
                "subject": subject,
                "html": html_body,
                "plainText": plain_text or subject,
            },
        }

        if self.client:
            try:
                poller = self.client.begin_send(message)
                result = poller.result()
                logger.info(f"Email sent to {to_addresses}, ID: {result.get('id')}")
                return {"status": "sent", "message_id": result.get("id")}
            except Exception as e:
                logger.error(f"Email send failed: {e}")
                return {"status": "failed", "error": str(e)}
        else:
            logger.info(f"[MOCK] Email sent to {to_addresses}: {subject}")
            return {"status": "mock_sent", "message_id": str(uuid.uuid4())}

    def send_bulk_email(self, recipients_data: List[Dict], subject_template: str, html_template: str) -> List[Dict]:
        """Send personalized emails to multiple recipients."""
        results = []
        for recipient in recipients_data:
            personalized_subject = subject_template.format(**recipient)
            personalized_html = html_template.format(**recipient)
            result = self.send_email(
                to_addresses=[recipient["email"]],
                subject=personalized_subject,
                html_body=personalized_html,
            )
            result["recipient"] = recipient["email"]
            results.append(result)
        return results


class AzureServiceManager:
    """Centralized manager for all Azure services."""

    def __init__(self, config):
        self.cosmos = CosmosDBService(
            endpoint=config.azure.cosmos_endpoint,
            key=config.azure.cosmos_key,
        )
        self.blob = BlobStorageService(
            connection_string=config.azure.storage_connection,
        )
        self.email = EmailService(
            connection_string=config.azure.communication_connection,
        )

    def health_check(self) -> Dict:
        """Check status of all Azure services."""
        return {
            "cosmos_db": "connected" if self.cosmos.client else "mock_mode",
            "blob_storage": "connected" if self.blob.client else "mock_mode",
            "email_service": "connected" if self.email.client else "mock_mode",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
