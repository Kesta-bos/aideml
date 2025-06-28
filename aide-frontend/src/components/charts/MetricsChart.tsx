import React from 'react';
import { Card, Empty, Typography } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { Node } from '@/types';

const { Text } = Typography;

interface MetricsChartProps {
  nodes: Node[];
  title?: string;
}

export function MetricsChart({ nodes, title = "Validation Metrics" }: MetricsChartProps) {
  // Filter nodes with valid metrics
  const validNodes = nodes.filter(node => 
    node.metric && 
    node.metric.value !== null && 
    node.metric.value !== undefined &&
    !node.isBuggy
  );

  if (validNodes.length === 0) {
    return (
      <Card title={title}>
        <Empty 
          description="No metric data available"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  }

  // Prepare data for chart
  const chartData = validNodes.map(node => ({
    step: node.step,
    metric: node.metric!.value,
    isBest: false, // Will be set below
  }));

  // Find best metric value
  const isMaximize = validNodes[0]?.metric?.maximize ?? true;
  const bestValue = isMaximize 
    ? Math.max(...chartData.map(d => d.metric!))
    : Math.min(...chartData.map(d => d.metric!));

  // Mark best points
  chartData.forEach(point => {
    point.isBest = point.metric === bestValue;
  });

  const formatTooltip = (value: any, name: string) => {
    if (name === 'metric') {
      return [value?.toFixed(4), 'Metric Value'];
    }
    return [value, name];
  };

  const formatYAxis = (value: number) => {
    return value.toFixed(3);
  };

  return (
    <Card title={title}>
      <div style={{ marginBottom: 16 }}>
        <Text type="secondary" style={{ fontSize: 12 }}>
          {validNodes.length} data points • {isMaximize ? 'Higher is better' : 'Lower is better'}
        </Text>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="step" 
            stroke="#666"
            fontSize={12}
            label={{ value: 'Step', position: 'insideBottom', offset: -5 }}
          />
          <YAxis 
            stroke="#666"
            fontSize={12}
            tickFormatter={formatYAxis}
            label={{ value: 'Metric', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip 
            formatter={formatTooltip}
            labelFormatter={(label) => `Step ${label}`}
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #d9d9d9',
              borderRadius: 6,
              fontSize: 12,
            }}
          />
          <Line 
            type="monotone" 
            dataKey="metric" 
            stroke="#1890ff" 
            strokeWidth={2}
            dot={{ fill: '#1890ff', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#1890ff', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>

      <div style={{ 
        marginTop: 16, 
        padding: 12, 
        background: '#f6f8fa', 
        borderRadius: 6,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <Text strong style={{ color: '#52c41a' }}>
            Best: {bestValue.toFixed(4)}
          </Text>
        </div>
        <div>
          <Text type="secondary" style={{ fontSize: 12 }}>
            Latest: {chartData[chartData.length - 1]?.metric.toFixed(4)}
          </Text>
        </div>
      </div>
    </Card>
  );
}
