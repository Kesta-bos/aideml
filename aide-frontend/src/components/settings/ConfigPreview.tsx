/**
 * Configuration Preview Component
 * Shows a real-time preview of the current configuration
 */

import React, { useMemo } from 'react';
import {
  Typography,
  Descriptions,
  Tag,
  Space,
  Divider,
  Alert,
} from 'antd';
import {
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';

import { ConfigSchema, ConfigCategory } from '@/types/config';

const { Text, Title } = Typography;

interface ConfigPreviewProps {
  config: ConfigSchema | null;
  category: ConfigCategory;
}

export function ConfigPreview({ config, category }: ConfigPreviewProps) {
  const previewData = useMemo(() => {
    if (!config) return null;

    switch (category) {
      case ConfigCategory.PROJECT:
        return renderProjectPreview(config);
      case ConfigCategory.AGENT:
        return renderAgentPreview(config);
      case ConfigCategory.EXECUTION:
        return renderExecutionPreview(config);
      case ConfigCategory.MODELS:
        return renderModelsPreview(config);
      case ConfigCategory.SEARCH:
        return renderSearchPreview(config);
      case ConfigCategory.REPORTING:
        return renderReportingPreview(config);
      default:
        return null;
    }
  }, [config, category]);

  if (!config) {
    return (
      <Alert
        message="No Configuration"
        description="Load a configuration to see the preview"
        type="info"
        showIcon
      />
    );
  }

  return (
    <div>
      <Title level={5} style={{ marginBottom: '16px' }}>
        {category.charAt(0).toUpperCase() + category.slice(1)} Preview
      </Title>
      {previewData}
    </div>
  );
}

const renderProjectPreview = (config: ConfigSchema) => (
  <Descriptions size="small" column={1} bordered>
    <Descriptions.Item label="Data Directory">
      <Text code>{config.data_dir || 'Not specified'}</Text>
    </Descriptions.Item>
    <Descriptions.Item label="Description File">
      <Text code>{config.desc_file || 'Not specified'}</Text>
    </Descriptions.Item>
    <Descriptions.Item label="Goal">
      <Text ellipsis={{ tooltip: config.goal }}>
        {config.goal || 'Not specified'}
      </Text>
    </Descriptions.Item>
    <Descriptions.Item label="Evaluation">
      <Text ellipsis={{ tooltip: config.eval }}>
        {config.eval || 'Not specified'}
      </Text>
    </Descriptions.Item>
    <Descriptions.Item label="Workspace">
      <Text code>{config.workspace_dir}</Text>
    </Descriptions.Item>
    <Descriptions.Item label="Data Processing">
      <Space>
        {config.preprocess_data && <Tag color="green">Preprocess</Tag>}
        {config.copy_data && <Tag color="blue">Copy Data</Tag>}
      </Space>
    </Descriptions.Item>
  </Descriptions>
);

const renderAgentPreview = (config: ConfigSchema) => (
  <div>
    <Descriptions size="small" column={1} bordered style={{ marginBottom: '16px' }}>
      <Descriptions.Item label="Improvement Steps">
        <Tag color="blue">{config.agent.steps} steps</Tag>
      </Descriptions.Item>
      <Descriptions.Item label="Cross Validation">
        <Tag color="green">{config.agent.k_fold_validation}-fold</Tag>
      </Descriptions.Item>
      <Descriptions.Item label="Features">
        <Space>
          {config.agent.expose_prediction && <Tag color="purple">Prediction Function</Tag>}
          {config.agent.data_preview && <Tag color="orange">Data Preview</Tag>}
        </Space>
      </Descriptions.Item>
    </Descriptions>

    <Title level={5} style={{ margin: '16px 0 8px 0' }}>Model Configuration</Title>
    <Descriptions size="small" column={1} bordered>
      <Descriptions.Item label="Code Model">
        <Space>
          <Text code>{config.agent.code.model}</Text>
          <Tag>temp: {config.agent.code.temp}</Tag>
        </Space>
      </Descriptions.Item>
      <Descriptions.Item label="Feedback Model">
        <Space>
          <Text code>{config.agent.feedback.model}</Text>
          <Tag>temp: {config.agent.feedback.temp}</Tag>
        </Space>
      </Descriptions.Item>
    </Descriptions>
  </div>
);

const renderExecutionPreview = (config: ConfigSchema) => (
  <Descriptions size="small" column={1} bordered>
    <Descriptions.Item label="Timeout">
      <Tag color="orange" icon={<ClockCircleOutlined />}>
        {Math.floor(config.exec.timeout / 60)} minutes
      </Tag>
    </Descriptions.Item>
    <Descriptions.Item label="Script File">
      <Text code>{config.exec.agent_file_name}</Text>
    </Descriptions.Item>
    <Descriptions.Item label="Traceback Format">
      <Tag color={config.exec.format_tb_ipython ? 'green' : 'default'}>
        {config.exec.format_tb_ipython ? 'IPython Style' : 'Standard'}
      </Tag>
    </Descriptions.Item>
  </Descriptions>
);

const renderModelsPreview = (config: ConfigSchema) => (
  <div>
    <Alert
      message="Model Overview"
      description="Current AI models configured for different tasks"
      type="info"
      showIcon
      style={{ marginBottom: '16px' }}
    />
    
    <Descriptions size="small" column={1} bordered>
      <Descriptions.Item label="Code Generation">
        <Space>
          <Text code>{config.agent.code.model}</Text>
          <Tag>temp: {config.agent.code.temp}</Tag>
        </Space>
      </Descriptions.Item>
      <Descriptions.Item label="Feedback Analysis">
        <Space>
          <Text code>{config.agent.feedback.model}</Text>
          <Tag>temp: {config.agent.feedback.temp}</Tag>
        </Space>
      </Descriptions.Item>
      <Descriptions.Item label="Report Generation">
        <Space>
          <Text code>{config.report.model}</Text>
          <Tag>temp: {config.report.temp}</Tag>
        </Space>
      </Descriptions.Item>
    </Descriptions>
  </div>
);

const renderSearchPreview = (config: ConfigSchema) => (
  <div>
    <Alert
      message="Tree Search Algorithm"
      description="Configuration for solution exploration strategy"
      type="info"
      showIcon
      style={{ marginBottom: '16px' }}
    />
    
    <Descriptions size="small" column={1} bordered>
      <Descriptions.Item label="Initial Drafts">
        <Tag color="blue">{config.agent.search.num_drafts} solutions</Tag>
      </Descriptions.Item>
      <Descriptions.Item label="Debug Depth">
        <Tag color="orange">{config.agent.search.max_debug_depth} levels</Tag>
      </Descriptions.Item>
      <Descriptions.Item label="Debug Probability">
        <Tag color="green">{Math.round(config.agent.search.debug_prob * 100)}%</Tag>
      </Descriptions.Item>
    </Descriptions>

    <div style={{ marginTop: '16px', padding: '12px', background: '#f6f8fa', borderRadius: '4px' }}>
      <Text type="secondary" style={{ fontSize: '12px' }}>
        <strong>Strategy:</strong> Generate {config.agent.search.num_drafts} initial solutions, 
        then explore via debugging with {Math.round(config.agent.search.debug_prob * 100)}% probability, 
        up to {config.agent.search.max_debug_depth} debug levels deep.
      </Text>
    </div>
  </div>
);

const renderReportingPreview = (config: ConfigSchema) => (
  <div>
    <Descriptions size="small" column={1} bordered>
      <Descriptions.Item label="Generate Reports">
        <Tag 
          color={config.generate_report ? 'green' : 'red'} 
          icon={config.generate_report ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
        >
          {config.generate_report ? 'Enabled' : 'Disabled'}
        </Tag>
      </Descriptions.Item>
      {config.generate_report && (
        <Descriptions.Item label="Report Model">
          <Space>
            <Text code>{config.report.model}</Text>
            <Tag>temp: {config.report.temp}</Tag>
          </Space>
        </Descriptions.Item>
      )}
    </Descriptions>

    {config.generate_report && (
      <div style={{ marginTop: '16px', padding: '12px', background: '#f6f8fa', borderRadius: '4px' }}>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          <strong>Report Features:</strong> Automatic experiment documentation, 
          methodology explanation, results analysis, and recommendations for improvement.
        </Text>
      </div>
    )}
  </div>
);