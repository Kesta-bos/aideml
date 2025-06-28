# AIDE ML Profile Management API

This document provides comprehensive documentation for the AIDE ML Profile Management API, which extends the base configuration system with advanced profile management, templates, history tracking, and backup/restore functionality.

## Overview

The Profile Management API enables users to:
- Create and manage multiple configuration profiles
- Apply predefined templates for common use cases
- Track configuration change history
- Compare different configurations
- Backup and restore configuration data
- Import/export profiles

## Base URL

All endpoints are prefixed with `/api/config`

## Authentication

Currently, no authentication is required. This may change in future versions.

## Core Concepts

### Configuration Profiles
Profiles are named collections of AIDE ML configuration settings that can be easily switched between. Each profile contains:
- Unique identifier and human-readable name
- Complete AIDE configuration data
- Metadata (tags, description, timestamps)
- Version tracking

### Templates
Templates are predefined configuration patterns optimized for specific use cases:
- **Quick Experiment**: Fast prototyping and exploration
- **Cost Optimized**: Budget-conscious configurations
- **Comprehensive Analysis**: Production-ready, high-quality analysis
- **Research Focused**: Academic and research-oriented settings
- **Educational**: Learning and teaching purposes

### History Tracking
All configuration changes are automatically tracked with:
- Timestamp and user action type
- Changed fields identification
- Previous configuration for rollback
- Descriptive change messages

## API Endpoints

### Profile Management

#### Create Profile
Create a new configuration profile.

```http
POST /api/config/profiles
Content-Type: application/json

{
  "name": "My Custom Profile",
  "description": "Profile for specific use case",
  "tags": ["custom", "experiment"],
  "copy_from_current": true,
  "set_as_active": false,
  "config_data": {
    "agent": {
      "steps": 15,
      "code": {"model": "gpt-4-turbo", "temp": 0.5}
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "profile_123",
    "name": "My Custom Profile",
    "description": "Profile for specific use case",
    "config_data": {...},
    "tags": ["custom", "experiment"],
    "is_default": false,
    "is_template": false,
    "is_active": false,
    "version": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "Profile 'My Custom Profile' created successfully"
}
```

#### List Profiles
Retrieve all configuration profiles.

```http
GET /api/config/profiles?include_templates=false
```

**Response:**
```json
{
  "success": true,
  "data": {
    "profiles": [
      {
        "id": "profile_123",
        "name": "My Custom Profile",
        "description": "Profile for specific use case",
        "config_data": {...},
        "tags": ["custom", "experiment"],
        "is_default": false,
        "is_template": false,
        "is_active": true,
        "version": 1,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total_count": 1,
    "active_profile_id": "profile_123",
    "default_profile_id": null
  },
  "message": "Retrieved 1 profiles"
}
```

#### Get Profile
Retrieve a specific profile by ID.

```http
GET /api/config/profiles/{profile_id}
```

#### Update Profile
Update an existing profile.

```http
PUT /api/config/profiles/{profile_id}
Content-Type: application/json

{
  "name": "Updated Profile Name",
  "description": "Updated description",
  "config_data": {
    "agent": {
      "steps": 20
    }
  },
  "tags": ["updated", "modified"]
}
```

#### Delete Profile
Delete a profile (cannot delete active or default profiles).

```http
DELETE /api/config/profiles/{profile_id}
```

#### Activate Profile
Activate a profile and apply its configuration.

```http
POST /api/config/profiles/{profile_id}/activate
```

**Response:**
```json
{
  "success": true,
  "data": {
    "profile": {...},
    "applied_config": {...},
    "message": "Profile 'My Custom Profile' activated successfully"
  },
  "message": "Profile 'My Custom Profile' activated successfully"
}
```

#### Search Profiles
Search profiles with filters and pagination.

```http
POST /api/config/profiles/search
Content-Type: application/json

{
  "query": "experiment",
  "tags": ["custom"],
  "is_template": false,
  "page": 1,
  "limit": 20
}
```

### Template Management

#### List Templates
Get all available templates.

```http
GET /api/config/templates?category=quick_experiment
```

**Response:**
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "name": "quick_experiment",
        "display_name": "Quick Experiment",
        "description": "Fast configuration for rapid prototyping",
        "category": "quick_experiment",
        "config_data": {...},
        "use_case": "Rapid prototyping, initial exploration",
        "estimated_cost": "$1-3",
        "estimated_time": "5-10 minutes",
        "complexity": "beginner",
        "prerequisites": ["Basic dataset understanding"],
        "tags": ["quick", "prototype", "beginner"],
        "is_builtin": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total_count": 1,
    "categories": ["quick_experiment", "cost_optimized", "comprehensive_analysis"]
  },
  "message": "Retrieved 1 templates"
}
```

#### Get Template
Retrieve a specific template.

```http
GET /api/config/templates/{template_name}
```

#### Apply Template
Apply a template to current configuration or specific profile.

```http
POST /api/config/templates/{template_name}/apply
Content-Type: application/json

