/**
 * API Client for SecureScan.ai Backend
 * 
 * This file provides type-safe API functions to interact with the FastAPI backend.
 * Your v0.dev components should import these functions to communicate with the backend.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Type definitions matching the Python backend data contract
export interface SecurityFinding {
  rule_id: string;
  severity: 'High' | 'Medium' | 'Low';
  cwe: string[];
  location: {
    file: string;
    line: number;
  };
  suggestion: string;
  codeSnippet: string;
}

export interface UploadResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface ScanStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  total_findings?: number;
}

/**
 * Upload a Python file for security analysis
 * @param file - The file to upload (.py files only)
 * @returns Upload response with job_id
 */
export async function uploadFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<UploadResponse>('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

/**
 * Check the status of a scan job
 * @param jobId - The job ID returned from uploadFile
 * @returns Current scan status
 */
export async function getScanStatus(jobId: string): Promise<ScanStatus> {
  const response = await apiClient.get<ScanStatus>(`/api/status/${jobId}`);
  return response.data;
}

/**
 * Get analysis results for a completed scan
 * @param jobId - The job ID returned from uploadFile
 * @returns Array of security findings
 */
export async function getResults(jobId: string): Promise<SecurityFinding[]> {
  const response = await apiClient.get<SecurityFinding[]>(`/api/results/${jobId}`);
  return response.data;
}

/**
 * Health check endpoint
 * @returns API health status
 */
export async function healthCheck(): Promise<any> {
  const response = await apiClient.get('/');
  return response.data;
}

export default apiClient;
