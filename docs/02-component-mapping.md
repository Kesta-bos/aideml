# Component Mapping: Streamlit to React

This document provides a comprehensive mapping of Streamlit components used in AIDE ML to their React equivalents, including recommended libraries and implementation patterns.

## Layout and Structure Components

### Page Configuration
**Streamlit**:
```python
st.set_page_config(
    page_title="AIDE: Machine Learning Engineer Agent",
    layout="wide",
)
```

**React Equivalent**:
```jsx
// Using React Helmet for head management
import { Helmet } from 'react-helmet';

function App() {
  return (
    <>
      <Helmet>
        <title>AIDE: Machine Learning Engineer Agent</title>
      </Helmet>
      <div className="app-container">
        {/* App content */}
      </div>
    </>
  );
}
```

### Columns Layout
**Streamlit**:
```python
input_col, results_col = st.columns([1, 3])
with input_col:
    # Input components
with results_col:
    # Results components
```

**React Equivalent**:
```jsx
// Using CSS Grid or Flexbox
function MainLayout() {
  return (
    <div className="main-layout">
      <div className="input-column">
        {/* Input components */}
      </div>
      <div className="results-column">
        {/* Results components */}
      </div>
    </div>
  );
}

// CSS
.main-layout {
  display: grid;
  grid-template-columns: 1fr 3fr;
  gap: 1rem;
}
```

### Sidebar
**Streamlit**:
```python
with st.sidebar:
    st.header("⚙️ Settings")
    # Sidebar content
```

**React Equivalent**:
```jsx
// Using a sidebar component library like Ant Design or custom
import { Layout } from 'antd';
const { Sider } = Layout;

function AppLayout() {
  return (
    <Layout>
      <Sider width={300}>
        <h2>⚙️ Settings</h2>
        {/* Sidebar content */}
      </Sider>
      <Layout.Content>
        {/* Main content */}
      </Layout.Content>
    </Layout>
  );
}
```

## Input Components

### Text Input (API Keys)
**Streamlit**:
```python
openai_key = st.text_input(
    "OpenAI API Key",
    value=self.env_vars["openai_key"],
    type="password",
    label_visibility="collapsed",
)
```

**React Equivalent**:
```jsx
// Using Ant Design Input
import { Input } from 'antd';

function ApiKeyInput({ label, value, onChange }) {
  return (
    <div className="api-key-input">
      <label>{label}</label>
      <Input.Password
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={`Enter ${label}`}
      />
    </div>
  );
}
```

### Text Area
**Streamlit**:
```python
goal_text = st.text_area(
    "Goal",
    value=st.session_state.get("goal", ""),
    placeholder="Example: Predict the sales price for each house",
)
```

**React Equivalent**:
```jsx
// Using Ant Design Input
import { Input } from 'antd';
const { TextArea } = Input;

function GoalInput({ value, onChange }) {
  return (
    <div className="goal-input">
      <label>Goal</label>
      <TextArea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Example: Predict the sales price for each house"
        rows={4}
      />
    </div>
  );
}
```

### Slider
**Streamlit**:
```python
num_steps = st.slider(
    "Number of Steps",
    min_value=1,
    max_value=20,
    value=st.session_state.get("steps", 10),
)
```

**React Equivalent**:
```jsx
// Using Ant Design Slider
import { Slider } from 'antd';

function StepsSlider({ value, onChange }) {
  return (
    <div className="steps-slider">
      <label>Number of Steps: {value}</label>
      <Slider
        min={1}
        max={20}
        value={value}
        onChange={onChange}
        marks={{
          1: '1',
          10: '10',
          20: '20'
        }}
      />
    </div>
  );
}
```

### File Upload
**Streamlit**:
```python
uploaded_files = st.file_uploader(
    "Upload your dataset",
    accept_multiple_files=True,
    type=["csv", "json", "txt", "zip"],
)
```

**React Equivalent**:
```jsx
// Using Ant Design Upload
import { Upload, Button } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

function FileUploader({ onFilesChange }) {
  const props = {
    multiple: true,
    accept: '.csv,.json,.txt,.zip',
    beforeUpload: (file) => {
      // Handle file validation
      return false; // Prevent auto upload
    },
    onChange: (info) => {
      onFilesChange(info.fileList);
    },
  };

  return (
    <Upload {...props}>
      <Button icon={<UploadOutlined />}>
        Upload Dataset
      </Button>
    </Upload>
  );
}
```

## Display Components

### Headers and Text
**Streamlit**:
```python
st.header("Input")
st.markdown("### 🔥 Running Step 1/10")
```

**React Equivalent**:
```jsx
// Using standard HTML elements or Ant Design Typography
import { Typography } from 'antd';
const { Title, Text } = Typography;

function Headers() {
  return (
    <>
      <Title level={2}>Input</Title>
      <Title level={3}>🔥 Running Step 1/10</Title>
    </>
  );
}
```

### Progress Bar
**Streamlit**:
```python
st.progress(progress)
```

