const API_BASE_URL = 'http://localhost:8000'

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: 'include',
  })

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`

    try {
      const data = await response.json()

      if (typeof data.detail === 'string') {
        message = data.detail
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(message)
  }

  return response.json() as Promise<T>
}

export interface AuthUser {
  id: number
  email: string
  name: string
  created_at: string
}

export interface AuthResponse {
  user: AuthUser
}

export interface JobDescriptionResponse {
  id: number
  text: string
  created_at: string
}

export interface JobListResponse {
  jobs: JobDescriptionResponse[]
}

export interface JobProfileResponse {
  id: number
  job_id: number
  title: string | null
  required_skills: BackendSkill[]
  preferred_skills: BackendSkill[]
  minimum_experience_years: number | null
  education_requirements: string[]
  responsibilities: string[]
  evidence: BackendEvidence[]
}

export interface JobCreatedResponse {
  job: JobDescriptionResponse
  profile: JobProfileResponse
}

export interface BackendEvidence {
  text: string
  location: string | null
}

export interface BackendSkill {
  name: string
  normalized_name: string
  required: boolean
  evidence: BackendEvidence[]
}

export interface CandidateResponse {
  id: number
  job_id: number
  source_filename: string
  profile: Record<string, unknown>
  processing_status: string
  error: string | null
  created_at: string
}

export interface RequiredSkillCoverage {
  matched: number
  total: number
  percentage: number
}

export interface CandidateResultResponse {
  candidate: CandidateResponse
  rank: number | null
  overall_score: number | null
  required_skill_coverage: RequiredSkillCoverage | null
  match_result: Record<string, unknown>
  score_breakdown: Record<string, unknown>
}

export interface CandidateListResponse {
  candidates: CandidateResultResponse[]
}

export interface CandidateComparisonResponse {
  candidates: CandidateResultResponse[]
}

export interface CandidateExplanationResponse {
  candidate_id: number
  explanation: string
  model: string
}

export interface CandidateComparisonExplanationResponse {
  candidate_ids: number[]
  explanation: string
  model: string
}

export async function register(
  name: string,
  email: string,
  password: string,
): Promise<AuthResponse> {
  return request<AuthResponse>('/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name,
      email,
      password,
    }),
  })
}

export async function login(
  email: string,
  password: string,
): Promise<AuthResponse> {
  return request<AuthResponse>('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
    }),
  })
}

export async function getCurrentUser(): Promise<AuthUser> {
  return request<AuthUser>('/auth/me')
}

export async function logout(): Promise<void> {
  await request('/auth/logout', {
    method: 'POST',
  })
}

export async function createJob(
  text: string,
): Promise<JobCreatedResponse> {
  return request<JobCreatedResponse>('/jobs', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  })
}

export async function uploadJob(
  file: File,
): Promise<JobCreatedResponse> {
  const formData = new FormData()
  formData.append('file', file)

  return request<JobCreatedResponse>('/jobs/upload', {
    method: 'POST',
    body: formData,
  })
}

export async function getJobHistory(): Promise<JobListResponse> {
  return request<JobListResponse>('/jobs')
}

export async function getJob(
  jobId: number,
): Promise<JobDescriptionResponse> {
  return request<JobDescriptionResponse>(
    `/jobs/${jobId}`,
  )
}

export async function uploadResumes(
  jobId: number,
  files: File[],
): Promise<CandidateListResponse> {
  const formData = new FormData()

  for (const file of files) {
    formData.append('resumes', file)
  }

  return request<CandidateListResponse>(
    `/jobs/${jobId}/resumes`,
    {
      method: 'POST',
      body: formData,
    },
  )
}

export async function getCandidates(
  jobId: number,
): Promise<CandidateListResponse> {
  return request<CandidateListResponse>(
    `/jobs/${jobId}/candidates`,
  )
}

export async function getJobProfile(
  jobId: number,
): Promise<JobProfileResponse> {
  return request<JobProfileResponse>(
    `/jobs/${jobId}/profile`,
  )
}

export async function getCandidate(
  jobId: number,
  candidateId: number,
): Promise<CandidateResultResponse> {
  return request<CandidateResultResponse>(
    `/jobs/${jobId}/candidates/${candidateId}`,
  )
}

export async function compareCandidates(
  jobId: number,
  candidateIds: number[],
): Promise<CandidateComparisonResponse> {
  return request<CandidateComparisonResponse>(
    `/jobs/${jobId}/candidates/compare`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        candidate_ids: candidateIds,
      }),
    },
  )
}

export async function getCandidateExplanation(
  jobId: number,
  candidateId: number,
): Promise<CandidateExplanationResponse> {
  return request<CandidateExplanationResponse>(
    `/jobs/${jobId}/candidates/${candidateId}/explanation`,
  )
}

export async function getComparisonExplanation(
  jobId: number,
  candidateIds: number[],
): Promise<CandidateComparisonExplanationResponse> {
  return request<CandidateComparisonExplanationResponse>(
    `/jobs/${jobId}/candidates/compare/explanation`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        candidate_ids: candidateIds,
      }),
    },
  )
}