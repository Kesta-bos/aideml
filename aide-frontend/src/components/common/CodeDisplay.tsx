import React, { useState } from 'react';
import { Card, Button, Typography, Space, message } from 'antd';
import { CopyOutlined, ExpandOutlined, CompressOutlined } from '@ant-design/icons';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco, github } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const { Text } = Typography;

interface CodeDisplayProps {
  code: string;
  language?: string;
  title?: string;
  maxHeight?: number;
  showLineNumbers?: boolean;
  theme?: 'light' | 'dark';
  copyable?: boolean;
  expandable?: boolean;
}

export function CodeDisplay({
  code,
  language = 'python',
  title,
  maxHeight = 400,
  showLineNumbers = true,
  theme = 'light',
  copyable = true,
  expandable = true,
}: CodeDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      message.success('Code copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      message.error('Failed to copy code');
    }
  };

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const getStyle = () => {
    return theme === 'dark' ? github : docco;
  };

  const getHeight = () => {
    if (isExpanded) {
      return 'auto';
    }
    return maxHeight;
  };

  const headerActions = (
    <Space>
      {copyable && (
        <Button
          type="text"
          size="small"
          icon={<CopyOutlined />}
          onClick={handleCopy}
          style={{ color: copied ? '#52c41a' : '#666' }}
        >
          {copied ? 'Copied!' : 'Copy'}
        </Button>
      )}
      {expandable && (
        <Button
          type="text"
          size="small"
          icon={isExpanded ? <CompressOutlined /> : <ExpandOutlined />}
          onClick={toggleExpanded}
          style={{ color: '#666' }}
        >
          {isExpanded ? 'Collapse' : 'Expand'}
        </Button>
      )}
    </Space>
  );

  const content = (
    <SyntaxHighlighter
      language={language}
      style={getStyle()}
      showLineNumbers={showLineNumbers}
      customStyle={{
        maxHeight: getHeight(),
        overflow: 'auto',
        margin: 0,
        borderRadius: 6,
        fontSize: 13,
        lineHeight: 1.5,
      }}
      codeTagProps={{
        style: {
          fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
        }
      }}
    >
      {code}
    </SyntaxHighlighter>
  );

  if (title) {
    return (
      <Card
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text strong>{title}</Text>
            {headerActions}
          </div>
        }
        size="small"
      >
        {content}
      </Card>
    );
  }

  return (
    <div style={{ position: 'relative' }}>
      {(copyable || expandable) && (
        <div style={{ 
          position: 'absolute', 
          top: 8, 
          right: 8, 
          zIndex: 10,
          background: 'rgba(255, 255, 255, 0.9)',
          borderRadius: 4,
          padding: 4,
        }}>
          {headerActions}
        </div>
      )}
      {content}
    </div>
  );
}

// Specialized components for common use cases
export function PythonCodeDisplay(props: Omit<CodeDisplayProps, 'language'>) {
  return <CodeDisplay {...props} language="python" />;
}

export function YamlCodeDisplay(props: Omit<CodeDisplayProps, 'language'>) {
  return <CodeDisplay {...props} language="yaml" />;
}

export function JsonCodeDisplay(props: Omit<CodeDisplayProps, 'language'>) {
  return <CodeDisplay {...props} language="json" />;
}
