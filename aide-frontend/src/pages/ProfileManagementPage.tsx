/**
 * Profile Management Page
 * Comprehensive profile management interface
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
  Modal,
  Form,
  Input,
  Select,
  Tag,
  Empty,
  message,
  Pagination,
  Radio,
  Dropdown,
  Tooltip,
  Alert,
  Divider,
} from 'antd';
import {
  PlusOutlined,
  SettingOutlined,
  EditOutlined,
  DeleteOutlined,
  CopyOutlined,
  PlayCircleOutlined,
  AppstoreOutlined,
  UnorderedListOutlined,
  FilterOutlined,
  ExportOutlined,
  SortAscendingOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

import { ProfileCard } from '@/components/settings/ProfileCard';
import { TemplateGallery } from '@/components/settings/TemplateGallery';
import { ProfileComparison } from '@/components/settings/ProfileComparison';
import { useConfigStore, useConfigProfiles, useConfigTemplates } from '@/stores/configStore';
import { Profile, Template } from '@/types/config';

dayjs.extend(relativeTime);

const { Content } = Layout;
const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

type ViewMode = 'grid' | 'list';
type SortBy = 'name' | 'created' | 'updated' | 'category';

export function ProfileManagementPage() {
  const navigate = useNavigate();
  const [form] = Form.useForm();

  // UI State
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [sortBy, setSortBy] = useState<SortBy>('updated');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [searchText, setSearchText] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(12);

  // Modal states
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [compareModalVisible, setCompareModalVisible] = useState(false);
  const [selectedProfileId, setSelectedProfileId] = useState<string | null>(null);
  const [selectedProfiles, setSelectedProfiles] = useState<string[]>([]);

  // Store state
  const {
    currentConfig,
    loadProfiles,
    loadTemplates,
    createProfile,
    updateProfile,
    deleteProfile,
    activateProfile,
    duplicateProfile,
  } = useConfigStore();

  const { profiles, activeProfile } = useConfigProfiles();
  const { templates } = useConfigTemplates();

  // Load data on mount
  useEffect(() => {
    const initializeData = async () => {
      try {
        await Promise.all([
          loadProfiles(),
          loadTemplates(),
        ]);
      } catch (error) {
        console.error('Failed to initialize profile data:', error);
        message.error('Failed to load profile data');
      }
    };

    initializeData();
  }, [loadProfiles, loadTemplates]);

  // Get unique categories for filtering
  const categories = ['all', ...new Set(profiles.map(p => p.category))];

  // Filter and sort profiles
  const filteredProfiles = profiles
    .filter(profile => {
      if (filterCategory !== 'all' && profile.category !== filterCategory) return false;
      if (searchText && !profile.name.toLowerCase().includes(searchText.toLowerCase()) &&
          !profile.description.toLowerCase().includes(searchText.toLowerCase())) return false;
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'created':
          return dayjs(b.created_at).valueOf() - dayjs(a.created_at).valueOf();
        case 'updated':
          return dayjs(b.updated_at).valueOf() - dayjs(a.updated_at).valueOf();
        case 'category':
          return a.category.localeCompare(b.category);
        default:
          return 0;
      }
    });

  // Paginated profiles
  const paginatedProfiles = filteredProfiles.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  const handleCreateProfile = async (values: any) => {
    try {
      await createProfile(values.name, values.description, values.category);
      message.success('Profile created successfully');
      setCreateModalVisible(false);
      form.resetFields();
    } catch (error) {
      message.error('Failed to create profile');
    }
  };

  const handleEditProfile = async (values: any) => {
    if (!selectedProfileId) return;

    try {
      await updateProfile(selectedProfileId, values);
      message.success('Profile updated successfully');
      setEditModalVisible(false);
      setSelectedProfileId(null);
      form.resetFields();
    } catch (error) {
      message.error('Failed to update profile');
    }
  };

  const handleDeleteProfile = (profileId: string) => {
    Modal.confirm({
      title: 'Delete Profile',
      content: 'Are you sure you want to delete this profile? This action cannot be undone.',
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await deleteProfile(profileId);
          message.success('Profile deleted successfully');
        } catch (error) {
          message.error('Failed to delete profile');
        }
      },
    });
  };

  const handleActivateProfile = async (profileId: string) => {
    try {
      await activateProfile(profileId);
      message.success('Profile activated successfully');
      navigate('/settings');
    } catch (error) {
      message.error('Failed to activate profile');
    }
  };

  const handleDuplicateProfile = async (profileId: string) => {
    const profile = profiles.find(p => p.id === profileId);
    if (!profile) return;

    const newName = `${profile.name} (Copy)`;
    try {
      await duplicateProfile(profileId, newName);
      message.success('Profile duplicated successfully');
    } catch (error) {
      message.error('Failed to duplicate profile');
    }
  };

  const handleEditClick = (profile: Profile) => {
    setSelectedProfileId(profile.id);
    form.setFieldsValue({
      name: profile.name,
      description: profile.description,
      category: profile.category,
      tags: profile.tags,
    });
    setEditModalVisible(true);
  };

  const handleCompareProfiles = () => {
    if (selectedProfiles.length < 2) {
      message.warning('Please select at least 2 profiles to compare');
      return;
    }
    setCompareModalVisible(true);
  };

  const toggleProfileSelection = (profileId: string) => {
    setSelectedProfiles(prev => {
      if (prev.includes(profileId)) {
        return prev.filter(id => id !== profileId);
      }
      return [...prev, profileId];
    });
  };

  const dropdownMenuItems = [
    {
      key: 'compare',
      label: 'Compare Selected',
      icon: <FilterOutlined />,
      disabled: selectedProfiles.length < 2,
      onClick: handleCompareProfiles,
    },
    {
      key: 'export',
      label: 'Export Selected',
      icon: <ExportOutlined />,
      disabled: selectedProfiles.length === 0,
    },
  ];

  return (
    <>
      <Helmet>
        <title>Profile Management - AIDE ML Configuration</title>
        <meta name="description" content="Manage AIDE ML configuration profiles and templates" />
      </Helmet>

      <Layout style={{ minHeight: 'calc(100vh - 64px)', background: '#f5f5f5' }}>
        <Content style={{ padding: '24px' }}>
          {/* Header */}
          <div style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <Title level={2} style={{ margin: 0 }}>
                  <SettingOutlined style={{ marginRight: '8px' }} />
                  Profile Management
                </Title>
                <Text type="secondary">
                  Create, manage, and organize your AIDE configuration profiles
                </Text>
              </div>

              <Space>
                <Button onClick={() => navigate('/settings')}>
                  Back to Settings
                </Button>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setCreateModalVisible(true)}
                >
                  Create Profile
                </Button>
              </Space>
            </div>

            {/* Controls */}
            <Card size="small" style={{ marginBottom: '16px' }}>
              <Row gutter={16} align="middle">
                <Col flex="auto">
                  <Space>
                    <Input.Search
                      placeholder="Search profiles..."
                      value={searchText}
                      onChange={(e) => setSearchText(e.target.value)}
                      style={{ width: 200 }}
                    />
                    <Select
                      value={filterCategory}
                      onChange={setFilterCategory}
                      style={{ width: 120 }}
                    >
                      {categories.map(category => (
                        <Option key={category} value={category}>
                          {category === 'all' ? 'All Categories' : category}
                        </Option>
                      ))}
                    </Select>
                    <Select
                      value={sortBy}
                      onChange={setSortBy}
                      style={{ width: 120 }}
                      suffixIcon={<SortAscendingOutlined />}
                    >
                      <Option value="updated">Last Updated</Option>
                      <Option value="created">Created Date</Option>
                      <Option value="name">Name</Option>
                      <Option value="category">Category</Option>
                    </Select>
                  </Space>
                </Col>
                
                <Col>
                  <Space>
                    {selectedProfiles.length > 0 && (
                      <>
                        <Text type="secondary">
                          {selectedProfiles.length} selected
                        </Text>
                        <Dropdown menu={{ items: dropdownMenuItems }} trigger={['click']}>
                          <Button>Actions</Button>
                        </Dropdown>
                      </>
                    )}
                    <Radio.Group
                      value={viewMode}
                      onChange={(e) => setViewMode(e.target.value)}
                    >
                      <Radio.Button value="grid">
                        <AppstoreOutlined />
                      </Radio.Button>
                      <Radio.Button value="list">
                        <UnorderedListOutlined />
                      </Radio.Button>
                    </Radio.Group>
                  </Space>
                </Col>
              </Row>
            </Card>

            {/* Active Profile Alert */}
            {activeProfile && (
              <Alert
                message={`Active Profile: ${activeProfile.name}`}
                description={activeProfile.description}
                type="info"
                showIcon
                style={{ marginBottom: '16px' }}
                action={
                  <Button size="small" onClick={() => navigate('/settings')}>
                    Edit Settings
                  </Button>
                }
              />
            )}
          </div>

          {/* Profiles Grid/List */}
          {filteredProfiles.length === 0 ? (
            <Card>
              <Empty
                description="No profiles found"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              >
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setCreateModalVisible(true)}
                >
                  Create Your First Profile
                </Button>
              </Empty>
            </Card>
          ) : (
            <>
              {viewMode === 'grid' ? (
                <Row gutter={[16, 16]}>
                  {paginatedProfiles.map(profile => (
                    <Col xs={24} sm={12} lg={8} xl={6} key={profile.id}>
                      <ProfileCard
                        profile={profile}
                        isActive={activeProfile?.id === profile.id}
                        isSelected={selectedProfiles.includes(profile.id)}
                        onActivate={() => handleActivateProfile(profile.id)}
                        onEdit={() => handleEditClick(profile)}
                        onDelete={() => handleDeleteProfile(profile.id)}
                        onDuplicate={() => handleDuplicateProfile(profile.id)}
                        onSelect={() => toggleProfileSelection(profile.id)}
                      />
                    </Col>
                  ))}
                </Row>
              ) : (
                <Card>
                  {/* List view implementation would go here */}
                  <Text>List view coming soon...</Text>
                </Card>
              )}

              {/* Pagination */}
              {filteredProfiles.length > pageSize && (
                <div style={{ textAlign: 'center', marginTop: '24px' }}>
                  <Pagination
                    current={currentPage}
                    total={filteredProfiles.length}
                    pageSize={pageSize}
                    onChange={setCurrentPage}
                    showSizeChanger={false}
                    showQuickJumper
                    showTotal={(total, range) =>
                      `${range[0]}-${range[1]} of ${total} profiles`
                    }
                  />
                </div>
              )}
            </>
          )}

          <Divider />

          {/* Template Gallery */}
          <TemplateGallery templates={templates} />
        </Content>
      </Layout>

      {/* Create Profile Modal */}
      <Modal
        title="Create New Profile"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="Create Profile"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateProfile}
        >
          <Form.Item
            name="name"
            label="Profile Name"
            rules={[{ required: true, message: 'Please enter a profile name' }]}
          >
            <Input placeholder="e.g., Quick Experiment Setup" />
          </Form.Item>

          <Form.Item
            name="description"
            label="Description"
            rules={[{ required: true, message: 'Please enter a description' }]}
          >
            <TextArea 
              rows={3} 
              placeholder="Describe what this profile is optimized for..."
            />
          </Form.Item>

          <Form.Item
            name="category"
            label="Category"
            rules={[{ required: true, message: 'Please select a category' }]}
          >
            <Select placeholder="Select category">
              <Option value="experiment">Experiment</Option>
              <Option value="production">Production</Option>
              <Option value="research">Research</Option>
              <Option value="education">Education</Option>
              <Option value="custom">Custom</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="tags"
            label="Tags (Optional)"
          >
            <Select
              mode="tags"
              placeholder="Add tags to organize your profile"
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Form>

        <Alert
          message="Note"
          description="The profile will be created with your current configuration settings."
          type="info"
          showIcon
          style={{ marginTop: '16px' }}
        />
      </Modal>

      {/* Edit Profile Modal */}
      <Modal
        title="Edit Profile"
        open={editModalVisible}
        onCancel={() => {
          setEditModalVisible(false);
          setSelectedProfileId(null);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="Update Profile"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleEditProfile}
        >
          <Form.Item
            name="name"
            label="Profile Name"
            rules={[{ required: true, message: 'Please enter a profile name' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="description"
            label="Description"
            rules={[{ required: true, message: 'Please enter a description' }]}
          >
            <TextArea rows={3} />
          </Form.Item>

          <Form.Item
            name="category"
            label="Category"
            rules={[{ required: true, message: 'Please select a category' }]}
          >
            <Select>
              <Option value="experiment">Experiment</Option>
              <Option value="production">Production</Option>
              <Option value="research">Research</Option>
              <Option value="education">Education</Option>
              <Option value="custom">Custom</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="tags"
            label="Tags"
          >
            <Select
              mode="tags"
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* Profile Comparison Modal */}
      <ProfileComparison
        visible={compareModalVisible}
        onClose={() => setCompareModalVisible(false)}
        profileIds={selectedProfiles}
        profiles={profiles}
      />
    </>
  );
}