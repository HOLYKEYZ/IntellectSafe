import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface ScanPromptRequest {
  prompt: string
  user_id?: string
  session_id?: string
  metadata?: Record<string, any>
}

export interface ScanResponse {
  scan_request_id: string
  verdict: 'blocked' | 'allowed' | 'flagged' | 'sanitized'
  risk_score: number
  risk_level: 'safe' | 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  explanation: string
  signals: Record<string, any>
  false_positive_probability?: number
  timestamp: string
}

export interface RiskScore {
  id: string
  scan_request_id: string
  module_type: string
  risk_score: number
  risk_level: string
  confidence: number
  verdict: string
  explanation: string
  created_at: string
}

export interface AuditLog {
  id: string
  created_at: string
  action_type: string
  actor?: string
  resource_type: string
  resource_id?: string
  description: string
  metadata?: Record<string, any>
}

export const scanPrompt = async (request: ScanPromptRequest): Promise<ScanResponse> => {
  const response = await api.post<ScanResponse>('/scan/prompt', request)
  return response.data
}

export const scanOutput = async (request: {
  output: string
  original_prompt?: string
  user_id?: string
  session_id?: string
}): Promise<ScanResponse> => {
  const response = await api.post<ScanResponse>('/scan/output', request)
  return response.data
}

export const scanContent = async (request: {
  content: string
  content_type: 'text' | 'image' | 'video' | 'audio'
  user_id?: string
  session_id?: string
  metadata?: Record<string, any>
}): Promise<ScanResponse> => {
  const response = await api.post<ScanResponse>('/scan/content', request)
  return response.data
}

export const getRiskScores = async (params?: {
  scan_request_id?: string
  module_type?: string
  limit?: number
  offset?: number
}): Promise<RiskScore[]> => {
  const response = await api.get<RiskScore[]>('/audit/risk-scores', { params })
  return response.data
}

export const getAuditLogs = async (params?: {
  limit?: number
  offset?: number
  action_type?: string
  resource_type?: string
}): Promise<AuditLog[]> => {
  const response = await api.get<AuditLog[]>('/audit/logs', { params })
  return response.data
}

export const getRiskReport = async (days: number = 7) => {
  const response = await api.get('/governance/risk/report', { params: { days } })
  return response.data
}

export const getSafetyScore = async (days: number = 7) => {
  const response = await api.get('/governance/risk/score', { params: { days } })
  return response.data
}

// Auth API
export interface LoginRequest {
  username: string  // email
  password: string
}

export interface SignupRequest {
  email: string
  password: string
  full_name?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export const login = async (request: LoginRequest): Promise<AuthResponse> => {
  // OAuth2 form data format
  const formData = new URLSearchParams()
  formData.append('username', request.username)
  formData.append('password', request.password)
  
  const response = await api.post<AuthResponse>('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
  return response.data
}

export const signup = async (request: SignupRequest): Promise<any> => {
  const response = await api.post('/auth/signup', request)
  return response.data
}

export default api


