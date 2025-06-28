/**
 * Quick Actions Component
 * Provides common configuration shortcuts and templates
 */

import React, { useState } from 'react';
import {
  Card,
  Button,
  Space,
  Dropdown,
  Modal,
  Typography,
  List,
  Tag,
  Row,
  Col,
  message,
  Upload,
} from 'antd';
import {
  ThunderboltOutlined,
  ExperimentOutlined,
  DollarOutlined,
  BookOutlined,
  SearchOutlined,
  DownloadOutlined,
  UploadOutlined,
  ReloadOutlined,
  CopyOutlined,
  HistoryOutlined,
} from '@ant-design/icons';
import type { MenuProps, UploadProps } from 'antd';

import { useConfigStore, useConfigTemplates } from '@/stores/configStore';
import { Template } from '@/types/config';

const { Text } = Typography;

export function QuickActions() {
  const [templateModalVisible, setTemplateModalVisible] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  
  const { 
    applyTemplate, 
    exportConfig, 
    importConfig, 
    resetToDefaults,
    loadCurrentConfig 
  } = useConfigStore();
  
  const { templates } = useConfigTemplates();

  // Template categories with descriptions
  const templateCategories = {
    'quick-experiment': {
      icon: <ThunderboltOutlined />,
      color: 'blue',
      description: 'Fast prototyping with minimal iterations'
    },
    'comprehensive-analysis': {
      icon: <SearchOutlined />,
      color: 'green',
      description: 'Thorough exploration with extensive search'
    },
    'cost-optimized': {
      icon: <DollarOutlined />,
      color: 'orange',
      description: 'Budget-friendly configuration'
    },
    'educational': {
      icon: <BookOutlined />,
      color: 'purple',
      description: 'Learning-focused with detailed explanations'
    },
    'research-focused': {
      icon: <ExperimentOutlined />,
      color: 'red',
      description: 'Advanced research methodologies'
    },
  };

  const handleTemplateSelect = async (template: Template) => {
    try {
      await applyTemplate(template.name);
      message.success(`Applied template: ${template.display_name}`);
      setTemplateModalVisible(false);
    } catch (error) {
      message.error('Failed to apply template');
    }
  };

  const handleExport = async () => {
    try {
      await exportConfig('yaml', false);
      message.success('Configuration exported successfully');
    } catch (error) {
      message.error('Failed to export configuration');
    }
  };

  const handleResetToDefaults = async () => {
    Modal.confirm({
      title: 'Reset to Default Configuration',
      content: 'Are you sure you want to reset all settings to their default values? This action cannot be undone.',
      okText: 'Reset',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await resetToDefaults();
          message.success('Configuration reset to defaults');
        } catch (error) {
          message.error('Failed to reset configuration');
        }
      },
    });
  };

  const uploadProps: UploadProps = {
    accept: '.yaml,.yml,.json',
    beforeUpload: (file) => {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const configData = e.target?.result as string;
          await importConfig(configData, true);
          message.success('Configuration imported successfully');
        } catch (error) {
          message.error('Failed to import configuration');
        }
      };
      reader.readAsText(file);
      return false; // Prevent automatic upload
    },
    showUploadList: false,
  };

  const quickActionItems: MenuProps['items'] = [
    {
      key: 'templates',
      label: 'Apply Template',
      icon: <ThunderboltOutlined />,
      onClick: () => setTemplateModalVisible(true),
    },
    {
      key: 'divider1',
      type: 'divider',
    },
    {
      key: 'export',
      label: 'Export Config',
      icon: <DownloadOutlined />,
      onClick: handleExport,
    },
    {
      key: 'import',
      label: (
        <Upload {...uploadProps}>
          <span>Import Config</span>
        </Upload>
      ),
      icon: <UploadOutlined />,
    },
    {
      key: 'divider2',
      type: 'divider',
    },
    {
      key: 'reload',
      label: 'Reload Config',
      icon: <ReloadOutlined />,
      onClick: () => loadCurrentConfig(),
    },
    {
      key: 'reset',
      label: 'Reset to Defaults',
      icon: <HistoryOutlined />,
      onClick: handleResetToDefaults,
    },
  ];

  return (
    <>
      <Card size="small" style={{ marginBottom: '16px' }}>
        <Row gutter={8} align="middle">
          <Col>
            <Text strong>Quick Actions:</Text>
          </Col>
          <Col>
            <Space size="small">
              <Button
                size="small"
                icon={<ThunderboltOutlined />}
                onClick={() => setTemplateModalVisible(true)}
              >
                Templates
              </Button>
              <Dropdown menu={{ items: quickActionItems }} trigger={['click']}>
                <Button size="small">
                  More Actions
                </Button>
              </Dropdown>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Template Selection Modal */}
      <Modal
        title="Choose Configuration Template"
        open={templateModalVisible}
        onCancel={() => setTemplateModalVisible(false)}
        footer={null}
        width={800}
      >
        <div style={{ marginBottom: '16px' }}>
          <Text type="secondary">
            Templates provide pre-configured settings optimized for different use cases. 
            Select one to quickly set up your AIDE configuration.
          </Text>
        </div>

        <List
          dataSource={templates}
          renderItem={(template) => {
            const category = templateCategories[template.category as keyof typeof templateCategories] || {
              icon: <ExperimentOutlined />,
              color: 'default',
              description: template.description
            };

            return (
              <List.Item
                actions={[
                  <Button
                    type="primary"
                    size="small"
                    onClick={() => handleTemplateSelect(template)}
                  >
                    Apply Template
                  </Button>
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <div style={{ 
                      width: '40px', 
                      height: '40px', 
                      borderRadius: '50%',
                      background: `var(--ant-color-${category.color})`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: '18px'
                    }}>
                      {category.icon}
                    </div>
                  }
                  title={
                    <Space>
                      <Text strong>{template.display_name}</Text>
                      <Tag color={category.color}>{template.category}</Tag>
                    </Space>
                  }
                  description={
                    <div>
                      <Text>{template.description}</Text>
                      <br />
                      {template.tags && template.tags.length > 0 && (
                        <div style={{ marginTop: '4px' }}>
                          {template.tags.map(tag => (
                            <Tag key={tag} size="small">{tag}</Tag>
                          ))}
                        </div>
                      )}
                      {template.author && (
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          by {template.author}
                        </Text>
                      )}
                    </div>
                  }
                />
              </List.Item>
            );
          }}
        />
      </Modal>
    </>
  );
}