"""
Complete configuration schema definitions for AIDE ML.
Contains the definitive schema used for validation and UI generation.
"""

from typing import Dict, Any, List


def get_aide_config_schema() -> Dict[str, Any]:
    """
    Get the complete AIDE ML configuration schema.
    
    This schema defines all configuration fields, their types, validation rules,
    and UI hints for frontend rendering.
    """
    
    return {
        "version": "1.0",
        "title": "AIDE ML Configuration",
        "description": "Complete configuration schema for AIDE Machine Learning Agent",
        
        "categories": {
            "project": {
                "title": "Project Settings",
                "description": "Basic project and task configuration",
                "icon": "folder",
                "order": 1
            },
            "agent": {
                "title": "Agent Configuration", 
                "description": "Agent behavior and workflow settings",
                "icon": "robot",
                "order": 2
            },
            "models": {
                "title": "AI Models",
                "description": "Language model configuration for different stages", 
                "icon": "brain",
                "order": 3
            },
            "search": {
                "title": "Search Algorithm",
                "description": "Tree search and exploration parameters",
                "icon": "search",
                "order": 4
            },
            "execution": {
                "title": "Execution Settings",
                "description": "Code execution environment configuration",
                "icon": "play",
                "order": 5
            },
            "reporting": {
                "title": "Reporting",
                "description": "Report generation and output settings",
                "icon": "file-text",
                "order": 6
            }
        },
        
        "fields": [
            # Project Settings
            {
                "name": "data_dir",
                "type": "string",
                "category": "project",
                "title": "Data Directory",
                "description": "Path to the directory containing your dataset files",
                "required": False,
                "nullable": True,
                "default": None,
                "validation": {
                    "rules": ["directory_exists"],
                    "messages": {
                        "directory_exists": "Directory must exist and be accessible"
                    }
                },
                "ui": {
                    "widget": "directory_picker",
                    "placeholder": "Select data directory...",
                    "help": "Choose the folder containing your dataset files (CSV, JSON, etc.)"
                }
            },
            {
                "name": "desc_file", 
                "type": "string",
                "category": "project",
                "title": "Description File",
                "description": "Path to a markdown file describing the task (alternative to goal field)",
                "required": False,
                "nullable": True,
                "default": None,
                "validation": {
                    "rules": ["file_exists"],
                    "messages": {
                        "file_exists": "File must exist and be readable"
                    }
                },
                "ui": {
                    "widget": "file_picker",
                    "accept": [".md", ".txt"],
                    "placeholder": "Select description file...",
                    "help": "Optional: Choose a markdown file describing your task"
                }
            },
            {
                "name": "goal",
                "type": "string", 
                "category": "project",
                "title": "Task Goal",
                "description": "Clear description of what you want to achieve with your data",
                "required": False,
                "nullable": True,
                "default": None,
                "validation": {
                    "rules": ["required_if_no_desc_file"],
                    "messages": {
                        "required_if_no_desc_file": "Goal is required when no description file is provided"
                    }
                },
                "ui": {
                    "widget": "textarea",
                    "rows": 3,
                    "placeholder": "e.g., Predict house prices using the given features...",
                    "help": "Describe what you want the AI to accomplish with your dataset"
                }
            },
            {
                "name": "eval",
                "type": "string",
                "category": "project", 
                "title": "Evaluation Criteria",
                "description": "How success should be measured (optional but recommended)",
                "required": False,
                "nullable": True,
                "default": None,
                "ui": {
                    "widget": "textarea",
                    "rows": 2,
                    "placeholder": "e.g., Minimize mean absolute error on test set...",
                    "help": "Specify how to evaluate the quality of solutions"
                }
            },
            {
                "name": "log_dir",
                "type": "string",
                "category": "project",
                "title": "Log Directory", 
                "description": "Directory where experiment logs will be stored",
                "required": True,
                "default": "logs",
                "validation": {
                    "rules": ["non_empty_string"],
                    "messages": {
                        "non_empty_string": "Log directory cannot be empty"
                    }
                },
                "ui": {
                    "widget": "text",
                    "help": "Logs include experiment history, configurations, and results"
                }
            },
            {
                "name": "workspace_dir",
                "type": "string",
                "category": "project",
                "title": "Workspace Directory",
                "description": "Directory where the agent will work with data and code",
                "required": True,
                "default": "workspaces",
                "validation": {
                    "rules": ["non_empty_string"],
                    "messages": {
                        "non_empty_string": "Workspace directory cannot be empty"
                    }
                },
                "ui": {
                    "widget": "text", 
                    "help": "Temporary workspace for data processing and code execution"
                }
            },
            {
                "name": "preprocess_data",
                "type": "boolean",
                "category": "project",
                "title": "Preprocess Data",
                "description": "Automatically extract ZIP files and preprocess data",
                "required": True,
                "default": True,
                "ui": {
                    "widget": "switch",
                    "help": "Enable to automatically unzip archives in your data directory"
                }
            },
            {
                "name": "copy_data",
                "type": "boolean", 
                "category": "project",
                "title": "Copy Data",
                "description": "Copy data to workspace instead of creating symbolic links",
                "required": True,
                "default": True,
                "ui": {
                    "widget": "switch",
                    "help": "Recommended to prevent accidental modification of original data"
                }
            },
            {
                "name": "exp_name",
                "type": "string",
                "category": "project",
                "title": "Experiment Name",
                "description": "Custom name for this experiment (auto-generated if empty)",
                "required": False,
                "nullable": True,
                "default": None,
                "validation": {
                    "rules": ["alphanumeric_with_dash_underscore"],
                    "messages": {
                        "alphanumeric_with_dash_underscore": "Only letters, numbers, hyphens, and underscores allowed"
                    }
                },
                "ui": {
                    "widget": "text",
                    "placeholder": "my-experiment-name",
                    "help": "Leave empty for auto-generated name based on current timestamp"
                }
            },
            
            # Agent Configuration
            {
                "name": "agent.steps",
                "type": "integer",
                "category": "agent",
                "title": "Improvement Steps",
                "description": "Number of iterative improvement steps to perform",
                "required": True,
                "default": 20,
                "validation": {
                    "rules": ["range"],
                    "min": 1,
                    "max": 100,
                    "messages": {
                        "range": "Steps must be between 1 and 100"
                    }
                },
                "ui": {
                    "widget": "slider",
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "marks": {
                        5: "Fast",
                        20: "Default", 
                        50: "Thorough",
                        100: "Extensive"
                    },
                    "help": "More steps = better solutions but longer runtime"
                }
            },
            {
                "name": "agent.k_fold_validation",
                "type": "integer",
                "category": "agent",
                "title": "Cross-Validation Folds",
                "description": "Number of folds for cross-validation (1 = no CV)",
                "required": True,
                "default": 5,
                "validation": {
                    "rules": ["range"],
                    "min": 1,
                    "max": 10,
                    "messages": {
                        "range": "K-fold must be between 1 and 10"
                    }
                },
                "ui": {
                    "widget": "select",
                    "options": [
                        {"value": 1, "label": "No Cross-Validation"},
                        {"value": 3, "label": "3-Fold CV"},
                        {"value": 5, "label": "5-Fold CV (Recommended)"},
                        {"value": 10, "label": "10-Fold CV (Rigorous)"}
                    ],
                    "help": "Higher values give more reliable evaluation but take longer"
                }
            },
            {
                "name": "agent.expose_prediction",
                "type": "boolean",
                "category": "agent",
                "title": "Generate Prediction Function",
                "description": "Create a standalone prediction function for deployment",
                "required": True,
                "default": False,
                "ui": {
                    "widget": "switch",
                    "help": "Enable if you need a function to make predictions on new data"
                }
            },
            {
                "name": "agent.data_preview",
                "type": "boolean",
                "category": "agent", 
                "title": "Provide Data Preview",
                "description": "Give the agent a preview of your data structure",
                "required": True,
                "default": True,
                "ui": {
                    "widget": "switch",
                    "help": "Recommended: helps the agent understand your dataset structure"
                }
            },
            
            # Model Configuration
            {
                "name": "agent.code.model",
                "type": "string",
                "category": "models",
                "title": "Code Generation Model",
                "description": "AI model used for generating and improving code",
                "required": True,
                "default": "gpt-4-turbo",
                "validation": {
                    "rules": ["supported_model"],
                    "messages": {
                        "supported_model": "Model must be supported by the system"
                    }
                },
                "ui": {
                    "widget": "model_select",
                    "provider_group": "coding",
                    "recommendations": ["claude-3-5-sonnet-20241022", "gpt-4-turbo", "gpt-4o"],
                    "help": "Choose a model optimized for code generation tasks"
                }
            },
            {
                "name": "agent.code.temp",
                "type": "number",
                "category": "models",
                "title": "Code Generation Temperature",
                "description": "Creativity level for code generation (0.0 = deterministic, 2.0 = very creative)",
                "required": True,
                "default": 0.5,
                "validation": {
                    "rules": ["range"],
                    "min": 0.0,
                    "max": 2.0,
                    "messages": {
                        "range": "Temperature must be between 0.0 and 2.0"
                    }
                },
                "ui": {
                    "widget": "slider",
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "marks": {
                        0.0: "Deterministic",
                        0.5: "Balanced",
                        1.0: "Creative",
                        2.0: "Very Creative"
                    },
                    "help": "Lower values = more consistent code, higher values = more creative solutions"
                }
            },
            {
                "name": "agent.feedback.model",
                "type": "string",
                "category": "models",
                "title": "Feedback Analysis Model", 
                "description": "AI model used for analyzing results and providing feedback",
                "required": True,
                "default": "gpt-4-turbo",
                "validation": {
                    "rules": ["supported_model"],
                    "messages": {
                        "supported_model": "Model must be supported by the system"
                    }
                },
                "ui": {
                    "widget": "model_select",
                    "provider_group": "feedback",
                    "recommendations": ["gpt-4-turbo", "claude-3-5-sonnet-20241022", "gpt-4"],
                    "help": "Model for analyzing execution results and providing improvement feedback"
                }
            },
            {
                "name": "agent.feedback.temp",
                "type": "number",
                "category": "models",
                "title": "Feedback Temperature",
                "description": "Creativity level for feedback analysis",
                "required": True,
                "default": 0.5,
                "validation": {
                    "rules": ["range"],
                    "min": 0.0,
                    "max": 2.0,
                    "messages": {
                        "range": "Temperature must be between 0.0 and 2.0"
                    }
                },
                "ui": {
                    "widget": "slider",
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "help": "Balanced temperature usually works best for analysis tasks"
                }
            },
            {
                "name": "report.model",
                "type": "string",
                "category": "models",
                "title": "Report Generation Model",
                "description": "AI model used for generating final experiment reports",
                "required": True,
                "default": "gpt-4-turbo",
                "validation": {
                    "rules": ["supported_model"],
                    "messages": {
                        "supported_model": "Model must be supported by the system"
                    }
                },
                "ui": {
                    "widget": "model_select",
                    "provider_group": "reporting",
                    "recommendations": ["gpt-4-turbo", "claude-3-5-sonnet-20241022", "gpt-4"],
                    "help": "Model for creating comprehensive experiment reports"
                }
            },
            {
                "name": "report.temp",
                "type": "number",
                "category": "models",
                "title": "Report Temperature",
                "description": "Creativity level for report generation",
                "required": True,
                "default": 1.0,
                "validation": {
                    "rules": ["range"],
                    "min": 0.0,
                    "max": 2.0,
                    "messages": {
                        "range": "Temperature must be between 0.0 and 2.0"
                    }
                },
                "ui": {
                    "widget": "slider",
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "help": "Higher temperature for more creative and comprehensive reports"
                }
            },
            
            # Search Algorithm
            {
                "name": "agent.search.max_debug_depth",
                "type": "integer",
                "category": "search",
                "title": "Maximum Debug Depth",
                "description": "How many times to try debugging a failed solution",
                "required": True,
                "default": 3,
                "validation": {
                    "rules": ["range"],
                    "min": 1,
                    "max": 10,
                    "messages": {
                        "range": "Debug depth must be between 1 and 10"
                    }
                },
                "ui": {
                    "widget": "slider",
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "marks": {
                        1: "Shallow",
                        3: "Default",
                        5: "Deep",
                        10: "Very Deep"
                    },
                    "help": "Higher values = more persistent debugging but longer runtime"
                }
            },
            {
                "name": "agent.search.debug_prob",
                "type": "number",
                "category": "search",
                "title": "Debug Probability",
                "description": "Probability of debugging vs trying a completely new approach",
                "required": True,
                "default": 0.5,
                "validation": {
                    "rules": ["range"],
                    "min": 0.0,
                    "max": 1.0,
                    "messages": {
                        "range": "Probability must be between 0.0 and 1.0"
                    }
                },
                "ui": {
                    "widget": "slider",
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "marks": {
                        0.0: "Never Debug",
                        0.5: "Balanced",
                        1.0: "Always Debug"
                    },
                    "help": "Balance between fixing existing solutions vs exploring new approaches"
                }
            },
            {
                "name": "agent.search.num_drafts",
                "type": "integer",
                "category": "search",
                "title": "Initial Drafts",
                "description": "Number of different initial solutions to generate",
                "required": True,
                "default": 5,
                "validation": {
                    "rules": ["range"],
                    "min": 1,
                    "max": 20,
                    "messages": {
                        "range": "Number of drafts must be between 1 and 20"
                    }
                },
                "ui": {
                    "widget": "slider",
                    "min": 1,
                    "max": 20,
                    "step": 1,
                    "marks": {
                        1: "Single",
                        5: "Default",
                        10: "Many",
                        20: "Exhaustive"
                    },
                    "help": "More drafts = better initial solutions but longer startup time"
                }
            },
            
            # Execution Settings
            {
                "name": "exec.timeout",
                "type": "integer",
                "category": "execution",
                "title": "Execution Timeout",
                "description": "Maximum time (seconds) to wait for code execution",
                "required": True,
                "default": 3600,
                "validation": {
                    "rules": ["range"],
                    "min": 60,
                    "max": 7200,
                    "messages": {
                        "range": "Timeout must be between 60 and 7200 seconds"
                    }
                },
                "ui": {
                    "widget": "duration_picker",
                    "presets": [
                        {"value": 300, "label": "5 minutes"},
                        {"value": 900, "label": "15 minutes"},
                        {"value": 1800, "label": "30 minutes"},
                        {"value": 3600, "label": "1 hour (default)"},
                        {"value": 7200, "label": "2 hours"}
                    ],
                    "help": "Longer timeouts allow for more complex computations"
                }
            },
            {
                "name": "exec.agent_file_name",
                "type": "string",
                "category": "execution",
                "title": "Script Filename",
                "description": "Name of the Python file generated by the agent",
                "required": True,
                "default": "runfile.py",
                "validation": {
                    "rules": ["python_filename"],
                    "messages": {
                        "python_filename": "Must be a valid Python filename ending in .py"
                    }
                },
                "ui": {
                    "widget": "text",
                    "suffix": ".py",
                    "help": "The agent will create and execute this Python file"
                }
            },
            {
                "name": "exec.format_tb_ipython",
                "type": "boolean",
                "category": "execution",
                "title": "IPython-style Tracebacks",
                "description": "Format error messages using IPython's rich traceback style",
                "required": True,
                "default": False,
                "ui": {
                    "widget": "switch",
                    "help": "Enable for more detailed and colorful error messages"
                }
            },
            
            # Reporting
            {
                "name": "generate_report",
                "type": "boolean",
                "category": "reporting",
                "title": "Generate Report",
                "description": "Create a comprehensive report at the end of the experiment",
                "required": True,
                "default": True,
                "ui": {
                    "widget": "switch",
                    "help": "Recommended: provides detailed analysis of the experiment results"
                }
            }
        ],
        
        "field_groups": [
            {
                "title": "Task Definition",
                "fields": ["data_dir", "goal", "desc_file", "eval"],
                "description": "Define what you want to accomplish"
            },
            {
                "title": "Agent Behavior", 
                "fields": ["agent.steps", "agent.k_fold_validation", "agent.expose_prediction", "agent.data_preview"],
                "description": "Configure how the agent works"
            },
            {
                "title": "Model Selection",
                "fields": ["agent.code.model", "agent.feedback.model", "report.model"],
                "description": "Choose AI models for different tasks"
            },
            {
                "title": "Model Parameters",
                "fields": ["agent.code.temp", "agent.feedback.temp", "report.temp"],
                "description": "Fine-tune model creativity"
            }
        ],
        
        "presets": {
            "quick_experiment": {
                "title": "Quick Experiment",
                "description": "Fast setup for initial exploration",
                "values": {
                    "agent.steps": 10,
                    "agent.search.num_drafts": 3,
                    "agent.k_fold_validation": 3
                }
            },
            "thorough_experiment": {
                "title": "Thorough Experiment", 
                "description": "Comprehensive search for best results",
                "values": {
                    "agent.steps": 50,
                    "agent.search.num_drafts": 10,
                    "agent.k_fold_validation": 10
                }
            },
            "budget_friendly": {
                "title": "Budget Friendly",
                "description": "Cost-optimized settings using cheaper models",
                "values": {
                    "agent.code.model": "gpt-3.5-turbo",
                    "agent.feedback.model": "gpt-3.5-turbo",
                    "report.model": "gpt-3.5-turbo",
                    "agent.steps": 15
                }
            }
        }
    }


