/**
 * Profile Card Component
 * Displays profile information with action buttons
 */

import React from 'react';
import {
  Card,
  Typography,
  Tag,
  Space,
  Button,
  Tooltip,
  Checkbox,
  Badge,
  Avatar,
} from 'antd';
import {
  SettingOutlined,
  EditOutlined,
  DeleteOutlined,
  CopyOutlined,
  PlayCircleOutlined,
  UserOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';

import { Profile } from '@/types/config';

const { Text, Title } = Typography;
const { Meta } = Card;

interface ProfileCardProps {
  profile: Profile;
  isActive?: boolean;
  isSelected?: boolean;
  onActivate?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  onDuplicate?: () => void;
  onSelect?: () => void;
}

export function ProfileCard({
  profile,
  isActive = false,
  isSelected = false,
  onActivate,
  onEdit,
  onDelete,
  onDuplicate,
  onSelect,
}: ProfileCardProps) {
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      experiment: 'blue',
      production: 'green',
      research: 'purple',
      education: 'orange',
      custom: 'gray',
    };
    return colors[category] || 'default';
  };

  const getCategoryIcon = (category: string) => {
    // Return appropriate icon based on category
    return '⚙️';
  };

  const actions = [
    <Tooltip title="Edit Profile" key="edit">
      <Button
        type="text"
        icon={<EditOutlined />}
        onClick={(e) => {
          e.stopPropagation();
          onEdit?.();
        }}
      />
    </Tooltip>,
    <Tooltip title="Duplicate Profile" key="duplicate">
      <Button
        type="text"
        icon={<CopyOutlined />}
        onClick={(e) => {
          e.stopPropagation();
          onDuplicate?.();
        }}
      />
    </Tooltip>,
    <Tooltip title="Delete Profile" key="delete">
      <Button
        type="text"
        danger
        icon={<DeleteOutlined />}
        onClick={(e) => {
          e.stopPropagation();
          onDelete?.();
        }}
      />
    </Tooltip>,
  ];

  if (!isActive) {
    actions.unshift(
      <Tooltip title="Activate Profile" key="activate">
        <Button
          type="text"
          icon={<PlayCircleOutlined />}
          onClick={(e) => {
            e.stopPropagation();
            onActivate?.();
          }}
          style={{ color: '#52c41a' }}
        />
      </Tooltip>
    );
  }

  return (
    <Badge.Ribbon 
      text={isActive ? 'Active' : undefined} 
      color="green" 
      style={{ display: isActive ? 'block' : 'none' }}
    >
      <Card
        hoverable
        className={`profile-card ${isActive ? 'active' : ''} ${isSelected ? 'selected' : ''}`}
        actions={actions}
        onClick={onSelect}
        style={{
          height: '100%',
          border: isActive ? '2px solid #52c41a' : isSelected ? '2px solid #1890ff' : '1px solid #d9d9d9',
          boxShadow: isActive ? '0 4px 12px rgba(82, 196, 26, 0.15)' : undefined,
          transition: 'all 0.3s ease',
        }}
        bodyStyle={{ padding: '16px' }}
        extra={
          onSelect && (
            <Checkbox
              checked={isSelected}
              onChange={(e) => {
                e.stopPropagation();
                onSelect();
              }}
              onClick={(e) => e.stopPropagation()}
            />
          )
        }
      >
        <Meta
          avatar={
            <Avatar 
              icon={<UserOutlined />} 
              style={{ 
                backgroundColor: getCategoryColor(profile.category),
                fontSize: '18px'
              }}
            >
              {getCategoryIcon(profile.category)}
            </Avatar>
          }
          title={
            <div>
              <Title level={5} style={{ margin: 0, marginBottom: '4px' }}>
                {profile.name}
              </Title>
              <Space size="small">
                <Tag color={getCategoryColor(profile.category)} size="small">
                  {profile.category}
                </Tag>
                {isActive && (
                  <Tag color="green" size="small">
                    Active
                  </Tag>
                )}
              </Space>
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
                {profile.description}
              </Text>
            </div>
          }
        />

        {/* Tags */}
        {profile.tags && profile.tags.length > 0 && (
          <div style={{ marginTop: '12px', marginBottom: '8px' }}>
            {profile.tags.slice(0, 3).map(tag => (
              <Tag key={tag} size="small" style={{ margin: '2px' }}>
                {tag}
              </Tag>
            ))}
            {profile.tags.length > 3 && (
              <Tag size="small" style={{ margin: '2px' }}>
                +{profile.tags.length - 3}
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
          <Space size="small">
            <ClockCircleOutlined style={{ fontSize: '12px', color: '#666' }} />
            <Text type="secondary" style={{ fontSize: '11px' }}>
              {dayjs(profile.updated_at).fromNow()}
            </Text>
          </Space>
          
          <Text type="secondary" style={{ fontSize: '11px' }}>
            Created {dayjs(profile.created_at).format('MMM DD')}
          </Text>
        </div>
      </Card>
    </Badge.Ribbon>
  );
}