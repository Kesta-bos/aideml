# AIDE ML - Streamlit to React Migration Documentation

This documentation provides comprehensive guidance for migrating the AIDE ML application from Streamlit to a React-based frontend architecture.

## Overview

AIDE ML is currently a Streamlit-based web application that provides an AI-powered machine learning engineering agent. The application allows users to upload datasets, define goals and evaluation criteria, and automatically generates ML solutions through an iterative agent-based approach.

## Migration Goals

The migration aims to:
- **Separate Frontend and Backend**: Create a clear separation between the UI layer (React) and the ML processing backend
- **Improve User Experience**: Leverage React's component-based architecture for better interactivity and performance
- **Enable Scalability**: Allow for easier feature additions and maintenance
- **Modernize Tech Stack**: Move to a more modern, industry-standard frontend framework

## Documentation Structure

### 1. [Current Architecture Analysis](./01-current-architecture.md)
Detailed analysis of the existing Streamlit application including:
- Application entry points and routing
- UI components and functionality
- Data flow and state management
- API endpoints and data sources
- Dependencies and integrations

### 2. [Component Mapping](./02-component-mapping.md)
Comprehensive mapping between Streamlit and React components:
- Forms and input components
- Data visualization components
- Layout and navigation elements
- Interactive widgets and state handling

### 3. [Migration Strategy](./03-migration-strategy.md)
Step-by-step migration plan including:
- Recommended React frameworks and libraries
- Backend API design and requirements
- Data fetching and state management approach
- Styling and theming considerations
- Implementation phases and timeline

### 4. [Technical Specifications](./04-technical-specifications.md)
Technical implementation details:
- Data models and schemas
- Authentication and authorization
- Configuration and environment variables
- Build and deployment processes
- Testing strategies

### 5. [API Design](./05-api-design.md)
Backend API specifications for the React frontend:
- RESTful API endpoints
- WebSocket connections for real-time updates
- Data transfer objects and serialization
- Error handling and validation

### 6. [Implementation Examples](./06-implementation-examples.md)
Code examples and patterns:
- React component implementations
- API integration patterns
- State management examples
- Styling and theming examples

## Quick Start

1. **Review Current Architecture**: Start with [Current Architecture Analysis](./01-current-architecture.md) to understand the existing system
2. **Plan Component Migration**: Use [Component Mapping](./02-component-mapping.md) to identify React equivalents
3. **Follow Migration Strategy**: Implement according to [Migration Strategy](./03-migration-strategy.md)
4. **Reference Technical Specs**: Use [Technical Specifications](./04-technical-specifications.md) for implementation details

## Key Considerations

- **Backward Compatibility**: Ensure the new React frontend provides all functionality of the current Streamlit app
- **Real-time Updates**: Maintain the live progress tracking and result visualization capabilities
- **File Handling**: Preserve file upload and processing functionality
- **Visualization**: Ensure all charts, trees, and data displays work seamlessly
- **Configuration**: Maintain API key management and configuration options

## Migration Timeline

The migration is designed to be implemented in phases:
1. **Phase 1**: Backend API development and core React setup
2. **Phase 2**: Basic UI components and file handling
3. **Phase 3**: Real-time features and visualizations
4. **Phase 4**: Advanced features and optimization
5. **Phase 5**: Testing, deployment, and documentation

## Support and Resources

- **Codebase**: Located in `aide/webui/` for current Streamlit implementation
- **Configuration**: See `aide/utils/config.yaml` for current settings
- **Dependencies**: Review `requirements.txt` for current package requirements
- **Examples**: Check `aide/example_tasks/` for sample data and use cases

---

*This documentation is designed to facilitate a smooth transition from Streamlit to React while preserving all existing functionality and improving the overall user experience.*
