/**
 * Main Settings Page
 * Provides comprehensive configuration management interface
 */

import React, { useEffect, useState } from 'react';
import {
  Layout,
  Typography,
  Card,
  Row,
  Col,
  Button,
  Space,
  Alert,
  Spin,
  message,
  Divider,
  Tour,
  FloatButton,
} from 'antd';
import {
  SettingOutlined,
  SaveOutlined,
  ReloadOutlined,
  ExportOutlined,
  ImportOutlined,
  QuestionCircleOutlined,
  HistoryOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet';

import { SettingsSidebar } from '@/components/settings/SettingsSidebar';
import { DynamicConfigForm } from '@/components/settings/DynamicConfigForm';
import { ConfigPreview } from '@/components/settings/ConfigPreview';
import { ValidationPanel } from '@/components/settings/ValidationPanel';
import { QuickActions } from '@/components/settings/QuickActions';
import { useConfigStore, useConfigUI, useConfigValidation } from '@/stores/configStore';
import { ConfigCategory } from '@/types/config';

const { Content, Sider } = Layout;
const { Title, Text } = Typography;

export function SettingsPage() {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState<ConfigCategory>(ConfigCategory.PROJECT);
  const [showTour, setShowTour] = useState(false);
  
  // Store state
  const {
    currentConfig,
    loadCurrentConfig,
    loadProfiles,
    loadTemplates,
    loadAvailableModels,
    updateConfigByCategory,
    validateConfig,
    exportConfig,
    clearError,
  } = useConfigStore();

  const { loading, saving, error, unsavedChanges } = useConfigUI();
  const { validation, validating } = useConfigValidation();

  // Initialize data on mount
  useEffect(() => {
    const initializeSettings = async () => {
      try {
        await Promise.all([
          loadCurrentConfig(),
          loadProfiles(),
          loadTemplates(),
          loadAvailableModels(),
        ]);
      } catch (error) {
        console.error('Failed to initialize settings:', error);
        message.error('Failed to load settings data');
      }
    };

    initializeSettings();
  }, [loadCurrentConfig, loadProfiles, loadTemplates, loadAvailableModels]);

  // Auto-validate when config changes
  useEffect(() => {
    if (currentConfig) {
      validateConfig();
    }
  }, [currentConfig, validateConfig]);

  const handleSaveConfig = async () => {
    try {
      if (!currentConfig) return;
      
      // Trigger validation before saving
      await validateConfig();
      
      // Check if there are validation errors
      if (validation && !validation.valid) {
        message.error('Please fix validation errors before saving');
        return;
      }

      message.success('Configuration saved successfully');
    } catch (error) {
      message.error('Failed to save configuration');
    }
  };

  const handleExportConfig = async () => {
    try {
      await exportConfig('yaml', false);
      message.success('Configuration exported successfully');
    } catch (error) {
      message.error('Failed to export configuration');
    }
  };

  const handleClearError = () => {
    clearError();
  };

  // Tour steps for onboarding
  const tourSteps = [
    {
      title: 'Welcome to AIDE Settings',
      description: 'This is your configuration management center. Here you can customize all aspects of the AIDE ML agent.',
      target: () => document.querySelector('.settings-main-title'),
    },
    {
      title: 'Settings Categories',
      description: 'Use the sidebar to navigate between different configuration categories like Project, Agent, and Models.',
      target: () => document.querySelector('.settings-sidebar'),
    },
    {
      title: 'Configuration Form',
      description: 'Modify settings here. Changes are validated in real-time and you can preview the impact.',
      target: () => document.querySelector('.config-form'),
    },
    {
      title: 'Validation Panel',
      description: 'This panel shows validation results and warnings to help you maintain a valid configuration.',
      target: () => document.querySelector('.validation-panel'),
    },
  ];

  if (loading && !currentConfig) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '60vh' 
      }}>
        <Spin size="large" tip="Loading configuration..." />
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>Settings - AIDE ML Configuration</title>
        <meta name="description" content="Configure AIDE ML agent settings, manage profiles, and customize your machine learning workflow" />
      </Helmet>

      <Layout style={{ minHeight: 'calc(100vh - 64px)', background: '#f5f5f5' }}>
        {/* Sidebar */}
        <Sider 
          width={300} 
          style={{ 
            background: '#fff',
            boxShadow: '2px 0 8px rgba(0,0,0,0.06)',
            overflow: 'auto',
          }}
          className="settings-sidebar"
        >
          <SettingsSidebar
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            validation={validation}
          />
        </Sider>

        {/* Main Content */}
        <Layout style={{ background: '#f5f5f5' }}>
          <Content style={{ padding: '24px' }}>
            {/* Header */}
            <div style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div>
                  <Title level={2} style={{ margin: 0 }} className="settings-main-title">
                    <SettingOutlined style={{ marginRight: '8px' }} />
                    AIDE Configuration
                  </Title>
                  <Text type="secondary">
                    Customize your machine learning agent behavior and preferences
                  </Text>
                </div>

                <Space>
                  <Button
                    icon={<QuestionCircleOutlined />}
                    onClick={() => setShowTour(true)}
                  >
                    Help
                  </Button>
                  <Button
                    icon={<HistoryOutlined />}
                    onClick={() => navigate('/settings/profiles')}
                  >
                    Profiles
                  </Button>
                  <Button
                    icon={<ExportOutlined />}
                    onClick={handleExportConfig}
                    loading={saving}
                  >
                    Export
                  </Button>
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    onClick={handleSaveConfig}
                    loading={saving || validating}
                    disabled={!unsavedChanges || (validation && !validation.valid)}
                  >
                    Save Changes
                  </Button>
                </Space>
              </div>

              {/* Quick Actions */}
              <QuickActions />

              {/* Error Alert */}
              {error && (
                <Alert
                  message="Configuration Error"
                  description={error}
                  type="error"
                  showIcon
                  closable
                  onClose={handleClearError}
                  style={{ marginBottom: '16px' }}
                />
              )}

              {/* Unsaved Changes Alert */}
              {unsavedChanges && (
                <Alert
                  message="You have unsaved changes"
                  description="Don't forget to save your configuration changes."
                  type="warning"
                  showIcon
                  style={{ marginBottom: '16px' }}
                />
              )}
            </div>

            {/* Main Configuration Area */}
            <Row gutter={24}>
              {/* Configuration Form */}
              <Col xs={24} lg={16}>
                <Card 
                  title={`${selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)} Settings`}
                  className="config-form"
                  style={{ marginBottom: '24px' }}
                  extra={
                    <Space>
                      <Button
                        size="small"
                        icon={<ReloadOutlined />}
                        onClick={() => loadCurrentConfig()}
                        loading={loading}
                      >
                        Reload
                      </Button>
                    </Space>
                  }
                >
                  <DynamicConfigForm
                    category={selectedCategory}
                    config={currentConfig}
                    onChange={(updates) => updateConfigByCategory(selectedCategory, updates)}
                    loading={saving}
                  />
                </Card>
              </Col>

              {/* Right Panel */}
              <Col xs={24} lg={8}>
                {/* Configuration Preview */}
                <Card 
                  title="Configuration Preview"
                  style={{ marginBottom: '16px' }}
                  size="small"
                >
                  <ConfigPreview 
                    config={currentConfig}
                    category={selectedCategory}
                  />
                </Card>

                {/* Validation Panel */}
                <ValidationPanel
                  validation={validation}
                  validating={validating}
                  className="validation-panel"
                />
              </Col>
            </Row>
          </Content>
        </Layout>
      </Layout>

      {/* Help Tour */}
      <Tour
        open={showTour}
        onClose={() => setShowTour(false)}
        steps={tourSteps}
        placement="bottom"
      />

      {/* Floating Help Button */}
      <FloatButton
        icon={<QuestionCircleOutlined />}
        tooltip="Get Help"
        onClick={() => setShowTour(true)}
        style={{ right: 24, bottom: 24 }}
      />
    </>
  );
}