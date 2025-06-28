import React, { useState } from 'react';
import { Form, Input, Slider, Button, Upload, message, Space, Divider } from 'antd';
import { UploadOutlined, DeleteOutlined, DatabaseOutlined } from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';
import { experimentAPI, fileAPI } from '@/services/api';
import { useExperimentStore } from '@/stores/experimentStore';
import { useExperimentDefaults } from '@/stores/settingsStore';
import { ExampleTaskSelector } from './ExampleTaskSelector';
import type { ExperimentCreateRequest, UploadedFile } from '@/types';

const { TextArea } = Input;

export function ExperimentForm() {
  const [form] = Form.useForm();
  const [showExampleTasks, setShowExampleTasks] = useState(false);
  const {
    uploadedFiles,
    isUploading,
    setCurrentExperiment,
    addUploadedFiles,
    removeUploadedFile,
    setIsUploading,
    setError,
    startExperiment
  } = useExperimentStore();
  const { defaultSteps, defaultEvalCriteria } = useExperimentDefaults();

  const uploadMutation = useMutation({
    mutationFn: fileAPI.upload,
    onMutate: () => {
      setIsUploading(true);
      setError(null);
    },
    onSuccess: (files: UploadedFile[]) => {
      addUploadedFiles(files);
      message.success(`${files.length} file(s) uploaded successfully`);
    },
    onError: (error: Error) => {
      message.error(`Upload failed: ${error.message}`);
      setError(error.message);
    },
    onSettled: () => {
      setIsUploading(false);
    },
  });

  const createExperimentMutation = useMutation({
    mutationFn: experimentAPI.create,
    onSuccess: async (experiment) => {
      setCurrentExperiment(experiment);
      message.success('Experiment created successfully');

      // Start the experiment immediately
      try {
        await experimentAPI.start(experiment.id);
        startExperiment(experiment.steps);
        message.info('Experiment started');
      } catch (error) {
        message.error('Failed to start experiment');
        setError(error instanceof Error ? error.message : 'Unknown error');
      }
    },
    onError: (error: Error) => {
      message.error(`Failed to create experiment: ${error.message}`);
      setError(error.message);
    },
  });

  const handleSubmit = (values: any) => {
    if (uploadedFiles.length === 0) {
      message.warning('Please upload at least one data file');
      return;
    }

    const request: ExperimentCreateRequest = {
      name: values.name || `Experiment ${new Date().toLocaleString()}`,
      goal: values.goal,
      eval: values.eval || undefined,
      steps: values.steps || 10,
      files: uploadedFiles.map(file => file.id),
    };

    createExperimentMutation.mutate(request);
  };

  const handleFileUpload = (info: any) => {
    const { fileList } = info;

    if (fileList.length > 0) {
      const files = fileList
        .filter((file: any) => file.originFileObj)
        .map((file: any) => file.originFileObj);

      if (files.length > 0) {
        uploadMutation.mutate(files);
      }
    }
  };

  const handleRemoveFile = (fileId: string) => {
    removeUploadedFile(fileId);
    message.info('File removed');
  };

  const uploadProps = {
    multiple: true,
    accept: '.csv,.json,.txt,.zip,.md,.xlsx',
    beforeUpload: (file: File) => {
      const isValidSize = file.size <= 100 * 1024 * 1024; // 100MB
      if (!isValidSize) {
        message.error(`${file.name} is too large. Maximum size is 100MB.`);
        return false;
      }
      return false; // Prevent auto upload
    },
    onChange: handleFileUpload,
    showUploadList: false,
  };

  const handleExampleTaskSelect = (task: any, uploadedFiles: UploadedFile[]) => {
    // Add the uploaded files to the store
    addUploadedFiles(uploadedFiles);

    // Extract goal and evaluation from the task
    const goal = task.sections.goal || '';
    const evaluation = task.sections.evaluation || task.sections.evaluation_metric || '';

    // Set form values
    form.setFieldsValue({
      name: task.title,
      goal: goal,
      eval: evaluation,
      steps: 10,
    });

    message.success(`Selected "${task.title}" with ${uploadedFiles.length} files`);
  };

  return (
    <div>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          steps: defaultSteps,
          eval: defaultEvalCriteria
        }}
      >
        <Form.Item
          name="name"
          label="Experiment Name"
        >
          <Input placeholder="e.g., House Price Prediction" />
        </Form.Item>

        <Form.Item
          name="goal"
          label="Goal"
          rules={[{ required: true, message: 'Please enter experiment goal' }]}
        >
          <TextArea
            rows={3}
            placeholder="Example: Predict the sales price for each house"
          />
        </Form.Item>

        <Form.Item
          name="eval"
          label="Evaluation Criteria (Optional)"
        >
          <TextArea
            rows={2}
            placeholder="Example: Use the RMSE metric between the logarithm of the predicted and observed values"
          />
        </Form.Item>

        <Form.Item
          name="steps"
          label="Number of Steps"
        >
          <Slider
            min={1}
            max={20}
            marks={{ 1: '1', 10: '10', 20: '20' }}
            tooltip={{ formatter: (value) => `${value} steps` }}
          />
        </Form.Item>

        <Divider />

        <div style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span style={{ fontWeight: 500 }}>Upload Dataset</span>
            <Button
              type="link"
              size="small"
              icon={<DatabaseOutlined />}
              onClick={() => setShowExampleTasks(true)}
              style={{ padding: 0 }}
            >
              Example Tasks
            </Button>
          </div>

          <Upload {...uploadProps}>
            <Button
              icon={<UploadOutlined />}
              loading={isUploading}
              block
            >
              {isUploading ? 'Uploading...' : 'Upload Files'}
            </Button>
          </Upload>
        </div>

        {uploadedFiles.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>
              Uploaded Files ({uploadedFiles.length}):
            </div>
            <Space direction="vertical" style={{ width: '100%' }}>
              {uploadedFiles.map((file) => (
                <div
                  key={file.id}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 12px',
                    background: '#f6f8fa',
                    borderRadius: 6,
                    fontSize: 12
                  }}
                >
                  <span>📄 {file.originalName}</span>
                  <Button
                    type="text"
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={() => handleRemoveFile(file.id)}
                    style={{ color: '#ff4d4f' }}
                  />
                </div>
              ))}
            </Space>
          </div>
        )}

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            size="large"
            block
            loading={createExperimentMutation.isPending}
            disabled={uploadedFiles.length === 0}
          >
            Run AIDE
          </Button>
        </Form.Item>
      </Form>

      <ExampleTaskSelector
        visible={showExampleTasks}
        onClose={() => setShowExampleTasks(false)}
        onSelect={handleExampleTaskSelect}
      />
    </div>
  );
}
