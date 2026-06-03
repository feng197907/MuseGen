/** Character asset — an anime character with reference image */
export interface Character {
  id: string
  project_id: string
  name: string
  description: string
  appearance: string
  personality: string
  image_url: string | null
  thumbnail_url: string | null
  reference_prompt: string
  voice_profile_id: string | null
  status: 'pending' | 'generating' | 'done' | 'failed'
  created_at: string
  updated_at: string
}

/** Scene / background asset */
export interface Scene {
  id: string
  project_id: string
  name: string
  description: string
  setting: string
  time_of_day: string
  weather: string
  image_url: string | null
  thumbnail_url: string | null
  reference_prompt: string
  status: 'pending' | 'generating' | 'done' | 'failed'
  created_at: string
  updated_at: string
}

/** Keyframe generated for a shot */
export interface KeyFrame {
  id: string
  shot_id: string
  image_url: string
  thumbnail_url: string
  prompt: string
  width: number
  height: number
  created_at: string
}

/** Animation clip generated from a keyframe */
export interface Animation {
  id: string
  keyframe_id: string
  video_url: string
  duration: number
  fps: number
  created_at: string
}

export type AssetStatus = 'pending' | 'generating' | 'done' | 'failed'
