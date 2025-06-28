import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Typography, Space, message, Divider } from 'antd';
import { EyeInvisibleOutlined, EyeTwoTone, CheckCircleOutlined } from '@ant-design/icons';
import { configAPI } from '@/services/api';
import { useApiKeys } from '@/stores/settingsStore';

const { Title, Text } = Typography;

interface ApiKeyFormData {
  openaiKey: string;
  anthropicKey: string;
  openrouterKey: string;
}

export function ApiKeySettings() {
  const [form] = Form.useForm();
  const [validationStatus, setValidationStatus] = useState<Record<string, boolean>>({});
  const [isValidating, setIsValidating] = useState<Record<string, boolean>>({});
  const { apiKeys, setApiKey, clearAllApiKeys } = useApiKeys();

  // Load saved API keys from store on mount
  useEffect(() => {
    form.setFieldsValue({
      openaiKey: apiKeys.openaiKey || '',
      anthropicKey: apiKeys.anthropicKey || '',
      openrouterKey: apiKeys.openrouterKey || '',
    });
  }, [form, apiKeys]);

  const validateApiKey = async (provider: string, apiKey: string) => {
    if (!apiKey.trim()) {
      setValidationStatus(prev => ({ ...prev, [provider]: false }));
      return;
    }

    setIsValidating(prev => ({ ...prev, [provider]: true }));
    
    try {
      await configAPI.validateApiKey(provider, apiKey);
      setValidationStatus(prev => ({ ...prev, [provider]: true }));
      message.success(`${provider} API key is valid`);
    } catch (error) {
      setValidationStatus(prev => ({ ...prev, [provider]: false }));
      message.error(`${provider} API key validation failed`);
    } finally {
      setIsValidating(prev => ({ ...prev, [provider]: false }));
    }
  };

  const handleSave = (values: ApiKeyFormData) => {
    // Save to store
    setApiKey('openaiKey', values.openaiKey || '');
    setApiKey('anthropicKey', values.anthropicKey || '');
    setApiKey('openrouterKey', values.openrouterKey || '');

    message.success('API keys saved successfully');
  };

  const handleClear = () => {
    form.resetFields();
    clearAllApiKeys();
    setValidationStatus({});
    message.info('API keys cleared');
  };

  const renderApiKeyInput = (
    name: string,
    label: string,
    provider: string,
    placeholder: string
  ) => (
    <Form.Item
      name={name}
      label={
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Text strong>{label}</Text>
          {validationStatus[provider] && (
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
          )}
        </div>
      }
    >
      <Input.Password
        placeholder={placeholder}
        iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
        suffix={
          <Button
            type="link"
            size="small"
            loading={isValidating[provider]}
            onClick={() => {
              const value = form.getFieldValue(name);
              validateApiKey(provider, value);
            }}
            style={{ padding: 0, height: 'auto' }}
          >
            Validate
          </Button>
        }
        onBlur={(e) => {
          const value = e.target.value;
          if (value) {
            validateApiKey(provider, value);
          }
        }}
      />
    </Form.Item>
  );

  return (
    <div style={{ padding: 24 }}>
      <Title level={4} style={{ marginBottom: 16 }}>
        API Configuration
      </Title>
      
      <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
        Configure your API keys for AI model providers. Keys are stored locally in your browser.
      </Text>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        autoComplete="off"
      >
        {renderApiKeyInput(
          'openaiKey',
          'OpenAI API Key',
          'openai',
          'sk-...'
        )}

        <Divider style={{ margin: '16px 0' }} />

        {renderApiKeyInput(
          'anthropicKey',
          'Anthropic API Key',
          'anthropic',
          'sk-ant-...'
        )}

        <Divider style={{ margin: '16px 0' }} />

        {renderApiKeyInput(
          'openrouterKey',
          'OpenRouter API Key',
          'openrouter',
          'sk-or-...'
        )}

        <Divider style={{ margin: '24px 0' }} />

        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Button onClick={handleClear}>
            Clear All
          </Button>
          <Button type="primary" htmlType="submit">
            Save Keys
          </Button>
        </Space>
      </Form>

      <Divider style={{ margin: '24px 0' }} />

      <div style={{ background: '#f6f8fa', padding: 16, borderRadius: 8 }}>
        <Text strong style={{ display: 'block', marginBottom: 8 }}>
          Security Note
        </Text>
        <Text type="secondary" style={{ fontSize: 12 }}>
          API keys are stored locally in your browser and are not transmitted to our servers. 
          They are only used to communicate directly with the respective AI service providers.
        </Text>
      </div>
    </div>
  );
}
