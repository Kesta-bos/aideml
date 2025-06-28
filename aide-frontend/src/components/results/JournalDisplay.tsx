import React from 'react';
import { Card, Timeline, Typography, Tag, Statistic, Row, Col, Empty } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import type { Journal } from '@/types';

const { Text, Paragraph } = Typography;

interface JournalDisplayProps {
  journal: Journal;
}

export function JournalDisplay({ journal }: JournalDisplayProps) {
  if (!journal.nodes || journal.nodes.length === 0) {
    return (
      <Card>
        <Empty 
          description="No journal entries available"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  }

  const timelineItems = journal.nodes.map((node) => ({
    key: node.id,
    dot: node.isBuggy ? (
      <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
    ) : (
      <CheckCircleOutlined style={{ color: '#52c41a' }} />
    ),
    children: (
      <Card 
        size="small" 
        style={{ marginBottom: 16 }}
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Step {node.step}</span>
            <div>
              {node.isBuggy && (
                <Tag color="error" style={{ marginRight: 8 }}>
                  Buggy
                </Tag>
              )}
              {node.execTime && (
                <Tag color="blue">
                  {node.execTime.toFixed(2)}s
                </Tag>
              )}
            </div>
          </div>
        }
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <div style={{ marginBottom: 16 }}>
              {node.metric && (
                <Statistic
                  title="Metric"
                  value={node.metric.value}
                  precision={4}
                  valueStyle={{ 
                    color: node.isBuggy ? '#ff4d4f' : '#3f8600',
                    fontSize: 16
                  }}
                />
              )}
            </div>
            
            {node.analysis && (
              <div style={{ marginBottom: 16 }}>
                <Text strong style={{ display: 'block', marginBottom: 8 }}>
                  Analysis:
                </Text>
                <Paragraph style={{ fontSize: 13, margin: 0 }}>
                  {node.analysis}
                </Paragraph>
              </div>
            )}

            {node.termOut && node.termOut.length > 0 && (
              <div>
                <Text strong style={{ display: 'block', marginBottom: 8 }}>
                  Output:
                </Text>
                <div style={{ 
                  background: '#f6f8fa', 
                  padding: 12, 
                  borderRadius: 6,
                  fontSize: 12,
                  fontFamily: 'monospace',
                  maxHeight: 150,
                  overflow: 'auto'
                }}>
                  {node.termOut.slice(-5).map((line, idx) => (
                    <div key={idx}>{line}</div>
                  ))}
                </div>
              </div>
            )}
          </Col>
          
          <Col xs={24} lg={12}>
            <Text strong style={{ display: 'block', marginBottom: 8 }}>
              Generated Code:
            </Text>
            <SyntaxHighlighter
              language="python"
              style={docco}
              customStyle={{
                maxHeight: '300px',
                overflow: 'auto',
                fontSize: 11,
                margin: 0,
              }}
            >
              {node.code.length > 500 ? 
                node.code.substring(0, 500) + '\n# ... (truncated)' : 
                node.code
              }
            </SyntaxHighlighter>
          </Col>
        </Row>
      </Card>
    ),
  }));

  return (
    <Card>
      <div style={{ marginBottom: 16 }}>
        <Text strong>
          Experiment Journal ({journal.nodes.length} steps)
        </Text>
        <Text type="secondary" style={{ display: 'block', fontSize: 12 }}>
          Created: {new Date(journal.createdAt).toLocaleString()}
        </Text>
      </div>
      
      <Timeline
        mode="left"
        items={timelineItems}
        style={{ marginTop: 16 }}
      />
    </Card>
  );
}
