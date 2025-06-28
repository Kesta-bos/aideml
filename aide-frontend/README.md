# AIDE ML Frontend

React-based frontend for the AIDE Machine Learning Engineer Agent.

## Features

- **Modern React Stack**: React 18 + TypeScript + Vite
- **UI Components**: Ant Design component library with custom styling
- **State Management**: Zustand for global state management
- **API Integration**: Axios with React Query for server state
- **Real-time Updates**: Socket.io for live experiment progress
- **Configuration Management**: Advanced settings UI with validation
- **Profile Management**: Save and manage configuration profiles
- **Template System**: Pre-configured templates for different use cases
- **Responsive Design**: Mobile-friendly interface with adaptive layouts
- **Code Highlighting**: Syntax highlighting for generated code
- **File Upload**: Drag-and-drop file upload with validation
- **Theme Support**: Customizable themes and dark mode (planned)

## Quick Start

### Development Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your API configuration
   ```

3. **Start Development Server**:
   ```bash
   npm run dev
   ```

4. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000 (must be running)

### Docker Setup

1. **Build Image**:
   ```bash
   docker build -t aide-frontend .
   ```

2. **Run Container**:
   ```bash
   docker run -p 80:80 aide-frontend
   ```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run test` - Run tests
- `npm run type-check` - TypeScript type checking

## Project Structure

```
aide-frontend/
├── src/
│   ├── components/          # React components
│   │   ├── experiment/     # Experiment-related components
│   │   ├── layout/         # Layout components
│   │   ├── results/        # Results display components
│   │   └── settings/       # Settings & configuration components
│   │       ├── ConfigPreview.tsx      # Configuration preview
│   │       ├── DynamicConfigForm.tsx  # Dynamic form generator
│   │       ├── ModelSelector.tsx      # AI model selection
│   │       ├── ProfileCard.tsx        # Profile display card
│   │       ├── ProfileComparison.tsx  # Profile comparison modal
│   │       ├── QuickActions.tsx       # Quick action buttons
│   │       ├── SettingsSidebar.tsx    # Settings navigation
│   │       ├── TemplateGallery.tsx    # Configuration templates
│   │       └── ValidationPanel.tsx    # Validation feedback
│   ├── pages/              # Page components
│   │   ├── SettingsPage.tsx          # Main settings interface
│   │   └── ProfileManagementPage.tsx # Profile management
│   ├── services/           # API service functions
│   │   └── configAPI.ts    # Configuration API client
│   ├── stores/             # Zustand state stores
│   │   └── configStore.ts  # Configuration state management
│   ├── types/              # TypeScript type definitions
│   │   └── config.ts       # Configuration-related types
│   ├── styles/             # Styling files
│   │   └── settings.scss   # Settings page styles
│   ├── config/             # Configuration files
│   └── test/               # Test utilities
├── public/                 # Static assets
└── package.json
```

## Key Components

### Layout
- `AppLayout` - Main application layout with header and navigation
- `ApiKeySettings` - API key configuration drawer

### Configuration Management
- `SettingsPage` - Main configuration interface with categories
- `DynamicConfigForm` - Auto-generating forms based on configuration schema
- `ConfigPreview` - Real-time configuration preview panel
- `ValidationPanel` - Real-time validation with error feedback
- `SettingsSidebar` - Category navigation with profile selector

### Profile Management
- `ProfileManagementPage` - Comprehensive profile management interface
- `ProfileCard` - Individual profile display with actions
- `ProfileComparison` - Side-by-side profile comparison modal
- `TemplateGallery` - Pre-configured template showcase

### Model & Resource Selection
- `ModelSelector` - Advanced AI model selection with provider grouping
- `FolderSelector` - File system browser for directory selection

### State Management
- `configStore` - Configuration and profile state with Zustand
- `experimentStore` - Global experiment state with Zustand
- React Query for server state management and caching

### API Integration
- `configAPI` - Configuration CRUD, validation, and template operations
- `experimentAPI` - Experiment CRUD operations
- `fileAPI` - File upload and management

## Environment Variables

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Development Configuration  
VITE_NODE_ENV=development

# Optional: Enable detailed logging
VITE_DEBUG=false
```

## Configuration Management Features

### Advanced Settings Interface
- **Category-based Organization**: Settings organized into logical categories (Project, Agent, Models, etc.)
- **Real-time Validation**: Instant feedback with field-level validation
- **Dynamic Forms**: Auto-generating forms based on backend schema
- **Live Preview**: Real-time configuration preview with impact analysis

### Profile Management
- **Save & Load Profiles**: Create and manage multiple configuration profiles
- **Profile Comparison**: Side-by-side comparison of different profiles
- **Template System**: Pre-configured templates for common use cases
- **Profile Metadata**: Tags, descriptions, and categorization

### Template Gallery
- **Quick Experiment**: Fast prototyping with minimal iterations
- **Comprehensive Analysis**: Thorough exploration with extensive search
- **Cost Optimized**: Budget-friendly configuration for cost control
- **Educational**: Learning-focused with detailed explanations
- **Research Focused**: Advanced research methodologies

### Model Management
- **Provider Support**: OpenAI, Anthropic, and OpenRouter integration
- **Model Discovery**: Automatic detection of available models
- **Compatibility Checking**: Validate model and API key combinations
- **Cost Estimation**: Predict experiment costs based on model pricing

## Integration with Backend

The frontend communicates with the FastAPI backend through:

- **REST API**: Standard CRUD operations for experiments and files
- **WebSocket**: Real-time updates during experiment execution
- **File Upload**: Multipart form data for dataset uploads

## Development Notes

- Uses Vite for fast development and building
- TypeScript for type safety
- Ant Design for consistent UI components
- Zustand for lightweight state management
- React Query for server state caching
- Socket.io for real-time communication

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Code splitting for optimal bundle sizes
- Lazy loading of components
- Image optimization
- Gzip compression in production
- Service worker caching (planned)
