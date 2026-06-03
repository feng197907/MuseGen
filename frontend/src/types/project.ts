/** Represents a user project container */
export interface Project {
  id: string
  name: string
  description: string
  cover_image: string | null
  status: 'draft' | 'in_progress' | 'completed'
  story_text: string
  created_at: string
  updated_at: string
  storyboard_id: string | null
}

export interface ProjectCreateRequest {
  name: string
  description?: string
  story_text?: string
}

export interface ProjectUpdateRequest {
  name?: string
  description?: string
  story_text?: string
  cover_image?: string
}

/** Storyboard is the sequenced container of shots */
export interface Storyboard {
  id: string
  project_id: string
  shots: Shot[]
  created_at: string
  updated_at: string
}

/** A single shot/scene in the storyboard */
export interface Shot {
  id: string
  storyboard_id: string
  order: number
  title: string
  description: string
  dialogue: string
  shot_type: string
  camera_movement: string
  duration: number
  mood: string
  prompt_override: string | null
  character_ids: string[]
  scene_id: string | null
  keyframe_id: string | null
  status: 'pending' | 'generating' | 'done' | 'failed'
  created_at: string
  updated_at: string
}

export interface ShotUpdateRequest {
  title?: string
  description?: string
  dialogue?: string
  shot_type?: string
  camera_movement?: string
  duration?: number
  mood?: string
  prompt_override?: string
  character_ids?: string[]
  scene_id?: string
}

export interface ShotReorderRequest {
  shot_ids: string[]
}
