import React, { useState } from 'react';
import { Layout, Typography, Button, Drawer, Menu } from 'antd';
import { SettingOutlined, MenuOutlined, ExperimentOutlined, BarChartOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { ApiKeySettings } from '@/components/settings/ApiKeySettings';

const { Header, Content } = Layout;
const { Title } = Typography;

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const [settingsVisible, setSettingsVisible] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    {
      key: '/',
      icon: <ExperimentOutlined />,
      label: 'Experiments',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header 
        style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          padding: '0 24px',
          background: '#fff',
          borderBottom: '1px solid #f0f0f0',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Title 
            level={3} 
            style={{ 
              margin: 0, 
              color: '#0D0F18',
              fontWeight: 600
            }}
          >
            AIDE: Machine Learning Engineer Agent
          </Title>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Menu
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={navItems}
            style={{ 
              border: 'none',
              background: 'transparent',
              minWidth: '200px'
            }}
            onClick={({ key }) => navigate(key)}
          />
          <Button
            type="text"
            icon={<SettingOutlined />}
            onClick={() => setSettingsVisible(true)}
            style={{ 
              display: 'flex', 
              alignItems: 'center',
              color: '#666'
            }}
          >
            <span className="mobile-hidden">API Keys</span>
          </Button>
        </div>
      </Header>

      <Content 
        style={{ 
          padding: '24px',
          background: '#F0EFE9',
          minHeight: 'calc(100vh - 64px)'
        }}
      >
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          {children}
        </div>
      </Content>

      <Drawer
        title="⚙️ Settings"
        placement="right"
        onClose={() => setSettingsVisible(false)}
        open={settingsVisible}
        width={400}
        styles={{
          body: { padding: 0 }
        }}
      >
        <ApiKeySettings />
      </Drawer>
    </Layout>
  );
}
