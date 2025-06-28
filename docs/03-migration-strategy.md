# Migration Strategy: Streamlit to React

This document outlines a comprehensive strategy for migrating AIDE ML from Streamlit to a React-based frontend with a separate backend API.

## Migration Approach

### Architecture Transformation
```
Current: Monolithic Streamlit App
┌─────────────────────────────────┐
│     Streamlit Application       │
│  ┌─────────┐ ┌─────────────────┐│
│  │   UI    │ │  Business Logic ││
│  │         │ │                 ││
│  │         │ │   ML Engine     ││
│  └─────────┘ └─────────────────┘│
└─────────────────────────────────┘

Target: Separated Frontend/Backend
┌─────────────────┐    ┌─────────────────┐
│  React Frontend │    │  FastAPI Backend│
│                 │    │                 │
│  ┌─────────────┐│    │ ┌─────────────┐ │
│  │     UI      ││◄──►│ │ REST API    │ │
│  │ Components  ││    │ │             │ │
│  └─────────────┘│    │ └─────────────┘ │
│                 │    │ ┌─────────────┐ │
│                 │    │ │ ML Engine   │ │
│                 │    │ │             │ │
│                 │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘
```

## Recommended Technology Stack

### Frontend Stack
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite (faster than Create React App)
- **UI Library**: Ant Design (comprehensive, professional)
- **State Management**: Zustand (lightweight) + TanStack Query (server state)
- **Styling**: Tailwind CSS + Ant Design theme customization
- **File Upload**: react-dropzone
- **Code Display**: react-syntax-highlighter
- **Charts**: recharts + D3.js for custom visualizations
- **Real-time**: Socket.io-client for live updates

### Backend Stack
- **Framework**: FastAPI (Python, async, automatic OpenAPI docs)
- **WebSocket**: FastAPI WebSocket support
- **File Handling**: aiofiles for async file operations
- **Validation**: Pydantic models
- **CORS**: FastAPI CORS middleware
- **Authentication**: JWT tokens (future enhancement)

### Development Tools
- **Package Manager**: pnpm (faster than npm)
- **Linting**: ESLint + Prettier
- **Testing**: Vitest + React Testing Library
- **Type Checking**: TypeScript strict mode

## Implementation Phases

### Phase 1: Backend API Development (2-3 weeks)

#### 1.1 Project Setup
```bash
# Create new FastAPI project
mkdir aide-backend
cd aide-backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install fastapi uvicorn python-multipart aiofiles
```

#### 1.2 Core API Endpoints
- `POST /api/experiments` - Create new experiment
- `GET /api/experiments/{id}` - Get experiment status
- `POST /api/experiments/{id}/start` - Start experiment execution
- `GET /api/experiments/{id}/results` - Get experiment results
- `POST /api/upload` - File upload endpoint
- `WebSocket /ws/experiments/{id}` - Real-time updates

#### 1.3 Data Models Migration
Extract existing data models from Streamlit app:
- Experiment configuration
- Node/Journal structures
- Result formats
- File handling logic

### Phase 2: React Frontend Setup (1-2 weeks)

#### 2.1 Project Initialization
```bash
# Create React project with Vite
npm create vite@latest aide-frontend -- --template react-ts
cd aide-frontend
npm install

# Install dependencies
npm install antd @ant-design/icons
npm install zustand @tanstack/react-query
npm install axios socket.io-client
npm install react-syntax-highlighter react-dropzone
npm install @types/react-syntax-highlighter
```

#### 2.2 Project Structure
```
aide-frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── common/         # Generic components
│   │   ├── forms/          # Form components
│   │   └── visualizations/ # Chart/graph components
│   ├── pages/              # Page components
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API service functions
│   ├── stores/             # Zustand stores
│   ├── types/              # TypeScript type definitions
│   └── utils/              # Utility functions
├── public/
└── package.json
```

#### 2.3 Core Components Development
- Layout components (Header, Sidebar, Main)
- Form components (API keys, experiment config)
- File upload component
- Results display components

### Phase 3: API Integration (2-3 weeks)

#### 3.1 API Service Layer
```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.VITE_API_URL || 'http://localhost:8000',
});

export const experimentService = {
  create: (config: ExperimentConfig) => 
    api.post('/api/experiments', config),
  
  start: (id: string) => 
    api.post(`/api/experiments/${id}/start`),
  
  getResults: (id: string) => 
    api.get(`/api/experiments/${id}/results`),
};
```

