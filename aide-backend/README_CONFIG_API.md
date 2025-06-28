# AIDE ML Configuration API

This document describes the comprehensive configuration management API for AIDE ML, which allows complete control over all AIDE settings through a web interface.

## Overview

The Configuration API provides 17 endpoints for managing every aspect of AIDE ML configuration:

- **Schema and Documentation**: Get field definitions, validation rules, and UI hints
- **Configuration Management**: Read, update, validate, and reset configurations
- **Model Management**: Discover supported models and check compatibility
- **Import/Export**: Save and load configurations in YAML/JSON formats

## Quick Start

### 1. Get Configuration Schema
```bash
GET /api/config/schema
```
Returns complete field definitions with validation rules and UI hints for building configuration interfaces.

### 2. View Current Configuration
```bash
GET /api/config
```
Returns the current AIDE ML configuration.

### 3. Update Configuration
```bash
PUT /api/config
Content-Type: application/json

{
  "agent": {
    "steps": 30,
    "k_fold_validation": 10
  },
  "exec": {
    "timeout": 1800
  }
}
```

### 4. Validate Configuration
```bash
POST /api/config/validate
Content-Type: application/json

{
  "data_dir": "/path/to/data",
  "goal": "Predict house prices",
  "agent": {
    "steps": 25
  }
}
```

## API Endpoints

### Schema and Discovery

#### `GET /api/config/schema`
Get complete configuration schema with field definitions, types, validation rules, and UI hints.

**Response:**
```json
{
  "success": true,
  "data": {
    "version": "1.0",
    "categories": {
      "project": "Project and Task Settings",
      "agent": "Agent Behavior Configuration",
      "models": "AI Model Configuration"
    },
    "fields": [
      {
        "name": "data_dir",
        "type": "string",
        "category": "project",
        "title": "Data Directory",
        "description": "Path to the directory containing your dataset files",
        "required": false,
        "validation_rules": [...],
        "ui_hints": {
          "widget": "directory_picker",
          "placeholder": "Select data directory..."
        }
      }
    ]
  }
}
```

#### `GET /api/config/categories`
Get configuration categories with descriptions.

**Response:**
```json
{
  "success": true,
  "data": {
    "project": "Project and Task Settings",
    "agent": "Agent Behavior Configuration",
    "models": "AI Model Configuration",
    "search": "Tree Search Parameters",
    "execution": "Code Execution Settings",
    "reporting": "Report Generation Settings"
  }
}
```

### Configuration Management

#### `GET /api/config`
Get current configuration values.

#### `GET /api/config/{category}`
Get configuration for specific category.

**Parameters:**
- `category`: One of `project`, `agent`, `models`, `search`, `execution`, `reporting`

#### `PUT /api/config`
Update complete configuration.

**Request Body:**
```json
{
  "data_dir": "/path/to/dataset",
  "goal": "Predict customer churn",
  "agent": {
    "steps": 25,
    "k_fold_validation": 5
  }
}
```

#### `PATCH /api/config/{category}`
Update specific category configuration.

**Example - Update agent settings:**
```bash
PATCH /api/config/agent
Content-Type: application/json

{
  "steps": 30,
  "k_fold_validation": 10,
  "data_preview": true
}
```

#### `POST /api/config/validate`
Validate configuration against schema and rules.

**Query Parameters:**
- `check_files` (bool): Check if files and directories exist (default: true)
- `check_api_keys` (bool): Validate API keys (default: false)  
- `check_models` (bool): Check model compatibility (default: false)

**Response:**
```json
{
  "success": false,
  "data": {
    "valid": false,
    "total_issues": 2,
    "errors": [
      {
        "field_path": "agent.steps",
        "severity": "error",
        "rule_type": "range",
        "message": "Steps must be between 1 and 100",
        "current_value": 150,
        "suggested_value": 100
      }
    ],
    "warnings": [],
    "suggestions": [
      "Consider using cross-validation for better evaluation"
    ]
  }
}
```

#### `POST /api/config/reset`
Reset configuration to default values.

### Model Management

#### `GET /api/config/models`
Get all supported AI models.

