import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type { ProcessResponse, FileProcessResult } from '../types/document';

export interface ProgressUpdate {
  type: 'progress';
  current: number;
  total: number;
  filename: string;
  percentage: number;
}

export interface ResultUpdate {
  type: 'result';
  result: FileProcessResult;
}

export interface CompleteUpdate {
  type: 'complete';
  summary: ProcessResponse;
}

export type StreamUpdate = ProgressUpdate | ResultUpdate | CompleteUpdate;

export interface ProgressCallbacks {
  onProgress?: (progress: ProgressUpdate) => void;
  onResult?: (result: ResultUpdate) => void;
  onComplete?: (complete: CompleteUpdate) => void;
  onError?: (error: Error) => void;
}

class APIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = 'http://127.0.0.1:8000') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL,
      timeout: 300000,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  async processDocuments(
    files: File[],
    callbacks?: ProgressCallbacks
  ): Promise<ProcessResponse> {
    const formData = new FormData();
 
    files.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await fetch(`${this.baseURL}/api/process`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let finalResult: ProcessResponse | null = null;

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const update: StreamUpdate = JSON.parse(line);

            switch (update.type) {
              case 'progress':
                callbacks?.onProgress?.(update);
                break;
              case 'result':
                callbacks?.onResult?.(update);
                break;
              case 'complete':
                callbacks?.onComplete?.(update);
                finalResult = update.summary;
                break;
            }
          } catch (parseError) {
            console.error('Failed to parse stream update:', parseError, line);
          }
        }
      }

      if (!finalResult) {
        throw new Error('No final result received from server');
      }

      return finalResult;
    } catch (error) {
      const errorObj = error instanceof Error ? error : new Error('Unknown error');
      callbacks?.onError?.(errorObj);
      throw errorObj;
    }
  }

  async healthCheck(): Promise<{ status: string; version: string }> {
    try {
      const response = await this.client.get('/api/health');
      return response.data;
    } catch (error) {
      throw new Error('Backend service unavailable');
    }
  }
}

export const apiClient = new APIClient();