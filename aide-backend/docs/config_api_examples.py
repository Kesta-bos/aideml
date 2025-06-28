"""
Configuration API examples and documentation.
Contains example requests and responses for all configuration endpoints.
"""

# Example API requests and responses for documentation

CONFIG_API_EXAMPLES = {
    "get_current_config": {
        "description": "Get the current AIDE ML configuration",
        "response_example": {
            "success": True,
            "data": {
                "data_dir": "/path/to/dataset",
                "goal": "Predict house prices using the given features",
                "eval": "Minimize mean absolute error on test set",
                "log_dir": "logs",
                "workspace_dir": "workspaces",
                "preprocess_data": True,
                "copy_data": True,
                "exp_name": "house-price-prediction",
                "exec": {
                    "timeout": 3600,
                    "agent_file_name": "runfile.py",
                    "format_tb_ipython": False
                },
                "generate_report": True,
                "report": {
                    "model": "gpt-4-turbo",
                    "temp": 1.0
                },
                "agent": {
                    "steps": 20,
                    "k_fold_validation": 5,
                    "expose_prediction": False,
                    "data_preview": True,
                    "code": {
                        "model": "gpt-4-turbo",
                        "temp": 0.5
                    },
                    "feedback": {
                        "model": "gpt-4-turbo",
                        "temp": 0.5
                    },
                    "search": {
                        "max_debug_depth": 3,
                        "debug_prob": 0.5,
                        "num_drafts": 5
                    }
                }
            },
            "message": "Current configuration retrieved successfully",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    },
    
    "update_config": {
        "description": "Update the complete configuration",
        "request_example": {
            "agent": {
                "steps": 30,
                "k_fold_validation": 3
            },
            "exec": {
                "timeout": 1800
            }
        },
        "response_example": {
            "success": True,
            "data": {
                "# Full updated configuration here": "..."
            },
            "message": "Configuration updated successfully",
            "timestamp": "2024-01-15T10:31:00Z"
        }
    },
    
    "update_config_category": {
        "description": "Update a specific configuration category",
        "path_params": {
            "category": "agent"
        },
        "request_example": {
            "steps": 25,
            "k_fold_validation": 10
        },
        "response_example": {
            "success": True,
            "data": {
                "# Updated configuration": "..."
            },
            "message": "Configuration category 'agent' updated successfully",
            "timestamp": "2024-01-15T10:32:00Z"
        }
    },
    
    "validate_config": {
        "description": "Validate configuration against schema and rules",
        "request_example": {
            "data_dir": "/nonexistent/path",
            "agent": {
                "steps": 150,  # Invalid: exceeds max
                "k_fold_validation": 5
            },
            "exec": {
                "timeout": 30  # Invalid: below minimum
            }
        },
        "query_params": {
            "check_files": True,
            "check_api_keys": False,
            "check_models": False
        },
        "response_example": {
            "success": False,
            "data": {
                "valid": False,
                "total_issues": 3,
                "errors": [
                    {
                        "field_path": "data_dir",
                        "severity": "error",
                        "rule_type": "directory_exists",
                        "message": "Directory does not exist or is not accessible",
                        "current_value": "/nonexistent/path"
                    },
                    {
                        "field_path": "agent.steps",
                        "severity": "error",
                        "rule_type": "range",
                        "message": "Steps must be between 1 and 100",
                        "current_value": 150,
                        "suggested_value": 100
                    },
                    {
                        "field_path": "exec.timeout",
                        "severity": "error",
                        "rule_type": "range",
                        "message": "Timeout must be between 60 and 7200 seconds",
                        "current_value": 30,
                        "suggested_value": 60
                    }
                ],
                "warnings": [],
                "info": [],
                "suggestions": [
                    "Consider using at least 10 steps for better solution quality",
                    "Enable data preview to help the agent understand your dataset"
                ],
                "validation_time": 0.25
            },
            "message": "Configuration validation completed",
            "timestamp": "2024-01-15T10:33:00Z"
        }
    },
    
    "get_config_schema": {
        "description": "Get the complete configuration schema",
        "response_example": {
            "success": True,
            "data": {
                "version": "1.0",
                "categories": {
                    "project": "Project and Task Settings",
                    "agent": "Agent Behavior Configuration",
                    "models": "AI Model Configuration",
                    "search": "Tree Search Parameters",
                    "execution": "Code Execution Settings",
                    "reporting": "Report Generation Settings"
                },
                "fields": [
                    {
                        "name": "data_dir",
                        "type": "string",
                        "category": "project",
                        "title": "Data Directory",
                        "description": "Path to the directory containing your dataset files",
                        "required": False,
                        "nullable": True,
                        "default": None,
                        "validation_rules": [
                            {
                                "field_path": "data_dir",
                                "rule_type": "directory_exists",
                                "error_message": "Directory must exist and be accessible"
                            }
                        ],
                        "ui_hints": {
                            "widget": "directory_picker",
                            "placeholder": "Select data directory...",
                            "help": "Choose the folder containing your dataset files"
                        }
                    }
                    # More fields...
                ],
                "dependencies": [
                    {
                        "field": "goal",
                        "depends_on": "desc_file", 
                        "condition": "if desc_file is None, goal is required"
                    }
                ]
            },
            "message": "Configuration schema retrieved successfully",
            "timestamp": "2024-01-15T10:34:00Z"
        }
    },
    
    "get_supported_models": {
        "description": "Get all supported AI models",
        "query_params": {
            "provider": None  # Optional filter by provider
        },
        "response_example": {
            "success": True,
            "data": [
                {
                    "name": "gpt-4-turbo",
                    "provider": "openai",
                    "display_name": "GPT-4 Turbo",
                    "description": "Latest GPT-4 model with improved performance and lower cost",
                    "supports_function_calling": True,
                    "max_tokens": 128000,
                    "cost_per_1k_tokens": 0.01
                },
                {
                    "name": "claude-3-5-sonnet-20241022",
                    "provider": "anthropic",
                    "display_name": "Claude 3.5 Sonnet",
                    "description": "Most intelligent Claude model with excellent coding abilities",
                    "supports_function_calling": True,
                    "max_tokens": 200000,
                    "cost_per_1k_tokens": 0.003
                }
                # More models...
            ],
            "message": "Retrieved 15 supported models",
            "timestamp": "2024-01-15T10:35:00Z"
        }
    },
    
    "check_model_compatibility": {
        "description": "Check if a model is compatible with the provided API key",
        "request_example": {
            "provider": "openai",
            "model": "gpt-4-turbo",
            "api_key": "sk-..."
        },
        "response_example": {
            "success": True,
            "data": {
                "compatible": True,
                "model_available": True,
                "api_key_valid": True,
                "message": "Model gpt-4-turbo is available and compatible",
                "estimated_cost": 2.50
            },
            "message": "Model gpt-4-turbo is available and compatible",
            "timestamp": "2024-01-15T10:36:00Z"
        }
    },
    
    "export_config": {
        "description": "Export configuration to YAML or JSON format",
        "query_params": {
            "format": "yaml",  # or "json"
            "include_sensitive": False
        },
        "response_example": {
            "# Returns raw YAML or JSON content": "...",
            "content_type": "application/x-yaml",
            "headers": {
                "Content-Disposition": "attachment; filename=aide_config.yaml"
            }
        }
    },
    
    "import_config": {
        "description": "Import configuration from YAML or JSON data",
        "request_example": {
            "config_data": "agent:\n  steps: 25\n  k_fold_validation: 3\nexec:\n  timeout: 1800",
            "merge": True,
            "validate_only": False
        },
        "response_example": {
            "success": True,
            "data": {
                "# Complete imported/merged configuration": "..."
            },
            "message": "Configuration imported successfully",
            "timestamp": "2024-01-15T10:37:00Z"
        }
    },
    
    "reset_config": {
        "description": "Reset configuration to default values",
        "response_example": {
            "success": True,
            "data": {
                "# Default configuration": "..."
            },
            "message": "Configuration reset to defaults successfully",
            "timestamp": "2024-01-15T10:38:00Z"
        }
    },
    
    "get_model_requirements": {
        "description": "Get API key requirements for a specific model",
        "path_params": {
            "model_name": "gpt-4-turbo"
        },
        "response_example": {
            "success": True,
            "data": {
                "model": "gpt-4-turbo",
                "provider": "openai",
                "api_key_required": True,
                "api_key_env_var": "OPENAI_API_KEY",
                "supports_function_calling": True,
                "max_tokens": 128000,
                "estimated_cost_per_experiment": 2.50
            },
            "message": "Requirements for model 'gpt-4-turbo' retrieved successfully",
            "timestamp": "2024-01-15T10:39:00Z"
        }
    }
}

# Common error responses
COMMON_ERROR_RESPONSES = {
    "400_bad_request": {
        "description": "Bad request - invalid input data",
        "example": {
            "success": False,
            "error": {
                "type": "ValidationError",
                "message": "Invalid configuration data",
                "details": {
                    "field": "agent.steps",
                    "error": "Steps must be between 1 and 100"
                }
            },
            "timestamp": "2024-01-15T10:40:00Z"
        }
    },
    
    "404_not_found": {
        "description": "Resource not found",
        "example": {
            "success": False,
            "error": {
                "type": "NotFoundError",
                "message": "Model 'invalid-model' not found"
            },
            "timestamp": "2024-01-15T10:41:00Z"
        }
    },
    
    "500_internal_error": {
        "description": "Internal server error",
        "example": {
            "success": False,
            "error": {
                "type": "InternalServerError",
                "message": "Failed to load configuration file"
            },
            "timestamp": "2024-01-15T10:42:00Z"
        }
    }
}

# Usage examples for different scenarios
USAGE_SCENARIOS = {
    "quick_setup": {
        "title": "Quick Experiment Setup",
        "description": "Set up a simple experiment with minimal configuration",
        "steps": [
            {
                "step": 1,
                "action": "Set data directory and goal",
                "endpoint": "PATCH /api/config/project",
                "payload": {
                    "data_dir": "/path/to/my/dataset",
                    "goal": "Predict customer churn using the given features"
                }
            },
            {
                "step": 2, 
                "action": "Configure for quick experiment",
                "endpoint": "PATCH /api/config/agent",
                "payload": {
                    "steps": 10,
                    "k_fold_validation": 3
                }
            },
            {
                "step": 3,
                "action": "Validate configuration",
                "endpoint": "POST /api/config/validate",
                "payload": "# Current configuration"
            }
        ]
    },
    
    "budget_optimization": {
        "title": "Budget-Friendly Configuration",
        "description": "Configure AIDE to use cost-effective models and settings",
        "steps": [
            {
                "step": 1,
                "action": "Switch to cheaper models",
                "endpoint": "PATCH /api/config/models",
                "payload": {
                    "agent.code.model": "gpt-3.5-turbo",
                    "agent.feedback.model": "gpt-3.5-turbo",
                    "report.model": "gpt-3.5-turbo"
                }
            },
            {
                "step": 2,
                "action": "Reduce iterations",
                "endpoint": "PATCH /api/config/agent", 
                "payload": {
                    "steps": 15,
                    "search.num_drafts": 3
                }
            }
        ]
    },
    
    "thorough_analysis": {
        "title": "Comprehensive Analysis Setup",
        "description": "Configure for maximum solution quality with extensive search",
        "steps": [
            {
                "step": 1,
                "action": "Use best models",
                "endpoint": "PATCH /api/config/models",
                "payload": {
                    "agent.code.model": "claude-3-5-sonnet-20241022",
                    "agent.feedback.model": "gpt-4-turbo"
                }
            },
            {
                "step": 2,
                "action": "Increase search parameters", 
                "endpoint": "PATCH /api/config/agent",
                "payload": {
                    "steps": 50,
                    "k_fold_validation": 10
                }
            },
            {
                "step": 3,
                "action": "Enhance search algorithm",
                "endpoint": "PATCH /api/config/search",
                "payload": {
                    "num_drafts": 10,
                    "max_debug_depth": 5
                }
            }
        ]
    }
}