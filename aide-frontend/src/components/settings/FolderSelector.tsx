/**
 * Folder Selector Component
 * File system browser for selecting directories
 */

import React, { useState } from 'react';
import {
  Input,
  Button,
  Modal,
  Tree,
  Typography,
  Space,
  Alert,
  Spin,
} from 'antd';
import {
  FolderOutlined,
  FolderOpenOutlined,
  SearchOutlined,
} from '@ant-design/icons';

const { Text } = Typography;
const { DirectoryTree } = Tree;

interface FolderSelectorProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
}

interface TreeNode {
  title: string;
  key: string;
  icon: React.ReactNode;
  children?: TreeNode[];
  isLeaf?: boolean;
}

export function FolderSelector({
  value,
  onChange,
  placeholder = "Select folder..."
}: FolderSelectorProps) {
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedPath, setSelectedPath] = useState<string>(value || '');
  const [treeData, setTreeData] = useState<TreeNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedKeys, setExpandedKeys] = useState<string[]>([]);

  // Mock file system tree (in real implementation, this would come from the backend)
  const mockFileSystem: TreeNode[] = [
    {
      title: 'Documents',
      key: '/home/user/Documents',
      icon: <FolderOutlined />,
      children: [
        {
          title: 'Projects',
          key: '/home/user/Documents/Projects',
          icon: <FolderOutlined />,
          children: [
            {
              title: 'ML_Project_1',
              key: '/home/user/Documents/Projects/ML_Project_1',
              icon: <FolderOutlined />,
              children: [
                {
                  title: 'data',
                  key: '/home/user/Documents/Projects/ML_Project_1/data',
                  icon: <FolderOutlined />,
                  isLeaf: true,
                },
                {
                  title: 'models',
                  key: '/home/user/Documents/Projects/ML_Project_1/models',
                  icon: <FolderOutlined />,
                  isLeaf: true,
                },
              ],
            },
            {
              title: 'House_Prices',
              key: '/home/user/Documents/Projects/House_Prices',
              icon: <FolderOutlined />,
              children: [
                {
                  title: 'train.csv',
                  key: '/home/user/Documents/Projects/House_Prices/train.csv',
                  icon: <FolderOutlined />,
                  isLeaf: true,
                },
              ],
            },
          ],
        },
        {
          title: 'Datasets',
          key: '/home/user/Documents/Datasets',
          icon: <FolderOutlined />,
          children: [
            {
              title: 'iris',
              key: '/home/user/Documents/Datasets/iris',
              icon: <FolderOutlined />,
              isLeaf: true,
            },
            {
              title: 'titanic',
              key: '/home/user/Documents/Datasets/titanic',
              icon: <FolderOutlined />,
              isLeaf: true,
            },
          ],
        },
      ],
    },
    {
      title: 'Desktop',
      key: '/home/user/Desktop',
      icon: <FolderOutlined />,
      children: [
        {
          title: 'temp_data',
          key: '/home/user/Desktop/temp_data',
          icon: <FolderOutlined />,
          isLeaf: true,
        },
      ],
    },
  ];

  const handleOpenModal = () => {
    setTreeData(mockFileSystem);
    setModalVisible(true);
    if (value) {
      setSelectedPath(value);
      // Auto-expand to show current selection
      const pathParts = value.split('/').filter(Boolean);
      const expanded: string[] = [];
      let currentPath = '';
      pathParts.forEach(part => {
        currentPath += '/' + part;
        expanded.push(currentPath);
      });
      setExpandedKeys(expanded);
    }
  };

  const handleModalOk = () => {
    onChange?.(selectedPath);
    setModalVisible(false);
  };

  const handleModalCancel = () => {
    setSelectedPath(value || '');
    setModalVisible(false);
  };

  const handleTreeSelect = (selectedKeys: React.Key[]) => {
    if (selectedKeys.length > 0) {
      setSelectedPath(selectedKeys[0] as string);
    }
  };

  const handleExpand = (expandedKeys: React.Key[]) => {
    setExpandedKeys(expandedKeys as string[]);
  };

  // Load directory contents (mock implementation)
  const onLoadData = ({ key, children }: any): Promise<void> => {
    return new Promise((resolve) => {
      if (children) {
        resolve();
        return;
      }

      setLoading(true);
      
      // Simulate API call delay
      setTimeout(() => {
        setTreeData((origin) => updateTreeData(origin, key, []));
        setLoading(false);
        resolve();
      }, 500);
    });
  };

  const updateTreeData = (list: TreeNode[], key: React.Key, children: TreeNode[]): TreeNode[] => {
    return list.map((node) => {
      if (node.key === key) {
        return {
          ...node,
          children,
        };
      }
      if (node.children) {
        return {
          ...node,
          children: updateTreeData(node.children, key, children),
        };
      }
      return node;
    });
  };

  const handleManualInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange?.(e.target.value);
  };

  return (
    <>
      <Input.Group compact>
        <Input
          style={{ width: 'calc(100% - 40px)' }}
          placeholder={placeholder}
          value={value}
          onChange={handleManualInput}
          prefix={<FolderOutlined />}
        />
        <Button
          style={{ width: '40px' }}
          icon={<SearchOutlined />}
          onClick={handleOpenModal}
          title="Browse folders"
        />
      </Input.Group>

      <Modal
        title={
          <Space>
            <FolderOpenOutlined />
            Select Folder
          </Space>
        }
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={600}
        bodyStyle={{ height: '400px', overflow: 'auto' }}
        okButtonProps={{ disabled: !selectedPath }}
      >
        <div style={{ marginBottom: '16px' }}>
          <Text type="secondary">Selected path:</Text>
          <br />
          <Text code={!!selectedPath} style={{ wordBreak: 'break-all' }}>
            {selectedPath || 'No folder selected'}
          </Text>
        </div>

        <Alert
          message="Folder Browser"
          description="Navigate through the directory structure and click on a folder to select it."
          type="info"
          showIcon
          style={{ marginBottom: '16px' }}
        />

        <Spin spinning={loading}>
          <DirectoryTree
            multiple={false}
            showIcon
            defaultExpandedKeys={expandedKeys}
            expandedKeys={expandedKeys}
            onExpand={handleExpand}
            selectedKeys={selectedPath ? [selectedPath] : []}
            onSelect={handleTreeSelect}
            treeData={treeData}
            loadData={onLoadData}
            style={{ 
              background: '#fafafa',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #d9d9d9'
            }}
          />
        </Spin>

        <div style={{ marginTop: '16px', padding: '8px', background: '#f6f8fa', borderRadius: '4px' }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            💡 Tip: You can also type the path directly in the input field above the modal.
          </Text>
        </div>
      </Modal>
    </>
  );
}