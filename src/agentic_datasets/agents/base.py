"""Base agent utilities for Strands SDK integration.

This module provides factory functions and utilities for creating and configuring
Strands agents with different model providers (Bedrock, Anthropic, OpenAI, etc).
"""

from typing import Any, Optional
import os
import logging

logger = logging.getLogger(__name__)


class AgentConfig:
    """Configuration for agent creation."""
    
    def __init__(
        self,
        provider: str = "bedrock",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ):
        """Initialize agent configuration.
        
        Args:
            provider: Model provider (bedrock, anthropic, openai, ollama)
            model_name: Specific model to use (provider-dependent defaults)
            temperature: Generation temperature (0.0-1.0, default 0.7)
            max_tokens: Maximum tokens to generate
            system_prompt: System prompt for the agent
        """
        self.provider = provider.lower()
        self.model_name = model_name or self._get_default_model()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
    
    def _get_default_model(self) -> str:
        """Get default model for the configured provider."""
        defaults = {
            "bedrock": "anthropic.claude-4-sonnet-20250514-v1:0",
            "anthropic": "claude-4-sonnet-20250514",
            "openai": "gpt-4-turbo-preview",
            "ollama": "llama3.2",
        }
        return defaults.get(self.provider, "anthropic.claude-4-sonnet-20250514-v1:0")


def create_agent(config: AgentConfig, tools: Optional[list] = None) -> Any:
    """Create a Strands agent with the specified configuration.
    
    NOTE: This is a placeholder implementation. The actual Strands SDK
    integration will be implemented once strands-agents is installed.
    
    Args:
        config: Agent configuration
        tools: Optional list of Strands @tool decorated functions
    
    Returns:
        Configured Strands agent instance
    
    Raises:
        ImportError: If strands-agents is not installed
        ValueError: If provider is not supported
    """
    try:
        # NOTE: Uncomment when strands-agents is installed
        # from strands.agents import Agent
        # from strands.providers import get_provider
        
        # provider = get_provider(
        #     provider_type=config.provider,
        #     model_name=config.model_name
        # )
        
        # agent = Agent(
        #     provider=provider,
        #     system_prompt=config.system_prompt,
        #     tools=tools or [],
        #     temperature=config.temperature,
        #     max_tokens=config.max_tokens,
        # )
        
        # return agent
        
        logger.warning(
            "Strands SDK not yet integrated. Install with: "
            "pip install strands-agents strands-agents-tools"
        )
        return None
        
    except ImportError as e:
        logger.error(f"Failed to import Strands SDK: {e}")
        raise ImportError(
            "Strands SDK is not installed. Run: "
            "pip install strands-agents strands-agents-tools"
        ) from e


def validate_provider_credentials(provider: str) -> bool:
    """Validate that required credentials are available for the provider.
    
    Args:
        provider: Model provider name (bedrock, anthropic, openai)
    
    Returns:
        True if credentials are available, False otherwise
    """
    if provider == "bedrock":
        # Check for AWS credentials
        return bool(
            os.getenv("AWS_ACCESS_KEY_ID") and 
            os.getenv("AWS_SECRET_ACCESS_KEY")
        ) or bool(os.getenv("AWS_PROFILE"))
    
    elif provider == "anthropic":
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    
    elif provider == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))
    
    elif provider == "ollama":
        # Ollama runs locally, no API key needed
        return True
    
    return False


def get_provider_setup_instructions(provider: str) -> str:
    """Get setup instructions for a specific provider.
    
    Args:
        provider: Model provider name
    
    Returns:
        Human-readable setup instructions
    """
    instructions = {
        "bedrock": """
        AWS Bedrock Setup:
        1. Configure AWS credentials:
           - Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables
           - OR configure AWS CLI with: aws configure
           - OR set AWS_PROFILE environment variable
        
        2. Enable Claude 4 in Bedrock console:
           - Go to AWS Bedrock console -> Model access
           - Request access to Anthropic Claude models
           - Wait for approval (usually instant for Claude)
        
        3. Install boto3: pip install boto3
        """,
        
        "anthropic": """
        Anthropic API Setup:
        1. Get API key from: https://console.anthropic.com/
        2. Set environment variable: export ANTHROPIC_API_KEY="your-key"
        3. Install client: pip install anthropic
        """,
        
        "openai": """
        OpenAI API Setup:
        1. Get API key from: https://platform.openai.com/api-keys
        2. Set environment variable: export OPENAI_API_KEY="your-key"
        3. Install client: pip install openai
        """,
        
        "ollama": """
        Ollama Setup (Local):
        1. Install Ollama: https://ollama.ai/download
        2. Pull a model: ollama pull llama3.2
        3. Ollama runs locally, no API key needed
        """,
    }
    
    return instructions.get(provider, "Provider not recognized")