**Query Parameters:**
- `provider` (optional): Filter by provider (`openai`, `anthropic`, `openrouter`)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "name": "gpt-4-turbo",
      "provider": "openai",
      "display_name": "GPT-4 Turbo",
      "description": "Latest GPT-4 model with improved performance",
      "supports_function_calling": true,
      "max_tokens": 128000,
      "cost_per_1k_tokens": 0.01
    }
  ]
}
```

#### `GET /api/config/models/recommendations`
Get recommended models for specific tasks.

**Query Parameters:**
- `task_type`: One of `general`, `coding`, `feedback`, `reporting`, `budget`

#### `POST /api/config/check-model-compatibility`
Check if model is compatible with API key.

**Request Body:**
```json
{
  "provider": "openai",
  "model": "gpt-4-turbo", 
  "api_key": "sk-..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "compatible": true,
    "model_available": true,
    "api_key_valid": true,
    "message": "Model gpt-4-turbo is available and compatible",
    "estimated_cost": 2.50
  }
}
```

#### `GET /api/config/model-requirements/{model_name}`
Get API key requirements for specific model.

### Import/Export

#### `GET /api/config/export`
Export configuration to YAML or JSON format.

**Query Parameters:**
- `format`: `yaml` or `json` (default: yaml)
- `include_sensitive`: Include sensitive data like API keys (default: false)

**Response:** Raw YAML or JSON file download

#### `POST /api/config/import`
Import configuration from YAML or JSON data.

**Request Body:**
```json
{
  "config_data": "agent:\n  steps: 25\n  k_fold_validation: 3",
  "merge": true,
  "validate_only": false
}
```

#### `GET /api/config/defaults`
Get default configuration values without applying them.

### Utility Endpoints

#### `GET /api/config/validation-rules`
Get all validation rules for configuration fields.

#### `GET /api/config/field-info/{field_path}`
Get detailed information about a specific configuration field.

## Configuration Categories

### Project Settings (`project`)
Basic project and task configuration:
- `data_dir`: Path to dataset directory
- `goal`: Task description
- `eval`: Evaluation criteria
- `exp_name`: Experiment name
- Directory and data processing settings

### Agent Configuration (`agent`)
Agent behavior and workflow settings:
- `steps`: Number of improvement iterations (1-100)
- `k_fold_validation`: Cross-validation folds (1-10)
- `expose_prediction`: Generate prediction function
- `data_preview`: Provide data preview to agent

### AI Models (`models`)
Language model configuration:
- `agent.code.model`: Model for code generation
- `agent.feedback.model`: Model for feedback analysis
- `report.model`: Model for report generation
- Temperature settings for each model

### Search Algorithm (`search`)
Tree search and exploration parameters:
- `max_debug_depth`: Maximum debugging attempts (1-10)
- `debug_prob`: Debug vs new attempt probability (0.0-1.0)
- `num_drafts`: Initial solution drafts (1-20)

### Execution Settings (`execution`)
Code execution environment:
- `timeout`: Maximum execution time (60-7200 seconds)
- `agent_file_name`: Generated script filename
- `format_tb_ipython`: IPython-style tracebacks

### Reporting (`reporting`)
Report generation settings:
- `generate_report`: Enable final report generation

## Validation Rules

The API includes comprehensive validation:

- **Type Validation**: Ensures correct data types
- **Range Validation**: Numeric values within bounds
- **Pattern Validation**: String format validation
- **File Existence**: Checks if paths exist
- **Dependencies**: Inter-field requirements
- **Model Compatibility**: API key and model validation

## Usage Examples

### Quick Experiment Setup
```bash
# 1. Set basic project settings
PATCH /api/config/project
{
  "data_dir": "/path/to/dataset",
  "goal": "Predict customer churn"
}

# 2. Configure for quick experiment  
PATCH /api/config/agent
{
  "steps": 10,
  "k_fold_validation": 3
}

# 3. Validate configuration
POST /api/config/validate
```

### Budget-Friendly Configuration
```bash
# Switch to cost-effective models
PATCH /api/config/models
{
  "agent.code.model": "gpt-3.5-turbo",
  "agent.feedback.model": "gpt-3.5-turbo",
  "report.model": "gpt-3.5-turbo"
}

# Reduce iterations
PATCH /api/config/agent
{
  "steps": 15
}
```

### Comprehensive Analysis Setup
```bash
# Use best models
PATCH /api/config/models
{
  "agent.code.model": "claude-3-5-sonnet-20241022",
  "agent.feedback.model": "gpt-4-turbo"
}

# Increase search parameters
PATCH /api/config/agent
{
  "steps": 50,
  "k_fold_validation": 10
}

PATCH /api/config/search
{
  "num_drafts": 10,
  "max_debug_depth": 5
}
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid input or validation errors
- `404 Not Found`: Resource not found (e.g., invalid model)
- `500 Internal Server Error`: Server-side errors

Error responses follow this format:
```json
{
  "success": false,
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
```

## Integration Notes

- All endpoints return consistent `ApiResponse` format
- Timestamps in ISO 8601 format
- Configuration changes are immediately applied to AIDE's config file
- API includes CORS support for web frontends
- Full OpenAPI/Swagger documentation available at `/api/docs`

This API provides complete control over AIDE ML configuration, enabling rich web interfaces for experiment setup and management.