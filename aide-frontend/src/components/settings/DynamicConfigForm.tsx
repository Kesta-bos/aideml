/**
 * Dynamic Configuration Form Component
 * Renders form fields based on configuration category and schema
 */

import React, { useMemo, useCallback } from 'react';
import {
  Form,
  Input,
  InputNumber,
  Switch,
  Select,
  Slider,
  Button,
  Typography,
  Space,
  Tooltip,
  Row,
  Col,
  Card,
  Divider,
} from 'antd';
import {
  FolderOpenOutlined,
  FileTextOutlined,
  InfoCircleOutlined,
  BrainOutlined,
} from '@ant-design/icons';
import { debounce } from 'lodash';

import { ConfigCategory, ConfigSchema, ModelProvider } from '@/types/config';
import { useConfigStore, useConfigModels, useConfigValidation } from '@/stores/configStore';
import { ModelSelector } from './ModelSelector';
import { FolderSelector } from './FolderSelector';

const { Text, Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

interface DynamicConfigFormProps {
  category: ConfigCategory;
  config: ConfigSchema | null;
  onChange: (updates: Record<string, any>) => void;
  loading?: boolean;
}

export function DynamicConfigForm({ 
  category, 
  config, 
  onChange,
  loading = false 
}: DynamicConfigFormProps) {
  const [form] = Form.useForm();
  const { validateField } = useConfigStore();
  const { fieldValidations } = useConfigValidation();
  const { availableModels } = useConfigModels();

  // Debounced validation function
  const debouncedValidateField = useMemo(
    () => debounce((field: string, value: any) => {
      validateField(field, value);
    }, 300),
    [validateField]
  );

  // Handle field changes
  const handleFieldChange = useCallback((field: string, value: any) => {
    // Update the configuration
    const updates = { [field]: value };
    onChange(updates);

    // Trigger validation
    debouncedValidateField(field, value);
  }, [onChange, debouncedValidateField]);

  // Get validation status for a field
  const getFieldValidation = (field: string) => {
    const validation = fieldValidations[field];
    if (!validation) return {};

    return {
      validateStatus: validation.valid ? 'success' : 'error',
      help: validation.valid ? undefined : validation.errors[0]?.message,
    };
  };

  // Render form fields based on category
  const renderFormFields = () => {
    if (!config) return null;

    switch (category) {
      case ConfigCategory.PROJECT:
        return renderProjectFields();
      case ConfigCategory.AGENT:
        return renderAgentFields();
      case ConfigCategory.EXECUTION:
        return renderExecutionFields();
      case ConfigCategory.MODELS:
        return renderModelsFields();
      case ConfigCategory.SEARCH:
        return renderSearchFields();
      case ConfigCategory.REPORTING:
        return renderReportingFields();
      default:
        return null;
    }
  };

  const renderProjectFields = () => (
    <>
      <Title level={4}>Project Configuration</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: '24px' }}>
        Define your project data sources, goals, and evaluation criteria.
      </Text>

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Form.Item
            label={
              <Space>
                Data Directory
                <Tooltip title="Path to the directory containing your dataset">
                  <InfoCircleOutlined />
                </Tooltip>
              </Space>
            }
            {...getFieldValidation('data_dir')}
          >
            <FolderSelector
              value={config.data_dir}
              onChange={(value) => handleFieldChange('data_dir', value)}
              placeholder="Select data directory..."
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item
            label={
              <Space>
                Description File
                <Tooltip title="Optional task description file (markdown supported)">
                  <InfoCircleOutlined />
                </Tooltip>
              </Space>
            }
            {...getFieldValidation('desc_file')}
          >
            <Input
              value={config.desc_file}
              onChange={(e) => handleFieldChange('desc_file', e.target.value)}
              placeholder="path/to/description.md"
              suffix={<FileTextOutlined />}
            />
          </Form.Item>
        </Col>
      </Row>

      <Form.Item
        label={
          <Space>
            Task Goal
            <Tooltip title="Describe what you want the AI agent to accomplish">
              <InfoCircleOutlined />
            </Tooltip>
          </Space>
        }
        {...getFieldValidation('goal')}
      >
        <TextArea
          value={config.goal}
          onChange={(e) => handleFieldChange('goal', e.target.value)}
          placeholder="e.g., Predict house prices using machine learning"
          rows={3}
        />
      </Form.Item>

      <Form.Item
        label={
          <Space>
            Evaluation Criteria
            <Tooltip title="How should the model performance be evaluated?">
              <InfoCircleOutlined />
            </Tooltip>
          </Space>
        }
        {...getFieldValidation('eval')}
      >
        <TextArea
          value={config.eval}
          onChange={(e) => handleFieldChange('eval', e.target.value)}
          placeholder="e.g., Mean absolute error on test set"
          rows={2}
        />
      </Form.Item>

      <Divider />

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Form.Item
            label="Log Directory"
            {...getFieldValidation('log_dir')}
          >
            <Input
              value={config.log_dir}
              onChange={(e) => handleFieldChange('log_dir', e.target.value)}
              placeholder="logs"
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item
            label="Workspace Directory"
            {...getFieldValidation('workspace_dir')}
          >
            <Input
              value={config.workspace_dir}
              onChange={(e) => handleFieldChange('workspace_dir', e.target.value)}
              placeholder="workspaces"
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Form.Item label="Preprocess Data" valuePropName="checked">
            <Switch
              checked={config.preprocess_data}
              onChange={(checked) => handleFieldChange('preprocess_data', checked)}
            />
            <Text type="secondary" style={{ display: 'block', fontSize: '12px' }}>
              Automatically extract archives in data directory
            </Text>
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item label="Copy Data" valuePropName="checked">
            <Switch
              checked={config.copy_data}
              onChange={(checked) => handleFieldChange('copy_data', checked)}
            />
            <Text type="secondary" style={{ display: 'block', fontSize: '12px' }}>
              Copy data to workspace instead of symlinking
            </Text>
          </Form.Item>
        </Col>
      </Row>

      <Form.Item
        label="Experiment Name"
        {...getFieldValidation('exp_name')}
      >
        <Input
          value={config.exp_name}
          onChange={(e) => handleFieldChange('exp_name', e.target.value)}
          placeholder="Auto-generated if empty"
        />
      </Form.Item>
    </>
  );

  const renderAgentFields = () => (
    <>
      <Title level={4}>Agent Behavior Configuration</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: '24px' }}>
        Control how the AI agent explores solutions and iterates on improvements.
      </Text>

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Form.Item
            label={
              <Space>
                Improvement Steps
                <Tooltip title="Number of iterations for solution improvement">
                  <InfoCircleOutlined />
                </Tooltip>
              </Space>
            }
            {...getFieldValidation('agent.steps')}
          >
            <Slider
              min={1}
              max={100}
              value={config.agent.steps}
              onChange={(value) => handleFieldChange('agent.steps', value)}
              marks={{
                1: '1',
                20: '20',
                50: '50',
                100: '100'
              }}
            />
            <InputNumber
              min={1}
              max={100}
              value={config.agent.steps}
              onChange={(value) => handleFieldChange('agent.steps', value)}
              style={{ width: '100%', marginTop: '8px' }}
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item
            label={
              <Space>
                K-Fold Validation
                <Tooltip title="Number of cross-validation folds">
                  <InfoCircleOutlined />
                </Tooltip>
              </Space>
            }
            {...getFieldValidation('agent.k_fold_validation')}
          >
            <Select
              value={config.agent.k_fold_validation}
              onChange={(value) => handleFieldChange('agent.k_fold_validation', value)}
            >
              {[1, 3, 5, 10].map(val => (
                <Option key={val} value={val}>{val}-fold</Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Form.Item label="Expose Prediction Function" valuePropName="checked">
            <Switch
              checked={config.agent.expose_prediction}
              onChange={(checked) => handleFieldChange('agent.expose_prediction', checked)}
            />
            <Text type="secondary" style={{ display: 'block', fontSize: '12px' }}>
              Generate a standalone prediction function
            </Text>
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item label="Data Preview" valuePropName="checked">
            <Switch
              checked={config.agent.data_preview}
              onChange={(checked) => handleFieldChange('agent.data_preview', checked)}
            />
            <Text type="secondary" style={{ display: 'block', fontSize: '12px' }}>
              Provide data overview to the agent
            </Text>
          </Form.Item>
        </Col>
      </Row>

      <Divider>Model Configuration</Divider>

      <Card title="Code Generation Model" size="small" style={{ marginBottom: '16px' }}>
        <Row gutter={16}>
          <Col xs={24} md={16}>
            <Form.Item label="Model" {...getFieldValidation('agent.code.model')}>
              <ModelSelector
                value={config.agent.code.model}
                onChange={(value) => handleFieldChange('agent.code.model', value)}
                availableModels={availableModels}
              />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item
              label="Temperature"
              {...getFieldValidation('agent.code.temp')}
            >
              <Slider
                min={0}
                max={2}
                step={0.1}
                value={config.agent.code.temp}
                onChange={(value) => handleFieldChange('agent.code.temp', value)}
                marks={{
                  0: '0',
                  0.5: '0.5',
                  1: '1',
                  1.5: '1.5',
                  2: '2'
                }}
              />
              <InputNumber
                min={0}
                max={2}
                step={0.1}
                value={config.agent.code.temp}
                onChange={(value) => handleFieldChange('agent.code.temp', value)}
                style={{ width: '100%', marginTop: '8px' }}
              />
            </Form.Item>
          </Col>
        </Row>
      </Card>

      <Card title="Feedback Evaluation Model" size="small">
        <Row gutter={16}>
          <Col xs={24} md={16}>
            <Form.Item label="Model" {...getFieldValidation('agent.feedback.model')}>
              <ModelSelector
                value={config.agent.feedback.model}
                onChange={(value) => handleFieldChange('agent.feedback.model', value)}
                availableModels={availableModels}
              />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item
              label="Temperature"
              {...getFieldValidation('agent.feedback.temp')}
            >
              <Slider
                min={0}
                max={2}
                step={0.1}
                value={config.agent.feedback.temp}
                onChange={(value) => handleFieldChange('agent.feedback.temp', value)}
                marks={{
                  0: '0',
                  0.5: '0.5',
                  1: '1',
                  1.5: '1.5',
                  2: '2'
                }}
              />
              <InputNumber
                min={0}
                max={2}
                step={0.1}
                value={config.agent.feedback.temp}
                onChange={(value) => handleFieldChange('agent.feedback.temp', value)}
                style={{ width: '100%', marginTop: '8px' }}
              />
            </Form.Item>
          </Col>
        </Row>
      </Card>
    </>
  );

  const renderExecutionFields = () => (
    <>
      <Title level={4}>Execution Environment</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: '24px' }}>
        Configure the runtime environment for code execution.
      </Text>

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Form.Item
            label={
              <Space>
                Execution Timeout (seconds)
                <Tooltip title="Maximum time allowed for code execution">
                  <InfoCircleOutlined />
                </Tooltip>
              </Space>
            }
            {...getFieldValidation('exec.timeout')}
          >
            <Slider
              min={60}
              max={7200}
              value={config.exec.timeout}
              onChange={(value) => handleFieldChange('exec.timeout', value)}
              marks={{
                60: '1m',
                1800: '30m',
                3600: '1h',
                7200: '2h'
              }}
            />
            <InputNumber
              min={60}
              max={7200}
              value={config.exec.timeout}
              onChange={(value) => handleFieldChange('exec.timeout', value)}
              style={{ width: '100%', marginTop: '8px' }}
              formatter={value => `${value}s`}
              parser={value => parseInt(value?.replace('s', '') || '3600')}
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item
            label="Agent Script Filename"
            {...getFieldValidation('exec.agent_file_name')}
          >
            <Input
              value={config.exec.agent_file_name}
              onChange={(e) => handleFieldChange('exec.agent_file_name', e.target.value)}
              placeholder="runfile.py"
            />
          </Form.Item>
        </Col>
      </Row>

      <Form.Item label="IPython Traceback Formatting" valuePropName="checked">
        <Switch
          checked={config.exec.format_tb_ipython}
          onChange={(checked) => handleFieldChange('exec.format_tb_ipython', checked)}
        />
        <Text type="secondary" style={{ display: 'block', fontSize: '12px' }}>
          Use IPython-style traceback formatting for better readability
        </Text>
      </Form.Item>
    </>
  );

  const renderModelsFields = () => (
    <>
      <Title level={4}>AI Model Configuration</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: '24px' }}>
        Configure AI models and providers for different tasks.
      </Text>

      <Card title="Code Generation Model" size="small" style={{ marginBottom: '16px' }}>
        <ModelSelector
          value={config.agent.code.model}
          onChange={(value) => handleFieldChange('agent.code.model', value)}
          availableModels={availableModels}
          showDetails
        />
      </Card>

      <Card title="Feedback Model" size="small" style={{ marginBottom: '16px' }}>
        <ModelSelector
          value={config.agent.feedback.model}
          onChange={(value) => handleFieldChange('agent.feedback.model', value)}
          availableModels={availableModels}
          showDetails
        />
      </Card>

      <Card title="Report Generation Model" size="small">
        <ModelSelector
          value={config.report.model}
          onChange={(value) => handleFieldChange('report.model', value)}
          availableModels={availableModels}
          showDetails
        />
      </Card>
    </>
  );

  const renderSearchFields = () => (
    <>
      <Title level={4}>Tree Search Configuration</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: '24px' }}>
        Control the solution exploration algorithm parameters.
      </Text>

      <Row gutter={16}>
        <Col xs={24} md={8}>
          <Form.Item
            label={
              <Space>
                Max Debug Depth
                <Tooltip title="Maximum debugging attempts per solution">
                  <InfoCircleOutlined />
                </Tooltip>
              </Space>
            }
            {...getFieldValidation('agent.search.max_debug_depth')}
          >
            <Slider
              min={1}
              max={10}
              value={config.agent.search.max_debug_depth}
              onChange={(value) => handleFieldChange('agent.search.max_debug_depth', value)}
              marks={{
                1: '1',
                3: '3',
                5: '5',
                10: '10'
              }}
            />
            <InputNumber
              min={1}
              max={10}
              value={config.agent.search.max_debug_depth}
              onChange={(value) => handleFieldChange('agent.search.max_debug_depth', value)}
              style={{ width: '100%', marginTop: '8px' }}
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={8}>
          <Form.Item
            label={
              <Space>
                Debug Probability
                <Tooltip title="Probability of debugging vs creating new solution">
                  <InfoCircleOutlined />
                </Tooltip>
              </Space>
            }
            {...getFieldValidation('agent.search.debug_prob')}
          >
            <Slider
              min={0}
              max={1}
              step={0.1}
              value={config.agent.search.debug_prob}
              onChange={(value) => handleFieldChange('agent.search.debug_prob', value)}
              marks={{
                0: '0%',
                0.5: '50%',
                1: '100%'
              }}
            />
            <InputNumber
              min={0}
              max={1}
              step={0.1}
              value={config.agent.search.debug_prob}
              onChange={(value) => handleFieldChange('agent.search.debug_prob', value)}
              style={{ width: '100%', marginTop: '8px' }}
              formatter={value => `${Math.round((value || 0) * 100)}%`}
              parser={value => parseFloat(value?.replace('%', '') || '0') / 100}
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={8}>
          <Form.Item
            label={
              <Space>
                Initial Drafts
                <Tooltip title="Number of initial solution drafts to generate">
                  <InfoCircleOutlined />
                </Tooltip>
              </Space>
            }
            {...getFieldValidation('agent.search.num_drafts')}
          >
            <Slider
              min={1}
              max={20}
              value={config.agent.search.num_drafts}
              onChange={(value) => handleFieldChange('agent.search.num_drafts', value)}
              marks={{
                1: '1',
                5: '5',
                10: '10',
                20: '20'
              }}
            />
            <InputNumber
              min={1}
              max={20}
              value={config.agent.search.num_drafts}
              onChange={(value) => handleFieldChange('agent.search.num_drafts', value)}
              style={{ width: '100%', marginTop: '8px' }}
            />
          </Form.Item>
        </Col>
      </Row>
    </>
  );

  const renderReportingFields = () => (
    <>
      <Title level={4}>Report Generation Settings</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: '24px' }}>
        Configure experiment documentation and reporting.
      </Text>

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Form.Item label="Generate Report" valuePropName="checked">
            <Switch
              checked={config.generate_report}
              onChange={(checked) => handleFieldChange('generate_report', checked)}
            />
            <Text type="secondary" style={{ display: 'block', fontSize: '12px' }}>
              Automatically generate experiment reports
            </Text>
          </Form.Item>
        </Col>
      </Row>

      {config.generate_report && (
        <Card title="Report Generation Model" size="small">
          <Row gutter={16}>
            <Col xs={24} md={16}>
              <Form.Item label="Model" {...getFieldValidation('report.model')}>
                <ModelSelector
                  value={config.report.model}
                  onChange={(value) => handleFieldChange('report.model', value)}
                  availableModels={availableModels}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                label="Temperature"
                {...getFieldValidation('report.temp')}
              >
                <Slider
                  min={0}
                  max={2}
                  step={0.1}
                  value={config.report.temp}
                  onChange={(value) => handleFieldChange('report.temp', value)}
                  marks={{
                    0: '0',
                    1: '1',
                    2: '2'
                  }}
                />
                <InputNumber
                  min={0}
                  max={2}
                  step={0.1}
                  value={config.report.temp}
                  onChange={(value) => handleFieldChange('report.temp', value)}
                  style={{ width: '100%', marginTop: '8px' }}
                />
              </Form.Item>
            </Col>
          </Row>
        </Card>
      )}
    </>
  );

  return (
    <Form form={form} layout="vertical" disabled={loading}>
      {renderFormFields()}
    </Form>
  );
}