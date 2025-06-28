/**
 * Model Selector Component
 * Advanced model selection with provider grouping and details
 */

import React, { useState, useEffect } from 'react';
import {
  Select,
  Typography,
  Tag,
  Space,
  Tooltip,
  Card,
  Row,
  Col,
  Button,
  Modal,
  Alert,
  Divider,
} from 'antd';
import {
  InfoCircleOutlined,
  DollarOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';

import { ModelInfo, ModelProvider } from '@/types/config';
import { useConfigStore } from '@/stores/configStore';

const { Text } = Typography;
const { Option, OptGroup } = Select;

interface ModelSelectorProps {
  value?: string;
  onChange?: (value: string) => void;
  availableModels: ModelInfo[];
  showDetails?: boolean;
  placeholder?: string;
}

export function ModelSelector({
  value,
  onChange,
  availableModels,
  showDetails = false,
  placeholder = "Select a model..."
}: ModelSelectorProps) {
  const [detailsVisible, setDetailsVisible] = useState(false);
  const [selectedModelInfo, setSelectedModelInfo] = useState<ModelInfo | null>(null);
  const { checkModelCompatibility } = useConfigStore();

  // Group models by provider
  const modelsByProvider = availableModels.reduce((acc, model) => {
    if (!acc[model.provider]) {
      acc[model.provider] = [];
    }
    acc[model.provider].push(model);
    return acc;
  }, {} as Record<ModelProvider, ModelInfo[]>);

  // Get current model info
  const currentModel = availableModels.find(m => m.name === value);

  useEffect(() => {
    if (value && !selectedModelInfo) {
      const modelInfo = availableModels.find(m => m.name === value);
      setSelectedModelInfo(modelInfo || null);
    }
  }, [value, availableModels, selectedModelInfo]);

  const handleModelChange = (selectedValue: string) => {
    const modelInfo = availableModels.find(m => m.name === selectedValue);
    setSelectedModelInfo(modelInfo || null);
    onChange?.(selectedValue);
  };

  const handleShowDetails = () => {
    setDetailsVisible(true);
  };

  const renderModelOption = (model: ModelInfo) => (
    <Option key={model.name} value={model.name}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Text strong>{model.display_name}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {model.description}
          </Text>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
          <Tag color={getProviderColor(model.provider)} size="small">
            {model.provider.toUpperCase()}
          </Tag>
          {model.cost_per_1k_tokens && (
            <Text type="secondary" style={{ fontSize: '11px' }}>
              ${model.cost_per_1k_tokens}/1k tokens
            </Text>
          )}
        </div>
      </div>
    </Option>
  );

  const getProviderColor = (provider: ModelProvider): string => {
    switch (provider) {
      case ModelProvider.OPENAI:
        return 'green';
      case ModelProvider.ANTHROPIC:
        return 'orange';
      case ModelProvider.OPENROUTER:
        return 'blue';
      default:
        return 'default';
    }
  };

  const renderProviderIcon = (provider: ModelProvider) => {
    // You can replace these with actual provider icons
    switch (provider) {
      case ModelProvider.OPENAI:
        return '🤖';
      case ModelProvider.ANTHROPIC:
        return '🧠';
      case ModelProvider.OPENROUTER:
        return '🔀';
      default:
        return '💡';
    }
  };

  return (
    <>
      <div>
        <Select
          value={value}
          onChange={handleModelChange}
          placeholder={placeholder}
          style={{ width: '100%' }}
          optionLabelProp="label"
          showSearch
          filterOption={(input, option) =>
            (option?.children as any)?.props?.children?.[0]?.props?.children
              ?.toLowerCase()
              ?.includes(input.toLowerCase()) || false
          }
        >
          {Object.entries(modelsByProvider).map(([provider, models]) => (
            <OptGroup 
              key={provider}
              label={
                <Space>
                  <span>{renderProviderIcon(provider as ModelProvider)}</span>
                  <Text strong>{provider.toUpperCase()}</Text>
                  <Tag size="small">{models.length} models</Tag>
                </Space>
              }
            >
              {models.map(renderModelOption)}
            </OptGroup>
          ))}
        </Select>

        {/* Model Info Display */}
        {currentModel && showDetails && (
          <Card 
            size="small" 
            style={{ marginTop: '8px', background: '#fafafa' }}
            bodyStyle={{ padding: '12px' }}
          >
            <Row gutter={16}>
              <Col span={16}>
                <Space direction="vertical" size="small">
                  <div>
                    <Text strong>{currentModel.display_name}</Text>
                    <Tag 
                      color={getProviderColor(currentModel.provider)} 
                      size="small" 
                      style={{ marginLeft: '8px' }}
                    >
                      {currentModel.provider.toUpperCase()}
                    </Tag>
                  </div>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {currentModel.description}
                  </Text>
                </Space>
              </Col>
              <Col span={8} style={{ textAlign: 'right' }}>
                <Space direction="vertical" size="small" style={{ alignItems: 'flex-end' }}>
                  {currentModel.cost_per_1k_tokens && (
                    <div>
                      <DollarOutlined style={{ color: '#52c41a' }} />
                      <Text style={{ fontSize: '12px', marginLeft: '4px' }}>
                        ${currentModel.cost_per_1k_tokens}/1k
                      </Text>
                    </div>
                  )}
                  {currentModel.supports_function_calling && (
                    <div>
                      <CheckCircleOutlined style={{ color: '#1890ff' }} />
                      <Text style={{ fontSize: '12px', marginLeft: '4px' }}>
                        Function Calling
                      </Text>
                    </div>
                  )}
                  <Button 
                    size="small" 
                    type="link" 
                    icon={<InfoCircleOutlined />}
                    onClick={handleShowDetails}
                    style={{ padding: 0, height: 'auto' }}
                  >
                    Details
                  </Button>
                </Space>
              </Col>
            </Row>
          </Card>
        )}
      </div>

      {/* Model Details Modal */}
      <Modal
        title={
          <Space>
            <span>{selectedModelInfo && renderProviderIcon(selectedModelInfo.provider)}</span>
            <span>{selectedModelInfo?.display_name} Details</span>
          </Space>
        }
        open={detailsVisible}
        onCancel={() => setDetailsVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailsVisible(false)}>
            Close
          </Button>
        ]}
        width={600}
      >
        {selectedModelInfo && (
          <div>
            <Card size="small" style={{ marginBottom: '16px' }}>
              <Row gutter={16}>
                <Col span={12}>
                  <Text strong>Provider</Text>
                  <br />
                  <Tag color={getProviderColor(selectedModelInfo.provider)}>
                    {selectedModelInfo.provider.toUpperCase()}
                  </Tag>
                </Col>
                <Col span={12}>
                  <Text strong>Model Name</Text>
                  <br />
                  <Text code>{selectedModelInfo.name}</Text>
                </Col>
              </Row>
            </Card>

            <Card size="small" style={{ marginBottom: '16px' }}>
              <Text strong>Description</Text>
              <br />
              <Text>{selectedModelInfo.description}</Text>
            </Card>

            <Row gutter={16}>
              {selectedModelInfo.max_tokens && (
                <Col span={12}>
                  <Card size="small">
                    <Text strong>Max Tokens</Text>
                    <br />
                    <Text>{selectedModelInfo.max_tokens.toLocaleString()}</Text>
                  </Card>
                </Col>
              )}
              
              {selectedModelInfo.cost_per_1k_tokens && (
                <Col span={12}>
                  <Card size="small">
                    <Text strong>Cost per 1K Tokens</Text>
                    <br />
                    <Text>${selectedModelInfo.cost_per_1k_tokens}</Text>
                  </Card>
                </Col>
              )}
            </Row>

            <Divider />

            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>Capabilities</Text>
              </div>
              
              <div>
                {selectedModelInfo.supports_function_calling ? (
                  <Tag color="green" icon={<CheckCircleOutlined />}>
                    Function Calling Supported
                  </Tag>
                ) : (
                  <Tag color="orange" icon={<ExclamationCircleOutlined />}>
                    No Function Calling
                  </Tag>
                )}
              </div>

              {selectedModelInfo.cost_per_1k_tokens && (
                <Alert
                  message="Cost Estimation"
                  description={`Estimated cost for a typical AIDE experiment: $${(selectedModelInfo.cost_per_1k_tokens * 50).toFixed(2)} - $${(selectedModelInfo.cost_per_1k_tokens * 200).toFixed(2)}`}
                  type="info"
                  showIcon
                  style={{ marginTop: '16px' }}
                />
              )}
            </Space>
          </div>
        )}
      </Modal>
    </>
  );
}