# Current Architecture Analysis

## Overview

AIDE ML is currently implemented as a Streamlit web application that provides an AI-powered machine learning engineering agent. The application follows a monolithic architecture where the UI, business logic, and ML processing are tightly integrated.

## Application Entry Points

### Main Entry Point
- **File**: `aide/webui/app.py`
- **Class**: `WebUI`
- **Launch**: `streamlit run app.py` (as documented in README.md)
- **Port**: Default Streamlit port (8501)

### CLI Entry Point
- **File**: `aide/run.py`
- **Function**: `run()`
- **Command**: `aide` (console script defined in setup.py)
- **Purpose**: Command-line interface for running experiments without UI

## Application Structure

### Core Components

#### 1. WebUI Class (`aide/webui/app.py`)
The main application controller that orchestrates the entire user interface:

```python
class WebUI:
    def __init__(self):
        self.env_vars = self.load_env_variables()
        self.project_root = Path(__file__).parent.parent.parent
        self.config_session_state()
        self.setup_page()
```

**Key Methods**:
- `run()`: Main application loop
- `render_sidebar()`: API key configuration
- `render_input_section()`: File upload and parameter input
- `run_aide()`: Execute ML experiments
- `render_live_results()`: Real-time result display

#### 2. Experiment Class (`aide/__init__.py`)
Core business logic for ML experiments:

```python
class Experiment:
    def __init__(self, data_dir: str, goal: str, eval: str | None = None)
    def run(self, steps: int) -> Solution
```

#### 3. Agent Class (`aide/agent.py`)
AI agent that generates and improves ML solutions:
- Implements search policy for solution exploration
- Handles code generation and debugging
- Manages solution evaluation and metrics

#### 4. Interpreter Class (`aide/interpreter.py`)
Code execution environment:
- Sandboxed Python execution
- Timeout management
- Error handling and traceback formatting

## UI Components and Layout

### Page Configuration
```python
st.set_page_config(
    page_title="AIDE: Machine Learning Engineer Agent",
    layout="wide",
)
```

### Layout Structure
1. **Sidebar**: API key configuration
   - OpenAI API Key input
   - Anthropic API Key input  
   - OpenRouter API Key input

2. **Main Area**: Two-column layout
   - **Input Column (1/4 width)**:
     - File upload section
     - Goal text area
     - Evaluation criteria text area
     - Number of steps slider
     - Run button
   - **Results Column (3/4 width)**:
     - Progress indicator
     - Configuration display
     - Live results with tabs

### Interactive Components

#### File Upload
- **Component**: `st.file_uploader`
- **Types**: Multiple file types supported (.csv, .json, .txt, etc.)
- **Features**: Multiple file selection, example data loading

#### Input Forms
- **Goal**: `st.text_area` for experiment objective
- **Evaluation**: `st.text_area` for success criteria
- **Steps**: `st.slider` for iteration count (1-20)

#### Results Display
- **Tabs**: Tree Visualization, Best Solution, Config, Journal, Validation Plot
- **Progress**: Real-time progress bar and step counter
- **Visualizations**: HTML components for tree plots

## Data Flow

### 1. User Input Flow
```
User Input → Session State → Experiment Configuration → Agent Execution
```

### 2. Experiment Execution Flow
```
File Upload → Data Preprocessing → Agent Initialization → 
Iterative Improvement → Result Collection → Visualization
```

### 3. Real-time Updates
```
Agent Step → Journal Update → Tree Export → UI Refresh → User Display
```

## State Management

### Streamlit Session State
The application uses Streamlit's session state for persistence:

```python
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "total_steps" not in st.session_state:
    st.session_state.total_steps = 0
if "progress" not in st.session_state:
    st.session_state.progress = 0
if "results" not in st.session_state:
    st.session_state.results = None
```

### Configuration Management
- **File**: `aide/utils/config.yaml`
- **Class**: `Config` dataclass
- **Scope**: Global application configuration
- **Environment**: API keys loaded from `.env` file

## API Endpoints and Data Sources

### External APIs
1. **OpenAI API**: GPT models for code generation
2. **Anthropic API**: Claude models for analysis
3. **OpenRouter API**: Alternative model access

### Internal Data Flow
- **No REST API**: Direct function calls between components
- **File System**: Local file operations for data and results
- **Memory**: In-process data sharing via Python objects

## Dependencies and Third-party Integrations

### Core Dependencies
- **streamlit==1.40.2**: Web framework
- **openai>=1.69.0**: OpenAI API client
- **anthropic>=0.20.0**: Anthropic API client
- **pandas==2.1.4**: Data manipulation
- **scikit-learn==1.5.0**: ML utilities
- **rich==13.7.0**: Terminal formatting

### ML/Data Science Stack
- **torch**: Deep learning framework
- **lightgbm**: Gradient boosting
- **matplotlib/seaborn**: Visualization
- **numpy/scipy**: Numerical computing

### Configuration and Utilities
- **omegaconf>=2.3.0**: Configuration management
- **dataclasses_json>=0.6.4**: Serialization
- **python-dotenv**: Environment variables

## File Structure and Organization

```
aide/
├── webui/
│   ├── app.py              # Main Streamlit application
│   └── style.css           # Custom CSS styling
├── agent.py                # AI agent implementation
├── interpreter.py          # Code execution environment
├── journal.py              # Experiment tracking
├── backend/                # API client implementations
├── utils/                  # Utility functions and config
└── example_tasks/          # Sample datasets
```

## Current Limitations

1. **Monolithic Architecture**: UI and business logic tightly coupled
2. **Single User**: No multi-user support or session isolation
3. **Limited Scalability**: Streamlit's single-threaded nature
4. **State Persistence**: Session state lost on page refresh
5. **Customization**: Limited UI customization options
6. **Real-time**: Polling-based updates, no WebSocket support

## Security Considerations

1. **API Keys**: Stored in session state (memory only)
2. **File Upload**: Temporary file handling
3. **Code Execution**: Sandboxed but local execution
4. **Environment**: No authentication or authorization layer
