"""
Central Configuration for Digital Marketing Automation System
All settings loaded from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, List

load_dotenv()


# ─────────────────────────────────────────────
# Claude AI Configuration
# ─────────────────────────────────────────────
class ClaudeConfig(BaseModel):
    api_key: str = Field(default_factory=lambda: os.getenv("CLAUDE_API_KEY", ""))
    model: str = Field(default_factory=lambda: os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"))
    max_tokens: int = Field(default_factory=lambda: int(os.getenv("CLAUDE_MAX_TOKENS", "4096")))
    temperature: float = 0.7


# ─────────────────────────────────────────────
# Azure Services Configuration
# ─────────────────────────────────────────────
class AzureConfig(BaseModel):
    subscription_id: str = Field(default_factory=lambda: os.getenv("AZURE_SUBSCRIPTION_ID", ""))
    resource_group: str = Field(default_factory=lambda: os.getenv("AZURE_RESOURCE_GROUP", ""))
    cosmos_endpoint: str = Field(default_factory=lambda: os.getenv("AZURE_COSMOS_ENDPOINT", ""))
    cosmos_key: str = Field(default_factory=lambda: os.getenv("AZURE_COSMOS_KEY", ""))
    cosmos_database: str = Field(
        default_factory=lambda: os.getenv("AZURE_COSMOS_DATABASE", "marketing_db")
    )
    storage_connection: str = Field(
        default_factory=lambda: os.getenv("AZURE_STORAGE_CONNECTION", "")
    )
    storage_container: str = Field(
        default_factory=lambda: os.getenv("AZURE_STORAGE_CONTAINER", "marketing-assets")
    )
    keyvault_url: str = Field(default_factory=lambda: os.getenv("AZURE_KEYVAULT_URL", ""))
    communication_connection: str = Field(
        default_factory=lambda: os.getenv("AZURE_COMMUNICATION_CONNECTION", "")
    )


# ─────────────────────────────────────────────
# Social Media Configuration
# ─────────────────────────────────────────────
class SocialMediaConfig(BaseModel):
    # Twitter / X
    twitter_api_key: str = Field(default_factory=lambda: os.getenv("TWITTER_API_KEY", ""))
    twitter_api_secret: str = Field(default_factory=lambda: os.getenv("TWITTER_API_SECRET", ""))
    twitter_access_token: str = Field(default_factory=lambda: os.getenv("TWITTER_ACCESS_TOKEN", ""))
    twitter_access_secret: str = Field(
        default_factory=lambda: os.getenv("TWITTER_ACCESS_SECRET", "")
    )
    twitter_bearer_token: str = Field(
        default_factory=lambda: os.getenv("TWITTER_BEARER_TOKEN", "")
    )
    # Meta (Facebook / Instagram)
    meta_access_token: str = Field(default_factory=lambda: os.getenv("META_ACCESS_TOKEN", ""))
    meta_page_id: str = Field(default_factory=lambda: os.getenv("META_PAGE_ID", ""))
    meta_instagram_id: str = Field(
        default_factory=lambda: os.getenv("META_INSTAGRAM_ACCOUNT_ID", "")
    )
    # LinkedIn
    linkedin_access_token: str = Field(
        default_factory=lambda: os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    )
    linkedin_org_id: str = Field(
        default_factory=lambda: os.getenv("LINKEDIN_ORGANIZATION_ID", "")
    )


# ─────────────────────────────────────────────
# Company Profile
# ─────────────────────────────────────────────
class CompanyProfile(BaseModel):
    name: str = Field(default_factory=lambda: os.getenv("COMPANY_NAME", "My Company"))
    industry: str = Field(default_factory=lambda: os.getenv("COMPANY_INDUSTRY", "Technology"))
    website: str = Field(default_factory=lambda: os.getenv("COMPANY_WEBSITE", ""))
    target_audience: str = Field(
        default_factory=lambda: os.getenv("TARGET_AUDIENCE", "B2B professionals")
    )
    brand_voice: str = Field(
        default_factory=lambda: os.getenv(
            "BRAND_VOICE", "Professional, innovative, approachable"
        )
    )
    unique_value_proposition: str = Field(
        default_factory=lambda: os.getenv("UNIQUE_VALUE_PROPOSITION", "")
    )
    key_products: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)


# ─────────────────────────────────────────────
# Email Configuration
# ─────────────────────────────────────────────
class EmailConfig(BaseModel):
    sender_address: str = Field(
        default_factory=lambda: os.getenv("EMAIL_SENDER_ADDRESS", "")
    )
    reply_to: str = Field(default_factory=lambda: os.getenv("EMAIL_REPLY_TO", ""))


# ─────────────────────────────────────────────
# Google Services Configuration
# ─────────────────────────────────────────────
class GoogleConfig(BaseModel):
    analytics_property_id: str = Field(
        default_factory=lambda: os.getenv("GOOGLE_ANALYTICS_PROPERTY_ID", "")
    )
    ads_customer_id: str = Field(
        default_factory=lambda: os.getenv("GOOGLE_ADS_CUSTOMER_ID", "")
    )
    search_console_site: str = Field(
        default_factory=lambda: os.getenv("GOOGLE_SEARCH_CONSOLE_SITE", "")
    )


# ─────────────────────────────────────────────
# Master Application Config
# ─────────────────────────────────────────────
class AppConfig(BaseModel):
    claude: ClaudeConfig = Field(default_factory=ClaudeConfig)
    azure: AzureConfig = Field(default_factory=AzureConfig)
    social: SocialMediaConfig = Field(default_factory=SocialMediaConfig)
    company: CompanyProfile = Field(default_factory=CompanyProfile)
    email: EmailConfig = Field(default_factory=EmailConfig)
    google: GoogleConfig = Field(default_factory=GoogleConfig)
    debug: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true"
    )
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    redis_url: str = Field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))


# ─────────────────────────────────────────────
# Global singleton
# ─────────────────────────────────────────────
config = AppConfig()
