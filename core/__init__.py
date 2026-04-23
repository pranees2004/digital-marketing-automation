"""
Core module — Claude AI Client + Azure Services
"""
from core.claude_client import MarketingAIClient
from core.azure_services import AzureServiceManager

__all__ = ["MarketingAIClient", "AzureServiceManager"]