#### 3.2 Real-time Integration
```typescript
// hooks/useExperimentSocket.ts
import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

export function useExperimentSocket(experimentId: string) {
  const [socket, setSocket] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const newSocket = io(`ws://localhost:8000/ws/experiments/${experimentId}`);
    
    newSocket.on('progress', (data) => {
      setProgress(data.progress);
      setCurrentStep(data.currentStep);
    });

    setSocket(newSocket);
    return () => newSocket.close();
  }, [experimentId]);

  return { socket, progress, currentStep };
}
```

#### 3.3 State Management
```typescript
// stores/experimentStore.ts
import { create } from 'zustand';

interface ExperimentState {
  currentExperiment: Experiment | null;
  isRunning: boolean;
  progress: number;
  results: ExperimentResults | null;
  
  // Actions
  setExperiment: (experiment: Experiment) => void;
  updateProgress: (progress: number) => void;
  setResults: (results: ExperimentResults) => void;
}

export const useExperimentStore = create<ExperimentState>((set) => ({
  currentExperiment: null,
  isRunning: false,
  progress: 0,
  results: null,
  
  setExperiment: (experiment) => set({ currentExperiment: experiment }),
  updateProgress: (progress) => set({ progress }),
  setResults: (results) => set({ results }),
}));
```

### Phase 4: Advanced Features (2-3 weeks)

#### 4.1 Visualization Migration
- Tree visualization component using D3.js
- Chart components using recharts
- Code syntax highlighting
- Progress indicators and metrics

#### 4.2 File Handling
- Drag-and-drop file upload
- File preview functionality
- Progress tracking for uploads
- Error handling and validation

#### 4.3 Configuration Management
- Environment-based configuration
- API key management
- User preferences storage

### Phase 5: Testing and Deployment (1-2 weeks)

#### 5.1 Testing Strategy
```typescript
// __tests__/components/ExperimentForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ExperimentForm } from '../components/ExperimentForm';

test('submits experiment with valid data', async () => {
  render(<ExperimentForm onSubmit={mockSubmit} />);
  
  fireEvent.change(screen.getByLabelText('Goal'), {
    target: { value: 'Predict house prices' }
  });
  
  fireEvent.click(screen.getByText('Run AIDE'));
  
  expect(mockSubmit).toHaveBeenCalledWith({
    goal: 'Predict house prices',
    // ...
  });
});
```

#### 5.2 Deployment Configuration
```dockerfile
# Frontend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Migration Timeline

### Week 1-2: Backend Foundation
- [ ] FastAPI project setup
- [ ] Core API endpoints
- [ ] Data model migration
- [ ] File upload handling

### Week 3-4: React Frontend Setup
- [ ] React project initialization
- [ ] Component library setup
- [ ] Basic layout components
- [ ] Form components

### Week 5-6: API Integration
- [ ] API service layer
- [ ] State management setup
- [ ] Real-time WebSocket integration
- [ ] Error handling

### Week 7-8: Advanced Features
- [ ] Visualization components
- [ ] File handling improvements
- [ ] Configuration management
- [ ] Performance optimization

### Week 9-10: Testing and Deployment
- [ ] Unit and integration tests
- [ ] End-to-end testing
- [ ] Docker containerization
- [ ] Deployment setup

## Risk Mitigation

### Technical Risks
1. **Complex Visualizations**: Start with simpler charts, gradually migrate complex tree visualizations
2. **Real-time Updates**: Implement polling fallback if WebSocket issues arise
3. **File Upload**: Use chunked uploads for large files
4. **State Synchronization**: Implement proper error boundaries and retry logic

### Business Risks
1. **Feature Parity**: Maintain detailed checklist of current features
2. **User Experience**: Conduct user testing during migration
3. **Performance**: Monitor and optimize bundle size and API response times
4. **Rollback Plan**: Keep Streamlit version available during transition

## Success Metrics

### Technical Metrics
- [ ] All current features migrated
- [ ] Page load time < 3 seconds
- [ ] API response time < 500ms
- [ ] 95%+ uptime
- [ ] Zero data loss during experiments

### User Experience Metrics
- [ ] Improved user satisfaction scores
- [ ] Reduced time to complete experiments
- [ ] Better mobile responsiveness
- [ ] Enhanced accessibility compliance

## Post-Migration Enhancements

### Immediate (Month 1)
- User authentication and sessions
- Experiment history and management
- Enhanced error reporting
- Mobile optimization

### Medium-term (Months 2-3)
- Multi-user support
- Experiment sharing and collaboration
- Advanced visualization options
- Performance monitoring

### Long-term (Months 4-6)
- Plugin architecture for custom models
- Advanced experiment scheduling
- Integration with external data sources
- Machine learning pipeline automation