**React Equivalent**:
```jsx
// Using Ant Design Progress
import { Progress } from 'antd';

function ProgressBar({ percent, status = "active" }) {
  return (
    <Progress
      percent={percent}
      status={status}
      strokeColor={{
        '0%': '#108ee9',
        '100%': '#87d068',
      }}
    />
  );
}
```

### Code Display
**Streamlit**:
```python
st.code(solution_code, language="python")
st.code(results["config"], language="yaml")
```

**React Equivalent**:
```jsx
// Using react-syntax-highlighter
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

function CodeDisplay({ code, language = "python" }) {
  return (
    <SyntaxHighlighter
      language={language}
      style={docco}
      customStyle={{
        maxHeight: '400px',
        overflow: 'auto'
      }}
    >
      {code}
    </SyntaxHighlighter>
  );
}
```

### Metrics Display
**Streamlit**:
```python
st.metric("Best Validation Score", f"{best_metric:.4f}")
```

**React Equivalent**:
```jsx
// Using Ant Design Statistic
import { Statistic } from 'antd';

function MetricDisplay({ title, value, precision = 4 }) {
  return (
    <Statistic
      title={title}
      value={value}
      precision={precision}
      valueStyle={{ color: '#3f8600' }}
    />
  );
}
```

## Interactive Components

### Buttons
**Streamlit**:
```python
if st.button("Run AIDE", type="primary", use_container_width=True):
    # Handle click
```

**React Equivalent**:
```jsx
// Using Ant Design Button
import { Button } from 'antd';

function RunButton({ onClick, loading = false }) {
  return (
    <Button
      type="primary"
      size="large"
      block
      loading={loading}
      onClick={onClick}
    >
      Run AIDE
    </Button>
  );
}
```

### Tabs
**Streamlit**:
```python
tabs = st.tabs([
    "Tree Visualization",
    "Best Solution", 
    "Config",
    "Journal",
    "Validation Plot",
])

with tabs[0]:
    self.render_tree_visualization(results)
with tabs[1]:
    self.render_best_solution(results)
```

**React Equivalent**:
```jsx
// Using Ant Design Tabs
import { Tabs } from 'antd';

function ResultsTabs({ results }) {
  const items = [
    {
      key: 'tree',
      label: 'Tree Visualization',
      children: <TreeVisualization data={results.tree} />,
    },
    {
      key: 'solution',
      label: 'Best Solution',
      children: <BestSolution code={results.solution} />,
    },
    {
      key: 'config',
      label: 'Config',
      children: <ConfigDisplay config={results.config} />,
    },
    {
      key: 'journal',
      label: 'Journal',
      children: <Journal data={results.journal} />,
    },
    {
      key: 'validation',
      label: 'Validation Plot',
      children: <ValidationPlot data={results.validation} />,
    },
  ];

  return <Tabs items={items} />;
}
```

## Visualization Components

### HTML Components (Tree Visualization)
**Streamlit**:
```python
import streamlit.components.v1 as components
components.html(html_content, height=600, scrolling=True)
```

**React Equivalent**:
```jsx
// Using dangerouslySetInnerHTML or iframe
function TreeVisualization({ htmlContent }) {
  return (
    <div 
      className="tree-visualization"
      style={{ height: '600px', overflow: 'auto' }}
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  );
}

// Alternative: Using iframe for better isolation
function TreeVisualizationIframe({ htmlContent }) {
  const srcDoc = htmlContent;
  
  return (
    <iframe
      srcDoc={srcDoc}
      style={{ 
        width: '100%', 
        height: '600px', 
        border: 'none' 
      }}
      title="Tree Visualization"
    />
  );
}
```

## State Management Mapping

### Session State
**Streamlit**:
```python
if "is_running" not in st.session_state:
    st.session_state.is_running = False
st.session_state.current_step = step + 1
```

**React Equivalent**:
```jsx
// Using React Context + useReducer or Zustand
import { create } from 'zustand';

const useAppStore = create((set) => ({
  isRunning: false,
  currentStep: 0,
  totalSteps: 0,
  progress: 0,
  results: null,
  
  setRunning: (running) => set({ isRunning: running }),
  setCurrentStep: (step) => set({ currentStep: step }),
  setResults: (results) => set({ results }),
  
  // Actions
  startExperiment: (totalSteps) => set({ 
    isRunning: true, 
    currentStep: 0, 
    totalSteps,
    progress: 0 
  }),
  
  updateProgress: (step) => set((state) => ({ 
    currentStep: step,
    progress: step / state.totalSteps 
  })),
}));
```

## Recommended React Libraries

### UI Component Library
- **Ant Design**: Comprehensive component library with excellent TypeScript support
- **Material-UI**: Google's Material Design implementation
- **Chakra UI**: Simple and modular component library

### State Management
- **Zustand**: Lightweight state management
- **Redux Toolkit**: For complex state management
- **React Query/TanStack Query**: For server state management

### Visualization
- **react-syntax-highlighter**: Code syntax highlighting
- **recharts**: Chart library for React
- **D3.js**: For custom visualizations

### File Handling
- **react-dropzone**: Enhanced file upload experience
- **file-saver**: File download functionality

### Real-time Communication
- **Socket.io-client**: WebSocket communication
- **EventSource**: Server-sent events for live updates
