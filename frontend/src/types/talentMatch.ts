export interface Skill {
  name: string
  normalizedName: string
  required: boolean
}

export type SkillMatchStatus = 'matched' | 'partial' | 'missing'

export interface SkillMatch {
  skill: Skill
  status: SkillMatchStatus
  matchScore: number
  evidence: Evidence[]
}

export interface Evidence {
  source: 'resume' | 'job_description'
  text: string
  location?: string
}

export interface JobProfile {
  id: string
  title: string
  requiredSkills: Skill[]
  preferredSkills: Skill[]
  minimumExperienceYears?: number
  educationRequirements: string[]
  responsibilities: string[]
}

export interface CandidateProfile {
  id: string
  name: string
  email?: string
  phone?: string
  skills: Skill[]
  experienceYears?: number
  education: string[]
  employmentHistory: string[]
  projects: string[]
  responsibilities: string[]
}

export interface ScoreBreakdown {
  requiredSkills: number
  relevantExperience: number
  responsibilitiesAlignment: number
  education: number
  preferredSkills: number
  total: number
}

export interface CandidateMatch {
  candidate: CandidateProfile
  score: number
  scoreBreakdown: ScoreBreakdown
  skillMatches: SkillMatch[]
  skillGaps: string[]
  evidence: Evidence[]
}