{
  "target_profile_id": "profile_123",
  "merge_strategy": "replace",
  "create_backup": true
}
```

**Merge Strategies:**
- `replace`: Completely replace configuration with template
- `merge`: Deep merge template with existing configuration
- `overlay`: Only update existing fields with template values

**Response:**
```json
{
  "success": true,
  "data": {
    "template": {...},
    "applied_config": {...},
    "backup_id": "backup_456",
    "merge_strategy": "replace",
    "message": "Successfully applied template 'Quick Experiment'"
  },
  "message": "Successfully applied template 'Quick Experiment'"
}
```

#### Create Custom Template
Create a new custom template.

```http
POST /api/config/templates
Content-Type: application/json

{
  "name": "my_custom_template",
  "display_name": "My Custom Template",
  "description": "Custom template for specific workflow",
  "category": "custom",
  "config_data": {
    "agent": {
      "steps": 25,
      "code": {"model": "gpt-4-turbo", "temp": 0.4}
    }
  },
  "use_case": "Specific analysis workflow",
  "complexity": "intermediate",
  "tags": ["custom", "workflow"]
}
```

#### Save Current as Template
Save current configuration as a new template.

```http
POST /api/config/templates/save-current
Content-Type: application/json

{
  "name": "current_config_template",
  "display_name": "Current Configuration Template",
  "description": "Template based on current active configuration",
  "category": "custom",
  "tags": ["current", "backup"]
}
```

#### Compare Templates
Compare configurations between multiple templates.

```http
POST /api/config/templates/compare
Content-Type: application/json

{
  "template_names": ["quick_experiment", "comprehensive_analysis"],
  "comparison_fields": ["agent.steps", "agent.code.model"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "comparisons": [
      {
        "template_name": "quick_experiment",
        "display_name": "Quick Experiment",
        "field_values": {
          "agent.steps": 5,
          "agent.code.model": "gpt-3.5-turbo"
        }
      },
      {
        "template_name": "comprehensive_analysis",
        "display_name": "Comprehensive Analysis",
        "field_values": {
          "agent.steps": 30,
          "agent.code.model": "gpt-4-turbo"
        }
      }
    ],
    "common_fields": ["agent.code.temp"],
    "different_fields": ["agent.steps", "agent.code.model"]
  },
  "message": "Compared 2 templates"
}
```

### History Management

#### Get Global History
Retrieve global configuration change history.

```http
GET /api/config/history?limit=50
```

#### Get Profile History
Retrieve history for a specific profile.

```http
GET /api/config/profiles/{profile_id}/history?limit=50
```

**Response:**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "id": "history_789",
        "profile_id": "profile_123",
        "config_data": {...},
        "change_description": "Updated agent steps from 10 to 15",
        "changed_fields": ["agent.steps"],
        "user_action": "manual_edit",
        "previous_config": {...},
        "timestamp": "2024-01-15T10:30:00Z"
      }
    ],
    "total_count": 1,
    "profile_id": "profile_123"
  },
  "message": "Retrieved 1 history entries for profile"
}
```

#### Rollback Configuration
Rollback to a previous configuration.

```http
POST /api/config/rollback
Content-Type: application/json

{
  "history_id": "history_789",
  "create_backup": true
}
```

### Configuration Comparison

#### Compare Profiles
Compare configurations between two profiles.

```http
GET /api/config/diff/profiles/{profile_id_1}/{profile_id_2}
```

#### Compare History Entries
Compare configurations between two history entries.

```http
GET /api/config/diff/history/{history_id_1}/{history_id_2}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "differences": [
      {
        "field_path": "agent.steps",
        "old_value": 10,
        "new_value": 15,
        "change_type": "modified"
      }
    ],
    "summary": "1 differences found",
    "from_version": "Profile A (v1)",
    "to_version": "Profile B (v2)"
  },
  "message": "1 differences found"
}
```

### Backup and Restore

#### Create Backup
Create a complete configuration backup.

```http
POST /api/config/backup
Content-Type: application/json

{
  "name": "Weekly Backup",
  "description": "Automated weekly backup of all configurations"
}
```

#### List Backups
List all available backups.

```http
GET /api/config/backups
```

#### Restore Backup
Restore configuration from backup.

```http
POST /api/config/restore/{backup_id}
```

### Import/Export

#### Export Profiles
Export profiles to YAML or JSON format.

```http
POST /api/config/export
Content-Type: application/json

{
  "profile_ids": ["profile_123", "profile_456"],
  "include_history": false,
  "format": "yaml"
}
```

