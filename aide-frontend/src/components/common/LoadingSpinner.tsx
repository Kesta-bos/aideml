import React from 'react';
import { Spin, Typography } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface LoadingSpinnerProps {
  size?: 'small' | 'default' | 'large';
  message?: string;
  tip?: string;
  spinning?: boolean;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}

export function LoadingSpinner({
  size = 'default',
  message,
  tip,
  spinning = true,
  children,
  style,
}: LoadingSpinnerProps) {
  const antIcon = <LoadingOutlined style={{ fontSize: size === 'large' ? 24 : 16 }} spin />;

  if (children) {
    return (
      <Spin 
        spinning={spinning} 
        indicator={antIcon} 
        tip={tip}
        size={size}
        style={style}
      >
        {children}
      </Spin>
    );
  }

  return (
    <div 
      style={{ 
        textAlign: 'center', 
        padding: '40px 20px',
        ...style 
      }}
      className="loading-spinner"
    >
      <Spin 
        indicator={antIcon} 
        size={size}
      />
      {(message || tip) && (
        <div style={{ marginTop: 16 }}>
          <Text type="secondary">
            {message || tip}
          </Text>
        </div>
      )}
    </div>
  );
}

// Specialized loading components
export function PageLoader({ message = "Loading..." }: { message?: string }) {
  return (
    <LoadingSpinner 
      size="large" 
      message={message}
      style={{ minHeight: '200px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
    />
  );
}

export function InlineLoader({ message }: { message?: string }) {
  return (
    <LoadingSpinner 
      size="small" 
      message={message}
      style={{ padding: '20px' }}
    />
  );
}

export function ButtonLoader() {
  return <Spin size="small" />;
}
