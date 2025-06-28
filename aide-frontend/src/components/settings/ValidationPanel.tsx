/**
 * Validation Panel Component
 * Shows configuration validation results and warnings
 */

import React from 'react';
import {
  Card,
  Alert,
  List,
  Typography,
  Space,
  Tag,
  Spin,
  Empty,
  Collapse,
  Button,
} from 'antd';
import {
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  WarningOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';

import { ConfigValidationResult } from '@/types/config';

const { Text, Title } = Typography;
const { Panel } = Collapse;

interface ValidationPanelProps {
  validation: ConfigValidationResult | null;
  validating?: boolean;
  onRevalidate?: () => void;
  className?: string;
}

export function ValidationPanel({ 
  validation, 
  validating = false, 
  onRevalidate,
  className 
}: ValidationPanelProps) {
  if (validating) {
    return (
      <Card 
        title="Validation"
        className={className}
        style={{ textAlign: 'center' }}
      >
        <Spin size="large" tip="Validating configuration..." />
      </Card>
    );
  }

  if (!validation) {
    return (
      <Card 
        title="Validation"
        className={className}
      >
        <Empty
          description="No validation results"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  }

  const hasErrors = validation.errors.length > 0;
  const hasWarnings = validation.warnings.length > 0;
  const isValid = validation.valid;

  const getStatusColor = () => {
    if (hasErrors) return 'error';
    if (hasWarnings) return 'warning';
    return 'success';
  };

  const getStatusIcon = () => {
    if (hasErrors) return <ExclamationCircleOutlined />;
    if (hasWarnings) return <WarningOutlined />;
    return <CheckCircleOutlined />;
  };

  const getStatusMessage = () => {
    if (hasErrors) return 'Configuration has errors';
    if (hasWarnings) return 'Configuration has warnings';
    return 'Configuration is valid';
  };

  return (
    <Card
      title={
        <Space>
          <span>Validation Results</span>
          {onRevalidate && (
            <Button 
              size="small" 
              icon={<ReloadOutlined />} 
              onClick={onRevalidate}
              loading={validating}
            >
              Revalidate
            </Button>
          )}
        </Space>
      }
      className={className}
      size="small"
    >
      {/* Overall Status */}
      <Alert
        message={getStatusMessage()}
        type={getStatusColor()}
        icon={getStatusIcon()}
        showIcon
        style={{ marginBottom: '16px' }}
        description={
          <Space>
            {hasErrors && <Tag color="red">{validation.errors.length} errors</Tag>}
            {hasWarnings && <Tag color="orange">{validation.warnings.length} warnings</Tag>}
            {isValid && !hasWarnings && <Tag color="green">All checks passed</Tag>}
          </Space>
        }
      />

      {/* Detailed Results */}
      {(hasErrors || hasWarnings) && (
        <Collapse size="small" ghost>
          {/* Errors */}
          {hasErrors && (
            <Panel 
              header={
                <Space>
                  <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
                  <Text strong style={{ color: '#ff4d4f' }}>
                    Errors ({validation.errors.length})
                  </Text>
                </Space>
              } 
              key="errors"
            >
              <List
                size="small"
                dataSource={validation.errors}
                renderItem={(error, index) => (
                  <List.Item key={index}>
                    <div style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Text strong style={{ color: '#ff4d4f' }}>
                          {error.field}
                        </Text>
                        {error.value !== undefined && (
                          <Tag size="small" style={{ fontSize: '10px' }}>
                            {String(error.value)}
                          </Tag>
                        )}
                      </div>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {error.message}
                      </Text>
                    </div>
                  </List.Item>
                )}
              />
            </Panel>
          )}

          {/* Warnings */}
          {hasWarnings && (
            <Panel 
              header={
                <Space>
                  <WarningOutlined style={{ color: '#faad14' }} />
                  <Text strong style={{ color: '#faad14' }}>
                    Warnings ({validation.warnings.length})
                  </Text>
                </Space>
              } 
              key="warnings"
            >
              <List
                size="small"
                dataSource={validation.warnings}
                renderItem={(warning, index) => (
                  <List.Item key={index}>
                    <div>
                      <WarningOutlined style={{ color: '#faad14', marginRight: '8px' }} />
                      <Text style={{ fontSize: '12px' }}>{warning}</Text>
                    </div>
                  </List.Item>
                )}
              />
            </Panel>
          )}
        </Collapse>
      )}

      {/* Success State */}
      {isValid && !hasWarnings && (
        <div style={{ textAlign: 'center', padding: '16px' }}>
          <CheckCircleOutlined 
            style={{ fontSize: '32px', color: '#52c41a', marginBottom: '8px' }} 
          />
          <br />
          <Text type="secondary">
            Your configuration looks great! No issues found.
          </Text>
        </div>
      )}

      {/* Help Text */}
      <div style={{ 
        marginTop: '16px', 
        padding: '8px', 
        background: '#f6f8fa', 
        borderRadius: '4px',
        borderLeft: '3px solid #1890ff'
      }}>
        <Space>
          <InfoCircleOutlined style={{ color: '#1890ff' }} />
          <Text type="secondary" style={{ fontSize: '11px' }}>
            Validation runs automatically when you make changes. 
            Fix any errors before saving your configuration.
          </Text>
        </Space>
      </div>
    </Card>
  );
}