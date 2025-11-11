export interface DocumentData {
  first_name: string;
  middle_name?: string;
  last_name: string;
  date_created: string;
  doc_number: string;
  facility_name: string;
  address: string;
  unit?: string;
  ai_summary: string;
  raw_text: string;
}

export interface FileProcessResult {
  filename: string;
  success: boolean;
  data?: DocumentData;
  error?: string;
  processing_time?: number;
}

export interface ProcessResponse {
  total_files: number;
  processed: number;
  failed: number;
  results: FileProcessResult[];
}

export type UploadStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';

export interface UploadState {
  status: UploadStatus;
  progress?: number;
  results?: ProcessResponse;
  error?: string;
}