def get_validation_rules() -> Dict[str, Dict[str, Any]]:
    """Get validation rules for all configuration fields."""
    
    return {
        "directory_exists": {
            "description": "Validates that a directory exists and is accessible",
            "parameters": [],
            "error_message": "Directory does not exist or is not accessible"
        },
        "file_exists": {
            "description": "Validates that a file exists and is readable",
            "parameters": [],
            "error_message": "File does not exist or is not readable"
        },
        "range": {
            "description": "Validates that a number is within specified range",
            "parameters": ["min", "max"],
            "error_message": "Value must be between {min} and {max}"
        },
        "non_empty_string": {
            "description": "Validates that a string is not empty",
            "parameters": [],
            "error_message": "Value cannot be empty"
        },
        "alphanumeric_with_dash_underscore": {
            "description": "Validates alphanumeric string with dashes and underscores",
            "parameters": [],
            "error_message": "Only letters, numbers, hyphens, and underscores are allowed"
        },
        "python_filename": {
            "description": "Validates Python filename format",
            "parameters": [],
            "error_message": "Must be a valid Python filename ending with .py"
        },
        "supported_model": {
            "description": "Validates that model is supported by the system",
            "parameters": [],
            "error_message": "Model is not supported or available"
        },
        "required_if_no_desc_file": {
            "description": "Field is required when desc_file is not provided",
            "parameters": [],
            "error_message": "This field is required when no description file is provided"
        }
    }