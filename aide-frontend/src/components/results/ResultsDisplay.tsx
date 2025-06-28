import React from 'react';
import { Card, Tabs, Statistic, Typography, Alert, Empty } from 'antd';
import { CheckCircleOutlined, TrophyOutlined } from '@ant-design/icons';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { TreeVisualization } from './TreeVisualization';
import { JournalDisplay } from './JournalDisplay';
import { ConfigDisplay } from './ConfigDisplay';
import { MetricsChart } from '@/components/charts/MetricsChart';
import type { ExperimentResults } from '@/types';

const { Text, Title } = Typography;

interface ResultsDisplayProps {
  results: ExperimentResults;
}

export function ResultsDisplay({ results }: ResultsDisplayProps) {
  const items = [
    {
      key: 'tree',
      label: (
        <span>
          🌳 Tree Visualization
        </span>
      ),
      children: <TreeVisualization htmlContent={results.treeVisualization} />,
    },
    {
      key: 'solution',
      label: (
        <span>
          <TrophyOutlined /> Best Solution
        </span>
      ),
      children: (
        <Card>
          {results.bestSolution ? (
            <>
              <div style={{ marginBottom: 24 }}>
                <Statistic
                  title="Best Validation Score"
                  value={results.bestSolution.metric.value}
                  precision={4}
                  valueStyle={{ color: '#3f8600' }}
                  prefix={<CheckCircleOutlined />}
                />
                {results.totalTime && (
                  <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
                    Total execution time: {results.totalTime.toFixed(1)}s
                  </Text>
                )}
              </div>

              <div>
                <Title level={5} style={{ marginBottom: 16 }}>
                  Generated Code:
                </Title>
                <SyntaxHighlighter
                  language="python"
                  style={docco}
                  customStyle={{
                    maxHeight: '500px',
                    overflow: 'auto',
                    borderRadius: 8,
                    fontSize: 13,
                  }}
                  showLineNumbers
                >
                  {results.bestSolution.code}
                </SyntaxHighlighter>
              </div>
            </>
          ) : (
            <Empty
              description="No solution available"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          )}
        </Card>
      ),
    },
    {
      key: 'config',
      label: (
        <span>
          ⚙️ Config
        </span>
      ),
      children: <ConfigDisplay config={results.config} />,
    },
    {
      key: 'journal',
      label: (
        <span>
          📋 Journal
        </span>
      ),
      children: <JournalDisplay journal={results.journal} />,
    },
    {
      key: 'validation',
      label: (
        <span>
          📊 Validation
        </span>
      ),
      children: (
        <div>
          {results.bestMetric && (
            <Card style={{ marginBottom: 16 }}>
              <div style={{ textAlign: 'center', padding: '20px' }}>
                <Statistic
                  title="Best Validation Score"
                  value={results.bestMetric.value}
                  precision={4}
                  valueStyle={{ color: '#3f8600', fontSize: 24 }}
                />
                <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
                  {results.bestMetric.maximize ? 'Higher is better' : 'Lower is better'}
                </Text>
              </div>
            </Card>
          )}

          {results.journal.nodes.length > 0 ? (
            <MetricsChart
              nodes={results.journal.nodes}
              title="Validation Progress"
            />
          ) : (
            <Card>
              <Empty
                description="No validation metrics available"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            </Card>
          )}
        </div>
      ),
    },
  ];

  return (
    <Card className="fade-in">
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={4} style={{ margin: 0 }}>
            Experiment Results
          </Title>
          <div style={{ textAlign: 'right' }}>
            <Text strong style={{ color: '#52c41a' }}>
              {results.status.toUpperCase()}
            </Text>
            {results.completedAt && (
              <Text type="secondary" style={{ display: 'block', fontSize: 12 }}>
                Completed: {new Date(results.completedAt).toLocaleString()}
              </Text>
            )}
          </div>
        </div>

        {results.status === 'failed' && (
          <Alert
            message="Experiment Failed"
            description="The experiment encountered an error during execution."
            type="error"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </div>

      <Tabs
        items={items}
        defaultActiveKey="solution"
        size="large"
        tabBarStyle={{ marginBottom: 24 }}
      />
    </Card>
  );
}
