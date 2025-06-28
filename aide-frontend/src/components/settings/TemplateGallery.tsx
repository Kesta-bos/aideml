/**
 * Template Gallery Component
 * Displays available configuration templates
 */

import React, { useState } from 'react';
import {
  Card,
  Row,
  Col,
  Typography,
  Tag,
  Button,
  Space,
  Modal,
  Input,
  Form,
  message,
  Tooltip,
  Divider,
  Alert,
} from 'antd';
import {
  ThunderboltOutlined,
  ExperimentOutlined,
  DollarOutlined,
  BookOutlined,
  SearchOutlined,
  PlayCircleOutlined,
  PlusOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';

import { Template } from '@/types/config';
import { useConfigStore } from '@/stores/configStore';

const { Title, Text } = Typography;
const { Meta } = Card;

interface TemplateGalleryProps {
  templates: Template[];
}

interface TemplateCardProps {
  template: Template;
  onApply: () => void;
  onCreateProfile: () => void;
}

export function TemplateGallery({ templates }: TemplateGalleryProps) {
  const [createProfileModalVisible, setCreateProfileModalVisible] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [form] = Form.useForm();

  const { applyTemplate, createProfileFromTemplate } = useConfigStore();

  const handleApplyTemplate = async (template: Template) => {
    try {
      await applyTemplate(template.name);
      message.success(`Applied template: ${template.display_name}`);
    } catch (error) {
      message.error('Failed to apply template');
    }
  };

  const handleCreateProfile = (template: Template) => {
    setSelectedTemplate(template);
    form.setFieldsValue({
      name: `${template.display_name} Profile`,
      description: `Profile based on ${template.display_name} template`,
    });
    setCreateProfileModalVisible(true);
  };

  const handleCreateProfileSubmit = async (values: any) => {
    if (!selectedTemplate) return;

    try {
      await createProfileFromTemplate(
        selectedTemplate.name,
        values.name,
        values.description
      );
      message.success('Profile created from template successfully');
      setCreateProfileModalVisible(false);
      setSelectedTemplate(null);
      form.resetFields();
    } catch (error) {
      message.error('Failed to create profile from template');
    }
  };

  return (
    <>
      <div style={{ marginBottom: '24px' }}>
        <Title level={3} style={{ marginBottom: '8px' }}>
          Configuration Templates
        </Title>
        <Text type="secondary">
          Quick-start templates optimized for different use cases. Apply directly or create a new profile.
        </Text>
      </div>

      <Row gutter={[16, 16]}>
        {templates.map(template => (
          <Col xs={24} sm={12} lg={8} xl={6} key={template.name}>
            <TemplateCard
              template={template}
              onApply={() => handleApplyTemplate(template)}
              onCreateProfile={() => handleCreateProfile(template)}
            />
          </Col>
        ))}
      </Row>

      {/* Create Profile from Template Modal */}
      <Modal
        title={`Create Profile from ${selectedTemplate?.display_name}`}
        open={createProfileModalVisible}
        onCancel={() => {
          setCreateProfileModalVisible(false);
          setSelectedTemplate(null);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="Create Profile"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateProfileSubmit}
        >
          <Alert
            message="Template Configuration"
            description={selectedTemplate?.description}
            type="info"
            showIcon
            style={{ marginBottom: '16px' }}
          />

          <Form.Item
            name="name"
            label="Profile Name"
            rules={[{ required: true, message: 'Please enter a profile name' }]}
          >
            <Input placeholder="Enter profile name" />
          </Form.Item>

          <Form.Item
            name="description"
            label="Description"
            rules={[{ required: true, message: 'Please enter a description' }]}
          >
            <Input.TextArea 
              rows={3} 
              placeholder="Describe how you'll use this profile"
            />
          </Form.Item>

          {selectedTemplate?.tags && selectedTemplate.tags.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <Text strong>Template Tags:</Text>
              <br />
              <Space wrap style={{ marginTop: '4px' }}>
                {selectedTemplate.tags.map(tag => (
                  <Tag key={tag} size="small">{tag}</Tag>
                ))}
              </Space>
            </div>
          )}
        </Form>
      </Modal>
    </>
  );
}

function TemplateCard({ template, onApply, onCreateProfile }: TemplateCardProps) {
  const getTemplateIcon = (category: string) => {
    const icons: Record<string, React.ReactNode> = {
      'quick-experiment': <ThunderboltOutlined />,
      'comprehensive-analysis': <SearchOutlined />,
      'cost-optimized': <DollarOutlined />,
      'educational': <BookOutlined />,
      'research-focused': <ExperimentOutlined />,
    };
    return icons[category] || <ExperimentOutlined />;
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'quick-experiment': 'blue',
      'comprehensive-analysis': 'green',
      'cost-optimized': 'orange',
      'educational': 'purple',
      'research-focused': 'red',
    };
    return colors[category] || 'default';
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      'quick-experiment': 'Quick Experiment',
      'comprehensive-analysis': 'Comprehensive',
      'cost-optimized': 'Cost Optimized',
      'educational': 'Educational',
      'research-focused': 'Research',
    };
    return labels[category] || category;
  };

  return (
    <Card
      hoverable
      className="template-card"
      style={{
        height: '100%',
        transition: 'all 0.3s ease',
      }}
      actions={[
        <Tooltip title="Apply Template" key="apply">
          <Button
            type="text"
            icon={<PlayCircleOutlined />}
            onClick={onApply}
            style={{ color: '#52c41a' }}
          >
            Apply
          </Button>
        </Tooltip>,
        <Tooltip title="Create Profile" key="profile">
          <Button
            type="text"
            icon={<PlusOutlined />}
            onClick={onCreateProfile}
            style={{ color: '#1890ff' }}
          >
            Profile
          </Button>
        </Tooltip>,
      ]}
    >
      <Meta
        avatar={
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '50%',
            background: `var(--ant-color-${getCategoryColor(template.category)})`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '20px'
          }}>
            {getTemplateIcon(template.category)}
          </div>
        }
        title={
          <div>
            <Title level={5} style={{ margin: 0, marginBottom: '4px' }}>
              {template.display_name}
            </Title>
            <Tag color={getCategoryColor(template.category)} size="small">
              {getCategoryLabel(template.category)}
            </Tag>
          </div>
        }
        description={
          <div style={{ minHeight: '60px' }}>
            <Text 
              type="secondary" 
              style={{ 
                fontSize: '13px',
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
              }}
            >
              {template.description}
            </Text>
          </div>
        }
      />

      {/* Tags */}
      {template.tags && template.tags.length > 0 && (
        <div style={{ marginTop: '12px', marginBottom: '8px' }}>
          {template.tags.slice(0, 3).map(tag => (
            <Tag key={tag} size="small" style={{ margin: '2px' }}>
              {tag}
            </Tag>
          ))}
          {template.tags.length > 3 && (
            <Tag size="small" style={{ margin: '2px' }}>
              +{template.tags.length - 3}
            </Tag>
          )}
        </div>
      )}

      {/* Footer */}
      <div style={{ 
        marginTop: '12px', 
        paddingTop: '8px', 
        borderTop: '1px solid #f0f0f0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        {template.author && (
          <Text type="secondary" style={{ fontSize: '11px' }}>
            by {template.author}
          </Text>
        )}
        {template.version && (
          <Text type="secondary" style={{ fontSize: '11px' }}>
            v{template.version}
          </Text>
        )}
      </div>
    </Card>
  );
}