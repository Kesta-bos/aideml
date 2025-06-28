import React from 'react';
import { Row, Col, Card } from 'antd';
import { ExperimentForm } from '@/components/experiment/ExperimentForm';
import { ExperimentProgress } from '@/components/experiment/ExperimentProgress';
import { ResultsDisplay } from '@/components/results/ResultsDisplay';
import { useExperimentStore } from '@/stores/experimentStore';

export function ExperimentPage() {
  const { currentExperiment, isRunning, results } = useExperimentStore();

  return (
    <div className="fade-in">
      <Row gutter={[24, 24]}>
        {/* Input Column */}
        <Col xs={24} lg={8}>
          <Card 
            title="Input" 
            style={{ height: 'fit-content' }}
            styles={{
              header: { 
                background: '#fafafa',
                borderBottom: '1px solid #f0f0f0'
              }
            }}
          >
            <ExperimentForm />
          </Card>
        </Col>

        {/* Results Column */}
        <Col xs={24} lg={16}>
          {!currentExperiment ? (
            <Card style={{ textAlign: 'center', padding: '60px 20px' }}>
              <div style={{ color: '#999', fontSize: 16 }}>
                Upload your dataset and configure your experiment to get started
              </div>
            </Card>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              {/* Progress Section */}
              {(isRunning || currentExperiment.status === 'running') && (
                <ExperimentProgress experiment={currentExperiment} />
              )}

              {/* Results Section */}
              {results && (
                <ResultsDisplay results={results} />
              )}

              {/* Experiment Info when not running and no results */}
              {!isRunning && !results && currentExperiment.status === 'pending' && (
                <Card>
                  <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                    <h3 style={{ color: '#0D0F18', marginBottom: 16 }}>
                      🚀 {currentExperiment.name}
                    </h3>
                    <p style={{ color: '#666', marginBottom: 24 }}>
                      Experiment configured and ready to run
                    </p>
                    <div style={{ 
                      background: '#f6f8fa', 
                      padding: 16, 
                      borderRadius: 8,
                      textAlign: 'left'
                    }}>
                      <p><strong>Goal:</strong> {currentExperiment.goal}</p>
                      {currentExperiment.eval && (
                        <p><strong>Evaluation:</strong> {currentExperiment.eval}</p>
                      )}
                      <p><strong>Steps:</strong> {currentExperiment.steps}</p>
                      <p><strong>Files:</strong> {currentExperiment.files.length} uploaded</p>
                    </div>
                  </div>
                </Card>
              )}
            </div>
          )}
        </Col>
      </Row>
    </div>
  );
}
