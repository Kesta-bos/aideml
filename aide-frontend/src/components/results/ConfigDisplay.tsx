import React from 'react';
import { Card, Typography, Empty } from 'antd';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const { Text } = Typography;

interface ConfigDisplayProps {
  config: Record<string, any>;
}

export function ConfigDisplay({ config }: ConfigDisplayProps) {
  if (!config || Object.keys(config).length === 0) {
    return (
      <Card>
        <Empty 
          description="No configuration available"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  }

  // Convert config to YAML-like format for display
  const formatConfig = (obj: any, indent = 0): string => {
    const spaces = '  '.repeat(indent);
    let result = '';
    
    for (const [key, value] of Object.entries(obj)) {
      if (value === null || value === undefined) {
        result += `${spaces}${key}: null\n`;
      } else if (typeof value === 'object' && !Array.isArray(value)) {
        result += `${spaces}${key}:\n`;
        result += formatConfig(value, indent + 1);
      } else if (Array.isArray(value)) {
        result += `${spaces}${key}:\n`;
        value.forEach((item, idx) => {
          if (typeof item === 'object') {
            result += `${spaces}  - \n`;
            result += formatConfig(item, indent + 2);
          } else {
            result += `${spaces}  - ${item}\n`;
          }
        });
      } else if (typeof value === 'string') {
        result += `${spaces}${key}: "${value}"\n`;
      } else {
        result += `${spaces}${key}: ${value}\n`;
      }
    }
    
    return result;
  };

  const configText = formatConfig(config);

  return (
    <Card>
      <div style={{ marginBottom: 16 }}>
        <Text strong>Experiment Configuration</Text>
        <Text type="secondary" style={{ display: 'block', fontSize: 12 }}>
          Configuration used for this experiment
        </Text>
      </div>
      
      <SyntaxHighlighter
        language="yaml"
        style={docco}
        customStyle={{
          maxHeight: '500px',
          overflow: 'auto',
          borderRadius: 8,
          fontSize: 13,
        }}
        showLineNumbers
      >
        {configText}
      </SyntaxHighlighter>
    </Card>
  );
}
