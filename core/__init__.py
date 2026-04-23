"""
Core module — Claude AI Client + Azure Services
"""
from core.claude_client import MarketingAIClient, ClaudeMarketingAI, ClaudeClient
from core.azure_services import AzureServiceManager

__all__ = ["MarketingAIClient", "ClaudeMarketingAI", "ClaudeClient", "AzureServiceManager"]
