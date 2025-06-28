/**
 * Settings Sidebar Component
 * Navigation and profile management for configuration
 */

import React from 'react';
import {
  Menu,
  Card,
  Select,
  Button,
  Typography,
  Space,
  Badge,
  Tooltip,
  Divider,
  Tag,
} from 'antd';
import {
  FolderOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  BrainOutlined,
  SearchOutlined,
  FileTextOutlined,
  UserOutlined,
  PlusOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

import { ConfigCategory, ConfigValidationResult, Profile } from '@/types/config';
import { useConfigStore, useConfigProfiles } from '@/stores/configStore';

const { Text, Title } = Typography;
const { Option } = Select;

interface SettingsSidebarProps {
  selectedCategory: ConfigCategory;
  onCategoryChange: (category: ConfigCategory) => void;
  validation?: ConfigValidationResult | null;
}

export function SettingsSidebar({ 
  selectedCategory, 
  onCategoryChange, 
  validation 
}: SettingsSidebarProps) {
  const navigate = useNavigate();
  const { profiles, activeProfile } = useConfigProfiles();
  const { activateProfile } = useConfigStore();

  // Category configuration with icons and descriptions
  const categories = [
    {
      key: ConfigCategory.PROJECT,
      icon: <FolderOutlined />,
      label: 'Project Settings',
      description: 'Data paths, goals, and evaluation criteria',
    },
    {
      key: ConfigCategory.AGENT,
      icon: <RobotOutlined />,
      label: 'Agent Behavior',
      description: 'ML agent workflow and parameters',
    },
    {
      key: ConfigCategory.EXECUTION,
      icon: <ThunderboltOutlined />,
      label: 'Execution Environment',
      description: 'Runtime settings and timeouts',
    },
    {
      key: ConfigCategory.MODELS,
      icon: <BrainOutlined />,
      label: 'AI Models',
      description: 'LLM configuration and providers',
    },
    {
      key: ConfigCategory.SEARCH,
      icon: <SearchOutlined />,
      label: 'Tree Search',
      description: 'Solution exploration algorithm',
    },
    {
      key: ConfigCategory.REPORTING,
      icon: <FileTextOutlined />,
      label: 'Report Generation',
      description: 'Experiment documentation settings',
    },
  ];

  // Get error count for each category
  const getErrorCount = (category: ConfigCategory): number => {
    if (!validation?.errors) return 0;
    return validation.errors.filter(error => 
      error.field.toLowerCase().includes(category.toLowerCase())
    ).length;
  };

  const handleProfileChange = async (profileId: string) => {
    try {
      await activateProfile(profileId);
    } catch (error) {
      console.error('Failed to activate profile:', error);
    }
  };

  const handleCreateProfile = () => {
    navigate('/settings/profiles');
  };

  const handleManageProfiles = () => {
    navigate('/settings/profiles');
  };

  return (
    <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Profile Selector */}
      <Card size="small" style={{ marginBottom: '16px' }}>
        <div style={{ marginBottom: '12px' }}>
          <Title level={5} style={{ margin: 0, display: 'flex', alignItems: 'center' }}>
            <UserOutlined style={{ marginRight: '8px' }} />
            Active Profile
          </Title>
        </div>
        
        <Select
          style={{ width: '100%', marginBottom: '8px' }}
          placeholder="Select a profile..."
          value={activeProfile?.id}
          onChange={handleProfileChange}
          allowClear
        >
          {profiles.map(profile => (
            <Option key={profile.id} value={profile.id}>
              <div>
                <Text strong>{profile.name}</Text>
                <br />
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {profile.category}
                </Text>
              </div>
            </Option>
          ))}
        </Select>

        <Space style={{ width: '100%' }} direction="vertical" size="small">
          <Button
            size="small"
            icon={<PlusOutlined />}
            onClick={handleCreateProfile}
            style={{ width: '100%' }}
          >
            Create Profile
          </Button>
          <Button
            size="small"
            onClick={handleManageProfiles}
            style={{ width: '100%' }}
          >
            Manage Profiles
          </Button>
        </Space>

        {activeProfile && (
          <div style={{ marginTop: '8px', padding: '8px', background: '#f6f8fa', borderRadius: '4px' }}>
            <Text style={{ fontSize: '12px', color: '#666' }}>
              {activeProfile.description}
            </Text>
            {activeProfile.tags && activeProfile.tags.length > 0 && (
              <div style={{ marginTop: '4px' }}>
                {activeProfile.tags.map(tag => (
                  <Tag key={tag} size="small">{tag}</Tag>
                ))}
              </div>
            )}
          </div>
        )}
      </Card>

      <Divider style={{ margin: '8px 0' }} />

      {/* Categories Menu */}
      <div style={{ flex: 1 }}>
        <Title level={5} style={{ marginBottom: '12px' }}>
          <SettingOutlined style={{ marginRight: '8px' }} />
          Configuration Categories
        </Title>

        <Menu
          mode="vertical"
          selectedKeys={[selectedCategory]}
          style={{ 
            border: 'none',
            background: 'transparent',
          }}
          onSelect={({ key }) => onCategoryChange(key as ConfigCategory)}
        >
          {categories.map(category => {
            const errorCount = getErrorCount(category.key);
            
            return (
              <Menu.Item 
                key={category.key}
                icon={category.icon}
                style={{ 
                  marginBottom: '4px',
                  borderRadius: '6px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text strong style={{ fontSize: '14px' }}>
                      {category.label}
                    </Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {category.description}
                    </Text>
                  </div>
                  
                  {errorCount > 0 && (
                    <Tooltip title={`${errorCount} validation errors`}>
                      <Badge count={errorCount} size="small" />
                    </Tooltip>
                  )}
                </div>
              </Menu.Item>
            );
          })}
        </Menu>
      </div>

      {/* Quick Stats */}
      {validation && (
        <Card size="small" style={{ marginTop: 'auto' }}>
          <div style={{ textAlign: 'center' }}>
            <Text style={{ fontSize: '12px', color: '#666' }}>Configuration Status</Text>
            <div style={{ marginTop: '8px' }}>
              {validation.valid ? (
                <Tag color="green">Valid</Tag>
              ) : (
                <Tag color="red">{validation.errors.length} Errors</Tag>
              )}
              {validation.warnings.length > 0 && (
                <Tag color="orange">{validation.warnings.length} Warnings</Tag>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}