**Response:** Raw YAML or JSON data

#### Import Profiles
Import profiles from YAML or JSON data.

```http
POST /api/config/import
Content-Type: application/json

{
  "data": "name: Imported Profile\nconfig_data:\n  agent:\n    steps: 20",
  "merge_strategy": "create_new",
  "set_as_active": false
}
```

### Utility Endpoints

#### Sync Current Configuration
Sync current AIDE configuration with active profile.

```http
POST /api/config/sync
```

#### Get Statistics
Get statistics about profiles and usage.

```http
GET /api/config/statistics
```

#### Cleanup Old Data
Clean up old profile data and history.

```http
POST /api/config/cleanup
Content-Type: application/json

{
  "retention_days": 30
}
```

#### Get Template Categories
Get available template categories.

```http
GET /api/config/template-categories
```

#### Get Template Recommendations
Get template recommendations based on criteria.

```http
GET /api/config/template-recommendations?use_case=prototyping&complexity=beginner&budget=low
```

## Common Usage Patterns

### Setting Up a New Experiment

1. **Choose a Template**
   ```http
   GET /api/config/templates
   ```

2. **Apply Template**
   ```http
   POST /api/config/templates/quick_experiment/apply
   ```

3. **Create Profile from Current Config**
   ```http
   POST /api/config/profiles
   ```

4. **Activate Profile**
   ```http
   POST /api/config/profiles/{profile_id}/activate
   ```

### Comparing Different Approaches

1. **Create Multiple Profiles**
   ```http
   POST /api/config/profiles (for each approach)
   ```

2. **Compare Profiles**
   ```http
   GET /api/config/diff/profiles/{id1}/{id2}
   ```

3. **Analyze Results and Choose Best**

### Backup and Recovery

1. **Create Regular Backups**
   ```http
   POST /api/config/backup
   ```

2. **Export Important Profiles**
   ```http
   POST /api/config/export
   ```

3. **Restore When Needed**
   ```http
   POST /api/config/restore/{backup_id}
   ```

## Error Handling

All endpoints return standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (validation error, business logic error)
- `404`: Not Found (profile, template, or resource not found)
- `500`: Internal Server Error

Error responses follow this format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Data Models

### ConfigProfile
```json
{
  "id": "string",
  "name": "string",
  "description": "string | null",
  "config_data": "object",
  "tags": "string[]",
  "is_default": "boolean",
  "is_template": "boolean",
  "is_active": "boolean",
  "version": "number",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### ConfigTemplate
```json
{
  "name": "string",
  "display_name": "string",
  "description": "string",
  "category": "string",
  "config_data": "object",
  "use_case": "string | null",
  "estimated_cost": "string | null",
  "estimated_time": "string | null",
  "complexity": "string",
  "prerequisites": "string[]",
  "tags": "string[]",
  "is_builtin": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### ConfigHistory
```json
{
  "id": "string",
  "profile_id": "string | null",
  "config_data": "object",
  "change_description": "string",
  "changed_fields": "string[]",
  "user_action": "string",
  "previous_config": "object | null",
  "timestamp": "datetime"
}
```

## Built-in Templates

### Quick Experiment
- **Use Case**: Rapid prototyping, initial exploration
- **Cost**: $1-3
- **Time**: 5-10 minutes
- **Model**: GPT-3.5-turbo
- **Steps**: 5
- **Best For**: Quick baseline models, proof of concepts

### Cost Optimized
- **Use Case**: Budget-conscious projects
- **Cost**: $2-5
- **Time**: 10-20 minutes
- **Model**: GPT-3.5-turbo
- **Steps**: 10
- **Best For**: Educational purposes, small business applications

### Comprehensive Analysis
- **Use Case**: Production models, research
- **Cost**: $15-40
- **Time**: 45-90 minutes
- **Model**: GPT-4-turbo
- **Steps**: 30
- **Best For**: Competition submissions, enterprise applications

### Research Focused
- **Use Case**: Academic research, experimental studies
- **Cost**: $10-25
- **Time**: 30-60 minutes
- **Model**: GPT-4-turbo
- **Steps**: 25
- **Best For**: Publications, novel technique exploration

### Educational
- **Use Case**: Learning and teaching
- **Cost**: $5-12
- **Time**: 20-40 minutes
- **Model**: Mixed (GPT-4-turbo + GPT-3.5-turbo)
- **Steps**: 15
- **Best For**: Courses, tutorials, demonstrations

## Rate Limits

Currently, no rate limits are enforced. This may change in future versions.

## Versioning

This API is version 2.0.0. Future breaking changes will increment the major version number.

## Support

For issues and questions, please refer to the main AIDE ML documentation or create an issue in the project repository.