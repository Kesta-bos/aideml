/**
 * Profile Comparison Component
 * Side-by-side comparison of multiple profiles
 */

import React, { useMemo } from 'react';
import {
  Modal,
  Table,
  Typography,
  Tag,
  Space,
  Card,
  Divider,
  Tooltip,
  Alert,
} from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined,
  DiffOutlined,
} from '@ant-design/icons';

import { Profile, ConfigSchema } from '@/types/config';

const { Text, Title } = Typography;

interface ProfileComparisonProps {
  visible: boolean;
  onClose: () => void;
  profileIds: string[];
  profiles: Profile[];
}

interface ComparisonRow {
  key: string;
  setting: string;
  category: string;
  [key: string]: any; // Dynamic profile columns
}

export function ProfileComparison({ 
  visible, 
  onClose, 
  profileIds, 
  profiles 
}: ProfileComparisonProps) {
  const selectedProfiles = profiles.filter(p => profileIds.includes(p.id));

  const comparisonData = useMemo(() => {
    if (selectedProfiles.length === 0) return [];

    const rows: ComparisonRow[] = [];

    // Helper function to add a comparison row
    const addRow = (key: string, setting: string, category: string, getValue: (config: ConfigSchema) => any) => {
      const row: ComparisonRow = {
        key,
        setting,
        category,
      };

      selectedProfiles.forEach(profile => {
        row[profile.id] = getValue(profile.config);
      });

      // Check if values are different across profiles
      const values = selectedProfiles.map(p => getValue(p.config));
      const unique = [...new Set(values.map(v => JSON.stringify(v)))];
      row.isDifferent = unique.length > 1;

      rows.push(row);
    };

    // Project settings
    addRow('data_dir', 'Data Directory', 'Project', (config) => config.data_dir || 'Not set');
    addRow('goal', 'Task Goal', 'Project', (config) => config.goal || 'Not set');
    addRow('eval', 'Evaluation Criteria', 'Project', (config) => config.eval || 'Not set');
    addRow('preprocess_data', 'Preprocess Data', 'Project', (config) => config.preprocess_data);
    addRow('copy_data', 'Copy Data', 'Project', (config) => config.copy_data);

    // Agent settings
    addRow('agent.steps', 'Improvement Steps', 'Agent', (config) => config.agent.steps);
    addRow('agent.k_fold_validation', 'K-Fold Validation', 'Agent', (config) => config.agent.k_fold_validation);
    addRow('agent.expose_prediction', 'Expose Prediction', 'Agent', (config) => config.agent.expose_prediction);
    addRow('agent.data_preview', 'Data Preview', 'Agent', (config) => config.agent.data_preview);

    // Model settings
    addRow('agent.code.model', 'Code Model', 'Models', (config) => config.agent.code.model);
    addRow('agent.code.temp', 'Code Temperature', 'Models', (config) => config.agent.code.temp);
    addRow('agent.feedback.model', 'Feedback Model', 'Models', (config) => config.agent.feedback.model);
    addRow('agent.feedback.temp', 'Feedback Temperature', 'Models', (config) => config.agent.feedback.temp);
    addRow('report.model', 'Report Model', 'Models', (config) => config.report.model);
    addRow('report.temp', 'Report Temperature', 'Models', (config) => config.report.temp);

    // Search settings
    addRow('agent.search.num_drafts', 'Initial Drafts', 'Search', (config) => config.agent.search.num_drafts);
    addRow('agent.search.max_debug_depth', 'Max Debug Depth', 'Search', (config) => config.agent.search.max_debug_depth);
    addRow('agent.search.debug_prob', 'Debug Probability', 'Search', (config) => `${Math.round(config.agent.search.debug_prob * 100)}%`);

    // Execution settings
    addRow('exec.timeout', 'Execution Timeout', 'Execution', (config) => `${Math.floor(config.exec.timeout / 60)} minutes`);
    addRow('exec.agent_file_name', 'Script Filename', 'Execution', (config) => config.exec.agent_file_name);
    addRow('exec.format_tb_ipython', 'IPython Traceback', 'Execution', (config) => config.exec.format_tb_ipython);

    // Reporting settings
    addRow('generate_report', 'Generate Report', 'Reporting', (config) => config.generate_report);

    return rows;
  }, [selectedProfiles]);

  const renderValue = (value: any, isDifferent: boolean = false) => {
    if (typeof value === 'boolean') {
      return (
        <Tag 
          color={value ? 'green' : 'red'} 
          icon={value ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
        >
          {value ? 'Yes' : 'No'}
        </Tag>
      );
    }

    if (typeof value === 'number') {
      return <Text code>{value}</Text>;
    }

    if (typeof value === 'string') {
      if (value === 'Not set') {
        return <Text type="secondary" italic>{value}</Text>;
      }
      return <Text>{value}</Text>;
    }

    return <Text>{String(value)}</Text>;
  };

  const columns = [
    {
      title: 'Setting',
      dataIndex: 'setting',
      key: 'setting',
      width: 200,
      fixed: 'left' as const,
      render: (text: string, record: ComparisonRow) => (
        <Space>
          <Text strong>{text}</Text>
          {record.isDifferent && (
            <Tooltip title="Values differ across profiles">
              <DiffOutlined style={{ color: '#faad14' }} />
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      fixed: 'left' as const,
      render: (category: string) => (
        <Tag size="small">{category}</Tag>
      ),
    },
    ...selectedProfiles.map(profile => ({
      title: (
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontWeight: 'bold' }}>{profile.name}</div>
          <Tag color="blue" size="small">{profile.category}</Tag>
        </div>
      ),
      dataIndex: profile.id,
      key: profile.id,
      width: 200,
      render: (value: any, record: ComparisonRow) => (
        <div style={{ 
          padding: '4px',
          background: record.isDifferent ? '#fff7e6' : 'transparent',
          borderRadius: '4px'
        }}>
          {renderValue(value, record.isDifferent)}
        </div>
      ),
    })),
  ];

  const getDifferenceCount = () => {
    return comparisonData.filter(row => row.isDifferent).length;
  };

  return (
    <Modal
      title={
        <Space>
          <DiffOutlined />
          <span>Profile Comparison</span>
          <Tag color="blue">{selectedProfiles.length} profiles</Tag>
        </Space>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={Math.min(1200, 400 + selectedProfiles.length * 250)}
      style={{ top: 20 }}
    >
      {selectedProfiles.length === 0 ? (
        <Alert
          message="No profiles selected"
          description="Please select profiles to compare from the profile management page."
          type="warning"
          showIcon
        />
      ) : (
        <>
          {/* Summary */}
          <Card size="small" style={{ marginBottom: '16px' }}>
            <Space split={<Divider type="vertical" />}>
              <div>
                <Text type="secondary">Profiles:</Text>
                <br />
                <Text strong>{selectedProfiles.length}</Text>
              </div>
              <div>
                <Text type="secondary">Differences:</Text>
                <br />
                <Text strong style={{ color: getDifferenceCount() > 0 ? '#faad14' : '#52c41a' }}>
                  {getDifferenceCount()} settings
                </Text>
              </div>
              <div>
                <Text type="secondary">Total Settings:</Text>
                <br />
                <Text strong>{comparisonData.length}</Text>
              </div>
            </Space>
          </Card>

          {/* Profile Headers */}
          <div style={{ marginBottom: '16px' }}>
            <Title level={5}>Comparing Profiles:</Title>
            <Space wrap>
              {selectedProfiles.map(profile => (
                <Card key={profile.id} size="small" style={{ minWidth: '200px' }}>
                  <Card.Meta
                    title={profile.name}
                    description={
                      <div>
                        <Tag color="blue" size="small">{profile.category}</Tag>
                        <br />
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {profile.description}
                        </Text>
                      </div>
                    }
                  />
                </Card>
              ))}
            </Space>
          </div>

          {/* Comparison Table */}
          <Table
            columns={columns}
            dataSource={comparisonData}
            pagination={false}
            scroll={{ x: 'max-content', y: 400 }}
            size="small"
            rowClassName={(record) => record.isDifferent ? 'comparison-row-different' : ''}
          />

          {/* Legend */}
          <div style={{ 
            marginTop: '16px', 
            padding: '12px', 
            background: '#f6f8fa', 
            borderRadius: '6px',
            border: '1px solid #e1e8ed'
          }}>
            <Space>
              <InfoCircleOutlined style={{ color: '#1890ff' }} />
              <Text style={{ fontSize: '12px' }}>
                <strong>Legend:</strong> Highlighted rows indicate settings that differ between profiles. 
                Use this comparison to understand the key differences and decide which profile to use.
              </Text>
            </Space>
          </div>
        </>
      )}

      <style jsx>{`
        .comparison-row-different {
          background-color: #fff7e6;
        }
        .comparison-row-different:hover {
          background-color: #fff1d6 !important;
        }
      `}</style>
    </Modal>
  );
}