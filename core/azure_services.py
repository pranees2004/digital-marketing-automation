"""
Azure Services Client — Storage, Database, Email, and Key Vault integrations.
Handles all Azure cloud infrastructure for the marketing automation system.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any

from config.settings import config

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Azure Cosmos DB — Marketing Data Store
# ─────────────────────────────────────────────
class CosmosDBClient:
    """
    Manages all database operations for marketing data:
    - Content records (blog posts, social posts, emails)
    - Campaign data
    - Analytics snapshots
    - Audit logs
    """

    def __init__(self):
        from azure.cosmos import CosmosClient, PartitionKey
        self.client = CosmosClient(config.azure.cosmos_endpoint, config.azure.cosmos_key)
        self.database = self.client.get_database_client(config.azure.cosmos_database)
        self._ensure_containers()

    def _ensure_containers(self):
        """Create containers if they don't exist."""
        containers = {
            "content": "/content_type",
            "campaigns": "/campaign_id",
            "analytics": "/channel",
            "schedules": "/platform",
            "audit_logs": "/action_type",
            "email_lists": "/segment",
            "reports": "/report_type",
        }
        from azure.cosmos import PartitionKey
        for name, partition_key in containers.items():
            try:
                self.database.create_container_if_not_exists(
                    id=name,
                    partition_key=PartitionKey(path=partition_key),
                    offer_throughput=400,
                )
            except Exception as e:
                logger.warning(f"Container '{name}' setup note: {e}")

    def get_container(self, container_name: str):
        return self.database.get_container_client(container_name)

    # ── Content Operations ──

    def save_content(self, content_type: str, data: Dict[str, Any]) -> Dict:
        """Save generated content (blog, social post, email, ad copy)."""
        container = self.get_container("content")
        record = {
            "id": str(uuid.uuid4()),
            "content_type": content_type,
            "data": data,
            "status": "draft",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "created_by": "automation",
        }
        container.create_item(body=record)
        logger.info(f"Saved {content_type} content: {record['id']}")
        return record

    def get_content(self, content_type: str, status: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Retrieve content records by type and optional status."""
        container = self.get_container("content")
        query = "SELECT * FROM c WHERE c.content_type = @type"
        params = [{"name": "@type", "value": content_type}]
        if status:
            query += " AND c.status = @status"
            params.append({"name": "@status", "value": status})
        query += " ORDER BY c.created_at DESC OFFSET 0 LIMIT @limit"
        params.append({"name": "@limit", "value": limit})

        items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
        return items

    def update_content_status(self, content_id: str, content_type: str, new_status: str) -> Dict:
        """Update status of a content item (draft -> approved -> published)."""
        container = self.get_container("content")
        item = container.read_item(item=content_id, partition_key=content_type)
        item["status"] = new_status
        item["updated_at"] = datetime.now(timezone.utc).isoformat()
        container.replace_item(item=content_id, body=item)
        return item

    # ── Campaign Operations ──

    def save_campaign(self, campaign_data: Dict[str, Any]) -> Dict:
        """Save a marketing campaign record."""
        container = self.get_container("campaigns")
        campaign_id = str(uuid.uuid4())
        record = {
            "id": campaign_id,
            "campaign_id": campaign_id,
            **campaign_data,
            "status": "planned",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        container.create_item(body=record)
        logger.info(f"Saved campaign: {campaign_id}")
        return record

    def get_campaigns(self, status: Optional[str] = None) -> List[Dict]:
        """Get campaigns, optionally filtered by status."""
        container = self.get_container("campaigns")
        query = "SELECT * FROM c"
        params = []
        if status:
            query += " WHERE c.status = @status"
            params.append({"name": "@status", "value": status})
        query += " ORDER BY c.created_at DESC"
        return list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

    # ── Analytics Operations ──

    def save_analytics_snapshot(self, channel: str, data: Dict[str, Any]) -> Dict:
        """Save a point-in-time analytics snapshot."""
        container = self.get_container("analytics")
        record = {
            "id": str(uuid.uuid4()),
            "channel": channel,
            "data": data,
            "snapshot_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        container.create_item(body=record)
        return record

    def get_analytics(self, channel: str, days: int = 30) -> List[Dict]:
        """Get analytics snapshots for a channel over N days."""
        container = self.get_container("analytics")
        from datetime import timedelta
        start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        query = "SELECT * FROM c WHERE c.channel = @channel AND c.snapshot_date >= @start ORDER BY c.snapshot_date DESC"
        params = [
            {"name": "@channel", "value": channel},
            {"name": "@start", "value": start_date},
        ]
        return list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

    # ── Schedule Operations ──

    def save_scheduled_post(self, platform: str, post_data: Dict, scheduled_time: str) -> Dict:
        """Save a post to the publishing schedule."""
        container = self.get_container("schedules")
        record = {
            "id": str(uuid.uuid4()),
            "platform": platform,
            "post_data": post_data,
            "scheduled_time": scheduled_time,
            "status": "scheduled",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        container.create_item(body=record)
        return record

    def get_pending_posts(self, platform: Optional[str] = None) -> List[Dict]:
        """Get posts that are scheduled and pending publication."""
        container = self.get_container("schedules")
        now = datetime.now(timezone.utc).isoformat()
        query = "SELECT * FROM c WHERE c.status = 'scheduled' AND c.scheduled_time <= @now"
        params = [{"name": "@now", "value": now}]
        if platform:
            query += " AND c.platform = @platform"
            params.append({"name": "@platform", "value": platform})
        return list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

    # ── Report Operations ──

    def save_report(self, report_type: str, report_data: Dict[str, Any]) -> Dict:
        """Save a generated marketing report."""
        container = self.get_container("reports")
        record = {
            "id": str(uuid.uuid4()),
            "report_type": report_type,
            "data": report_data,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        container.create_item(body=record)
        return record

    # ── Audit Log ──

    def log_action(self, action_type: str, details: Dict[str, Any]):
        """Log an automation action for audit trail."""
        container = self.get_container("audit_logs")
        record = {
            "id": str(uuid.uuid4()),
            "action_type": action_type,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        container.create_item(body=record)


# ─────────────────────────────────────────────
# Azure Blob Storage — Asset Management
# ─────────────────────────────────────────────
class BlobStorageClient:
    """
    Manages marketing assets: images, documents, reports, exports.
    """

    def __init__(self):
        from azure.storage.blob import BlobServiceClient
        self.service = BlobServiceClient.from_connection_string(config.azure.storage_connection)
        self.container_name = config.azure.storage_container
        self._ensure_container()

    def _ensure_container(self):
        try:
            self.service.create_container(self.container_name)
        except Exception:
            pass  # Container already exists

    def upload_file(self, blob_name: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload a file and return its URL."""
        from azure.storage.blob import ContentSettings
        blob_client = self.service.get_blob_client(container=self.container_name, blob=blob_name)
        blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        return blob_client.url

    def upload_json(self, blob_name: str, data: Dict) -> str:
        """Upload a JSON object as a blob."""
        json_bytes = json.dumps(data, indent=2, default=str).encode("utf-8")
        return self.upload_file(blob_name, json_bytes, "application/json")

    def upload_html(self, blob_name: str, html_content: str) -> str:
        """Upload HTML content (e.g., email templates, reports)."""
        return self.upload_file(blob_name, html_content.encode("utf-8"), "text/html")

    def download_file(self, blob_name: str) -> bytes:
        """Download a file from blob storage."""
        blob_client = self.service.get_blob_client(container=self.container_name, blob=blob_name)
        return blob_client.download_blob().readall()

    def list_blobs(self, prefix: Optional[str] = None) -> List[str]:
        """List blobs in the container, optionally filtered by prefix."""
        container = self.service.get_container_client(self.container_name)
        blobs = container.list_blobs(name_starts_with=prefix)
        return [blob.name for blob in blobs]

    def delete_file(self, blob_name: str):
        """Delete a blob."""
        blob_client = self.service.get_blob_client(container=self.container_name, blob=blob_name)
        blob_client.delete_blob()

    def get_blob_url(self, blob_name: str) -> str:
        """Get the URL for a blob."""
        blob_client = self.service.get_blob_client(container=self.container_name, blob=blob_name)
        return blob_client.url


# ─────────────────────────────────────────────
# Azure Communication Services — Email
# ─────────────────────────────────────────────
class AzureEmailClient:
    """
    Sends transactional and marketing emails via Azure Communication Services.
    """

    def __init__(self):
        from azure.communication.email import EmailClient
        self.client = EmailClient.from_connection_string(config.azure.communication_connection)
        self.sender = config.email.sender_address

    def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        html_body: str,
        plain_text: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send an email to one or more recipients."""
        message = {
            "senderAddress": self.sender,
            "recipients": {
                "to": [{"address": addr} for addr in to_addresses],
            },
            "content": {
                "subject": subject,
                "html": html_body,
            },
        }
        if plain_text:
            message["content"]["plainText"] = plain_text
        if reply_to or config.email.reply_to:
            message["replyTo"] = [{"address": reply_to or config.email.reply_to}]

        poller = self.client.begin_send(message)
        result = poller.result()
        logger.info(f"Email sent to {to_addresses}, Message ID: {result['id']}")
        return {"message_id": result["id"], "status": result["status"]}

    def send_bulk_email(
        self,
        recipients: List[Dict[str, str]],
        subject: str,
        html_template: str,
    ) -> List[Dict]:
        """Send personalized emails to a list of recipients.
        
        Each recipient dict should have: email, first_name, last_name, and any
        other personalization fields used in the template.
        """
        results = []
        for recipient in recipients:
            personalized_html = html_template
            for key, value in recipient.items():
                personalized_html = personalized_html.replace(f"{{{{{key}}}}}", value)

            result = self.send_email(
                to_addresses=[recipient["email"]],
                subject=subject.replace("{{first_name}}", recipient.get("first_name", "")),
                html_body=personalized_html,
            )
            results.append({"email": recipient["email"], **result})
        return results


# ─────────────────────────────────────────────
# Azure Key Vault — Secrets Management
# ─────────────────────────────────────────────
class KeyVaultClient:
    """Manage secrets securely via Azure Key Vault."""

    def __init__(self):
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=config.azure.keyvault_url, credential=credential)

    def get_secret(self, name: str) -> str:
        """Retrieve a secret value."""
        secret = self.client.get_secret(name)
        return secret.value

    def set_secret(self, name: str, value: str) -> None:
        """Store a secret."""
        self.client.set_secret(name, value)


# ─────────────────────────────────────────────
# Service Factory — Lazy initialization
# ─────────────────────────────────────────────
class AzureServices:
    """
    Factory class providing lazy-initialized Azure service clients.
    Usage:
        services = AzureServices()
        services.db.save_content(...)
        services.storage.upload_file(...)
        services.email.send_email(...)
    """

    _db: Optional[CosmosDBClient] = None
    _storage: Optional[BlobStorageClient] = None
    _email: Optional[AzureEmailClient] = None
    _keyvault: Optional[KeyVaultClient] = None

    @property
    def db(self) -> CosmosDBClient:
        if self._db is None:
            self._db = CosmosDBClient()
        return self._db

    @property
    def storage(self) -> BlobStorageClient:
        if self._storage is None:
            self._storage = BlobStorageClient()
        return self._storage

    @property
    def email(self) -> AzureEmailClient:
        if self._email is None:
            self._email = AzureEmailClient()
        return self._email

    @property
    def keyvault(self) -> KeyVaultClient:
        if self._keyvault is None:
            self._keyvault = KeyVaultClient()
        return self._keyvault
