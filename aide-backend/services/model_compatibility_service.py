"""
Model compatibility and API key validation service for AIDE ML.
Handles model availability checks and provider compatibility.
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
import httpx

from models.config_models import (
    ModelInfo,
    ModelProvider,
    ModelCompatibilityCheck,
    ModelCompatibilityResult
)


logger = logging.getLogger("aide")


class ModelCompatibilityService:
    """Service for checking model compatibility and API key validation."""
    
    def __init__(self):
        self.supported_models = self._initialize_supported_models()
        self.provider_endpoints = {
            ModelProvider.OPENAI: "https://api.openai.com/v1/models",
            ModelProvider.ANTHROPIC: "https://api.anthropic.com/v1/messages",
            ModelProvider.OPENROUTER: "https://openrouter.ai/api/v1/models"
        }
    
    def _initialize_supported_models(self) -> List[ModelInfo]:
        """Initialize the list of supported models."""
        return [
            # OpenAI Models
            ModelInfo(
                name="gpt-4-turbo",
                provider=ModelProvider.OPENAI,
                display_name="GPT-4 Turbo",
                description="Latest GPT-4 model with improved performance and lower cost",
                supports_function_calling=True,
                max_tokens=128000,
                cost_per_1k_tokens=0.01
            ),
            ModelInfo(
                name="gpt-4",
                provider=ModelProvider.OPENAI,
                display_name="GPT-4",
                description="Most capable OpenAI model, great for complex reasoning",
                supports_function_calling=True,
                max_tokens=8192,
                cost_per_1k_tokens=0.03
            ),
            ModelInfo(
                name="gpt-3.5-turbo",
                provider=ModelProvider.OPENAI,
                display_name="GPT-3.5 Turbo",
                description="Fast and cost-effective model for most tasks",
                supports_function_calling=True,
                max_tokens=16385,
                cost_per_1k_tokens=0.001
            ),
            ModelInfo(
                name="gpt-4o",
                provider=ModelProvider.OPENAI,
                display_name="GPT-4o",
                description="Optimized version of GPT-4 with better performance",
                supports_function_calling=True,
                max_tokens=128000,
                cost_per_1k_tokens=0.005
            ),
            ModelInfo(
                name="gpt-4o-mini",
                provider=ModelProvider.OPENAI,
                display_name="GPT-4o Mini",
                description="Compact version of GPT-4o, faster and more affordable",
                supports_function_calling=True,
                max_tokens=128000,
                cost_per_1k_tokens=0.0002
            ),
            
            # Anthropic Models
            ModelInfo(
                name="claude-3-5-sonnet-20241022",
                provider=ModelProvider.ANTHROPIC,
                display_name="Claude 3.5 Sonnet",
                description="Most intelligent Claude model with excellent coding abilities",
                supports_function_calling=True,
                max_tokens=200000,
                cost_per_1k_tokens=0.003
            ),
            ModelInfo(
                name="claude-3.5-sonnet",
                provider=ModelProvider.ANTHROPIC,
                display_name="Claude 3.5 Sonnet (Alias)",
                description="Alias for the latest Claude 3.5 Sonnet model",
                supports_function_calling=True,
                max_tokens=200000,
                cost_per_1k_tokens=0.003
            ),
            ModelInfo(
                name="claude-3-7-sonnet-20250219",
                provider=ModelProvider.ANTHROPIC,
                display_name="Claude 3.7 Sonnet",
                description="Latest Claude 3.7 model with enhanced capabilities",
                supports_function_calling=True,
                max_tokens=200000,
                cost_per_1k_tokens=0.003
            ),
            ModelInfo(
                name="claude-3.7-sonnet",
                provider=ModelProvider.ANTHROPIC,
                display_name="Claude 3.7 Sonnet (Alias)",
                description="Alias for the latest Claude 3.7 Sonnet model",
                supports_function_calling=True,
                max_tokens=200000,
                cost_per_1k_tokens=0.003
            ),
            ModelInfo(
                name="claude-3-sonnet-20240229",
                provider=ModelProvider.ANTHROPIC,
                display_name="Claude 3 Sonnet",
                description="Balanced model offering good performance and speed",
                supports_function_calling=True,
                max_tokens=200000,
                cost_per_1k_tokens=0.003
            ),
            ModelInfo(
                name="claude-3-haiku-20240307",
                provider=ModelProvider.ANTHROPIC,
                display_name="Claude 3 Haiku",
                description="Fastest Claude model, optimized for speed and cost",
                supports_function_calling=True,
                max_tokens=200000,
                cost_per_1k_tokens=0.00025
            ),
            
            # OpenRouter Models (representative selection)
            ModelInfo(
                name="meta-llama/llama-3.1-405b-instruct",
                provider=ModelProvider.OPENROUTER,
                display_name="Llama 3.1 405B Instruct",
                description="Meta's largest and most capable Llama model",
                supports_function_calling=False,
                max_tokens=131072,
                cost_per_1k_tokens=0.003
            ),
            ModelInfo(
                name="meta-llama/llama-3.1-70b-instruct",
                provider=ModelProvider.OPENROUTER,
                display_name="Llama 3.1 70B Instruct",
                description="High-performance Llama model with good balance of capabilities and cost",
                supports_function_calling=False,
                max_tokens=131072,
                cost_per_1k_tokens=0.0008
            ),
            ModelInfo(
                name="mistralai/mistral-7b-instruct",
                provider=ModelProvider.OPENROUTER,
                display_name="Mistral 7B Instruct",
                description="Efficient and capable model from Mistral AI",
                supports_function_calling=False,
                max_tokens=32768,
                cost_per_1k_tokens=0.0001
            ),
            ModelInfo(
                name="google/gemini-pro-1.5",
                provider=ModelProvider.OPENROUTER,
                display_name="Gemini Pro 1.5",
                description="Google's advanced multimodal model via OpenRouter",
                supports_function_calling=False,
                max_tokens=2097152,
                cost_per_1k_tokens=0.0025
            )
        ]
    
    def get_supported_models(self) -> List[ModelInfo]:
        """Get all supported models."""
        return self.supported_models
    
    def get_models_by_provider(self, provider: ModelProvider) -> List[ModelInfo]:
        """Get models for a specific provider."""
        return [model for model in self.supported_models if model.provider == provider]
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model."""
        for model in self.supported_models:
            if model.name == model_name:
                return model
        return None
    
    async def check_model_compatibility(self, check: ModelCompatibilityCheck) -> ModelCompatibilityResult:
        """Check if a model is compatible with the provided API key."""
        try:
            # First, check if we know about this model
            model_info = self.get_model_info(check.model)
            if not model_info:
                return ModelCompatibilityResult(
                    compatible=False,
                    model_available=False,
                    api_key_valid=False,
                    message=f"Unknown model: {check.model}",
                    estimated_cost=None
                )
            
            # Check if the model provider matches
            if model_info.provider != check.provider:
                return ModelCompatibilityResult(
                    compatible=False,
                    model_available=False,
                    api_key_valid=False,
                    message=f"Model {check.model} is not available from provider {check.provider}",
                    estimated_cost=None
                )
            
            # Validate the API key with the provider
            api_key_valid = await self._validate_api_key_with_provider(check.provider, check.api_key)
            
            if not api_key_valid:
                return ModelCompatibilityResult(
                    compatible=False,
                    model_available=False,
                    api_key_valid=False,
                    message="Invalid API key for the specified provider",
                    estimated_cost=None
                )
            
            # Check if the specific model is available
            model_available = await self._check_model_availability(check.provider, check.model, check.api_key)
            
            # Calculate estimated cost for a typical experiment
            estimated_cost = self._estimate_experiment_cost(model_info)
            
            if model_available:
                return ModelCompatibilityResult(
                    compatible=True,
                    model_available=True,
                    api_key_valid=True,
                    message=f"Model {check.model} is available and compatible",
                    estimated_cost=estimated_cost
                )
            else:
                return ModelCompatibilityResult(
                    compatible=False,
                    model_available=False,
                    api_key_valid=True,
                    message=f"Model {check.model} is not available with this API key",
                    estimated_cost=None
                )
        
        except Exception as e:
            logger.error(f"Error checking model compatibility: {e}")
            return ModelCompatibilityResult(
                compatible=False,
                model_available=False,
                api_key_valid=False,
                message=f"Error checking compatibility: {str(e)}",
                estimated_cost=None
            )
    
    async def _validate_api_key_with_provider(self, provider: ModelProvider, api_key: str) -> bool:
        """Validate an API key with its provider."""
        try:
            timeout = httpx.Timeout(10.0)  # 10 second timeout
            
            if provider == ModelProvider.OPENAI:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                    return response.status_code == 200
            
            elif provider == ModelProvider.ANTHROPIC:
                # Anthropic requires a test message to validate
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": api_key,
                            "content-type": "application/json",
                            "anthropic-version": "2023-06-01"
                        },
                        json={
                            "model": "claude-3-haiku-20240307",
                            "max_tokens": 1,
                            "messages": [{"role": "user", "content": "Hi"}]
                        }
                    )
                    # Accept both success and rate limit as valid API key
                    return response.status_code in [200, 429]
            
            elif provider == ModelProvider.OPENROUTER:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        "https://openrouter.ai/api/v1/models",
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                    return response.status_code == 200
            
            return False
        
        except Exception as e:
            logger.error(f"Error validating API key for {provider}: {e}")
            return False
    
    async def _check_model_availability(self, provider: ModelProvider, model_name: str, api_key: str) -> bool:
        """Check if a specific model is available with the API key."""
        try:
            timeout = httpx.Timeout(10.0)
            
            if provider == ModelProvider.OPENAI:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                    if response.status_code == 200:
                        models_data = response.json()
                        available_models = [model["id"] for model in models_data.get("data", [])]
                        return model_name in available_models
            
            elif provider == ModelProvider.ANTHROPIC:
                # Anthropic doesn't have a models endpoint, so we check our known models
                known_anthropic_models = [
                    "claude-3-5-sonnet-20241022", "claude-3.5-sonnet",
                    "claude-3-7-sonnet-20250219", "claude-3.7-sonnet", 
                    "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
                ]
                return model_name in known_anthropic_models
            
            elif provider == ModelProvider.OPENROUTER:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        "https://openrouter.ai/api/v1/models",
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                    if response.status_code == 200:
                        models_data = response.json()
                        available_models = [model["id"] for model in models_data.get("data", [])]
                        return model_name in available_models
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking model availability for {model_name}: {e}")
            return False
    
    def _estimate_experiment_cost(self, model_info: ModelInfo) -> Optional[float]:
        """Estimate the cost of running a typical experiment with this model."""
        if model_info.cost_per_1k_tokens is None:
            return None
        
        # Rough estimates for a typical AIDE experiment:
        # - 20 iterations
        # - ~2000 tokens per code generation request
        # - ~1000 tokens per feedback request
        # - ~3000 tokens for final report
        # - Both input and output tokens
        
        estimated_tokens = (
            20 * 2000 * 2 +  # Code generation (input + output)
            20 * 1000 * 2 +  # Feedback (input + output)
            3000 * 2         # Report generation (input + output)
        )
        
        # Convert to thousands of tokens
        tokens_in_thousands = estimated_tokens / 1000
        
        # Calculate cost
        estimated_cost = tokens_in_thousands * model_info.cost_per_1k_tokens
        
        return round(estimated_cost, 2)
    
    def get_provider_from_model(self, model_name: str) -> Optional[ModelProvider]:
        """Get the provider for a given model name."""
        model_info = self.get_model_info(model_name)
        return model_info.provider if model_info else None
    
    def get_recommended_models_for_task(self, task_type: str = "general") -> List[ModelInfo]:
        """Get recommended models for different task types."""
        if task_type == "coding":
            # Models that are particularly good at code generation
            recommended = ["claude-3-5-sonnet-20241022", "gpt-4-turbo", "gpt-4o"]
        elif task_type == "feedback":
            # Models good at analyzing output and providing feedback
            recommended = ["gpt-4-turbo", "claude-3-5-sonnet-20241022", "gpt-4"]
        elif task_type == "reporting":
            # Models good at generating comprehensive reports
            recommended = ["gpt-4-turbo", "claude-3-5-sonnet-20241022", "gpt-4"]
        elif task_type == "budget":
            # Cost-effective models
            recommended = ["gpt-3.5-turbo", "claude-3-haiku-20240307", "gpt-4o-mini"]
        else:
            # General purpose recommendations
            recommended = ["gpt-4-turbo", "claude-3-5-sonnet-20241022", "gpt-4o"]
        
        return [model for model in self.supported_models if model.name in recommended]