import React, { useState, useEffect } from 'react';
import { 
  Modal, 
  Card, 
  Row, 
  Col, 
  Typography, 
  Button, 
  Spin, 
  message, 
  Tag, 
  Descriptions,
  List,
  Tooltip,
  Space
} from 'antd';
import { 
  FileTextOutlined, 
  DownloadOutlined, 
  DatabaseOutlined,
  InfoCircleOutlined,
  FileOutlined
} from '@ant-design/icons';
import { exampleTaskAPI, fileAPI } from '@/services/api';

const { Title, Text, Paragraph } = Typography;

interface ExampleTask {
  id: string;
  title: string;
  filename: string;
  sections: {
    goal?: string;
    background?: string;
    evaluation?: string;
    evaluation_metric?: string;
    data_description?: string;
  };
  data_files: Array<{
    name: string;
    size: number;
    type: string;
    path: string;
    preview?: string;
  }>;
  file_count: number;
  has_data: boolean;
}

interface ExampleTaskSelectorProps {
  visible: boolean;
  onClose: () => void;
  onSelect: (task: ExampleTask, uploadedFiles: any[]) => void;
}

export function ExampleTaskSelector({ visible, onClose, onSelect }: ExampleTaskSelectorProps) {
  const [tasks, setTasks] = useState<ExampleTask[]>([]);
  const [selectedTask, setSelectedTask] = useState<ExampleTask | null>(null);
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (visible) {
      loadTasks();
    }
  }, [visible]);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const data = await exampleTaskAPI.list();
      setTasks(data);
    } catch (error) {
      message.error('Failed to load example tasks');
      console.error('Error loading tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTaskDetails = async (taskId: string) => {
    setDetailLoading(true);
    try {
      const taskDetail = await exampleTaskAPI.get(taskId);
      setSelectedTask(taskDetail);
    } catch (error) {
      message.error('Failed to load task details');
      console.error('Error loading task details:', error);
    } finally {
      setDetailLoading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'csv':
        return <DatabaseOutlined style={{ color: '#52c41a' }} />;
      case 'txt':
      case 'md':
        return <FileTextOutlined style={{ color: '#1890ff' }} />;
      default:
        return <FileOutlined style={{ color: '#8c8c8c' }} />;
    }
  };

  const handleSelectTask = async (task: ExampleTask) => {
    if (!task.has_data) {
      message.warning('This task has no data files to upload');
      return;
    }

    setUploading(true);
    try {
      // Download all files from the example task and upload them
      const uploadPromises = task.data_files.map(async (file) => {
        try {
          const blob = await exampleTaskAPI.downloadFile(task.id, file.name);
          const fileObj = new File([blob], file.name, { type: blob.type });
          return fileObj;
        } catch (error) {
          console.error(`Error downloading file ${file.name}:`, error);
          throw error;
        }
      });

      const files = await Promise.all(uploadPromises);
      const uploadedFiles = await fileAPI.upload(files);

      message.success(`Selected "${task.title}" and uploaded ${uploadedFiles.length} files`);
      onSelect(task, uploadedFiles);
      onClose();
    } catch (error) {
      message.error('Failed to upload task files');
      console.error('Error selecting task:', error);
    } finally {
      setUploading(false);
    }
  };

  const renderTaskCard = (task: ExampleTask) => (
    <Card
      key={task.id}
      hoverable
      onClick={() => loadTaskDetails(task.id)}
      style={{ marginBottom: 16 }}
      actions={[
        <Button
          type="primary"
          icon={<DatabaseOutlined />}
          loading={uploading}
          disabled={!task.has_data}
          onClick={(e) => {
            e.stopPropagation();
            handleSelectTask(task);
          }}
        >
          Use This Task
        </Button>
      ]}
    >
      <Card.Meta
        title={
          <Space>
            <Text strong>{task.title}</Text>
            {task.has_data && (
              <Tag color="green">{task.file_count} files</Tag>
            )}
          </Space>
        }
        description={
          <div>
            {task.sections.goal && (
              <Paragraph ellipsis={{ rows: 2 }}>
                {task.sections.goal}
              </Paragraph>
            )}
            {!task.has_data && (
              <Text type="warning">No data files available</Text>
            )}
          </div>
        }
      />
    </Card>
  );

  const renderTaskDetail = () => {
    if (!selectedTask) return null;

    return (
      <div style={{ padding: '0 24px' }}>
        <Title level={4}>{selectedTask.title}</Title>
        
        {selectedTask.sections.goal && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>Goal</Title>
            <Paragraph>{selectedTask.sections.goal}</Paragraph>
          </div>
        )}

        {selectedTask.sections.background && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>Background</Title>
            <Paragraph>{selectedTask.sections.background}</Paragraph>
          </div>
        )}

        {(selectedTask.sections.evaluation || selectedTask.sections.evaluation_metric) && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>Evaluation</Title>
            <Paragraph>
              {selectedTask.sections.evaluation || selectedTask.sections.evaluation_metric}
            </Paragraph>
          </div>
        )}

        {selectedTask.data_files.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>Data Files ({selectedTask.data_files.length})</Title>
            <List
              size="small"
              dataSource={selectedTask.data_files}
              renderItem={(file) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={getFileIcon(file.type)}
                    title={
                      <Space>
                        <Text>{file.name}</Text>
                        <Text type="secondary">({formatFileSize(file.size)})</Text>
                      </Space>
                    }
                    description={
                      file.preview && (
                        <div style={{ 
                          background: '#f5f5f5', 
                          padding: 8, 
                          borderRadius: 4,
                          fontSize: 12,
                          fontFamily: 'monospace',
                          marginTop: 8
                        }}>
                          {file.preview}
                        </div>
                      )
                    }
                  />
                </List.Item>
              )}
            />
          </div>
        )}

        <div style={{ textAlign: 'right', marginTop: 24 }}>
          <Space>
            <Button onClick={() => setSelectedTask(null)}>
              Back to List
            </Button>
            <Button
              type="primary"
              icon={<DatabaseOutlined />}
              loading={uploading}
              disabled={!selectedTask.has_data}
              onClick={() => handleSelectTask(selectedTask)}
            >
              Use This Task
            </Button>
          </Space>
        </div>
      </div>
    );
  };

  return (
    <Modal
      title={
        <Space>
          <DatabaseOutlined />
          Example Tasks
          <Tooltip title="Choose from pre-built example tasks with datasets">
            <InfoCircleOutlined style={{ color: '#8c8c8c' }} />
          </Tooltip>
        </Space>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
      bodyStyle={{ padding: selectedTask ? 0 : 24 }}
      style={{ top: 20 }}
    >
      <Spin spinning={loading || detailLoading}>
        {!selectedTask ? (
          <div>
            {tasks.length === 0 && !loading ? (
              <div style={{ textAlign: 'center', padding: 48 }}>
                <Text type="secondary">No example tasks available</Text>
              </div>
            ) : (
              <div style={{ maxHeight: 600, overflowY: 'auto' }}>
                {tasks.map(renderTaskCard)}
              </div>
            )}
          </div>
        ) : (
          <div style={{ maxHeight: 600, overflowY: 'auto' }}>
            {renderTaskDetail()}
          </div>
        )}
      </Spin>
    </Modal>
  );
}