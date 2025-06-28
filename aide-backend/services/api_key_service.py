"""
API Key Validation Service

Validates API keys for different LLM providers by making minimal API calls.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Tuple
import openai
import anthropic

logger = logging.getLogger("aide")


class ApiKeyValidationError(Exception):
    """Custom exception for API key validation errors."""
    pass


class ApiKeyService:
    """Service for validating API keys from different providers."""
    
    def __init__(self):
        self.validation_cache = {}  # Simple in-memory cache
        
    async def validate_openai_key(self, api_key: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate OpenAI API key by making a minimal API call.
        
        Args:
            api_key: The OpenAI API key to validate
            
        Returns:
            Tuple of (is_valid, error_message, extra_info)
        """
        try:
            client = openai.OpenAI(api_key=api_key, max_retries=0)
            
            # Make a minimal API call to check key validity
            # Using the models endpoint is cheaper than completions
            response = await asyncio.to_thread(client.models.list)
            
            # Check if we have access to any models
            models = list(response.data)
            if not models:
                return False, "No models available with this API key", {}
                
            # Extract available GPT models
            gpt_models = [model.id for model in models if 'gpt' in model.id.lower()]
            
            return True, "Valid API key", {
                "provider": "openai",
                "available_models": gpt_models[:5],  # First 5 models
                "total_models": len(models)
            }
            
        except openai.AuthenticationError:
            return False, "Invalid API key", {}
        except openai.PermissionDeniedError:
            return False, "Permission denied - check API key permissions", {}
        except openai.RateLimitError:
            return False, "Rate limit exceeded - try again later", {}
        except openai.APIConnectionError:
            return False, "Connection error - check internet connection", {}
        except Exception as e:
            logger.error(f"Unexpected error validating OpenAI key: {e}")
            return False, f"Validation error: {str(e)}", {}
    
    async def validate_anthropic_key(self, api_key: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate Anthropic API key by making a minimal API call.
        
        Args:
            api_key: The Anthropic API key to validate
            
        Returns:
            Tuple of (is_valid, error_message, extra_info)
        """
        try:
            client = anthropic.Anthropic(api_key=api_key, max_retries=0)
            
            # Make a minimal message to test the key
            # This is the cheapest way to validate an Anthropic key
            response = await asyncio.to_thread(
                client.messages.create,
                model="claude-3-haiku-20240307",  # Cheapest model
                max_tokens=1,
                messages=[{"role": "user", "content": "hi"}]
            )
            
            return True, "Valid API key", {
                "provider": "anthropic",
                "model_used": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
            
        except anthropic.AuthenticationError:
            return False, "Invalid API key", {}
        except anthropic.PermissionDeniedError:
            return False, "Permission denied - check API key permissions", {}
        except anthropic.RateLimitError:
            return False, "Rate limit exceeded - try again later", {}
        except anthropic.APIConnectionError:
            return False, "Connection error - check internet connection", {}
        except Exception as e:
            logger.error(f"Unexpected error validating Anthropic key: {e}")
            return False, f"Validation error: {str(e)}", {}
    
    async def validate_openrouter_key(self, api_key: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate OpenRouter API key by making a minimal API call.
        
        Args:
            api_key: The OpenRouter API key to validate
            
        Returns:
            Tuple of (is_valid, error_message, extra_info)
        """
        try:
            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                max_retries=0
            )
            
            # Check available models
            response = await asyncio.to_thread(client.models.list)
            
            models = list(response.data)
            if not models:
                return False, "No models available with this API key", {}
            
            # Get some popular models
            popular_models = [
                model.id for model in models 
                if any(name in model.id.lower() for name in ['gpt', 'claude', 'llama'])
            ]
            
            return True, "Valid API key", {
                "provider": "openrouter",
                "available_models": popular_models[:10],  # First 10 popular models
                "total_models": len(models)
            }
            
        except openai.AuthenticationError:
            return False, "Invalid API key", {}
        except openai.PermissionDeniedError:
            return False, "Permission denied - check API key permissions", {}
        except openai.RateLimitError:
            return False, "Rate limit exceeded - try again later", {}
        except openai.APIConnectionError:
            return False, "Connection error - check internet connection", {}
        except Exception as e:
            logger.error(f"Unexpected error validating OpenRouter key: {e}")
            return False, f"Validation error: {str(e)}", {}
    
    async def validate_api_key(self, provider: str, api_key: str) -> Dict[str, Any]:
        """
        Validate an API key for the specified provider.
        
        Args:
            provider: The LLM provider (openai, anthropic, openrouter)
            api_key: The API key to validate
            
        Returns:
            Dictionary with validation results
        """
        if not provider or not api_key:
            raise ApiKeyValidationError("Provider and API key are required")
        
        provider = provider.lower()
        
        # Check cache first (simple caching by key prefix)
        cache_key = f"{provider}:{api_key[:8]}..."
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        if provider == "openai":
            is_valid, message, extra_info = await self.validate_openai_key(api_key)
        elif provider == "anthropic":
            is_valid, message, extra_info = await self.validate_anthropic_key(api_key)
        elif provider == "openrouter":
            is_valid, message, extra_info = await self.validate_openrouter_key(api_key)
        else:
            raise ApiKeyValidationError(f"Unsupported provider: {provider}")
        
        result = {
            "valid": is_valid,
            "provider": provider,
            "message": message,
            **extra_info
        }
        
        # Cache successful validations for 5 minutes
        if is_valid:
            self.validation_cache[cache_key] = result
            # Simple cache cleanup - remove after some time
            asyncio.create_task(self._cleanup_cache_entry(cache_key, 300))  # 5 minutes
        
        return result
    
    async def _cleanup_cache_entry(self, cache_key: str, delay: int):
        """Remove cache entry after delay."""
        await asyncio.sleep(delay)
        self.validation_cache.pop(cache_key, None)