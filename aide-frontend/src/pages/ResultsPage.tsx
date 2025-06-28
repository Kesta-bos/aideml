import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { Card, Spin, Alert } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { experimentAPI } from '@/services/api';
import { ResultsDisplay } from '@/components/results/ResultsDisplay';

export function ResultsPage() {
  const { experimentId } = useParams<{ experimentId: string }>();

  if (!experimentId) {
    return <Navigate to="/" replace />;
  }

  const { 
    data: results, 
    isLoading, 
    error 
  } = useQuery({
    queryKey: ['experiment-results', experimentId],
    queryFn: () => experimentAPI.getResults(experimentId),
    retry: 2,
  });

  if (isLoading) {
    return (
      <Card style={{ textAlign: 'center', padding: '60px 20px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16, color: '#666' }}>
          Loading experiment results...
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <Alert
          message="Error Loading Results"
          description={error instanceof Error ? error.message : 'Failed to load experiment results'}
          type="error"
          showIcon
        />
      </Card>
    );
  }

  if (!results) {
    return (
      <Card style={{ textAlign: 'center', padding: '60px 20px' }}>
        <Alert
          message="No Results Available"
          description="This experiment has not completed yet or results are not available."
          type="info"
          showIcon
        />
      </Card>
    );
  }

  return (
    <div className="fade-in">
      <ResultsDisplay results={results} />
    </div>
  );
}
