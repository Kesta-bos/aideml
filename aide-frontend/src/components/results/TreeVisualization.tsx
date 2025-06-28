import React, { useState, useEffect } from 'react';
import { Card, Empty, Spin, Button, message, Space, Typography } from 'antd';
import { ReloadOutlined, FullscreenOutlined, EyeOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title } = Typography;

interface TreeVisualizationProps {
  experimentId?: string;
  htmlContent?: string;
}

export function TreeVisualization({ experimentId, htmlContent }: TreeVisualizationProps) {
  const [loading, setLoading] = useState(false);
  const [visualizationHtml, setVisualizationHtml] = useState<string | null>(htmlContent || null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (experimentId && !htmlContent) {
      loadVisualization();
    }
  }, [experimentId, htmlContent]);

  const loadVisualization = async () => {
    if (!experimentId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/experiments/${experimentId}/tree-visualization`,
        { 
          headers: { 'Accept': 'text/html' },
          timeout: 30000 
        }
      );
      
      setVisualizationHtml(response.data);
    } catch (err: any) {
      console.error('Error loading tree visualization:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to load visualization');
      message.error('Failed to load tree visualization');
    } finally {
      setLoading(false);
    }
  };

  const loadDemoVisualization = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/visualizations/demo-tree`,
        { 
          headers: { 'Accept': 'text/html' },
          timeout: 30000 
        }
      );
      
      setVisualizationHtml(response.data);
      message.success('Demo visualization loaded');
    } catch (err: any) {
      console.error('Error loading demo visualization:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to load demo');
      message.error('Failed to load demo visualization');
    } finally {
      setLoading(false);
    }
  };

  const openInNewWindow = () => {
    if (!visualizationHtml) return;

    const newWindow = window.open('', '_blank', 'width=1200,height=800');
    if (newWindow) {
      newWindow.document.write(visualizationHtml);
      newWindow.document.close();
    } else {
      message.error('Unable to open visualization in new window. Please check popup settings.');
    }
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: 400 
        }}>
          <Spin size="large" />
        </div>
      );
    }

    if (error) {
      return (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Empty 
            description={
              <div>
                <p>Failed to load tree visualization</p>
                <p style={{ color: '#ff4d4f', fontSize: 12 }}>{error}</p>
              </div>
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
          <Space style={{ marginTop: 16 }}>
            {experimentId && (
              <Button onClick={loadVisualization} icon={<ReloadOutlined />}>
                Retry
              </Button>
            )}
            <Button onClick={loadDemoVisualization} icon={<EyeOutlined />}>
              View Demo
            </Button>
          </Space>
        </div>
      );
    }

    if (!visualizationHtml) {
      return (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Empty 
            description="Tree visualization not available"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
          <Button 
            type="primary" 
            onClick={loadDemoVisualization} 
            icon={<EyeOutlined />}
            style={{ marginTop: 16 }}
          >
            View Demo Visualization
          </Button>
        </div>
      );
    }

    return (
      <div 
        className="tree-visualization"
        style={{ 
          height: '600px', 
          width: '100%',
          border: '1px solid #d9d9d9',
          borderRadius: 6,
          overflow: 'hidden',
          background: '#f2f0e7'
        }}
      >
        <iframe
          srcDoc={visualizationHtml}
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
            borderRadius: 6
          }}
          title="AIDE Tree Visualization"
          sandbox="allow-scripts allow-same-origin"
        />
      </div>
    );
  };

  return (
    <Card 
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={4} style={{ margin: 0 }}>Experiment Tree</Title>
          <Space>
            {experimentId && (
              <Button 
                size="small" 
                icon={<ReloadOutlined />} 
                onClick={loadVisualization}
                loading={loading}
              >
                Refresh
              </Button>
            )}
            {visualizationHtml && (
              <Button 
                size="small" 
                icon={<FullscreenOutlined />} 
                onClick={openInNewWindow}
              >
                Full Screen
              </Button>
            )}
            {!visualizationHtml && !loading && (
              <Button 
                size="small" 
                type="primary"
                icon={<EyeOutlined />} 
                onClick={loadDemoVisualization}
              >
                Demo
              </Button>
            )}
          </Space>
        </div>
      }
      bodyStyle={{ padding: 16 }}
    >
      {renderContent()}
    </Card>
  );
}
