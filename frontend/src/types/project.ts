/** Represents a user project container */
export interface Project {
  id: string
  name: string
  description: string
  coverImage: string | null
  status: 'draft' | 'in_progress' | 'completed'
  storyText: string
  createdAt: string
  updatedAt: string
  storyboardId: string | null
}

export interface ProjectCreateRequest {
  name: string
  description?: string
  storyText?: string
}

export interface ProjectUpdateRequest {
  name?: string
  description?: string
  storyText?: string
  coverImage?: string
}

/** Storyboard is the sequenced container of shots */
export interface Storyboard {
  id: string
  projectId: string
  shots: Shot[]
  createdAt: string
  updatedAt: string
}

/** A single shot/scene in the storyboard */
export interface Shot {
  id: string
  storyboardId: string
  order: number
  title: string
  description: string
  dialogue: string
  shotType: string
  cameraMovement: string
  duration: number
  mood: string
  promptOverride: string | null
  characterIds: string[]
  sceneId: string | null
  keyframeId: string | null
  status: 'pending' | 'generating' | 'done' | 'failed'
  createdAt: string
  updatedAt: string
}

export interface ShotUpdateRequest {
  title?: string
  description?: string
  dialogue?: string
  shotType?: string
  cameraMovement?: string
  duration?: number
  mood?: string
  promptOverride?: string
  characterIds?: string[]
  sceneId?: string
}

export interface ShotReorderRequest {
  shotIds: string[]
}
